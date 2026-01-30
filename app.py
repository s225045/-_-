import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="종암중 급식 알리미", page_icon="🍱")

# 1. 학교 정보 설정
ATP_PT_CODE = "J10"  # 서울특별시교육청
SD_SCHUL_CODE = "7031154"  # 종암중학교
# 종암중학교 홈페이지 급식 게시판 주소 (예시 - 실제 경로 확인 필요)
SCHOOL_URL = "https://jongam.sen.ms.kr/71337/subMenu.do" 

def get_meal_data(start_date, end_date):
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ATP_PT_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "MLSV_FROM_YMD": start_date,
        "MLSV_TO_YMD": end_date
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    except:
        return None

def get_meal_image(target_date):
    """
    학교 홈페이지에서 식단 사진을 크롤링하는 함수
    (참고: 홈페이지 구조가 바뀌면 수정이 필요합니다.)
    """
    try:
        # 실제 학교 홈페이지의 급식 갤러리/게시판 구조에 맞춰 requests를 보냅니다.
        # 아래는 일반적인 학교 홈페이지 크롤링 예시입니다.
        res = requests.get(SCHOOL_URL, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 날짜와 매칭되는 이미지 태그를 찾는 로직 (예: '2024-05-20' 포함된 게시물)
        # ※ 실제 홈페이지 태그 구조(class명 등)를 분석하여 적용해야 합니다.
        img_tag = soup.find('img', alt=True) # 예시용 로직
        if img_tag:
            return img_tag['src']
    except:
        return None
    return None

st.title("🍱 종암중학교 급식 알리미")

# 사이드바 날짜 선택
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.now())
selected_date_str = selected_date.strftime("%Y%m%d")

# 데이터 로드
start_of_week = (selected_date - timedelta(days=selected_date.weekday())).strftime("%Y%m%d")
end_of_week = (selected_date + timedelta(days=6-selected_date.weekday())).strftime("%Y%m%d")
data = get_meal_data(start_of_week, end_of_week)

tab1, tab2 = st.tabs(["오늘의 메뉴", "주간 식단"])

with tab1:
    st.subheader(f"📅 {selected_date.strftime('%Y년 %m월 %d일')}")
    
    found = False
    if data and "mealServiceDietInfo" in data:
        for row in data["mealServiceDietInfo"][1]["row"]:
            if row["MLSV_YMD"] == selected_date_str:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.success("#### 🍴 식단 메뉴")
                    menu = row["DDISH_NM"].replace("<br/>", "\n")
                    st.text(menu)
                    st.info(f"🔥 {row['CAL_INFO']}")
                
                with col2:
                    st.success("#### 📸 식단 사진")
                    img_url = get_meal_image(selected_date_str)
                    if img_url:
                        st.image(img_url, use_column_width=True)
                    else:
                        st.warning("등록된 식단 사진이 없습니다.")
                
                found = True
    
    if not found:
        st.error("💬 선택하신 날짜에는 급식 메뉴가 등록되지 않았습니다.")

with tab2:
    st.header("🗓️ 주간 식단표")
    if data and "mealServiceDietInfo" in data:
        for row in data["mealServiceDietInfo"][1]["row"]:
            date_obj = datetime.strptime(row["MLSV_YMD"], "%Y%m%d")
            with st.expander(f"{date_obj.strftime('%m/%d (%a)')}"):
                st.write(row["DDISH_NM"].replace("<br/>", ", "))
    else:
        st.write("데이터가 없습니다.")

st.divider()
st.caption("제작: Streamlit 급식 앱 | 데이터 출처: NEIS API")
