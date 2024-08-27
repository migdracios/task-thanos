# auth.py

import streamlit as st

# 관리자 비밀번호 (실제 애플리케이션에서는 더 안전한 방법으로 저장해야 합니다)
ADMIN_PASSWORD = "tmvkfmxkzhsxpscm7515!"

def check_admin_password():
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        password = st.text_input("관리자 비밀번호를 입력하세요", type="password")
        if st.button("확인"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("관리자 인증 성공!")
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    return st.session_state.admin_authenticated

def admin_required(func):
    def wrapper(*args, **kwargs):
        if check_admin_password():
            return func(*args, **kwargs)
    return wrapper