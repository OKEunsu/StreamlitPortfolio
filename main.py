import streamlit as st


home = st.Page("pages/0홈.py", title="홈", icon="🏠", default=True)
allocation = st.Page("pages/1비중.py", title="비중", icon="🧩")
single_asset = st.Page("pages/2개별 분석.py", title="개별 분석", icon="🔎")
portfolio_analysis = st.Page("pages/3포트폴리오 분석.py", title="포트폴리오 분석", icon="📈")
portfolio_eval = st.Page("pages/4포트폴리오 평가.py", title="포트폴리오 평가", icon="🧠")
correlation = st.Page("pages/5포트폴리오 상관관계 분석.py", title="상관관계 분석", icon="🔗")
feedback = st.Page("pages/6피드백.py", title="피드백", icon="✍️")

navigation = st.navigation(
    [home, allocation, single_asset, portfolio_analysis, portfolio_eval, correlation, feedback],
    position="hidden",
)
navigation.run()
