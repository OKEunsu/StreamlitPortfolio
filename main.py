import streamlit as st
import yfinance as yf

# CSS 삽입
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
._profileContainer_gzau3_53 {
            display: none;
        }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Function to delete a stock from the list
def delete_stock(index):
    del st.session_state.stock_list[index]
    st.success("삭제완료")

st.title('주식 포트폴리오 관리')

with st.expander("도움말"):
    st.image("imgs/Tiger나스닥.JPG")
    st.write('''
        1. 한국 상장 주식 경우 빨간색 체크표시의 티커이름을 확인해주세요. \n
        2. 코스피 상장인 경우 티커번호.KS, 코스닥 상장인 경우 티커번호.KQ을 입력해주세요
        3. ex) TIGER 미국나스닥100 -> 133690.KS
    ''')

# 증권사 모음
coly, coln = st.columns(2)
with coly:
    st.page_link("https://finance.yahoo.com/", label="야후 증권", icon="🟪")
with coln:
    st.page_link("https://finance.naver.com/", label="네이버 증권", icon="🟩")

# session_state에 키 값 체크, 없으면 초기값 할당
if "stock_list" not in st.session_state:
    st.session_state.stock_list = []

# Form for adding new stocks
with st.form(key="form"):
    col1, col2 = st.columns(2)
    with col1:
        stock_name = st.text_input(label="티커")
    with col2:
        price_unit = st.selectbox(
            "화폐단위",
            ("USD($)", "원(₩)")
        )

    col3, col4, col5 = st.columns(3)
    with col3:
        stock_num = st.text_input(label="보유수")
    with col4:
        stock_current = st.text_input(label="현재가")
    with col5:
        stock_price = st.text_input(label="평단가")

    add = st.form_submit_button(label="추가")

    # Validation
    if add:
        valid_input = True

        stock_name = stock_name.upper()

        try:
            quote_type = yf.Ticker(stock_name).info['quoteType']
            if quote_type not in ['EQUITY', 'ETF']:
                st.error("지원하지 않은 티커 입니다.")
                valid_input = False

        except KeyError:
            st.error(f"{stock_name} 티커명을 확인해주세요.")
            valid_input = False

        try:
            if (stock_name.endswith('.KS') or stock_name.endswith('.KQ')) and price_unit != '원(₩)':
                st.error("한국 주식의 화폐단위는 원(₩)이어야 합니다.")
                valid_input = False
            elif ('.KS' not in stock_name and '.KQ' not in stock_name) and price_unit != 'USD($)':
                st.error("외국 주식의 화폐단위는 USD($)이어야 합니다.")
                valid_input = False

        except ValueError:
            st.error("화폐 단위 확인해주세요.")
            valid_input = False


        try:
            stock_num = float(stock_num)
        except ValueError:
            st.error("주식 수량은 숫자여야 합니다.")
            valid_input = False

        try:
            stock_current = float(stock_current)
        except ValueError:
            st.error("현재가는 숫자여야 합니다.")
            valid_input = False

        try:
            stock_price = float(stock_price)
        except ValueError:
            st.error("평단가는 숫자여야 합니다.")
            valid_input = False

        if valid_input:
            st.session_state.stock_list.append({
                "stock_name": stock_name,
                "stock_num": stock_num,
                "stock_current" : stock_current,
                "stock_price": stock_price,
                "currency_unit": price_unit
            })
            st.success(f"{stock_name} 추가완료")


# Displaying the portfolio
st.subheader('내 포트폴리오')
for i, stock in enumerate(st.session_state.stock_list):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(
            f"{i + 1}. 티커: {stock['stock_name']}, 보유수: {stock['stock_num']}, 현재가: {stock['stock_current']} ,평단가: {stock['stock_price']}, {stock['currency_unit']}")
    with col2:
        delete_button = st.button(f"삭제 {i + 1}", key=f"delete_{i}")
        if delete_button:
            delete_stock(i)
            st.rerun()  # Reload the app to reflect the changes

if st.button("완료"):
    st.switch_page("pages/1비중.py")
