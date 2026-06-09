"""운동 기록 페이지 — 종목을 탭으로 선택하고 중량과 함께 한 번에 저장."""
import datetime as dt

import pandas as pd
import streamlit as st

import auth
import data
import db
import style

st.set_page_config(page_title="운동 기록", page_icon="🏃")
style.inject()
auth.require_login()
data.ensure_db()

# 모바일에서도 '종목 버튼'과 '중량칸'을 같은 줄에 유지(좁은 화면 자동 줄바꿈 방지)
st.markdown(
    """
    <style>
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- 종목 구성 ----------
WEIGHT_EXERCISES = ["풀업", "데드리프트", "벤치프레스", "오버헤드프레스", "팔"]  # 중량 입력 있음
TOGGLE_ONLY = ["복근", "유산소"]                                              # 했다/안했다만
MAIN = "본운동"                                                              # 부위 선택
BODY_PARTS = ["가슴", "등", "어깨", "하체"]
ORDER = WEIGHT_EXERCISES + TOGGLE_ONLY + [MAIN]
DEFAULT_WEIGHT = 50.0  # 과거 기록이 없을 때 중량 기본값

style.hero("운동 기록 🏃", "오늘 한 종목을 눌러 선택하세요.")

# 저장 직후 안내 메시지(새로고침 후에도 보이도록 세션에 잠시 보관)
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

date = st.date_input("날짜", dt.date.today())
st.caption("7~8회 가능한 중량 * 4세트")

# ---------- 종목 토글 + 중량/부위 ----------
for name in ORDER:
    sel_key = f"sel_{name}"
    selected = st.session_state.get(sel_key, False)

    left, right = st.columns([1, 1.2], vertical_alignment="center")
    with left:
        if st.button(
            name,
            key=f"btn_{name}",
            type="primary" if selected else "secondary",
            use_container_width=True,
        ):
            selected = not selected
            st.session_state[sel_key] = selected
            # 중량 종목을 새로 켤 때 마지막 중량을 기본값으로 채운다.
            if selected and name in WEIGHT_EXERCISES and f"w_{name}" not in st.session_state:
                last = db.get_last_weight(name)
                st.session_state[f"w_{name}"] = last if last is not None else DEFAULT_WEIGHT
            st.rerun()

    with right:
        if selected and name in WEIGHT_EXERCISES:
            st.number_input(
                "중량(kg)", min_value=0.0, max_value=500.0, step=5.0,
                key=f"w_{name}", label_visibility="collapsed",
            )
        elif selected and name == MAIN:
            st.selectbox(
                "부위", BODY_PARTS, key="part_main", label_visibility="collapsed",
            )

st.write("")

# ---------- 저장 ----------
if st.button("💾 저장", type="primary", use_container_width=True):
    chosen = [n for n in ORDER if st.session_state.get(f"sel_{n}")]
    if not chosen:
        st.warning("선택된 운동이 없습니다.")
    else:
        for n in chosen:
            if n in WEIGHT_EXERCISES:
                db.add_exercise(date.isoformat(), n, weight=float(st.session_state.get(f"w_{n}", 0)))
            elif n == MAIN:
                db.add_exercise(date.isoformat(), n, detail=st.session_state.get("part_main"))
            else:  # 복근, 유산소
                db.add_exercise(date.isoformat(), n)
        # 선택/중량/부위 상태 초기화
        for n in ORDER:
            st.session_state.pop(f"sel_{n}", None)
            st.session_state.pop(f"w_{n}", None)
        st.session_state.pop("part_main", None)
        data.refresh()
        st.session_state["flash"] = f"저장 완료: {', '.join(chosen)}"
        st.rerun()

st.divider()

# ---------- 최근 기록 + 삭제 ----------
st.subheader("최근 운동 기록")
df = data.load_df("exercise")
if df.empty:
    st.info("아직 기록이 없습니다.")
else:
    show = df[["date", "name", "weight", "detail"]].rename(
        columns={"date": "날짜", "name": "운동", "weight": "중량(kg)", "detail": "부위"}
    )
    st.dataframe(show.head(30), use_container_width=True, hide_index=True)

    with st.expander("기록 삭제"):
        # id 를 외우지 않고, 보기 좋은 라벨로 골라 삭제한다.
        def _label(row) -> str:
            parts = [row.date, row.name]
            if pd.notna(row.weight):
                parts.append(f"{row.weight:g}kg")
            if isinstance(row.detail, str) and row.detail:
                parts.append(f"({row.detail})")
            return " · ".join(parts[:2]) + (" " + " ".join(parts[2:]) if len(parts) > 2 else "")

        options = {_label(r): r.id for r in df.head(50).itertuples()}
        pick = st.selectbox("삭제할 기록 선택", list(options.keys()))
        if st.button("삭제", type="secondary"):
            db.delete_row("exercise", int(options[pick]))
            data.refresh()
            st.rerun()
