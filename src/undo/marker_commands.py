from src.undo.command import Command


class AddMarkerCommand(Command):
    """
    Fügt einen Marker hinzu und unterstützt Undo/Redo.
    """

    def __init__(
        self,
        controller,
        lat,
        lon,
        text=""
    ):

        self.controller = controller

        self.lat = lat
        self.lon = lon
        self.text = text

        self.marker_id = None

    def execute(self):

        if self.marker_id is None:

            self.marker_id = self.controller.add_marker(
                self.lat,
                self.lon,
                self.text
            )

        else:

            marker = self.controller.add_marker(
                self.lat,
                self.lon,
                self.text
            )

            self.marker_id = marker

    def undo(self):

        self.controller.remove_marker(
            self.marker_id
        )