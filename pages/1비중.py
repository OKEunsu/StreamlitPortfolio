import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import yfinance as yf
import pandas as pd
import numpy as np

def get_ticker_short_name(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    short_name = info.get('shortName', 'N/A')  # 'shortName' 키가 없을 경우 'N/A'로 반환
    return short_name

# 최근 환율 계산기
def get_usd_to_krw_exchange_rate():
    ticker = 'KRW=X'
    data = yf.Ticker(ticker).history(period="1d")
    latest_data = data.iloc[-1]
    return round(latest_data['Close'],2)

def format_value(value):
    if isinstance(value, (int, float)):
        if value >= 1e12:
            return f"{value / 1e12:.2f}조"  # 조 단위
        elif value >= 1e9:
            return f"{value / 1e9:.2f}억"  # 십억 단위
        elif value >= 1e6:
            return f"{value / 1e6:.2f}백만"  # 백만 단위
        elif value >= 1e3:
            return f"{value / 1e3:.2f}천"  # 천 단위
        else:
            return f"{value:.2f}원"
    else:
        return "N/A"

def get_info_sector(tickers):
    sectors = []
    for ticker in tickers:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        if 'sector' in info:
            sectors.append(info['sector'])
        elif info['quoteType'] == 'ETF':
            sectors.append('ETF')
        else:
            sectors.append('Unknown')  # 섹터 정보가 없을 경우
    return sectors


@st.cache_data
def ploty_sector(tickers, values):
    # 섹터 리스트 생성
    sectors = get_info_sector(tickers)

    # 각 티커의 shortName을 가져오기
    short_names = [get_ticker_short_name(ticker) for ticker in tickers]

    # 중복 카테고리 합산
    category_values = defaultdict(float)
    for sector, value in zip(sectors, values):
        category_values[sector] += value

    # 합산된 데이터로부터 카테고리와 값 리스트 생성
    unique_categories = list(category_values.keys())
    summed_values = list(category_values.values())

    # 전체 값 계산
    total = sum(summed_values)

    # 퍼센트로 변환하고 내림차순으로 정렬
    percentages = [(value / total * 100, category) for category, value in zip(unique_categories, summed_values)]
    percentages.sort(reverse=True, key=lambda x: x[0])

    # 정렬된 순서에 따라 차트 생성
    fig_sector = go.Figure()

    for percent, category in percentages:
        fig_sector.add_trace(go.Bar(
            x=[percent],  # 퍼센트 값 사용
            y=[''],  # 빈 문자열을 사용하여 동일한 y축에 추가
            name=category,
            orientation='h',
            text=[f'{percent:.2f}%'],
            textposition='inside',
            hoverinfo='text+name',
            width=[1]
        ))

    fig_sector.update_layout(
        title='섹터 비중',
        barmode='stack',
        xaxis=dict(
            showticklabels=False,
            range=[0, 100]
        ),
        yaxis=dict(
            showticklabels=False  # y축 레이블을 숨김
        ),
        height=200,  # 기본값보다 작은 높이로 설정
        legend=dict(
            x=0.5,
            y=-0.2,
            xanchor='center',
            yanchor='top',
            orientation='h',
            traceorder='normal'  # trace 순서대로 legend 표시
        ))

    # 섹터 트리맵 데이터프레임 생성 시, shortName을 사용하여 레이블 지정
    df = pd.DataFrame({
        'Sector': sectors,
        'Ticker': short_names,  # 여기서 shortNames을 사용
        'Price': values
    })

    fig_tree = px.treemap(df, path=[px.Constant("Portfolio"), 'Sector', 'Ticker'], values='Price',
                          color='Price', hover_data=['Price'],
                          color_continuous_scale='dense',
                          color_continuous_midpoint=np.average(df['Price'], weights=df['Price']))
    fig_tree.update_layout(title='섹터 트리맵', margin=dict(t=50, l=25, r=25, b=25))
    fig_tree.update_traces(marker=dict(cornerradius=5))

    return fig_sector, fig_tree

@st.cache_data
def ploty_pie_portfolio(labels, values):
    # Plotly Pie chart
    fig = px.pie(values=values, names=labels, title='비중', hole=0.5)
    fig.update_traces(
        textinfo='percent',
        textfont_size=20
    )
    # 파이 차트에 텍스트 추가
    fig.add_annotation(
        text=f'₩ {format_value(sum(values))}',
        x=0.5, y=0.5,  # 텍스트 위치 설정 (0.5, 0.5는 중앙)
        showarrow=False,
        font=dict(size=19, color="white"),  # 폰트 설정
        align="center"
    )
    return fig

st.title('포트폴리오 요약')

# 주식 목록 출력 및 파이차트 생성
if "stock_list" in st.session_state and st.session_state.stock_list:
    st.subheader('내 포트폴리오')

    # 주식 목록 출력
    labels_name = []
    labels = []
    for i, stock in enumerate(st.session_state.stock_list):
        short_name = get_ticker_short_name(stock['stock_name'])
        labels_name.append(short_name)
        labels.append(stock['stock_name'])
        st.write(f"{i + 1}. 티커: {short_name}, 보유수: {stock['stock_num']}, 현재가 : {stock['stock_current']}, 평단가: {stock['stock_price']}, 화폐: {stock['currency_unit']}")

    usd_to_krw = get_usd_to_krw_exchange_rate()
    # 파이차트를 위한 데이터 준비
    values = []
    for stock in st.session_state.stock_list:
        try:
            stock_num = float(stock['stock_num'])  # 보유수
            stock_current = float(stock['stock_current'])  # 현재가
        except ValueError:
            st.error(f"유효하지 않은 데이터 형식: {stock}")
            continue

        total_value = stock_num * stock_current
        if stock['currency_unit'] == 'USD($)':
            total_value *= usd_to_krw  # Convert USD to KRW
        values.append(total_value)

    fig_pie = ploty_pie_portfolio(labels_name, values)
    st.plotly_chart(fig_pie, use_container_width=True)

    fig_sector, fig_tree = ploty_sector(labels, values)
    st.plotly_chart(fig_sector, use_container_width=True)
    st.plotly_chart(fig_tree, use_container_width=True)

else:
    st.write("포트폴리오에 주식이 없습니다.")

if st.button("다음"):
    st.switch_page("pages/2개별 분석.py")

