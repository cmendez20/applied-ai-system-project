import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

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
                    priority=int(priority),
                )
            )
            st.success("Task added.")
        except ValueError as exc:
            st.error(str(exc))
else:
    st.info("Add at least one pet before adding tasks.")

if owner.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "Description": task.description,
                "Pet ID": task.pet_id,
                "Duration (min)": task.duration_in_minutes,
                "Frequency": task.frequency,
                "Priority": task.priority,
                "Completed": task.is_completed,
            }
            for task in owner.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate an ordered plan from tasks tied to this owner's pets.")

available_minutes = st.number_input(
    "Available minutes today", min_value=0, value=60, step=5
)
include_completed = st.checkbox("Include completed tasks", value=False)

if st.button("Generate schedule"):
    schedule = scheduler.generate_schedule_for_owner(
        owner,
        available_minutes=int(available_minutes),
        include_completed=include_completed,
    )
    if schedule:
        st.success("Schedule generated.")
        st.table(
            [
                {
                    "Task": task.description,
                    "Pet ID": task.pet_id,
                    "Duration (min)": task.duration_in_minutes,
                    "Priority": task.priority,
                    "Frequency": task.frequency,
                }
                for task in schedule
            ]
        )
    else:
        st.info("No tasks scheduled with the current time budget/filters.")
