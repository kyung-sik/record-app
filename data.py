"""성능을 위한 DB 접근 캐싱 계층.

매 상호작용(버튼 탭)마다 클라우드 DB에 접속하면 느리므로:
  - DB 준비(init_db)는 프로세스당 한 번만 (cache_resource)
  - 데이터 조회(get_df)는 캐시해 두고, 저장/삭제 시에만 갱신 (cache_data)
"""
import streamlit as st

import db


@st.cache_resource
def ensure_db() -> bool:
    """테이블 준비/마이그레이션을 프로세스 생애 한 번만 수행한다."""
    db.init_db()
    return True


@st.cache_data(ttl=600, show_spinner=False)
def load_df(table: str):
    """테이블 데이터를 캐시해서 반환한다(최대 10분)."""
    return db.get_df(table)


def refresh() -> None:
    """저장/삭제 후 호출 — 다음 조회 때 최신 데이터를 다시 불러오게 한다."""
    load_df.clear()
