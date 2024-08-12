import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px

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

            stock_data.columns = [f"{symbol}_{col}" for col in stock_data.columns]

            if not symbol.endswith(('.KS', '.KQ')):
                stock_data = stock_data * KRW

            all_dates.update(stock_data.index)
            data_frames.append(stock_data)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    if not data_frames:
        raise ValueError("No data frames were created. Check the symbols and internet connection.")

    all_dates = sorted(all_dates)
    combined_data = pd.DataFrame(index=all_dates)

    for df in data_frames:
        combined_data = combined_data.join(df, how='outer')

    result_df = combined_data.dropna()
    return result_df

if "stock_list" in st.session_state and st.session_state.stock_list:
    st.title('자산 상관관계')

    labels = [stock['stock_name'] for stock in st.session_state.stock_list]
    df = stock_df(labels, get_krw_usd())

    corr_df = pd.DataFrame(index=df.index)

    for stock in labels:
        corr_df[stock] = df[f'{stock}_Close']

    # 상관계수 계산
    correlation_matrix = round(corr_df.corr(), 2)

    # 상관계수 히트맵 시각화 (Plotly)
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='Purples',
        zmin=-1, zmax=1
    )
    fig.update_layout(
        title='Stock Correlation Matrix',
        xaxis_title='Stocks',
        yaxis_title='Stocks',
        font=dict(size=16)
    )
    st.plotly_chart(fig)

    # 로그 수익률 계산
    log_returns = np.log(corr_df / corr_df.shift(1))

    # 상관계수 계산
    return_corr_matrix = round(log_returns.corr(), 2)

    # 상관계수 히트맵 시각화 (Plotly)
    fig_return = px.imshow(
        return_corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='Blues',
        zmin=-1, zmax=1
    )
    fig_return.update_layout(
        title='Stock Log(Return) Correlation Matrix',
        xaxis_title='Stocks',
        yaxis_title='Stocks',
        font=dict(size=16)
    )
    st.plotly_chart(fig_return)

    if st.button("다음"):
        st.switch_page("pages/5포트폴리오 상관관계 분석.py")

else:
    st.title("포트폴리오 상관관계 분석")
    st.write("포트폴리오에 주식이 없습니다.")
