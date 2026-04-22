import os
from datetime import date

import streamlit as st

from ai_planner import run_ai_planner_pipeline
from demo_seed import available_demo_scenarios, load_demo_scenario
from pawpal_system import Owner, Pet, Scheduler, Task
from ui_helpers import (
    completion_feedback_message,
    conflict_ui_payload,
    filter_tasks_by_due_date,
)


def _format_demo_name(name: str) -> str:
    return name.replace("_", " ").title()


def _apply_demo_scenario(name: str) -> None:
    st.session_state.owner = load_demo_scenario(name)
    st.session_state.demo_loaded_scenario = name
    st.session_state.build_ai_planner_mode = True
    st.session_state.build_show_planner_trace = True
    st.session_state.build_today_only_schedule = True
    st.session_state.build_include_completed = False
    st.session_state.build_use_time_tiebreaker = True

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name="Jordan")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

if "build_available_minutes" not in st.session_state:
    st.session_state.build_available_minutes = 60
if "build_include_completed" not in st.session_state:
    st.session_state.build_include_completed = False
if "build_use_time_tiebreaker" not in st.session_state:
    st.session_state.build_use_time_tiebreaker = True
if "build_today_only_schedule" not in st.session_state:
    st.session_state.build_today_only_schedule = True
if "build_ai_planner_mode" not in st.session_state:
    st.session_state.build_ai_planner_mode = False
if "build_show_planner_trace" not in st.session_state:
    st.session_state.build_show_planner_trace = False
if "demo_loaded_scenario" not in st.session_state:
    st.session_state.demo_loaded_scenario = None
if "demo_message" not in st.session_state:
    st.session_state.demo_message = ""

demo_scenarios = available_demo_scenarios()
if "demo_selected_scenario" not in st.session_state:
    st.session_state.demo_selected_scenario = demo_scenarios[0]

if "demo_auto_seed_checked" not in st.session_state:
    st.session_state.demo_auto_seed_checked = True
    env_scenario = os.getenv("PAWPAL_DEMO_SCENARIO", "").strip()
    if env_scenario:
        try:
            _apply_demo_scenario(env_scenario)
            st.session_state.demo_selected_scenario = env_scenario
            st.session_state.demo_message = (
                "Auto-loaded demo scenario "
                f"'{_format_demo_name(env_scenario)}' from PAWPAL_DEMO_SCENARIO."
            )
        except ValueError as exc:
            st.session_state.demo_message = str(exc)

with st.sidebar:
    st.header("Demo Controls")
    st.caption("Seed repeatable demo data for live walkthroughs.")

    selected_demo_scenario = st.selectbox(
        "Load demo scenario",
        options=demo_scenarios,
        key="demo_selected_scenario",
        format_func=_format_demo_name,
    )

    sidebar_col1, sidebar_col2 = st.columns(2)
    with sidebar_col1:
        if st.button("Load scenario", use_container_width=True):
            _apply_demo_scenario(selected_demo_scenario)
            st.session_state.demo_message = (
                f"Loaded '{_format_demo_name(selected_demo_scenario)}'. "
                "AI planner mode and trace are enabled."
            )
            st.rerun()
    with sidebar_col2:
        if st.button("Reset demo data", use_container_width=True):
            st.session_state.owner = Owner(owner_name="Jordan")
            st.session_state.demo_loaded_scenario = None
            st.session_state.build_ai_planner_mode = False
            st.session_state.build_show_planner_trace = False
            st.session_state.demo_message = "Reset to empty owner profile."
            st.rerun()

    if st.session_state.demo_loaded_scenario:
        st.success(
            f"Active demo: {_format_demo_name(st.session_state.demo_loaded_scenario)}"
        )
    if st.session_state.demo_message:
        st.info(st.session_state.demo_message)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.owner_name)
owner.owner_name = owner_name

st.markdown("### Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_id = st.text_input("Pet ID", placeholder="pet-1")
    pet_name = st.text_input("Pet name", placeholder="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    submit_pet = st.form_submit_button("Add pet")

if submit_pet:
    try:
        owner.add_pet(
            Pet(pet_id=pet_id.strip(), pet_name=pet_name.strip(), species=species)
        )
        st.success(f"Added pet '{pet_name.strip()}'.")
    except ValueError as exc:
        st.error(str(exc))

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "Pet ID": pet.pet_id,
                "Name": pet.pet_name,
                "Species": pet.species,
                "Task count": len(pet.tasks),
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Create tasks and assign each task to a pet.")

if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        description = st.text_input("Task description", placeholder="Morning walk")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20, step=1
        )
        task_time = st.time_input("Scheduled time", value=None)
        due_date = st.date_input("Due date", value=date.today())
        frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
        priority = st.number_input("Priority (1-5)", min_value=1, max_value=5, value=3)

        pet_options = {
            f"{pet.pet_name} ({pet.pet_id})": pet.pet_id for pet in owner.pets
        }
        selected_pet_label = st.selectbox("Assign to pet", list(pet_options.keys()))

        submit_task = st.form_submit_button("Add task")

    if submit_task:
        try:
            owner.add_task(
                Task(
                    description=description.strip(),
                    duration_in_minutes=int(duration),
                    frequency=frequency,
                    pet_id=pet_options[selected_pet_label],
                    due_date=due_date,
                    time=task_time.strftime("%H:%M") if task_time else "00:00",
                    priority=int(priority),
                )
            )
            st.success("Task added.")
        except ValueError as exc:
            st.error(str(exc))
else:
    st.info("Add at least one pet before adding tasks.")

if owner.tasks:
    st.write("Current tasks")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_pet_filter = st.selectbox(
            "Filter by pet",
            ["All pets"] + [pet.pet_name for pet in owner.pets],
        )
    with col2:
        selected_status_filter = st.selectbox(
            "Filter by status",
            ["All", "Pending", "Completed"],
        )
    with col3:
        sort_tasks_by_time = st.checkbox("Sort filtered tasks by time", value=True)

    only_due_today = st.checkbox("Show only tasks due today", value=False)

    status_map = {"All": None, "Pending": False, "Completed": True}
    pet_filter = None if selected_pet_filter == "All pets" else selected_pet_filter
    filtered_tasks = owner.filter_tasks(
        is_completed=status_map[selected_status_filter],
        pet_name=pet_filter,
    )
    if only_due_today:
        filtered_tasks = filter_tasks_by_due_date(filtered_tasks, date.today())

    if sort_tasks_by_time:
        filtered_tasks = scheduler.sort_by_time(filtered_tasks)

    if filtered_tasks:
        st.table(
            [
                {
                    "Description": task.description,
                    "Pet": owner.get_pet(task.pet_id).pet_name
                    if owner.get_pet(task.pet_id)
                    else task.pet_id,
                    "Time": task.time,
                    "Due Date": task.due_date.isoformat(),
                    "Duration (min)": task.duration_in_minutes,
                    "Frequency": task.frequency,
                    "Priority": task.priority,
                    "Status": "Done" if task.is_completed else "Pending",
                }
                for task in filtered_tasks
            ]
        )
    else:
        st.info("No tasks match the current filters.")

    pending_tasks = owner.filter_tasks(is_completed=False)
    pending_tasks = filter_tasks_by_due_date(pending_tasks, date.today())
    if pending_tasks:
        pending_task_options = {
            (
                f"{task.time} - {task.description} "
                f"({owner.get_pet(task.pet_id).pet_name if owner.get_pet(task.pet_id) else task.pet_id})"
            ): task
            for task in scheduler.sort_by_time(pending_tasks)
        }
        selected_task_label = st.selectbox(
            "Mark task complete",
            list(pending_task_options.keys()),
        )
        if st.button("Complete selected task"):
            next_task = scheduler.mark_task_complete(
                owner,
                pending_task_options[selected_task_label],
            )
            st.success(completion_feedback_message(next_task))
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate an ordered plan from tasks tied to this owner's pets.")

available_minutes = st.number_input(
    "Available minutes today", min_value=0, step=5, key="build_available_minutes"
)
include_completed = st.checkbox("Include completed tasks", key="build_include_completed")
use_time_tiebreaker = st.checkbox(
    "Use time as tie-breaker", key="build_use_time_tiebreaker"
)
today_only_schedule = st.checkbox(
    "Only include tasks due today", key="build_today_only_schedule"
)
ai_planner_mode = st.checkbox("AI planner mode", key="build_ai_planner_mode")
show_planner_trace = st.checkbox("Show planner trace", key="build_show_planner_trace")

tasks_for_planning = owner.get_tasks_for_pets()
if today_only_schedule:
    tasks_for_planning = filter_tasks_by_due_date(tasks_for_planning, date.today())

conflict_warnings = scheduler.detect_time_conflicts(
    owner,
    tasks_for_planning,
    include_completed=include_completed,
)
conflict_status, conflict_messages = conflict_ui_payload(conflict_warnings)
if conflict_status == "warning":
    for message in conflict_messages:
        st.warning(message)
else:
    for message in conflict_messages:
        st.success(message)

if st.button("Generate schedule"):
    if ai_planner_mode:
        planner_output = run_ai_planner_pipeline(
            owner=owner,
            scheduler=scheduler,
            tasks=tasks_for_planning,
            available_minutes=int(available_minutes),
            include_completed=include_completed,
            today_only_schedule=today_only_schedule,
            use_time_tiebreaker=use_time_tiebreaker,
        )
        schedule = planner_output.final_schedule

        st.info(f"AI planner confidence: {planner_output.confidence:.2f}")
        for warning in planner_output.warnings:
            st.warning(warning)

        if show_planner_trace:
            with st.expander("Planner trace", expanded=False):
                st.table(planner_output.trace)
    else:
        schedule = scheduler.generate_schedule(
            tasks_for_planning,
            available_minutes=int(available_minutes),
            include_completed=include_completed,
            use_time_tiebreaker=use_time_tiebreaker,
        )

    if schedule:
        st.success("Schedule generated.")
        st.table(
            [
                {
                    "Task": task.description,
                    "Pet": owner.get_pet(task.pet_id).pet_name
                    if owner.get_pet(task.pet_id)
                    else task.pet_id,
                    "Time": task.time,
                    "Due Date": task.due_date.isoformat(),
                    "Duration (min)": task.duration_in_minutes,
                    "Priority": task.priority,
                    "Frequency": task.frequency,
                    "Status": "Done" if task.is_completed else "Pending",
                }
                for task in schedule
            ]
        )
    else:
        st.info("No tasks scheduled with the current time budget/filters.")
