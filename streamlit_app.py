import os
import streamlit as st
from datetime import datetime, timedelta
import json
import uuid


### >>>>> 함수 시작
def load_team_members():
    with open("team_members.json", "r", encoding="utf-8") as file:
        team_members = json.load(file)
    
    # 팀 멤버 이름을 오름차순으로 정렬
    sorted_team_members = sorted(team_members)
    
    return sorted_team_members

def load_projects():
    try:
        if os.path.exists("projects.json") and os.path.getsize("projects.json") > 0:
            with open("projects.json", "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            return []
    except json.JSONDecodeError:
        st.error("프로젝트 파일이 손상되었습니다. 새로운 프로젝트 목록을 시작합니다.")
        return []

def save_projects(projects):
    with open("projects.json", "w", encoding="utf-8") as file:
        json.dump(projects, file, ensure_ascii=False, indent=2)
        
def calculate_workdays(start_date, days):
    current_date = start_date
    workdays = 0
    while workdays < days:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            workdays += 1
        current_date += timedelta(days=1)
    return current_date - timedelta(days=1)  # Subtract one day as we want the last workday

def create_tasks(project):
    tasks = []
    start_date = datetime.strptime(project['created_at'], "%Y-%m-%d %H:%M:%S.%f").date()
    
    for task_name, days in project['task_days'].items():
        if days > 0:  # 1일 이상 계획된 태스크만 생성
            end_date = calculate_workdays(start_date, days)
            task = {
                "id": str(uuid.uuid4()),
                "name": task_name,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "duration": days,
                "completed": False
            }
            tasks.append(task)
            
            # 각 태스크에 대해 팀 멤버와 공유하는 태스크 생성
            for member in project['team_members']:
                share_task = {
                    "id": str(uuid.uuid4()),
                    "name": f"Share {task_name} status with {member}",
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "duration": days,
                    "completed": False
                }
                tasks.append(share_task)
            
            start_date = end_date + timedelta(days=1)
    
    return tasks

def calculate_project_progress(tasks):
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task['completed'])
    return (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

def load_archived_projects():
    try:
        if os.path.exists("archived_projects.json") and os.path.getsize("archived_projects.json") > 0:
            with open("archived_projects.json", "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            return []
    except json.JSONDecodeError:
        st.error("아카이브된 프로젝트 파일이 손상되었습니다. 새로운 아카이브를 시작합니다.")
        return []

def save_archived_projects(projects):
    with open("archived_projects.json", "w", encoding="utf-8") as file:
        json.dump(projects, file, ensure_ascii=False, indent=2)
        
def add_custom_task(project, task_name, task_days, start_date):
    end_date = calculate_workdays(start_date, task_days)
    new_task = {
        "id": str(uuid.uuid4()),
        "name": task_name,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "duration": task_days,
        "completed": False
    }
    project['tasks'].append(new_task)
    
    # 공유 태스크 생성
    for member in project['team_members']:
        share_task = {
            "id": str(uuid.uuid4()),
            "name": f"Share {task_name} status with {member}",
            "start_date": str(start_date),
            "end_date": str(end_date),
            "duration": task_days,
            "completed": False
        }
        project['tasks'].append(share_task)
    
    # 프로젝트의 total_planned_days 업데이트
    project['total_planned_days'] += task_days

### 함수 끝 <<<<<

### >>> 데이터 획득/관리
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
### 데이터 획득/관리 <<<<<

### Streamlit UI 구성 >>>>>
# 헤더
st.title("태스크 ㄸ-ㅐ노스")
st.divider()
st.subheader(":blue[일을 놓치지 말고, 잘 쳐내자.]")
st.caption("일 하나 못했다고 골머리 싸지 말고, 그런 생각은 빨리 잘라내자. 하쿠나 마타타 o(*￣▽￣*)o")
st.image("https://cdn.marvel.com/content/1x/019tha_ons_mas_mob_01_0.jpg")
st.markdown('<br/>', unsafe_allow_html=True)

# 프로젝트 폼 추가
st.subheader("프로젝트 생성", divider=True)
with st.form("my_form"):
    st.write(":blue[새로운 프로젝트를 만들어주세요]")
    project_name = st.text_input("프로젝트 이름을 작성해주세요")

    deadline_date = st.date_input("프로젝트 마감일을 설정해주세요", value=None)
    st.write("설정된 마감일은 :", deadline_date)

    # 리소스 입력을 위한 열 생성
    columns = st.columns(5)
    
    # 리소스 입력 필드 생성 및 값 저장
    resource_days = {}
    for i, (key, label) in enumerate(resource_categories.items()):
        with columns[i % 5]:
            resource_days[key] = st.number_input(f"{label}(일)", min_value=0, step=1, value=0)

    # 작업 내용 공유할 팀 동료 선택
    selected_members = st.multiselect(
        "작업 내용을 공유해야 할 팀 동료를 선택해주세요",
        informed_team_members
    )
    st.markdown('<br/>', unsafe_allow_html=True)
    
    # 리소스 계산 및 프로젝트 확정 버튼
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
            # 리소스 계산
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
            
            # 리소스 결과 표시
            result_columns = st.columns(5)
            for i, (key, label) in enumerate(resource_categories.items()):
                with result_columns[i % 5]:
                    st.write(f"{label} :green[{resource_days[key]}] 일")

            if confirm_button:
                # 프로젝트 데이터 생성 및 저장 로직
                project_data = {
                    "id": str(uuid.uuid4()),
                    "name": project_name,
                    "deadline": str(deadline_date),
                    "created_at": str(datetime.now()),
                    "task_days": resource_days,
                    "team_members": selected_members,
                    "total_planned_days": total_planned_resource_days,
                    "available_days": available_resource_days
                }
                
                # 태스크 생성
                project_data['tasks'] = create_tasks(project_data)
                
                # 프로젝트 저장
                projects = load_projects()
                projects.append(project_data)
                save_projects(projects)
                st.success('프로젝트가 성공적으로 생성되었습니다!', icon="✅")
                st.rerun()  # 페이지를 새로고침하여 새 프로젝트를 표시합니다.

# 기존 프로젝트 목록 표시 및 태스크 관리
st.subheader("프로젝트 목록", divider=True)
projects = load_projects()
for i, project in enumerate(projects):
    # 프로젝트 완료 상태에 따라 제목 설정
    project_status = ":green[DONE]" if project.get('completed', False) else ""
    expander_title = f"{project['name']} 마감일: :red[{project['deadline']}] {project_status}"
    
    with st.expander(expander_title):
        st.divider()
        st.write(f"생성일: :red[{project['created_at']}]")
        st.write(f"총 계획 일수: :red[{project['total_planned_days']} 일]")
        st.write(f"가용 일수: :red[{project['available_days']} 일]")
        st.write("태스크 공유 멤버:", ", ".join(project['team_members']))
        
        # 프로젝트 진행률 표시
        progress = calculate_project_progress(project['tasks'])
        st.progress(int(progress))
        st.write(f"프로젝트 진행률: {progress:.2f}%")
        
        # 프로젝트 완료 및 아카이브, 커스텀 태스크 추가
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("프로젝트 완료", key=f"complete_{project['id']}"):
                project['completed'] = True
                save_projects(projects)
                st.success("프로젝트가 완료되었습니다!")
                st.rerun()
        with col2:
            if st.button("프로젝트 아카이브", key=f"archive_{project['id']}"):
                archived_projects = load_archived_projects()
                archived_projects.append(project)
                save_archived_projects(archived_projects)
                projects.remove(project)
                save_projects(projects)
                st.success("프로젝트가 아카이브되었습니다.")
                st.rerun()
        with col3:
            if st.button("커스텀 태스크 추가", key=f"add_task_{project['id']}"):
                st.session_state[f"show_task_form_{project['id']}"] = True

        # 커스텀 태스크 추가 폼
        if st.session_state.get(f"show_task_form_{project['id']}", False):
            st.write("새 태스크 추가")
            task_name = st.text_input("태스크 이름", key=f"task_name_{project['id']}")
            task_days = st.number_input("사용 리소스 일자", min_value=1, value=1, key=f"task_days_{project['id']}")
            start_date = st.date_input("업무 시작일", value=datetime.now().date(), key=f"start_date_{project['id']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("리소스 계산", key=f"calculate_resource_{project['id']}"):
                    end_date = calculate_workdays(start_date, task_days)
                    st.write(f"예상 종료일: {end_date}")
                    st.write(f"총 계획 일수: {project['total_planned_days'] + task_days} 일")
            
            with col2:
                if st.button("태스크 추가하기", key=f"add_task_confirm_{project['id']}"):
                    add_custom_task(project, task_name, task_days, start_date)
                    save_projects(projects)
                    st.success("새 태스크가 추가되었습니다!")
                    st.session_state[f"show_task_form_{project['id']}"] = False
                    st.rerun()
            with col3:
                if st.button("취소", key=f"cancel_add_task_{project['id']}"):
                    st.session_state[f"show_task_form_{project['id']}"] = False
                    st.rerun()
        
        # 태스크 목록 표시 및 관리
        st.write(":blue[TASKS]")
        
        # 업무 태스크와 공유 태스크를 분리하여 표시
        work_tasks = [task for task in project['tasks'] if not task['name'].startswith("Share")]
        share_tasks = [task for task in project['tasks'] if task['name'].startswith("Share")]
        
        for task in work_tasks:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
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
                    key=f"{project['id']}_{task['id']}",
                    label_visibility="collapsed"
                )
        
        st.write(":blue[업무 공유]")
        for task in share_tasks:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            with col1:
                st.write(f"**{task['name']}**")
            with col2:
                st.write(f"공유 일자 : {task['end_date']}")
            with col3:
                st.write(f"당일 업무 종료 이후 1시간 이내")
            with col4:
                task['completed'] = st.checkbox(
                    label=f"완료 - {task['name']}",
                    value=task['completed'],
                    key=f"{project['id']}_{task['id']}",
                    label_visibility="collapsed"
                )
        
        # 프로젝트 업데이트 (태스크 완료 상태 변경 시)
        if st.button("프로젝트 업데이트", key=f"update_{project['id']}"):
            save_projects(projects)
            st.success("프로젝트가 업데이트되었습니다!")
            st.rerun()

### Streamlit UI 구성 <<<<<