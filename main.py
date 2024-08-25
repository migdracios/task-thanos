import streamlit as st
from datetime import datetime

# 헤더
st.title("태스크 ㄸ-ㅐ노스")
st.divider()
st.subheader(":blue[일을 놓치지 말고, 잘 쳐내자.]")
st.caption("일 하나 못했다고 골머리 싸지 말고, 그런 생각은 빨리 잘라내자 :ninja:")
st.image("https://cdn.marvel.com/content/1x/019tha_ons_mas_mob_01_0.jpg")
st.html('<br/>')

# 프로젝트 폼 추가
st.subheader("프로젝트 목록", divider=True)
with st.form("my_form"):
    st.write(":blue[새로운 프로젝트를 만들어주세요]")
    project_name = st.text_input("프로젝트 이름을 작성해주세요")

    deadline_date = st.date_input("프로젝트 마감일을 설정해주세요", value=None)
    st.write("설정된 마감일은 :", deadline_date)
    form_col1, form_col2, form_col3 = st.columns(3)
    with form_col1:
        design_days = st.number_input("기획(일)", step=1)
        recruit_days = st.number_input("섭외(일)", step=1)
    with form_col2:
        confirm_course_days = st.number_input("강의 작업 확정(일)", step=1)
        code_source_days = st.number_input("소스 작성(일)", step=1)
        write_notion_days = st.number_input("자료 작성(일)", step=1)
    with form_col3:
        record_days = st.number_input("영상 촬영(일)", step=1)
        edit_days = st.number_input("편집 검수(일)", step=1)
        backoffice_days = st.number_input("백오피스 작업(일)", step=1)
    
    # 리소스 계산 버튼 클릭 시 입력 오류 확인 
    if st.form_submit_button('리소스 계산'):
        if project_name == "":
            st.error('ERROR : 프로젝트 제목을 설정해주세요', icon="🚨")
        elif deadline_date is None:
            st.error('ERROR : 프로젝트 마감일을 설정해주세요', icon="🚨")
        elif deadline_date <= datetime.today().date():
            st.error('ERROR : 마감일은 오늘 날짜보다 이후여야 합니다.', icon="🚨")
        else:
            # 폼 제출 시 리소스 계산 및 프로젝트 추가 항목
            st.write(":green[리소스 계산 결과]")
            today_date = datetime.today().date()
            available_resource_days = (deadline_date - today_date).days
            total_planned_resource_days = design_days + recruit_days + confirm_course_days + code_source_days + write_notion_days + record_days + edit_days + backoffice_days
            
            if available_resource_days < total_planned_resource_days:
                st.write(f"마감일 기준 리소스 : :red[{available_resource_days} 일]")
                st.write(f"내가 계획한 리소스 : :red[{total_planned_resource_days} 일]")
            else:
                st.write(f"마감일 기준 리소스 : :blue[{available_resource_days} 일]")
                st.write(f"내가 계획한 리소스 : :blue[{total_planned_resource_days} 일]")
            form_result_col1, form_result_col2, form_result_col3 = st.columns(3)
            with form_result_col1:
                st.write(f"기획 :green[{design_days}] 일")
                st.write(f"섭외 :green[{recruit_days}] 일")
            with form_result_col2:
                st.write(f"강의 작업 확정 :green[{confirm_course_days}] 일")
                st.write(f"소스 작성 :green[{code_source_days}] 일")
                st.write(f"자료 작성 :green[{write_notion_days}] 일")
            with form_result_col3:
                st.write(f"영상 촬영 :green[{record_days}] 일")
                st.write(f"편집 검수 :green[{edit_days}] 일")
                st.write(f"백오피스 작업 :green[{backoffice_days}] 일")
            
            options = st.multiselect(
                "작업 내용을 공유 해야할 팀 동료를 선택해주세요",
                ["최지웅", "유현승", "김예지", "박응수"],
                ["Yellow", "Red"],
            )
            if st.form_submit_button("프로젝트 확정하기", type="primary"):
                st.success('프로젝트 생성 완료!', icon="✅")
            
# 기본 팀 동료 목록
default_team_members = ["최지웅", "유현승", "김예지", "박응수"]

# 사용자 세션 상태를 사용하여 동적으로 팀 동료 목록을 유지
if 'team_members' not in st.session_state:
    st.session_state.team_members = default_team_members.copy()

# 팀 동료 추가 기능
def add_team_member():
    new_member = st.session_state.new_member
    if new_member and new_member not in st.session_state.team_members:
        st.session_state.team_members.append(new_member)
        st.session_state.new_member = ""  # 입력 필드 비우기
    elif new_member in st.session_state.team_members:
        st.warning(f"{new_member}는 이미 목록에 있습니다.")

# UI 구성
st.title("팀 동료 관리")

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
        
        
        