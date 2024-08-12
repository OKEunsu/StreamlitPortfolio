import streamlit as st

with st.form("my_form"):
    st.write("피드백")

    txt = st.text_area(
        "피드백 내용을 적어주세요.",
    )

    sentiment_mapping = ["one", "two", "three", "four", "five"]
    selected = st.feedback("stars")

    submitted = st.form_submit_button("제출")
    if submitted:
        st.write("감사합니다")

