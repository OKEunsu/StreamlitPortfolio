import streamlit as st
import datetime
import requests
import json
from ui_theme import apply_theme

apply_theme("리뷰")

# 환경 변수에서 API 키와 데이터베이스 ID 가져오기
api_key = st.secrets["api_key"]
database_id = st.secrets["database_id"]
url = 'https://api.notion.com/v1/pages/'

headers = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Streamlit UI
st.title('리뷰')
with st.form("my_form"):
    date = datetime.datetime.now().strftime('%Y-%m-%d')  # 날짜를 오늘로 설정
    st.subheader("피드백")

    txt = st.text_area("피드백 내용을 적어주세요.")

    sentiment_mapping = ["1", "2", "3", "4", "5"]
    selected = st.feedback("stars")

    submitted = st.form_submit_button("제출")
    if submitted:
        # 요청 본문 구성
        body = {
            'parent': {
                'type': 'database_id',
                'database_id': database_id,
            },
            'properties': {
                '이름': {
                    'title': [
                        {
                            'text': {
                                'content': 'STREAMLIT_Portfolio'
                            }
                        }
                    ]
                },
                '날짜': {  # 날짜 속성
                    'date': {
                        'start': date  # 현재 날짜
                    }
                },
                '별점': {  # 별점 속성 (숫자)
                    'number': int(selected)  # 사용자가 선택한 별점
                },
                '텍스트': {  # 텍스트 속성
                    'rich_text': [
                        {
                            'text': {
                                'content': txt  # 피드백 내용
                            }
                        }
                    ]
                }
            },
            'children': [
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [
                            {
                                'type': 'text',
                                'text': {
                                    'content': '여기에 추가적인 정보를 입력할 수 있습니다.'
                                }
                            }
                        ]
                    }
                }
            ]
        }

        # API 요청
        response = requests.post(url, headers=headers, data=json.dumps(body))

        if response.status_code == 200:
            st.write(f"감사합니다! 날짜 : {date}")
        else:
            st.write(f"문제가 발생했습니다: {response.status_code}, {response.text}")
