import streamlit as st
from datetime import datetime, timedelta
from mongo_atlas_controller import (
    load_team_members, load_projects, save_project, update_project,
    delete_project, load_tasks, save_task, update_task, delete_task
)

# Helper functions
def calculate_workdays(start_date, days):
    current_date = start_date
    workdays = 0
    while workdays < days:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            workdays += 1
        current_date += timedelta(days=1)
    return current_date - timedelta(days=1)

def create_tasks(project):
    tasks = []
    start_date = datetime.strptime(project['created_at'], "%Y-%m-%d %H:%M:%S.%f").date()
    
    for task_name, days in project['task_days'].items():
        if days > 0:
            end_date = calculate_workdays(start_date, days)
            task = {
                "project_id": project['_id'],
                "name": task_name,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "duration": days,
                "completed": False
            }
            task_id = save_task(task)
            task['_id'] = task_id
            tasks.append(task)
            
            for member in project['team_members']:
                share_task = {
                    "project_id": project['_id'],
                    "name": f"Share {task_name} status with {member}",
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "duration": days,
                    "completed": False
                }
                share_task_id = save_task(share_task)
                share_task['_id'] = share_task_id
                tasks.append(share_task)
            
            start_date = end_date + timedelta(days=1)
    
    return tasks

def calculate_project_progress(tasks):
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task['completed'])
    return (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

# Data management
informed_team_members = load_team_members()
resource_categories = {
    "design": "기획",
    "recruit": "섭외",
    "confirm_course": "강의 작업 확정",
    "code_source": "소스 작성",
    "write_notion": "자료 작성",
    "record": "영상 촬영",
    "edit": "편집 검수",
    "backoffice": "백오피스 작업",
    "non_bau": "NON-BAU",
    "communication": "고객 소통",
    "team_automation": "업무 자동화",
    "crm_message": "CRM 메시지",
    "live_course": "라이브 특강",
    "make_landing": "랜딩 페이지"
}

# Streamlit UI
st.title("태스크 ㄸ-ㅐ노스")
st.divider()
st.subheader(":blue[일을 놓치지 말고, 잘 쳐내자.]")
st.caption("일 하나 못했다고 골머리 싸지 말고, 그런 생각은 빨리 잘라내자. 하쿠나 마타타 o(*￣▽￣*)o")
st.image("https://cdn.marvel.com/content/1x/019tha_ons_mas_mob_01_0.jpg")
st.markdown('<br/>', unsafe_allow_html=True)

# Project creation form
st.subheader("프로젝트 생성", divider=True)
with st.form("my_form"):
    st.write(":blue[새로운 프로젝트를 만들어주세요]")
    project_name = st.text_input("프로젝트 이름을 작성해주세요")
    deadline_date = st.date_input("프로젝트 마감일을 설정해주세요", value=None)
    st.write("설정된 마감일은 :", deadline_date)

    columns = st.columns(5)
    resource_days = {}
    for i, (key, label) in enumerate(resource_categories.items()):
        with columns[i % 5]:
            resource_days[key] = st.number_input(f"{label}(일)", min_value=0, step=1, value=0)

    selected_members = st.multiselect(
        "작업 내용을 공유해야 할 팀 동료를 선택해주세요",
        informed_team_members
    )
    st.markdown('<br/>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        calculate_button = st.form_submit_button('리소스 계산')
    with col2:
        confirm_button = st.form_submit_button("프로젝트 확정하기", type="primary")
    
    if calculate_button or confirm_button:
        if project_name == "":
            st.error('ERROR : 프로젝트 제목을 설정해주세요', icon="🚨")
        elif deadline_date is None:
            st.error('ERROR : 프로젝트 마감일을 설정해주세요', icon="🚨")
        elif deadline_date <= datetime.today().date():
            st.error('ERROR : 마감일은 오늘 날짜보다 이후여야 합니다.', icon="🚨")
        else:
            today_date = datetime.today().date()
            available_resource_days = (deadline_date - today_date).days
            total_planned_resource_days = sum(resource_days.values())
            
            st.write(":green[리소스 계산 결과]")
            if available_resource_days < total_planned_resource_days:
                st.write(f"마감일 기준 리소스 : :red[{available_resource_days} 일]")
                st.write(f"내가 계획한 리소스 : :red[{total_planned_resource_days} 일]")
            else:
                st.write(f"마감일 기준 리소스 : :blue[{available_resource_days} 일]")
                st.write(f"내가 계획한 리소스 : :blue[{total_planned_resource_days} 일]")
            
            result_columns = st.columns(5)
            for i, (key, label) in enumerate(resource_categories.items()):
                with result_columns[i % 5]:
                    st.write(f"{label} :green[{resource_days[key]}] 일")

            if confirm_button:
                project_data = {
                    "name": project_name,
                    "deadline": str(deadline_date),
                    "created_at": str(datetime.now()),
                    "task_days": resource_days,
                    "team_members": selected_members,
                    "total_planned_days": total_planned_resource_days,
                    "available_days": available_resource_days
                }
                
                project_id = save_project(project_data)
                project_data['_id'] = project_id
                project_data['tasks'] = create_tasks(project_data)
                
                st.success('프로젝트가 성공적으로 생성되었습니다!', icon="✅")
                st.rerun()

# Project list and task management
st.subheader("프로젝트 목록", divider=True)
projects = load_projects()
for project in projects:
    project_status = ":green[DONE]" if project.get('completed', False) else ""
    expander_title = f"{project['name']} 마감일: :red[{project['deadline']}] {project_status}"
    
    with st.expander(expander_title):
        st.divider()
        st.write(f"생성일: :red[{project['created_at']}]")
        st.write(f"총 계획 일수: :red[{project['total_planned_days']} 일]")
        st.write(f"가용 일수: :red[{project['available_days']} 일]")
        st.write("태스크 공유 멤버:", ", ".join(project['team_members']))
        
        tasks = load_tasks(project['_id'])
        progress = calculate_project_progress(tasks)
        st.progress(int(progress))
        st.write(f"프로젝트 진행률: {progress:.2f}%")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("완료", key=f"complete_{project['_id']}"):
                project['completed'] = True
                update_project(project)
                st.success("프로젝트가 완료되었습니다!")
                st.rerun()
        with col2:
            if st.button("다시 진행", key=f"inprogress_{project['_id']}"):
                project['completed'] = False
                update_project(project)
                st.rerun()
        with col3:
            if st.button("아카이브", key=f"archive_{project['_id']}"):
                delete_project(project['_id'])
                st.success("프로젝트가 아카이브되었습니다.")
                st.rerun()
        with col4:
            if st.button("커스텀 태스크", key=f"add_task_{project['_id']}"):
                st.session_state[f"show_task_form_{project['_id']}"] = True

        if st.session_state.get(f"show_task_form_{project['_id']}", False):
            st.write("새 태스크 추가")
            task_name = st.text_input("태스크 이름", key=f"task_name_{project['_id']}")
            task_days = st.number_input("사용 리소스 일자", min_value=1, value=1, key=f"task_days_{project['_id']}")
            start_date = st.date_input("업무 시작일", value=datetime.now().date(), key=f"start_date_{project['_id']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("리소스 계산", key=f"calculate_resource_{project['_id']}"):
                    end_date = calculate_workdays(start_date, task_days)
                    st.write(f"예상 종료일: {end_date}")
                    st.write(f"총 계획 일수: {project['total_planned_days'] + task_days} 일")
            
            with col2:
                if st.button("태스크 추가하기", key=f"add_task_confirm_{project['_id']}"):
                    new_task = {
                        "project_id": project['_id'],
                        "name": task_name,
                        "start_date": str(start_date),
                        "end_date": str(calculate_workdays(start_date, task_days)),
                        "duration": task_days,
                        "completed": False
                    }
                    save_task(new_task)
                    project['total_planned_days'] += task_days
                    update_project(project)
                    st.success("새 태스크가 추가되었습니다!")
                    st.session_state[f"show_task_form_{project['_id']}"] = False
                    st.rerun()
            with col3:
                if st.button("취소", key=f"cancel_add_task_{project['_id']}"):
                    st.session_state[f"show_task_form_{project['_id']}"] = False
                    st.rerun()
        
        st.write(":blue[TASKS]")
        
        work_tasks = [task for task in tasks if not task['name'].startswith("Share")]
        share_tasks = [task for task in tasks if task['name'].startswith("Share")]
        
        for task in work_tasks:
            col1, col2, col3, col4, col5, col6 = st.columns([3, 4, 2, 1, 1, 1])
            with col1:
                st.write(f"**{task['name']}**")
            with col2:
                st.write(f"{task['start_date']} ~ {task['end_date']}")
            with col3:
                st.write(f"리소스: {task['duration']}일")
            with col4:
                task['completed'] = st.checkbox(
                    label=f"완료 - {task['name']}",
                    value=task['completed'],
                    key=f"{project['_id']}_{task['_id']}",
                    label_visibility="collapsed"
                )
            with col5:
                if st.button("💬", key=f"edit_{task['_id']}"):
                    st.session_state[f"edit_task_{task['_id']}"] = True
            with col6:
                if st.button("❌", key=f"delete_{task['_id']}"):
                    delete_task(task['_id'])
                    project['total_planned_days'] -= task['duration']
                    update_project(project)
                    st.success("태스크가 삭제되었습니다.")
                    st.rerun()
            
            if st.session_state.get(f"edit_task_{task['_id']}", False):
                st.write("태스크 수정")
                new_name = st.text_input("태스크 이름", value=task['name'], key=f"new_name_{task['_id']}")
                new_days = st.number_input("사용 리소스 일자", min_value=1, value=task['duration'], key=f"new_days_{task['_id']}")
                new_start_date = st.date_input("업무 시작일", value=datetime.strptime(task['start_date'], "%Y-%m-%d").date(), key=f"new_start_date_{task['_id']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("수정 완료", key=f"confirm_edit_{task['_id']}"):
                        updated_task = {
                            "_id": task['_id'],
                            "project_id": project['_id'],
                            "name": new_name,
                            "start_date": str(new_start_date),
                            "end_date": str(calculate_workdays(new_start_date, new_days)),
                            "duration": new_days,
                            "completed": task['completed']
                        }
                        update_task(updated_task)
                        project['total_planned_days'] += (new_days - task['duration'])
                        update_project(project)
                        st.success("태스크가 수정되었습니다.")
                        st.session_state[f"edit_task_{task['_id']}"] = False
                        st.rerun()
                with col2:
                    if st.button("취소", key=f"cancel_edit_{task['_id']}"):
                        st.session_state[f"edit_task_{task['_id']}"] = False
                        st.rerun()
        
        st.write(":blue[업무 공유]")
        for task in share_tasks:
            col1, col2, col3, col4, col5, col6 = st.columns([3, 4, 2, 1, 1, 1])
            with col1:
                st.write(f"**{task['name']}**")
            with col2:
                st.write(f"공유 일자 : {task['end_date']}")
            with col3:
                st.write(f"1시간 이내")
            with col4:
                task['completed'] = st.checkbox(
                    label=f"완료 - {task['name']}",
                    value=task['completed'],
                    key=f"{project['_id']}_{task['_id']}_share",
                    label_visibility="collapsed"
                )
            with col5:
                if st.button("💬", key=f"edit_{task['_id']}_share"):
                    st.session_state[f"edit_task_{task['_id']}_share"] = True
            with col6:
                if st.button("❌", key=f"delete_{task['_id']}_share"):
                    delete_task(task['_id'])
                    st.success("공유 태스크가 삭제되었습니다.")
                    st.rerun()
            
            if st.session_state.get(f"edit_task_{task['_id']}_share", False):
                st.write("공유 태스크 수정")
                new_name = st.text_input("태스크 이름", value=task['name'], key=f"new_name_{task['_id']}_share")
                new_end_date = st.date_input("공유 일자", value=datetime.strptime(task['end_date'], "%Y-%m-%d").date(), key=f"new_end_date_{task['_id']}_share")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("수정 완료", key=f"confirm_edit_{task['_id']}_share"):
                        updated_task = {
                            "_id": task['_id'],
                            "project_id": project['_id'],
                            "name": new_name,
                            "start_date": task['start_date'],
                            "end_date": str(new_end_date),
                            "duration": task['duration'],
                            "completed": task['completed']
                        }
                        update_task(updated_task)
                        st.success("공유 태스크가 수정되었습니다.")
                        st.session_state[f"edit_task_{task['_id']}_share"] = False
                        st.rerun()
                with col2:
                    if st.button("취소", key=f"cancel_edit_{task['_id']}_share"):
                        st.session_state[f"edit_task_{task['_id']}_share"] = False
                        st.rerun()
        
        # 프로젝트 업데이트 (태스크 완료 상태 변경 시)
        if st.button("프로젝트 업데이트", key=f"update_{project['_id']}"):
            for task in tasks:
                update_task(task)
            update_project(project)
            st.success("프로젝트가 업데이트되었습니다!")
            st.rerun()