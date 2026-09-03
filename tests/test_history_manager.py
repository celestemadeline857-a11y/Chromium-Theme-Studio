from utils.history_manager import HistoryManager


def test_undo_returns_previous_state_and_redo_restores_current():
    history = HistoryManager()
    history.push_state({"value": 1})
    history.push_state({"value": 2})

    assert history.undo({"value": 2}) == {"value": 1}
    assert history.redo({"value": 1}) == {"value": 2}


def test_duplicate_snapshots_are_not_stored():
    history = HistoryManager()
    state = {"value": 1}
    history.push_state(state)
    history.push_state(state)
    assert history.undo({"value": 1}) is None
