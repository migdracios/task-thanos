# recruitment_applications.py

import streamlit as st
import json
import os

RECRUITMENT_FILE_PATH = "course_recruitments.json"

def load_recruitments():
    if os.path.exists(RECRUITMENT_FILE_PATH):
        with open(RECRUITMENT_FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return []

def save_recruitments(recruitments):
    with open(RECRUITMENT_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(recruitments, file, ensure_ascii=False, indent=4)

if 'recruitments' not in st.session_state:
    st.session_state.recruitments = load_recruitments()

def assign_freelancer(recruitment_id, freelancer_name):
    for recruitment in st.session_state.recruitments:
        if recruitment['id'] == recruitment_id:
            recruitment['assigned_to'] = freelancer_name
            recruitment['status'] = 'Assigned'
            save_recruitments(st.session_state.recruitments)
            st.success(f"{freelancer_name}님이 {recruitment['course_name']} 강의에 배정되었습니다.")
            st.rerun()

st.title("구인 신청 및 배정 관리")
st.divider()

if st.session_state.get('user_role') == 'admin':
    st.subheader("구인 신청 목록")
    for recruitment in st.session_state.recruitments:
        if recruitment['status'] == 'Open' and recruitment['applicants']:
            st.write(f"강의명: {recruitment['course_name']}")
            st.write(f"필요한 역할: {', '.join(recruitment['roles_needed'])}")
            st.write(f"지원자: {', '.join(recruitment['applicants'])}")
            assigned_freelancer = st.selectbox(f"배정할 외주자 선택 (ID: {recruitment['id']})", 
                                               ['선택하세요'] + recruitment['applicants'], 
                                               key=f"assign_{recruitment['id']}")
            if assigned_freelancer != '선택하세요':
                if st.button(f"배정하기 (ID: {recruitment['id']})", key=f"assign_button_{recruitment['id']}"):
                    assign_freelancer(recruitment['id'], assigned_freelancer)
            st.divider()
elif st.session_state.get('user_role') == 'freelancer':
    st.subheader("나의 배정 현황")
    for recruitment in st.session_state.recruitments:
        if recruitment['assigned_to'] == st.session_state.get('user_name'):
            st.write(f"강의명: {recruitment['course_name']}")
            st.write(f"설명: {recruitment['description']}")
            st.write(f"역할: {', '.join(recruitment['roles_needed'])}")
            st.write("상태: 배정됨")
            st.divider()