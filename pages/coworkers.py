import streamlit as st
import json
import os

# 동료 목록을 저장할 파일 경로
FILE_PATH = "team_members.json"

# 파일에서 동료 목록 불러오기
def load_team_members():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return ["최지웅", "유현승", "김예지", "박응수"]  # 기본 동료 목록

# 동료 목록을 파일에 저장하기
def save_team_members(members):
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(members, file, ensure_ascii=False, indent=4)

# 사용자 세션 상태를 사용하여 동적으로 팀 동료 목록을 유지
if 'team_members' not in st.session_state:
    st.session_state.team_members = load_team_members()

# 팀 동료 추가 기능
def add_team_member():
    new_member = st.session_state.new_member
    if new_member and new_member not in st.session_state.team_members:
        st.session_state.team_members.append(new_member)
        save_team_members(st.session_state.team_members)  # 목록 업데이트 시 저장
        st.session_state.new_member = ""  # 입력 필드 비우기
    elif new_member in st.session_state.team_members:
        st.warning(f"{new_member}는 이미 목록에 있습니다.")

# UI 구성
st.title("팀 동료 관리")
st.divider()

# 새로운 팀 동료 추가
st.subheader("팀 동료 추가")
st.text_input("추가할 팀 동료 이름", key="new_member")
st.button("팀 동료 추가", on_click=add_team_member)

# 팀 동료 목록 표시
st.subheader("현재 팀 동료 목록")
st.write(st.session_state.team_members)

# 작업 내용 공유할 팀 동료 선택
selected_members = st.multiselect(
    "작업 내용을 공유해야 할 팀 동료를 선택해주세요",
    st.session_state.team_members
)

st.write("선택된 팀 동료:", selected_members)
