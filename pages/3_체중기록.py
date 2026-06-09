"""체중 기록 페이지 — 몸무게 입력/조회/삭제와 추이 그래프."""
import datetime as dt

import streamlit as st

import auth
import data
import db
import style

st.set_page_config(page_title="체중 기록", page_icon="⚖️")
style.inject()
auth.require_login()
data.ensure_db()

style.hero("체중 기록 ⚖️", "몸무게를 기록하고 추이를 확인하세요.")

# ---------- 입력 폼 ----------
with st.form("weight_form", clear_on_submit=True):
    date = st.date_input("날짜", dt.date.today())
    weight_kg = st.number_input("몸무게(kg)", min_value=0.0, max_value=300.0, value=60.0, step=0.1)
    memo = st.text_area("메모", placeholder="공복/식후 등")
    submitted = st.form_submit_button("저장")

    if submitted:
        db.add_weight(date.isoformat(), float(weight_kg), memo.strip())
        data.refresh()
        st.success(f"저장 완료: {date} · {weight_kg} kg")

st.divider()

# ---------- 추이 그래프 ----------
df = data.load_df("weight")
if df.empty:
    st.info("아직 기록이 없습니다.")
else:
    st.subheader("체중 추이")
    chart_df = df.sort_values("date").set_index("date")[["weight_kg"]]
    st.line_chart(chart_df, y="weight_kg")

    st.subheader("전체 체중 기록")
    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("기록 삭제"):
        del_id = st.number_input("삭제할 기록의 id", min_value=0, step=1, value=0)
        if st.button("삭제", type="primary"):
            db.delete_row("weight", int(del_id))
            data.refresh()
            st.success(f"id {del_id} 기록을 삭제했습니다.")
            st.rerun()
