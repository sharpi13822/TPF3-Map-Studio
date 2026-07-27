from PySide6.QtCore import QObject, Slot


class Bridge(QObject):
    """
    Bridge zwischen JavaScript und Python.
    """

    def __init__(self, controller):
        super().__init__()

        self.controller = controller

    # ---------------------------------------------------------
    # Kartenklick
    # ---------------------------------------------------------

    @Slot(float, float)
    def mapClicked(
        self,
        lat: float,
        lon: float
    ):
        print(
            f"Klick: {lat:.6f}, {lon:.6f}"
        )

        self.controller.map_clicked(
            lat,
            lon
        )

    # ---------------------------------------------------------
    # Marker angeklickt
    # ---------------------------------------------------------

    @Slot(str)
    def markerClicked(
        self,
        marker_id: str
    ):
        """
        Wird aufgerufen, wenn ein Marker angeklickt wurde.
        """

        print(
            f"Marker geklickt: {marker_id}"
        )

        self.controller.marker_clicked(
            marker_id
        )    

    # ---------------------------------------------------------
    # Rechteck (temporär)
    # ---------------------------------------------------------

    @Slot(float, float, float, float)
    def selectionChanged(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ):
        """
        Wird in Sprint 4.4.3 entfernt.
        Aktuell noch als Übergang vorhanden.
        """

        self.controller.selection_changed(
            lat1,
            lon1,
            lat2,
            lon2
        )