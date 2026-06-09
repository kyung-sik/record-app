"""비밀번호 로그인 + 자동 로그인(쿠키 기억).

로그인에 성공하면 브라우저 쿠키에 인증 토큰을 30일간 저장한다.
이후에는 앱을 다시 열어도 쿠키가 살아 있으면 자동으로 통과된다.
토큰은 비밀번호의 해시라서, 비밀번호를 모르면 쿠키를 위조할 수 없다.
"""
import datetime as dt
import hashlib
import hmac
import time

import extra_streamlit_components as stx
import streamlit as st

COOKIE = "record_app_auth"
REMEMBER_DAYS = 30


def _manager() -> stx.CookieManager:
    # 한 번의 실행에서 하나의 인스턴스만 생성한다.
    return stx.CookieManager(key="record_app_cookie_manager")


def _token(password: str) -> str:
    """비밀번호로부터 쿠키에 저장할 토큰(해시)을 만든다."""
    return hashlib.sha256(f"record-app::{password}".encode()).hexdigest()


def require_login() -> None:
    """로그인 확인. 쿠키가 있으면 자동 로그인, 없으면 로그인 폼을 띄운다."""
    expected = st.secrets.get("app_password", "") if hasattr(st, "secrets") else ""
    if not expected:
        return  # 비밀번호 미설정(주로 로컬) → 통과

    token = _token(expected)
    cm = _manager()
    cookies = cm.get_all() or {}  # 브라우저 쿠키 로드

    # 쿠키에 저장된 토큰이 맞으면 자동 로그인
    if not st.session_state.get("authenticated") and cookies.get(COOKIE) == token:
        st.session_state["authenticated"] = True

    if st.session_state.get("authenticated"):
        _logout_button(cm)
        return

    # ── 로그인 폼 ──
    st.title("🔒 로그인")
    pw = st.text_input("비밀번호", type="password", key="login_pw")
    if st.button("로그인", type="primary", use_container_width=True):
        if hmac.compare_digest(pw, expected):
            st.session_state["authenticated"] = True
            expires = dt.datetime.now() + dt.timedelta(days=REMEMBER_DAYS)
            cm.set(COOKIE, token, expires_at=expires, key="set_auth")
            time.sleep(0.3)  # 쿠키가 브라우저에 저장될 시간을 잠깐 준다.
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop()


def _logout_button(cm: stx.CookieManager) -> None:
    """사이드바에 로그아웃 버튼을 둔다(자동 로그인 해제)."""
    with st.sidebar:
        if st.button("로그아웃", key="logout_btn", use_container_width=True):
            cm.delete(COOKIE, key="del_auth")
            st.session_state["authenticated"] = False
            time.sleep(0.3)
            st.rerun()
