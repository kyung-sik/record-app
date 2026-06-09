"""식단 기록 페이지 — 끼니별 음식과 칼로리 입력/조회/삭제."""
import datetime as dt

import streamlit as st

import auth
import data
import db

st.set_page_config(page_title="식단 기록", page_icon="🍽️")
auth.require_login()
data.ensure_db()

st.title("🍽️ 식단 기록")

# ---------- 입력 폼 ----------
with st.form("diet_form", clear_on_submit=True):
    date = st.date_input("날짜", dt.date.today())
    meal = st.selectbox("끼니", ["아침", "점심", "저녁", "간식"])
    food = st.text_input("음식 내용", placeholder="예: 닭가슴살 샐러드, 현미밥")
    calories = st.number_input("칼로리(kcal)", min_value=0, max_value=5000, value=0, step=50)
    memo = st.text_area("메모", placeholder="자유롭게")
    submitted = st.form_submit_button("저장")

    if submitted:
        if not food.strip():
            st.error("음식 내용을 입력해 주세요.")
        else:
            db.add_diet(date.isoformat(), meal, food.strip(), int(calories), memo.strip())
            data.refresh()
            st.success(f"저장 완료: {date} · {meal} · {food}")

st.divider()

# ---------- 기록 조회 ----------
st.subheader("전체 식단 기록")
df = data.load_df("diet")
if df.empty:
    st.info("아직 기록이 없습니다.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("기록 삭제"):
        del_id = st.number_input("삭제할 기록의 id", min_value=0, step=1, value=0)
        if st.button("삭제", type="primary"):
            db.delete_row("diet", int(del_id))
            data.refresh()
            st.success(f"id {del_id} 기록을 삭제했습니다.")
            st.rerun()
