import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go


THEME_CSS = """
<style>
:root {
  --primary-color: #22c1c3;
  --background-color: #0b1220;
  --secondary-background-color: #111b2e;
  --text-color: #e5ecf5;
  --sidebar-width: 18rem;
  --plot-box-extra: 20px;
}

.stApp {
  background:
    radial-gradient(circle at 10% 15%, rgba(99, 120, 180, 0.10), transparent 35%),
    radial-gradient(circle at 90% 80%, rgba(71, 95, 160, 0.08), transparent 40%),
    linear-gradient(160deg, #0d1b2e 0%, #111d30 50%, #0f1929 100%);
  color: #e5ecf5;
}

[data-testid="stAppViewContainer"] {
  background: transparent;
}

[data-testid="stHeader"] {
  background: transparent;
}

[data-testid="stSidebar"] {
  background-color: #0e1728;
}

[data-testid="stSidebar"] * {
  color: #d9e4f2;
}

[data-testid="stSidebarNav"] {
  display: none !important;
}

[data-testid="collapsedControl"] {
  z-index: 1000;
}

@media (min-width: 992px) {
  [data-testid="stSidebar"] {
    border-right: 1px solid #2c3f5d;
  }

  [data-testid="stSidebarContent"] {
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
  }
}

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp p, .stApp label, .stApp li {
  color: #e5ecf5;
  line-height: 1.45;
  letter-spacing: 0.01em;
}

.stButton > button,
.stFormSubmitButton > button {
  background: linear-gradient(135deg, #f43f5e 0%, #fb7185 100%);
  color: #0b1220;
  border: 1px solid #fda4af;
  border-radius: 10px;
  font-weight: 700 !important;
  letter-spacing: 0.01em;
}

.stButton > button *,
.stFormSubmitButton > button * {
  color: inherit !important;
  font-weight: 700 !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
  background: linear-gradient(135deg, #fb7185 0%, #fda4af 100%);
  color: #0b1220;
  border-color: #fecdd3;
}

.stButton > button:disabled,
.stFormSubmitButton > button:disabled {
  background: #4b2730;
  color: #f0dde1;
  border: 1px solid #6a3844;
  opacity: 1;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
.stTextArea textarea,
.stTextInput input,
.stNumberInput input {
  background: #111b2e;
  color: #e5ecf5;
  border-radius: 10px;
  border: 1px solid #2c3f5d;
}

[data-baseweb="tab-list"] {
  gap: 10px;
  padding-bottom: 4px;
}

[data-baseweb="tab"] {
  background: #111b2e;
  border: 1px solid #2c3f5d;
  border-radius: 10px;
  min-height: 40px;
  padding: 8px 14px;
  font-size: 1.02rem;
  font-weight: 500;
  letter-spacing: 0.01em;
}

[data-baseweb="tab"][aria-selected="true"] {
  background: #17314c;
  border-color: #2bb9bc;
}

[data-testid="stDataFrame"] {
  background: #111b2e;
  border: 1px solid #2c3f5d;
  border-radius: 12px;
}

[data-testid="stPlotlyChart"] {
  background: rgba(12, 20, 34, 0.78);
  border: 1px solid #243652;
  border-radius: 14px;
  padding: 12px 10px 8px 10px;
  box-sizing: border-box;
  width: calc(100% + var(--plot-box-extra));
  margin-right: calc(-1 * var(--plot-box-extra));
  overflow: visible;
}

[data-testid="stPlotlyChart"] > div {
  width: calc(100% - var(--plot-box-extra)) !important;
  max-width: calc(100% - var(--plot-box-extra)) !important;
}

/* Keep Streamlit connection/error dialogs readable */
[role="dialog"],
[role="alertdialog"] {
  background: #111b2e !important;
  color: #e5ecf5 !important;
  border: 1px solid #2c3f5d !important;
}

[role="dialog"] *,
[role="alertdialog"] * {
  color: #e5ecf5 !important;
}

[role="dialog"] code,
[role="alertdialog"] code {
  background: #0b1220 !important;
  color: #9ad1d4 !important;
}
</style>
"""


def _apply_plotly_template() -> None:
    base = pio.templates["plotly_dark"]
    layout_update = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5ecf5", size=14),
        title=dict(font=dict(size=24)),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            x=1.01,
            xanchor="left",
            y=0.99,
            yanchor="top",
            font=dict(size=14),
        ),
        margin=dict(l=40, r=24, t=60, b=40),
    )
    pio.templates["portfolio_dark"] = go.layout.Template(
        layout=base.layout.update(layout_update)
    )
    pio.templates.default = "portfolio_dark"


def _render_sidebar_nav() -> None:
    st.sidebar.markdown("### Portfolio Lab")
    st.sidebar.caption("Analysis Menu")
    st.sidebar.page_link("pages/0홈.py", label="홈 · 포트폴리오 입력", icon="🏠")
    st.sidebar.page_link("pages/1비중.py", label="비중 · 구성 요약", icon="🧩")
    st.sidebar.page_link("pages/2개별 분석.py", label="종목 · 개별 분석", icon="🔎")
    st.sidebar.page_link("pages/3포트폴리오 분석.py", label="포트폴리오 · 성과 분석", icon="📈")
    st.sidebar.page_link("pages/4포트폴리오 평가.py", label="포트폴리오 · 샤프 평가", icon="🧠")
    st.sidebar.page_link("pages/5포트폴리오 상관관계 분석.py", label="리스크 · 상관관계", icon="🔗")
    st.sidebar.page_link("pages/6피드백.py", label="피드백", icon="✍️")


def apply_theme(
    page_title: str,
    hide_streamlit_chrome: bool = False,
    render_sidebar_nav: bool = True,
) -> None:
    st.set_page_config(page_title=page_title, layout="wide", initial_sidebar_state="expanded")
    _apply_plotly_template()
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    if render_sidebar_nav:
        _render_sidebar_nav()

    if hide_streamlit_chrome:
        st.markdown(
            """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """,
            unsafe_allow_html=True,
        )
