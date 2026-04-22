from demo_seed import available_demo_scenarios, load_demo_scenario


def test_available_demo_scenarios_contains_expected_names() -> None:
    assert available_demo_scenarios() == [
        "normal_day",
        "tight_budget",
        "conflict_heavy",
    ]


def test_load_demo_scenario_returns_owner_with_data() -> None:
    owner = load_demo_scenario("conflict_heavy")

    assert owner.owner_name == "Demo Jordan"
    assert len(owner.pets) == 2
    assert len(owner.tasks) > 0


def test_load_demo_scenario_rejects_unknown_name() -> None:
    try:
        load_demo_scenario("unknown")
        assert False, "Expected ValueError for unknown scenario name"
    except ValueError as exc:
        assert "Unknown demo scenario" in str(exc)
