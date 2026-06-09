"""식단 기록 페이지 — 끼니(단일 선택) + 음식(다중 선택)을 한 번에 저장."""
import datetime as dt

import streamlit as st

import auth
import data
import db
import style

st.set_page_config(page_title="식단 기록", page_icon="🍽️",
                   initial_sidebar_state="expanded")
style.inject()
auth.require_login()
data.ensure_db()

style.hero("식단 기록 🍽️", "끼니를 고르고 먹은 음식을 선택하세요.")
style.top_nav()

# ---------- 구성 ----------
MEALS = ["아침", "점심", "저녁", "야식"]                       # 하나만 선택
FOODS = ["밥 210g", "밥 300g", "닭가슴살 100g", "닭가슴살 200g", "일반식"]  # 여러 개 선택

# 저장 직후 안내 메시지
if "diet_flash" in st.session_state:
    st.success(st.session_state.pop("diet_flash"))

date = st.date_input("날짜", dt.date.today())

# ---------- 끼니 (단일 선택) ----------
st.markdown("**끼니**")
mcols = st.columns(len(MEALS))
for col, m in zip(mcols, MEALS):
    active = st.session_state.get("meal_sel") == m
    if col.button(m, key=f"mealbtn_{m}",
                  type="primary" if active else "secondary",
                  use_container_width=True):
        st.session_state["meal_sel"] = None if active else m  # 다시 누르면 해제
        st.rerun()

# ---------- 음식 (다중 선택, 2열 그리드) ----------
st.markdown("**음식** (여러 개 선택 가능)")
for i in range(0, len(FOODS), 2):
    cols = st.columns(2)
    for col, f in zip(cols, FOODS[i:i + 2]):
        active = st.session_state.get(f"food_{f}", False)
        if col.button(f, key=f"foodbtn_{f}",
                      type="primary" if active else "secondary",
                      use_container_width=True):
            st.session_state[f"food_{f}"] = not active
            st.rerun()

st.write("")

# ---------- 저장 ----------
if st.button("💾 저장", type="primary", use_container_width=True):
    meal = st.session_state.get("meal_sel")
    chosen = [f for f in FOODS if st.session_state.get(f"food_{f}")]
    if not meal:
        st.warning("끼니를 선택하세요.")
    elif not chosen:
        st.warning("음식을 하나 이상 선택하세요.")
    else:
        for f in chosen:
            db.add_diet(date.isoformat(), meal, f, None, None)
        data.refresh()
        # 선택 상태 초기화
        st.session_state.pop("meal_sel", None)
        for f in FOODS:
            st.session_state.pop(f"food_{f}", None)
        st.session_state["diet_flash"] = f"저장 완료: {meal} · {', '.join(chosen)}"
        st.rerun()

st.divider()

# ---------- 최근 기록 + 삭제 ----------
st.subheader("최근 식단 기록")
df = data.load_df("diet")
if df.empty:
    st.info("아직 기록이 없습니다.")
else:
    show = df[["date", "meal", "food"]].rename(
        columns={"date": "날짜", "meal": "끼니", "food": "음식"}
    )
    st.dataframe(show.head(30), use_container_width=True, hide_index=True)

    with st.expander("기록 삭제"):
        options = {f"{r.date} · {r.meal} · {r.food}": r.id for r in df.head(50).itertuples()}
        pick = st.selectbox("삭제할 기록 선택", list(options.keys()))
        if st.button("삭제", type="secondary"):
            db.delete_row("diet", int(options[pick]))
            data.refresh()
            st.rerun()
