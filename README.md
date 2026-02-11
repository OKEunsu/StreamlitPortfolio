# 📊 StreamlitPortfolio

Live Demo: https://stockportfolioanlysis.streamlit.app/

StreamlitPortfolio는 **주식 포트폴리오 분석**을 위한 대시보드 앱입니다.  
Streamlit을 기반으로 사용자가 입력한 포트폴리오를 시각화하고 주요 리스크/수익 지표를 계산하여 직관적으로 분석할 수 있도록 설계되었습니다.

---

## 🚀 주요 기능

- 📈 티커별 포트폴리오 성과 시각화
- 📉 수익률 / 변동성 / 샤프 비율 등 핵심 지표 분석
- 🧮 보유 비중 기반 계산 및 현재가 반영 성과 분석
- 🗓️ 누적 수익률 및 리스크 비교 차트 제공
- 📝 피드백폼 + Notion API 연동

---

## 📅 개발 히스토리

| 날짜 | 변경사항 |
|------|----------|
| 2024-08-12 | 개별 분석 페이지 완성 - 포트폴리오 평가 기능 구현 |
| 2024-08-13 | 피드백 폼 완성 - Notion API 연동 추가 |
| 2024-08-15 | 티커 표시 개선 / 평단 → 현재가 기반 비중 계산으로 지표 보정 |

---

## 🧠 프로젝트 목적

이 프로젝트의 목표는 다음과 같습니다:

- 개인 투자 포트폴리오의 성과를 **시각적으로 직관**하게 이해할 수 있도록 돕는다.
- Python + Streamlit 기반으로 **빠르게 배포 가능한 분석 UI**를 설계한다.
- API 연동, 데이터 파싱, 대시보드 구성까지 **풀 스택 분석 경험**을 쌓는다.

---

## 🛠 기술 스택

- **Python 3.10+**
- **Streamlit**: UI 및 데시보드
- **Pandas / NumPy**: 데이터 처리
- **Plotly / Matplotlib**: 시각화
- **Notion API**: 피드백 저장

---

## 📦 설치 및 실행

1. 저장소를 클론합니다.
    ```bash
    git clone https://github.com/OKEunsu/StreamlitPortfolio.git
    cd StreamlitPortfolio
    ```

2. 가상환경 생성 후 의존성 설치:
    ```bash
    python -m venv venv
    source venv/bin/activate       # macOS / Linux
    venv\Scripts\activate          # Windows
    pip install -r requirements.txt
    ```

3. 앱 실행:
    ```bash
    streamlit run main.py
    ```

---

## 📁 폴더 구조
├── imgs/ # 이미지/아이콘 리소스  
├── pages/ # 서브 페이지 구성  
├── .streamlit/ # Streamlit 설정  
├── main.py # 메인 앱 실행 파일  
├── requirements.txt # 의존성  
└── README.md # 문서  


---

## 🤝 기여

기여는 언제나 환영합니다!  
버그 리포트, 기능 개선 제안, 코드 리뷰 모두 환영합니다.

1. Fork
2. Branch 생성 (`feature/YourFeature`)
3. Commit & Push
4. Pull Request 생성

---

## 📫 연락 / 피드백
- Notion 피드백 폼 (앱 내부)
