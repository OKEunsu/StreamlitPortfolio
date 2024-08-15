import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# 티커 이름 변환
def get_ticker_short_name(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    short_name = info.get('shortName', 'N/A')  # 'shortName' 키가 없을 경우 'N/A'로 반환
    return short_name

# 단위 변환
def format_usd(value):
    if isinstance(value, (int, float)):
        if value >= 1e12:
            return f"$ {value / 1e12:.1f}T"  # 조 단위
        elif value >= 1e9:
            return f"$ {value / 1e9:.1f}B"  # 십억 단위
        elif value >= 1e6:
            return f"$ {value / 1e6:.1f}M"  # 백만 단위
        elif value >= 1e3:
            return f"$ {value / 1e3:.1f}K"  # 천 단위
        else:
            return f"$ {value:.1f}"
    else:
        return "N/A"

def format_won(value):
    if isinstance(value, (int, float)):
        if value >= 1e12:
            return f"{value / 1e12:.1f}조"  # 조 단위
        elif value >= 1e9:
            return f"{value / 1e9:.1f}억"  # 십억 단위
        elif value >= 1e6:
            return f"{value / 1e6:.1f}백만"  # 백만 단위
        elif value >= 1e3:
            return f"{value / 1e3:.1f}천"  # 천 단위
        else:
            return f"{value:.1f}원"
    else:
        return "N/A"


# 주식 지표
def get_financial_metrics(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    dtype = info.get('quoteType')  # 자산 종류

    # 코스피, 코스닥
    if ticker_symbol.endswith('.KS') or ticker_symbol.endswith('.KQ'):
        market_cap = format_won(info.get('marketCap', 'N/A'))  # 시가총액
        dividend_yield = round(info.get('dividendYield', 0) * 100, 2)  # 배당 수익률
        pbr = info.get('priceToBook', 0)  # PBR
        per = info.get('forwardPE', 0)  # PER
        roe = info.get('returnOnEquity', 0) * 100  # ROE
        psr = info.get('priceToSalesTrailing12Months', 0)  # PSR
        beta = info.get('beta')  # 시장 베타 계수
        roa = info.get('returnOnAssets', 0) * 100  # ROA

    else:
        market_cap = format_usd(info.get('marketCap', 'N/A'))  # 시가총액
        dividend_yield = round(info.get('dividendYield', 0) * 100, 2)  # 배당 수익률
        pbr = info.get('priceToBook', 0)  # PBR
        per = info.get('forwardPE', 0)  # PER
        roe = info.get('returnOnEquity', 0) * 100  # ROE
        psr = info.get('priceToSalesTrailing12Months', 0)  # PSR
        beta = info.get('beta')  # 시장 베타 계수
        roa = info.get('returnOnAssets', 0) * 100  # ROA

    return {
        'Market Cap': market_cap,
        'Dividend Yield': dividend_yield,
        'PBR': f"{pbr:.2f}",
        'PER': f"{per:.2f}",
        'ROE': f"{roe:.2f}",
        'PSR': f"{psr:.2f}",
        'Beta': beta,
        'ROA': f"{roa:.2f}",
        'type': dtype
    }


# 재무제표
def get_fundamental_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    financials = ticker.financials

    if 'Operating Income' in financials.index:
        financials_df = financials.loc[['Total Revenue', 'Operating Income', 'Net Income'], :].dropna(axis=1)
        financials_df.columns = financials_df.columns.strftime('%Y')
        fig_fundamental = go.Figure(data=[
            go.Bar(name='Total Revenue', x=financials_df.columns, y=financials_df.loc['Total Revenue'].to_list(),
                   marker_color='#324FBB'),
            go.Bar(name='Operating Income', x=financials_df.columns,
                   y=financials_df.loc['Operating Income'].to_list(),
                   marker_color='#2E71B9'),
            go.Bar(name='Net Income', x=financials_df.columns, y=financials_df.loc['Net Income'].to_list(),
                   marker_color='#689AD0')
        ])
    else:
        financials_df = financials.loc[['Total Revenue', 'Normalized Income', 'Net Income'], :].dropna(axis=1)
        financials_df.columns = financials_df.columns.strftime('%Y')
        fig_fundamental = go.Figure(data=[
            go.Bar(name='Total Revenue', x=financials_df.columns, y=financials_df.loc['Total Revenue'].to_list(),
                   marker_color='#324FBB'),
            go.Bar(name='Operating Income', x=financials_df.columns,
                   y=financials_df.loc['Normalized Income'].to_list(),
                   marker_color='#2E71B9'),
            go.Bar(name='Net Income', x=financials_df.columns, y=financials_df.loc['Net Income'].to_list(),
                   marker_color='#689AD0')
        ])

    fig_fundamental.update_layout(barmode='group', title='Financial Metrics')

    if ('Basic EPS' in financials.index) and ('Diluted EPS' in financials.index):
        eps_df = financials.loc[['Diluted EPS', 'Basic EPS'], :].dropna(axis=1)
        eps_df_T = eps_df.transpose()
        fig_eps = px.scatter(eps_df_T, x=eps_df_T.index, y=eps_df_T.columns, title='EPS Trends Over Years',
                             labels={'value': 'EPS', 'index': 'Year', 'x': 'Date'})
        fig_eps.update_traces(marker=dict(size=30, opacity=0.7), selector=dict(mode='markers'))
    else:
        fig_eps = None

    return fig_fundamental, fig_eps


# 부채비율,
def get_ratio(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    balance_sheet = ticker.balance_sheet
    ratio_columns = ['Total Equity Gross Minority Interest', 'Total Liabilities Net Minority Interest',
                     'Current Assets',
                     'Current Liabilities']
    if all(col in balance_sheet.index for col in ratio_columns):
        bs_df = balance_sheet.loc[['Total Equity Gross Minority Interest', 'Total Liabilities Net Minority Interest',
                                   'Current Assets', 'Current Liabilities'], :].dropna(axis=1).T[::-1]

        bs_df['Debt Ratio'] = bs_df['Total Liabilities Net Minority Interest'] / bs_df[
            'Total Equity Gross Minority Interest'] * 100
        bs_df['Current Ratio'] = bs_df['Current Assets'] / bs_df['Current Liabilities'] * 100

        bs_df.reset_index(inplace=True)
        bs_df.rename(columns={'index': 'Date'}, inplace=True)
        bs_df['Date'] = pd.to_datetime(bs_df['Date']).dt.strftime('%Y')

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bs_df.Date, y=bs_df['Debt Ratio'], mode='lines+markers', name='Debt Ratio',
                                 text=bs_df['Debt Ratio']))
        fig.add_trace(go.Scatter(x=bs_df.Date, y=bs_df['Current Ratio'], mode='lines+markers', name='Current Ratio',
                                 text=bs_df['Current Ratio']))
        fig.update_layout(title='Debt Ratio and Current Ratio Over Years',
                          xaxis_title='Year', yaxis_title='Ratio',
                          xaxis=dict(tickmode='array', tickvals=bs_df['Date'], ticktext=bs_df['Date']))
    else:
        fig = None

    return fig


# 애널리스트 추천
def get_recommend(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    recommendations = ticker.recommendations
    recommendations = recommendations[::-1]

    fig = px.bar(recommendations, x="period", y=['strongSell', 'sell', 'hold', 'buy', 'strongBuy'],
                 title="Analyst Recommendations",
                 labels={'period': 'Period', 'value': 'Count', 'variable': 'Recommendation Type'},
                 color_discrete_sequence=['#E61830', '#E9573E', '#F6BB43', '#8CC051', '#3C5222'],
                 text_auto=True)
    fig.update_layout(bargap=0.5, legend={'traceorder': 'reversed'})
    return fig


@st.cache_data
def stock_df(label):
    ticker = yf.Ticker(label)
    stock_data = ticker.history(interval='1d', period='max')
    stock_data.columns = [f"{label}_{col}" for col in stock_data.columns]
    return stock_data


def ohlc_plot(data, label, price):
    # Calculate cumulative return and CAGR
    data = calculate_cumulative_return(data, label)
    cagr = calculate_cagr(data, label)

    # Create a line plot for the close price
    fig = go.Figure()

    # Add a line trace for the close price
    fig.add_trace(go.Scatter(
        x=data.index,  # X-axis values are taken from the index of the dataframe
        y=data[f'{label}_Close'],  # Y-axis values are the close price
        mode='lines',  # Plot as a line
        name=f'{get_ticker_short_name(label)}'  # Legend label
    ))

    # Add a horizontal line trace for the specified price
    fig.add_trace(go.Scatter(
        x=data.index,
        y=[price] * len(data),
        mode='lines',
        line=dict(color='red', width=1, dash='dash'),
        name=f'평단가'
    ))

    # Update the layout with a title and legend position
    fig.update_layout(
        title=f"CAGR: {cagr:.2%}",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation='h',  # Horizontal orientation
            yanchor='bottom',  # Anchor the y position at the bottom of the legend
            y=1.1,  # Position the legend slightly above the plot
            xanchor='center',  # Center the x position
            x=0.5  # Center the legend horizontally
        )
    )

    return fig


def calculate_cumulative_return(data, label):
    data['Cumulative Return'] = (data[f'{label}_Close'] / data[f'{label}_Close'].iloc[0]) - 1
    return data


def calculate_cagr(data, label):
    start_price = data[f'{label}_Close'].iloc[0]
    end_price = data[f'{label}_Close'].iloc[-1]
    n_years = (data.index[-1] - data.index[0]).days / 252  # Convert days to years
    cagr = (end_price / start_price) ** (1 / n_years) - 1
    return cagr


@st.cache_data
def mdd_stock(DataFrame, stock_name):
    window = 252
    peak = DataFrame[f'{stock_name}_Close'].rolling(window, min_periods=1).max()
    drawdown = DataFrame[f'{stock_name}_Close'] / peak - 1.0
    max_dd = drawdown.rolling(window, min_periods=1).min()

    # plotly용 트레이스 생성
    trace_drawdown = go.Scatter(x=drawdown.index, y=drawdown.values, mode='lines', name='DD',
                                line=dict(color='#0063B2'))
    trace_max_dd = go.Scatter(x=max_dd.index, y=max_dd.values, mode='lines', name='MDD', line=dict(color='#9CC3D5'))

    # 레이아웃 생성
    layout = go.Layout(
        title="DD & MDD",
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price'),
        showlegend=True,
        template='plotly'
    )
    # 데이터를 트레이스에 결합
    data = [trace_drawdown, trace_max_dd]
    # 피규어 생성
    fig = go.Figure(data=data, layout=layout)
    return fig


st.title('개별 분석')
if "stock_list" in st.session_state and st.session_state.stock_list:

    labels = [stock['stock_name'] for stock in st.session_state.stock_list]
    stock_mean_price = [stock['stock_price'] for stock in st.session_state.stock_list]

    tabs = st.tabs(labels)
    for i, tab in enumerate(tabs):
        with tab:
            stock_name_ticker = get_ticker_short_name(labels[i])
            st.subheader(stock_name_ticker)
            df = stock_df(labels[i])

            # 각 탭에서 Plotly 그래프 그리기
            stock_name = labels[i]
            stock_price = stock_mean_price[i]
            ticker = yf.Ticker(stock_name)
            info = ticker.info
            dtype = info.get('quoteType')

            fig_ohlc = ohlc_plot(df, stock_name, stock_price)
            st.plotly_chart(fig_ohlc)

            # DD & MDD
            fig_mdd = mdd_stock(df, stock_name)
            st.plotly_chart(fig_mdd)

            financial_metrics = get_financial_metrics(stock_name)

            if financial_metrics['type'] == 'EQUITY':
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Market Cap", financial_metrics['Market Cap'])
                col2.metric("Dividend Yield", round(float(financial_metrics['Dividend Yield']), 4))
                col3.metric("PBR", financial_metrics['PBR'])
                col4.metric("PER", financial_metrics['PER'])

                col5, col6, col7, col8 = st.columns(4)
                col5.metric("ROE", financial_metrics['ROE'])
                col6.metric("PSR", financial_metrics['PSR'])
                col7.metric("Beta", financial_metrics['Beta'])
                col8.metric("ROA", financial_metrics['ROA'])

                fig_fundamental, fig_eps = get_fundamental_data(stock_name)
                fig_recommend = get_recommend(stock_name)
                fig_ratio = get_ratio(stock_name)
                st.plotly_chart(fig_fundamental)
                st.plotly_chart(fig_eps)
                if fig_ratio is not None:
                    st.plotly_chart(fig_ratio)
                st.plotly_chart(fig_recommend)

            elif dtype == 'ETF' and not (stock_name.endswith('.KS') or stock_name.endswith('.KQ')):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Assets", format_usd(info['totalAssets']))
                col2.metric("Dividend Yield", round(float(info['yield']), 3))
                col3.metric("beta3Year", round(float(info['beta3Year']), 3))
                col4.metric("NavPrice", info['navPrice'])

                st.write('')
                st.subheader('ETF 상세페이지')
                st.markdown(
                    f"""
                    <style>
                    .button {{
                        display: inline-block;
                        padding: 10px 15px;
                        font-size: 14px;
                        color: #ffffff;
                        background-color: #007bff;
                        border-radius: 5px;
                        text-decoration: none;
                        font-weight: bold;
                        transition: background-color 0.3s ease;
                    }}
                    .button:hover {{
                        background-color: #0056b3;
                    }}
                    </style>
                    <a class="button" href="https://www.etf.com/{stock_name}" target="_blank">More details on ETF.com</a>
                    """,
                    unsafe_allow_html=True
                )
                st.write('')
            else:
                kor_etf_ticker = stock_name.replace('.KS', '')
                st.write('')
                st.subheader('ETF 상세페이지')
                st.markdown(
                    f"""
                    <style>
                    .button {{
                        display: inline-block;
                        padding: 10px 15px;
                        font-size: 14px;
                        color: #ffffff;
                        background-color: #007bff;
                        border-radius: 5px;
                        text-decoration: none;
                        font-weight: bold;
                        transition: background-color 0.3s ease;
                    }}
                    .button:hover {{
                        background-color: #0056b3;
                    }}
                    </style>
                    <a class="button" href="https://www.etfcheck.co.kr/mobile/etpitem/{kor_etf_ticker}/basic" target="_blank">More details on ETF.com</a>
                    """,
                    unsafe_allow_html=True
                )
                st.write('')

    if st.button("다음"):
        st.switch_page("pages/3포트폴리오 분석.py")

else:
    st.write("포트폴리오에 주식이 없습니다.")
