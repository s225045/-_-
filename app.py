import streamlit as st
import requests
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="종암중 급식표", page_icon="🍱")

# 학교 정보 설정 (종암중학교 고유 코드)
ATP_PT_CODE = "J10"  # 서울특별시교육청
SD_SCHUL_CODE = "7031154"  # 종암중학교

def get_meal_data(start_date, end_date):
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": "YOUR_API_KEY", # 여기에 본인의 API 키를 넣으면 더 안정적입니다.
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ATP_PT_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "MLSV_FROM_YMD": start_date,
        "MLSV_TO_YMD": end_date
    }
    
    response = requests.get(url, params=params)
    return response.json()

st.title("🍱 종암중학교 급식 알리미")

# 날짜 계산
today = datetime.now()
today_str = today.strftime("%Y%m%d")
start_of_week = (today - timedelta(days=today.weekday())).strftime("%Y%m%d")
end_of_week = (today + timedelta(days=6-today.weekday())).strftime("%Y%m%d")

# 데이터 가져오기
data = get_meal_data(start_of_week, end_of_week)

# 탭 구성
tab1, tab2 = st.tabs(["오늘의 급식", "이번 주 급식"])

with tab1:
    st.header(f"📅 {today.strftime('%Y년 %m월 %d일')}")
    
    found_today = False
    if "mealServiceDietInfo" in data:
        for row in data["mealServiceDietInfo"][1]["row"]:
            if row["MLSV_YMD"] == today_str:
                # 메뉴 정제 (알러지 정보 등 제거)
                menu = row["DDISH_NM"].replace("<br/>", "\n")
                st.success("#### [오늘의 메뉴]")
                st.text(menu)
                st.info(f"칼로리: {row['CAL_INFO']}")
                
                # 사진 정보 (나이스 API는 식단 사진 URL을 직접 제공하지 않는 경우가 많아 
                # 학교 홈페이지 사진 연동은 추가 크롤링이 필요할 수 있습니다.)
                st.warning("⚠️ 사진은 학교 홈페이지 사정에 따라 제공되지 않을 수 있습니다.")
                found_today = True
    
    if not found_today:
        st.error("❌ 오늘은 급식 메뉴가 등록되어 있지 않습니다.")

with tab2:
    st.header("🗓️ 이번 주 전체 식단")
    if "mealServiceDietInfo" in data:
        for row in data["mealServiceDietInfo"][1]["row"]:
            with st.expander(f"{row['MLSV_YMD'][4:6]}월 {row['MLSV_YMD'][6:]}일 식단"):
                st.write(row["DDISH_NM"].replace("<br/>", ", "))
    else:
        st.write("이번 주 급식 정보가 없습니다.")