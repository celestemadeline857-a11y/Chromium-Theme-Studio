import copy


class HistoryManager:
    def __init__(self, max_depth=50):
        self.undo_stack = []
        self.redo_stack = []
        self.max_depth = max_depth

    def push_state(self, state_data):
        snapshot = copy.deepcopy(state_data)
        if self.undo_stack and self.undo_stack[-1] == snapshot:
            return
        self.undo_stack.append(snapshot)
        if len(self.undo_stack) > self.max_depth:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self, current_state):
        # Keep current state on redo, then return the previous distinct snapshot.
        if len(self.undo_stack) < 2:
            return None
        self.redo_stack.append(copy.deepcopy(current_state))
        self.undo_stack.pop()
        return copy.deepcopy(self.undo_stack[-1])

    def redo(self, current_state):
        if not self.redo_stack:
            return None
        self.undo_stack.append(copy.deepcopy(current_state))
        return self.redo_stack.pop()
