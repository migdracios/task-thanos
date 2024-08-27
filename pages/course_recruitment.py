# course_recruitment.py

import streamlit as st
import json
import os
from datetime import datetime

# 관리자 비밀번호 (실제 애플리케이션에서는 더 안전한 방법으로 저장해야 합니다)
ADMIN_PASSWORD = "admin123"

# 파일 경로 설정
RECRUITMENT_FILE_PATH = "course_recruitments.json"
FREELANCERS_FILE_PATH = "freelancers.json"

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_data(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def show_course_recruitment():
    st.title("신규 강의 제작 편집/검수자 구인")
    
    recruitments = load_data(RECRUITMENT_FILE_PATH)
    freelancers = load_data(FREELANCERS_FILE_PATH)
    
    # 구인 중인 강의 목록
    st.subheader("구인 중인 강의 목록")
    with st.expander("구인 중인 강의 보기"):
        for index, recruitment in enumerate(recruitments):
            st.write(f"강의명: {recruitment['course_name']}")
            st.write(f"분량: {recruitment['duration']}")
            st.write(f"추가 금액: {recruitment['additional_pay']}")
            st.write(f"편집 일정: {recruitment['editing_schedule']}")
            st.write(f"검수 일정: {recruitment['review_schedule']}")
            st.write(f"필요한 역할: {', '.join(recruitment['roles_needed'])}")
            st.write(f"등록일: {recruitment['created_at']}")
            
            # 지원하기 기능
            freelancer_names = [f['name'] for f in freelancers]
            selected_freelancer = st.multiselect("지원하기", freelancer_names, key=f"apply_{index}")
            if st.button("지원 확인", key=f"apply_confirm_{index}"):
                if selected_freelancer:
                    recruitment['applicants'] = recruitment.get('applicants', []) + selected_freelancer
                    save_data(recruitments, RECRUITMENT_FILE_PATH)
                    st.success(f"{', '.join(selected_freelancer)}님의 지원이 완료되었습니다.")
                    st.rerun()
            st.divider()
    
    # 새 구인 공고 등록 폼
    st.subheader("새 구인 공고 등록")
    with st.expander("새 구인 공고 등록"):
        with st.form("new_recruitment_form"):
            course_name = st.text_input("강의명")
            duration = st.text_input("분량 (예: 8주차, 주차별 2시간)")
            additional_pay = st.text_input("추가 금액 (옵션)")
            editing_schedule = st.text_input("편집 일정")
            review_schedule = st.text_input("검수 일정")
            roles_needed = st.multiselect("필요한 역할", ["편집자", "검수자"])
            
            # 비밀번호 입력 필드
            admin_password = st.text_input("관리자 비밀번호", type="password")
            
            submit_button = st.form_submit_button("구인 공고 등록")
            
            if submit_button:
                if admin_password == ADMIN_PASSWORD:
                    new_recruitment = {
                        "course_name": course_name,
                        "duration": duration,
                        "additional_pay": additional_pay,
                        "editing_schedule": editing_schedule,
                        "review_schedule": review_schedule,
                        "roles_needed": roles_needed,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "applicants": []
                    }
                    recruitments.append(new_recruitment)
                    save_data(recruitments, RECRUITMENT_FILE_PATH)
                    st.success("새로운 구인 공고가 등록되었습니다.")
                    st.rerun()
                else:
                    st.error("관리자 비밀번호가 올바르지 않습니다.")

if __name__ == "__main__":
    show_course_recruitment()