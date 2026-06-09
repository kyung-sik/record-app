"""개인용 운동·식단·체중 기록 앱 — 메인 대시보드.

실행: streamlit run app.py
왼쪽 사이드바에서 운동/식단/체중 기록 페이지로 이동할 수 있다.
"""
import datetime as dt

import streamlit as st

import auth
import data
import style

st.set_page_config(page_title="나의 건강 기록", page_icon="💪", layout="centered",
                   initial_sidebar_state="expanded")
style.inject()

# 로그인 확인 후, DB 테이블을 준비한다(프로세스당 1회 캐싱).
auth.require_login()
data.ensure_db()

style.hero("나의 건강 기록 💪", "매일의 운동·식단·체중을 기록하고 추이를 확인하세요.")
style.top_nav()

# 데이터 불러오기(캐시)
ex_df = data.load_df("exercise")
diet_df = data.load_df("diet")
wt_df = data.load_df("weight")

today = dt.date.today().isoformat()

# ---------- 오늘 요약 ----------
st.subheader("오늘 요약")
c1, c2, c3 = st.columns(3)

today_ex = ex_df[ex_df["date"] == today]
ex_names = list(dict.fromkeys(today_ex["name"].tolist()))  # 중복 제거, 순서 유지
c1.metric("오늘 운동", f"{len(today_ex)} 종목",
          ", ".join(ex_names) if ex_names else None)

today_diet = diet_df[diet_df["date"] == today]
diet_meals = list(dict.fromkeys(today_diet["meal"].tolist()))
c2.metric("오늘 식단", f"{len(today_diet)} 개",
          ", ".join(diet_meals) if diet_meals else None)

if not wt_df.empty:
    latest = wt_df.iloc[0]
    delta = None
    if len(wt_df) > 1:
        delta = round(float(latest["weight_kg"]) - float(wt_df.iloc[1]["weight_kg"]), 1)
    c3.metric("최근 체중", f"{latest['weight_kg']} kg",
              f"{delta:+} kg" if delta is not None else None)
else:
    c3.metric("최근 체중", "기록 없음")

st.divider()

# ---------- 체중 추이 ----------
st.subheader("체중 추이")
if wt_df.empty:
    st.info("아직 체중 기록이 없습니다. 상단 메뉴의 '체중'에서 추가해 보세요.")
else:
    chart_df = wt_df.sort_values("date").set_index("date")[["weight_kg"]]
    st.line_chart(chart_df, y="weight_kg")

st.divider()

# ---------- 최근 기록 ----------
st.subheader("최근 기록")
t1, t2, t3 = st.tabs(["🏃 운동", "🍽️ 식단", "⚖️ 체중"])
with t1:
    if ex_df.empty:
        st.info("운동 기록이 없습니다.")
    else:
        ex_show = ex_df[["date", "name", "weight", "detail"]].rename(
            columns={"date": "날짜", "name": "운동", "weight": "중량(kg)", "detail": "부위"})
        st.dataframe(ex_show.head(10), use_container_width=True, hide_index=True)
with t2:
    if diet_df.empty:
        st.info("식단 기록이 없습니다.")
    else:
        diet_show = diet_df[["date", "meal", "food"]].rename(
            columns={"date": "날짜", "meal": "끼니", "food": "음식"})
        st.dataframe(diet_show.head(10), use_container_width=True, hide_index=True)
with t3:
    if wt_df.empty:
        st.info("체중 기록이 없습니다.")
    else:
        wt_show = wt_df[["date", "weight_kg"]].rename(
            columns={"date": "날짜", "weight_kg": "몸무게(kg)"})
        st.dataframe(wt_show.head(10), use_container_width=True, hide_index=True)
