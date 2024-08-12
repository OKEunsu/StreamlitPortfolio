import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# 환율 데이터
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
def total_return(dataframe, labels):
    data = pd.DataFrame(index=dataframe.index)

    for label in labels:
        label_close_col = f'{label}_Close'
        label_dividends_col = f'{label}_Dividends'
        data[f'{label}'] = dataframe[label_close_col] + dataframe[label_dividends_col]

    log_norm_data = data.div(data.iloc[0]).mul(100)
    log_norm_df = np.log1p(log_norm_data)

    return data, log_norm_data
@st.cache_data
def yoy_return_risk(data):
    daily_ret = data.pct_change()
    annual_ret = daily_ret.mean() * 252  # 연간 기대 수익률 계산

    # 일간 수익률의 표준편차 (변동성)
    daily_volatility = daily_ret.std()
    # 연간화된 변동성 계산
    annual_volatility = daily_volatility * np.sqrt(252)

    return annual_ret, annual_volatility
@st.cache_data
def yoy_return_hist(dataframe, labels):
  daily_returns = dataframe.pct_change().dropna()

  # 각 주식별 연도별 첫 번째 값과 마지막 값을 추출하여 연간 수익률 계산
  annual_returns = daily_returns.groupby([daily_returns.index.year]).apply(lambda x: x.mean()*252*100)

  # 구간화를 위한 범위 설정
  min_return = annual_returns.min().min()
  max_return = annual_returns.max().max()
  bins = np.arange(min_return, max_return,5)

  # 주식별 수익률 데이터 준비
  hist_data = [annual_returns[col].dropna().values for col in labels]

  # Plotly의 create_distplot 함수를 사용하여 시각화
  fig = ff.create_distplot(
      hist_data, labels, bin_size=bins, show_rug=True, show_hist=False
  )

  # 그래프 반환
  return fig

if "stock_list" in st.session_state and st.session_state.stock_list:
    st.title('포트폴리오 분석')
    # 원본 데이터
    labels = [stock['stock_name'] for stock in st.session_state.stock_list]
    df = stock_df(labels, get_krw_usd())

    # 성장률 비교
    total_df, log_total_df = total_return(df, labels)
    st.subheader('성장률(100기준)')
    fig_line = px.line(log_total_df, x=log_total_df.index, y=labels)
    st.plotly_chart(fig_line)

    # 연간 수익률, 변동성 비교
    annual_ret, annual_volatility = yoy_return_risk(total_df)
    st.subheader('연간 수익 & 리스크')
    # 개별 수익, 변동성
    fig_scatter = px.scatter(x=annual_volatility, y=annual_ret, text=labels, labels={'x': 'Risk', 'y': 'Return'},
                             color_discrete_sequence=['blue'])
    # 텍스트 색상과 스타일 업데이트
    fig_scatter.update_traces(
        marker=dict(size=40),
        textfont=dict(color='white', size=14, weight='bold')
    )
    st.plotly_chart(fig_scatter)

    # 일간 변동성 히스토그램
    st.subheader('연간 수익률 히스토그램')
    fig_hist = yoy_return_hist(total_df, labels)
    st.plotly_chart(fig_hist)

    if st.button("다음"):
        st.switch_page("pages/4포트폴리오 평가.py")

else:
    st.title('포트폴리오')
    st.write("포트폴리오에 주식이 없습니다.")