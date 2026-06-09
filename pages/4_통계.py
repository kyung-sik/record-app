"""통계 페이지 — 주간/월간 운동·식단·체중 요약."""
import datetime as dt

import streamlit as st

import auth
import data
import style

st.set_page_config(page_title="통계", page_icon="📊",
                   initial_sidebar_state="expanded")
style.inject()
auth.require_login()
data.ensure_db()

style.hero("통계 📊", "기간별 운동·식단·체중을 한눈에 확인하세요.")
style.top_nav()

# ---------- 기간 선택 ----------
period = st.radio("기간", ["주간 (최근 7일)", "월간 (최근 30일)"],
                  horizontal=True, label_visibility="collapsed")
days = 7 if period.startswith("주간") else 30
cutoff = (dt.date.today() - dt.timedelta(days=days - 1)).isoformat()
st.caption(f"{cutoff} ~ {dt.date.today().isoformat()} ({days}일간)")

# 데이터 로드 + 기간 필터
ex_df = data.load_df("exercise")
diet_df = data.load_df("diet")
wt_df = data.load_df("weight")

ex_p = ex_df[ex_df["date"] >= cutoff] if not ex_df.empty else ex_df
diet_p = diet_df[diet_df["date"] >= cutoff] if not diet_df.empty else diet_df
wt_p = wt_df[wt_df["date"] >= cutoff] if not wt_df.empty else wt_df

st.divider()

# ---------- 운동 통계 ----------
st.subheader("🏃 운동")
if ex_p.empty:
    st.info("이 기간에 운동 기록이 없습니다.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("운동한 날", f"{ex_p['date'].nunique()} 일")
    c2.metric("총 기록", f"{len(ex_p)} 건")
    c3.metric("하루 평균", f"{len(ex_p) / max(ex_p['date'].nunique(), 1):.1f} 종목")

    st.markdown("**종목별 횟수**")
    st.bar_chart(ex_p["name"].value_counts())

    main_df = ex_p[ex_p["name"] == "본운동"]
    if not main_df.empty and main_df["detail"].notna().any():
        st.markdown("**본운동 부위별 횟수**")
        st.bar_chart(main_df["detail"].dropna().value_counts())

st.divider()

# ---------- 식단 통계 ----------
st.subheader("🍽️ 식단")
if diet_p.empty:
    st.info("이 기간에 식단 기록이 없습니다.")
else:
    c1, c2 = st.columns(2)
    c1.metric("기록한 날", f"{diet_p['date'].nunique()} 일")
    c2.metric("총 음식 수", f"{len(diet_p)} 개")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**끼니별 횟수**")
        st.bar_chart(diet_p["meal"].value_counts())
    with col_b:
        st.markdown("**음식별 횟수**")
        st.bar_chart(diet_p["food"].value_counts())

st.divider()

# ---------- 체중 통계 ----------
st.subheader("⚖️ 체중")
if wt_p.empty:
    st.info("이 기간에 체중 기록이 없습니다.")
else:
    wt_sorted = wt_p.sort_values("date")
    start = float(wt_sorted.iloc[0]["weight_kg"])
    end = float(wt_sorted.iloc[-1]["weight_kg"])
    change = round(end - start, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("평균", f"{wt_p['weight_kg'].mean():.1f} kg")
    c2.metric("최저", f"{wt_p['weight_kg'].min():.1f} kg")
    c3.metric("최고", f"{wt_p['weight_kg'].max():.1f} kg")
    c4.metric("변화", f"{change:+} kg")

    chart_df = wt_sorted.set_index("date")[["weight_kg"]]
    st.line_chart(chart_df, y="weight_kg")
