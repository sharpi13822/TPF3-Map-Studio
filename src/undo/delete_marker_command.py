from src.undo.command import Command


class DeleteMarkerCommand(Command):

    def __init__(
        self,
        controller,
        marker
    ):
        self.controller = controller
        self.marker = marker

    def execute(self):

        self.controller.remove_marker(
            self.marker.id
        )

    def undo(self):

        self.controller.add_marker(
            self.marker.lat,
            self.marker.lon,
            self.marker.text,
            self.marker.id
        )