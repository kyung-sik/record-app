"""운동 기록 페이지 — 입력 폼과 전체 기록 조회/삭제."""
import datetime as dt

import streamlit as st

import auth
import db

st.set_page_config(page_title="운동 기록", page_icon="🏃")
auth.require_login()
db.init_db()

st.title("🏃 운동 기록")

# ---------- 입력 폼 ----------
with st.form("exercise_form", clear_on_submit=True):
    date = st.date_input("날짜", dt.date.today())
    name = st.text_input("운동 종류", placeholder="예: 달리기, 헬스, 수영")
    col1, col2 = st.columns(2)
    minutes = col1.number_input("운동 시간(분)", min_value=0, max_value=600, value=30, step=5)
    sets = col2.number_input("세트 수", min_value=0, max_value=100, value=0, step=1)
    memo = st.text_area("메모", placeholder="강도, 컨디션 등 자유롭게")
    submitted = st.form_submit_button("저장")

    if submitted:
        if not name.strip():
            st.error("운동 종류를 입력해 주세요.")
        else:
            db.add_exercise(date.isoformat(), name.strip(), int(minutes), int(sets), memo.strip())
            st.success(f"저장 완료: {date} · {name}")

st.divider()

# ---------- 기록 조회 ----------
st.subheader("전체 운동 기록")
df = db.get_df("exercise")
if df.empty:
    st.info("아직 기록이 없습니다.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 기록 삭제
    with st.expander("기록 삭제"):
        del_id = st.number_input("삭제할 기록의 id", min_value=0, step=1, value=0)
        if st.button("삭제", type="primary"):
            db.delete_row("exercise", int(del_id))
            st.success(f"id {del_id} 기록을 삭제했습니다. 새로고침하면 반영됩니다.")
            st.rerun()
