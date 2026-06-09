"""비밀번호 로그인 모듈.

비밀번호는 코드가 아니라 Streamlit secrets( app_password )에 저장한다.
각 페이지 맨 위에서 require_login() 을 호출하면, 통과하기 전까지 화면이 잠긴다.
"""
import hmac

import streamlit as st


def require_login() -> None:
    """로그인되지 않았으면 비밀번호 입력 화면을 띄우고 실행을 멈춘다."""
    # secrets 에 비밀번호가 설정되지 않은 경우(주로 로컬) — 경고만 하고 통과시킨다.
    expected = st.secrets.get("app_password", "") if hasattr(st, "secrets") else ""
    if not expected:
        return

    if st.session_state.get("authenticated"):
        return

    def _check():
        if hmac.compare_digest(st.session_state.get("password", ""), expected):
            st.session_state["authenticated"] = True
            del st.session_state["password"]  # 입력값을 세션에 남기지 않는다.
        else:
            st.session_state["authenticated"] = False

    st.title("🔒 로그인")
    st.text_input("비밀번호", type="password", key="password", on_change=_check)
    if st.session_state.get("authenticated") is False:
        st.error("비밀번호가 틀렸습니다.")
    st.stop()
