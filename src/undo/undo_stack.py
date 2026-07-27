from PySide6.QtCore import QObject, Signal


class UndoStack(QObject):

    stack_changed = Signal()

    def __init__(self):

        super().__init__()

        self.undo_stack = []
        self.redo_stack = []

    # -----------------------------------------------------

    def push(self, command):

        command.execute()

        self.undo_stack.append(command)

        self.redo_stack.clear()

        self.stack_changed.emit()

    # -----------------------------------------------------

    def undo(self):

        if not self.undo_stack:
            return

        command = self.undo_stack.pop()

        command.undo()

        self.redo_stack.append(command)

        self.stack_changed.emit()

    # -----------------------------------------------------

    def redo(self):

        if not self.redo_stack:
            return

        command = self.redo_stack.pop()

        command.execute()

        self.undo_stack.append(command)

        self.stack_changed.emit()

    # -----------------------------------------------------

    def clear(self):

        self.undo_stack.clear()

        self.redo_stack.clear()

        self.stack_changed.emit()

    # -----------------------------------------------------

    @property
    def can_undo(self):

        return len(self.undo_stack) > 0

    @property
    def can_redo(self):

        return len(self.redo_stack) > 0