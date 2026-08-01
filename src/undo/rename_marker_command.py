from src.undo.command import Command


class RenameMarkerCommand(Command):
    """
    Benennt einen Marker um und unterstützt Undo/Redo.
    """

    def __init__(
        self,
        controller,
        marker_id,
        old_text,
        new_text
    ):

        self.controller = controller

        self.marker_id = marker_id

        self.old_text = old_text
        self.new_text = new_text

    def execute(self):

        self.controller.rename_marker(
            self.marker_id,
            self.new_text
        )

    def undo(self):

        self.controller.rename_marker(
            self.marker_id,
            self.old_text
        )