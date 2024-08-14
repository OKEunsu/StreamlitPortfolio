import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def format_value(value):
    if isinstance(value, (int, float)):
        if value >= 1e12:
            return f"{value / 1e12:.2f}조"  # 조 단위
        elif value >= 1e9:
            return f"{value / 1e9:.2f}억"  # 십억 단위
        elif value >= 1e6:
            return f"{value / 1e6:.1f}백만"  # 백만 단위
        elif value >= 1e3:
            return f"{value / 1e3:.2f}천"  # 천 단위
        else:
            return f"{value:.2f}원"
    else:
        return "N/A"
@st.cache_data
def get_krw_usd():
    ticker = 'KRW=X'
    data = yf.Ticker(ticker).history(period="1d")
    latest_data = data.iloc[-1]
    return latest_data['Close']
@st.cache_data
def stock_df(labels, KRW):
    data_frames = []
    all_dates = set()

    for symbol in labels:
        try:
            ticker = yf.Ticker(symbol)
            stock_data = ticker.history(interval='1d', period='max')
            stock_data.index = pd.to_datetime(stock_data.index.strftime('%Y-%m-%d'))

            if stock_data.empty:
                print(f"No data for {symbol}")
                continue

            # 열 이름을 심볼과 연결하여 중복되지 않도록 함
            stock_data.columns = [f"{symbol}_{col}" for col in stock_data.columns]

            # 미국 주식에 대해 환율 변환 적용
            if not symbol.endswith(('.KS', '.KQ')):
                stock_data = stock_data * KRW

            # 모든 날짜를 수집
            all_dates.update(stock_data.index)

            # 데이터 프레임을 리스트에 추가
            data_frames.append(stock_data)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    if not data_frames:
        raise ValueError("No data frames were created. Check the symbols and internet connection.")

    # 모든 날짜를 인덱스로 사용하여 빈 데이터 프레임 생성
    all_dates = sorted(all_dates)  # 날짜를 정렬
    combined_data = pd.DataFrame(index=all_dates)

    # 모든 데이터 프레임을 날짜 기준으로 합침
    for df in data_frames:
        combined_data = combined_data.join(df, how='outer')

    # 결측값 없는 행만 추출
    result_df = combined_data.dropna()

    return result_df

@st.cache_data
def sharp_ratio(data, stocks, having_qty, stock_prices, krw_usd_rate):
    dataframe = pd.DataFrame(index=data.index)

    for stock in stocks:
        dataframe[stock] = data[f'{stock}_Close']

    daily_ret = dataframe.pct_change()  # 일간 수익률
    annual_ret = daily_ret.mean() * 252  # 연간 수익률
    daily_cov = daily_ret.cov()  # 일간 리스크
    annual_cov = daily_cov * 252  # 연간 리스크

    port_ret = []
    port_risk = []
    port_weights = []
    sharpe_ratio = []

    # 몬테카를로 시뮬레이션
    for _ in range(2000):
        weights = np.random.random(len(stocks))
        weights /= np.sum(weights)

        returns = np.dot(weights, annual_ret)
        risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

        port_ret.append(returns)
        port_risk.append(risk)
        port_weights.append(weights)
        sharpe_ratio.append(returns / risk)

    portfolio = {'Returns': port_ret, 'Risk': port_risk, 'Sharpe': sharpe_ratio}

    for i, s in enumerate(stocks):
        portfolio[s] = [weight[i] for weight in port_weights]

    df = pd.DataFrame(portfolio)
    df = df[['Returns', 'Risk', 'Sharpe'] + [s for s in stocks]]

    max_sharpe = df.loc[df['Sharpe'] == df['Sharpe'].max()].reset_index(drop=True)
    min_risk = df.loc[df['Risk'] == df['Risk'].min()].reset_index(drop=True)
    st.session_state.max_sharpe = max_sharpe
    st.session_state.min_risk = min_risk

    # 환율을 사용하여 가격 변환
    stock_prices_krw = []
    for price, symbol in zip(stock_prices, stocks):
        if symbol.endswith(('.KS', '.KQ')):
            stock_prices_krw.append(price)
        else:
            stock_prices_krw.append(price * krw_usd_rate)

    # 각 주식의 현재 가치 계산
    current_values = [qty * price for qty, price in zip(having_qty, stock_prices_krw)]

    # 전체 자산 가치 계산
    total_value = sum(current_values)

    # 각 주식의 비중 계산
    hav_weights = [value / total_value for value in current_values]

    # 포트폴리오의 예상 수익률 계산
    hav_ret = np.dot(annual_ret, hav_weights)
    # 포트폴리오의 예상 리스크 계산
    hav_cov = np.dot(hav_weights, np.dot(annual_cov, hav_weights))
    hav_risk = np.sqrt(hav_cov)

    # 샤프 지수 계산
    hav_sharpe = hav_ret / hav_risk

    st.write("Your Portfolio")
    port_df = pd.DataFrame([[hav_ret, hav_risk, hav_sharpe] + hav_weights], columns = ['Returns', 'Risk', 'Sharpe'] + stocks)

    st.dataframe(port_df, use_container_width = True, hide_index=True)
    st.session_state.port_df = port_df
    st.write("Max Sharp Ratio")
    st.dataframe(round(max_sharpe, 4), use_container_width=True, hide_index=True)
    st.write("Min Risk")
    st.dataframe(round(min_risk, 4), use_container_width=True, hide_index=True)

    # minimum-variance portfolio와 mean-variance portfolio 시각화
    # plotly로 그래프 그리기
    fig = go.Figure()

    # 모든 포트폴리오를 산점도로 추가
    fig.add_trace(go.Scatter(x=df['Risk'], y=df['Returns'], mode='markers',
                             marker=dict(color=df['Sharpe'], colorscale='Viridis', size=10,
                                         line=dict(color='black', width=0.5)),
                             name='Portfolios'))

    # 최적 포트폴리오 표시
    fig.add_trace(go.Scatter(x=max_sharpe['Risk'], y=max_sharpe['Returns'], mode='markers',
                             marker=dict(color='red', symbol='star', size=24, line=dict(color='black', width=2)),
                             name='Max Sharpe Ratio'))

    # 최소 리스크 포트폴리오 표시
    fig.add_trace(go.Scatter(x=min_risk['Risk'], y=min_risk['Returns'], mode='markers',
                             marker=dict(color='blue', symbol='x', size=20, line=dict(color='black', width=2)),
                             name='Min Risk'))

    # 현재 포트폴리오 표시
    fig.add_trace(go.Scatter(x=[hav_risk], y=[hav_ret], mode='markers',
                             marker=dict(color='white', symbol='circle', size=20, line=dict(color='black', width=2)),
                             name='Current Portfolio'))

    # 레이아웃 설정
    fig.update_layout(title='Portfolio Optimization',
                      xaxis_title='Risk',
                      yaxis_title='Expected Returns',
                      width=900, height=600)

    # plotly 그림 출력
    return fig

def make_df(stock_df, ratio, labels, money):
    close_columns = [label + '_Close' for label in labels]
    if isinstance(ratio, pd.DataFrame):
        portfolio_series = ratio.iloc[0]
    else:
        portfolio_series = pd.Series(ratio, index=labels)

    portfolio_series.index = portfolio_series.index + '_Close'
    close_prices = stock_df[close_columns].iloc[0]

    shares = money * portfolio_series / close_prices

    portfolio_value = pd.DataFrame(index=stock_df.index)
    for ticker in shares.index:
        close_col = ticker.replace('_Close', '')
        div_col = ticker.replace('_Close', '_Dividends')

        portfolio_value[ticker.replace('_Close', '_Value')] = shares[ticker] * stock_df[ticker]
        if div_col in stock_df.columns:
            portfolio_value[ticker.replace('_Close', '_Dividends')] = shares[ticker] * stock_df[div_col]

    value_cols = portfolio_value.filter(regex='_Value').columns
    dividend_cols = portfolio_value.filter(regex='_Dividends').columns
    portfolio_value['TotalValue'] = portfolio_value[value_cols].sum(axis=1) + portfolio_value[dividend_cols].sum(axis=1)
    portfolio_value['DailyReturns'] = portfolio_value['TotalValue'].pct_change()

    return portfolio_value
# 예시 mdd_stock 함수
def mdd_stock(dataframe):
    window = 252
    peak = dataframe['TotalValue'].rolling(window, min_periods=1).max()
    drawdown = dataframe['TotalValue'] / peak - 1.0
    max_dd = drawdown.rolling(window, min_periods=1).min()

    trace_drawdown = go.Scatter(x=drawdown.index, y=drawdown.values, mode='lines', name='DD',
                                line=dict(color='#0063B2'))
    trace_max_dd = go.Scatter(x=max_dd.index, y=max_dd.values, mode='lines', name='MDD', line=dict(color='#9CC3D5'))

    layout = go.Layout(
        title="DD & MDD",
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price'),
        showlegend=True,
        template='plotly'
    )
    data = [trace_drawdown, trace_max_dd]
    fig = go.Figure(data=data, layout=layout)
    return fig, max_dd

if "stock_list" in st.session_state and st.session_state.stock_list:
    st.title('포트폴리오 평가(샤프지수)')
    labels = [stock['stock_name'] for stock in st.session_state.stock_list]
    stock_mean_price = [stock['stock_price'] for stock in st.session_state.stock_list]
    qtys = [stock['stock_num'] for stock in st.session_state.stock_list]
    krw_usd_rate = get_krw_usd()
    df = stock_df(labels, krw_usd_rate)

    fig = sharp_ratio(df, labels, qtys, stock_mean_price, krw_usd_rate)
    st.subheader('Sharp Portfolio')
    st.plotly_chart(fig)

    st.subheader('수익률 분석')
    money = 10000000 # 백만

    # 포트폴리오 데이터프레임 생성
    max_sharpe_df = st.session_state.max_sharpe
    max_sharpe_df = max_sharpe_df[labels]

    min_risk_df = st.session_state.min_risk
    min_risk_df = min_risk_df[labels]

    prot_df = st.session_state.port_df
    prot_df = prot_df[labels]

    # 포트폴리오 가치 계산
    p1 = make_df(df, prot_df.iloc[0], labels, money)
    p2 = make_df(df, max_sharpe_df.iloc[0], labels, money)
    p3 = make_df(df, min_risk_df.iloc[0], labels, money)
    p4 = make_df(df, [1 / len(labels)] * len(labels), labels, money)  # 균등 비중으로 설정

    # 그래프 생성
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=p1.index, y=p1['TotalValue'], mode='lines', name='Your Portfolio'))
    fig.add_trace(go.Scatter(x=p2.index, y=p2['TotalValue'], mode='lines', name='Max Sharpe Ratio'))
    fig.add_trace(go.Scatter(x=p3.index, y=p3['TotalValue'], mode='lines', name='Min Risk Ratio'))
    fig.add_trace(go.Scatter(x=p4.index, y=p4['TotalValue'], mode='lines', name='Simulation'))

    fig.update_layout(
        title='Portfolio Comparison',
        xaxis_title='Date',
        yaxis_title='Values'
    )

    st.plotly_chart(fig, use_container_width=True)

    dataList = [p1, p2, p3, p4]
    tabList = ['Your Portfolio', 'Max Sharpe Ratio', 'Min Risk Ratio', 'Simulation']
    tabs = st.tabs(tabList)

    for i, tab in enumerate(tabs):
        with tab:
            dataframe = dataList[i]
            fig_mdd, mdd = mdd_stock(dataframe)
            st.plotly_chart(fig_mdd)
            date_diff = round((dataframe.index[-1] - dataframe.index[0]).days / 365.25, 2)
            start_asset = float(dataframe.loc[dataframe.index[0], 'TotalValue'])
            end_asset = float(dataframe.loc[dataframe.index[-1], 'TotalValue'])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Years", date_diff)
            col2.metric("Initial assets", format_value(start_asset))
            col3.metric("Final asset", format_value(end_asset))
            col4.metric("MDD", f'{round(min(mdd) * 100)} %')

    if st.button("다음"):
        st.switch_page("pages/5포트폴리오 상관관계 분석.py")

else:
    st.title('포트폴리오 평가')
    st.write("포트폴리오에 주식이 없습니다.")
