from src.undo.command import Command


class MoveMarkerCommand(Command):

    def __init__(
        self,
        controller,
        marker_id,
        old_lat,
        old_lon,
        new_lat,
        new_lon
    ):
        self.controller = controller
        self.marker_id = marker_id

        self.old_lat = old_lat
        self.old_lon = old_lon

        self.new_lat = new_lat
        self.new_lon = new_lon

    def execute(self):

        self.controller.move_marker(
            self.marker_id,
            self.new_lat,
            self.new_lon
        )

    def undo(self):

        self.controller.move_marker(
            self.marker_id,
            self.old_lat,
            self.old_lon
        )