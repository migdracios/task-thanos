# freelancers.py

import streamlit as st
import json
import os

# 외주자 목록을 저장할 파일 경로
FILE_PATH = "freelancers.json"

# 파일에서 외주자 목록 불러오기
def load_freelancers():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return []  # 기본 빈 목록

# 외주자 목록을 파일에 저장하기
def save_freelancers(freelancers):
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(freelancers, file, ensure_ascii=False, indent=4)

# 사용자 세션 상태를 사용하여 동적으로 외주자 목록을 유지
if 'freelancers' not in st.session_state:
    st.session_state.freelancers = load_freelancers()

# 외주자 추가 기능
def add_freelancer():
    new_freelancer = st.session_state.new_freelancer
    roles = st.session_state.roles
    if new_freelancer:
        # 이름으로 기존 외주자 검색
        existing_freelancer = next((f for f in st.session_state.freelancers if f['name'] == new_freelancer), None)
        if existing_freelancer:
            st.warning(f"{new_freelancer}는 이미 목록에 있습니다. 역할이 업데이트됩니다.")
            existing_freelancer['roles'] = roles
        else:
            st.session_state.freelancers.append({
                'name': new_freelancer,
                'roles': roles
            })
        save_freelancers(st.session_state.freelancers)  # 목록 업데이트 시 저장
        st.session_state.new_freelancer = ""  # 입력 필드 비우기
        st.session_state.roles = []  # 역할 선택 초기화
    else:
        st.warning("외주자 이름을 입력해주세요.")

# UI 구성
st.title("외주자(편집/검수자) 관리")
st.divider()

# 새로운 외주자 추가
st.subheader("외주자 추가")
st.text_input("추가할 외주자 이름", key="new_freelancer")
st.multiselect("역할 선택", ["편집자", "검수자"], key="roles")
st.button("외주자 추가", on_click=add_freelancer)

# 외주자 목록 표시
st.subheader("현재 외주자 목록")
for freelancer in st.session_state.freelancers:
    st.write(f"{freelancer['name']} - 역할: {', '.join(freelancer['roles'])}")

# 작업 내용 공유할 외주자 선택
selected_freelancers = st.multiselect(
    "작업 내용을 공유해야 할 외주자를 선택해주세요",
    [f['name'] for f in st.session_state.freelancers]
)

st.write("선택된 외주자:", selected_freelancers)

# 외주자 삭제 기능
st.subheader("외주자 삭제")
freelancer_to_delete = st.selectbox("삭제할 외주자 선택", [f['name'] for f in st.session_state.freelancers])
if st.button("선택한 외주자 삭제"):
    st.session_state.freelancers = [f for f in st.session_state.freelancers if f['name'] != freelancer_to_delete]
    save_freelancers(st.session_state.freelancers)
    st.success(f"{freelancer_to_delete}가 삭제되었습니다.")
    st.rerun()