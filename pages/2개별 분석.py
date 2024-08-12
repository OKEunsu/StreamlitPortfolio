import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

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
        name=f'{label} 종가'  # Legend label
    ))

    # Add a horizontal line trace for the specified price
    fig.add_trace(go.Scatter(
        x=data.index,
        y=[price] * len(data),
        mode='lines',
        line=dict(color='red', width=1, dash='dash'),
        name=f'평단가'
    ))

    # Update the layout with a title
    fig.update_layout(
        title=f"{label} - CAGR: {cagr:.2%}",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
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
            df = stock_df(labels[i])

            # 예제: 각 탭에서 Plotly 그래프 그리기
            stock_name = labels[i]
            stock_price = stock_mean_price[i]
            fig_ohlc = ohlc_plot(df, stock_name, stock_price)
            st.plotly_chart(fig_ohlc)

            # DD & MDD
            fig_mdd = mdd_stock(df, stock_name)
            st.plotly_chart(fig_mdd)

    if st.button("다음"):
        st.switch_page("pages/3포트폴리오 분석.py")

else:
    st.write("포트폴리오에 주식이 없습니다.")

