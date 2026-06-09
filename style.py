"""앱 공용 디자인 — 다크 모던(피트니스) 테마.

각 페이지 맨 위에서 style.inject() 를 호출해 커스텀 CSS를 입힌다.
style.hero(title, subtitle) 로 그라데이션 히어로 헤더를 그린다.
"""
import streamlit as st

_CSS = """
<style>
/* ── 한국어 전용 폰트 Pretendard ── */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

html, body, .stApp, [data-testid="stAppViewContainer"], .stMarkdown,
button, input, textarea, select, [data-baseweb] {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── 배경: 위쪽에서 은은하게 퍼지는 네이비 그라데이션 ── */
.stApp {
    background: radial-gradient(1100px 520px at 50% -8%, #16263f 0%, #0F172A 58%) fixed;
}

/* 본문 폭을 모바일/데스크톱 모두 보기 좋게 가운데로 */
.block-container { padding-top: 2.2rem; padding-bottom: 4rem; max-width: 720px; }

/* 군더더기 정리(우상단 메뉴/푸터만 숨김 — 사이드바는 건드리지 않는다) */
#MainMenu, footer { visibility: hidden; height: 0; }

/* 사이드바 펼침 버튼이 어두운 배경에 묻히지 않도록 또렷하게 */
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg { color: #38BDF8 !important; fill: #38BDF8 !important; }

/* 사이드바(페이지 메뉴) 배경/글자 */
[data-testid="stSidebar"] { background: #0c1322; border-right: 1px solid #1e293b; }
[data-testid="stSidebarNav"] a span { color: #cbd5e1 !important; }

/* ── 제목 ── */
h1, h2, h3 { color: #F1F5F9; letter-spacing: -0.02em; font-weight: 700; }

/* ── 히어로 헤더 ── */
.hero { padding: 4px 0 16px; }
.hero-title {
    font-size: 2rem; font-weight: 800; line-height: 1.15; letter-spacing: -0.03em;
    background: linear-gradient(120deg, #38BDF8 0%, #22D3EE 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub { color: #94A3B8; font-size: 0.92rem; margin-top: 4px; }

/* ── 지표 카드 ── */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, #1E293B 0%, #1a2436 100%);
    border: 1px solid #2b3a52; border-radius: 16px;
    padding: 16px 18px; box-shadow: 0 6px 22px rgba(0,0,0,0.28);
}
[data-testid="stMetricValue"] { color: #38BDF8; font-weight: 800; }
[data-testid="stMetricLabel"] p { color: #94A3B8; font-weight: 600; }

/* ── 버튼(기본=어두운 카드) ── */
.stButton > button {
    border-radius: 12px; border: 1px solid #334155;
    background: #1E293B; color: #cbd5e1; font-weight: 600;
    padding: 0.5rem 0.9rem; transition: all .15s ease;
}
.stButton > button:hover { border-color: #38BDF8; color: #f1f5f9; }

/* ── primary 버튼 = 네온 하늘색 ── */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #38BDF8 0%, #22D3EE 100%);
    color: #06283b; border: none; font-weight: 700;
    box-shadow: 0 0 18px rgba(56,189,248,0.45);
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 0 28px rgba(56,189,248,0.72); transform: translateY(-1px);
}

/* ── 입력 위젯 둥글게 ── */
[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input,
[data-testid="stDateInput"] input, [data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
    border-radius: 10px !important;
}

/* ── 표/차트 카드 느낌 ── */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border-radius: 12px; overflow: hidden; border: 1px solid #2b3a52;
}

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 8px 14px; }

/* ── 구분선 ── */
hr { border-color: #2b3a52; }

/* ── 확장 패널 ── */
[data-testid="stExpander"] {
    border: 1px solid #2b3a52; border-radius: 12px; background: #16213550;
}

/* ── 상단 페이지 내비게이션 바 ── */
[data-testid="stHorizontalBlock"]:has([data-testid="stPageLink"]) {
    flex-wrap: nowrap !important; gap: 6px !important;
}
[data-testid="stHorizontalBlock"]:has([data-testid="stPageLink"]) > [data-testid="stColumn"] {
    min-width: 0 !important; flex: 1 1 0 !important;
}
[data-testid="stPageLink"] a {
    display: flex; justify-content: center; align-items: center;
    background: #1E293B; border: 1px solid #2b3a52; border-radius: 10px;
    padding: 9px 2px; color: #cbd5e1 !important; font-weight: 600;
    white-space: nowrap;
}
[data-testid="stPageLink"] a:hover { border-color: #38BDF8; color: #ffffff !important; }
[data-testid="stPageLink"] a p { font-size: 0.9rem; }
</style>
"""

# 상단 내비게이션에 쓸 페이지 목록 (경로는 메인 앱 기준 상대경로)
_NAV = [
    ("app.py", "홈", "🏠"),
    ("pages/1_운동기록.py", "운동", "🏃"),
    ("pages/2_식단기록.py", "식단", "🍽️"),
    ("pages/3_체중기록.py", "체중", "⚖️"),
]


def top_nav() -> None:
    """화면 상단에 페이지 이동 버튼 바를 그린다(사이드바와 무관하게 항상 표시)."""
    cols = st.columns(len(_NAV), gap="small")
    for col, (path, label, icon) in zip(cols, _NAV):
        with col:
            st.page_link(path, label=label, icon=icon)


def inject() -> None:
    """커스텀 CSS를 페이지에 주입한다(페이지 최상단에서 호출)."""
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str = "") -> None:
    """그라데이션 히어로 헤더를 그린다."""
    sub = f'<div class="hero-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="hero"><div class="hero-title">{title}</div>{sub}</div>',
        unsafe_allow_html=True,
    )
