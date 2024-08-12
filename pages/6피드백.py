import streamlit as st
import datetime

st.title('리뷰')
with st.form("my_form"):
    date = datetime.datetime.now()
    st.write("피드백")

    txt = st.text_area(
        "피드백 내용을 적어주세요.",
    )

    sentiment_mapping = ["1", "2", "3", "4", "5"]
    selected = st.feedback("stars")

    submitted = st.form_submit_button("제출")
    if submitted:
        st.write(f"감사합니다! 날짜 : {date}, 피드백: {txt}, 별점: {sentiment_mapping[selected]}")

