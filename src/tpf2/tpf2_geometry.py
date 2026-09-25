import math


class TPF2Geometry:
    """
    Konvertiert OSM-Koordinaten (Lat/Lon)
    in lokale metrische TPF2-Koordinaten.

    OSM:
        latitude  = Nord/Süd
        longitude = Ost/West

    TPF2 lokal:
        x = Ost/West in Metern
        y = Nord/Süd in Metern
        z = Höhe in Metern

    Der Ursprung wird vom TPF2Exporter bestimmt.
    Alle Koordinaten sind relativ zu diesem Ursprung.
    """

    METERS_PER_DEGREE_LAT = 111_320.0

    def __init__(
        self,
        origin_lat,
        origin_lon,
        rotation_deg=0.0,
    ):
        self.origin_lat = float(origin_lat)
        self.origin_lon = float(origin_lon)
        self.rotation_deg = float(rotation_deg)

        # Längengrad wird abhängig von der
        # geografischen Breite skaliert.
        self._lon_scale = (
            self.METERS_PER_DEGREE_LAT
            * math.cos(
                math.radians(
                    self.origin_lat
                )
            )
        )

        # Rechteck-Tool / gedrehtes Kartenband:
        # "up" zeigt in Richtung des gedrehten Kartennordens,
        # "right" steht im 90 Grad Winkel dazu. Bei rotation_deg=0
        # ist das exakt die Identitaet (up=Nord, right=Ost) - bestehende
        # Aufrufe ohne Drehwinkel verhalten sich dadurch unveraendert.
        theta = math.radians(self.rotation_deg)
        self._up = (
            math.sin(theta),
            math.cos(theta),
        )
        self._right = (
            math.sin(theta + math.pi / 2),
            math.cos(theta + math.pi / 2),
        )

    # ------------------------------------------------------------------
    # Einzelpunkt
    # ------------------------------------------------------------------

    def convert(
        self,
        lat,
        lon,
    ):
        """
        Konvertiert einen OSM-Punkt
        (latitude, longitude)

        in lokale TPF2-Koordinaten:

            (x, y)
        """

        lat = float(lat)
        lon = float(lon)

        # Erst wie bisher: Ost-/Nordversatz zum Ursprung in Metern
        # (unrotiert, e = Ost, n = Nord).
        e = (
            lon - self.origin_lon
        ) * self._lon_scale

        n = (
            lat - self.origin_lat
        ) * self.METERS_PER_DEGREE_LAT

        # Dann in das (ggf. gedrehte) Kartenband-Koordinatensystem
        # drehen. Bei rotation_deg=0 ist das die Identitaet (x=e, y=n),
        # also exakt das bisherige Verhalten.
        x = e * self._right[0] + n * self._right[1]
        y = e * self._up[0] + n * self._up[1]

        return (
            x,
            y,
        )

    # ------------------------------------------------------------------
    # Umkehrung: lokale x,y -> lat,lon
    # ------------------------------------------------------------------

    def inverse(
        self,
        x,
        y,
    ):
        """
        Kehrt convert() um: aus lokalen (gedrehten) TPF2-Koordinaten
        wieder echte lat/lon-Koordinaten berechnen. Wird fuer den
        Heightmap-Export gebraucht (dort wird fuer jedes Pixel im
        Kartenband die zugehoerige lat/lon-Position gesucht, um dort
        den Hoehenwert abzufragen).

        Exakte Umkehrung von convert(), da right/up ein orthonormales
        Koordinatensystem bilden (die Transponierte ist die Inverse).
        """

        x = float(x)
        y = float(y)

        e = x * self._right[0] + y * self._up[0]
        n = x * self._right[1] + y * self._up[1]

        lat = self.origin_lat + n / self.METERS_PER_DEGREE_LAT
        lon = self.origin_lon + e / self._lon_scale

        return (
            lat,
            lon,
        )

    # ------------------------------------------------------------------
    # Punkt mit Höhe
    # ------------------------------------------------------------------

    def convert_3d(
        self,
        lat,
        lon,
        z=0.0,
    ):
        """
        Konvertiert einen OSM-Punkt direkt
        in eine TPF2-3D-Koordinate.

        Ergebnis:

            [x, y, z]
        """

        x, y = self.convert(
            lat,
            lon,
        )

        return [
            float(x),
            float(y),
            float(z),
        ]

    # ------------------------------------------------------------------
    # Linie
    # ------------------------------------------------------------------

    def line(
        self,
        coordinates,
    ):
        """
        Konvertiert eine komplette OSM-Linie.

        Eingabe:

            [
                (lat, lon),
                (lat, lon),
                ...
            ]

        Ausgabe:

            [
                (x, y),
                (x, y),
                ...
            ]
        """

        if not coordinates:
            return []

        result = []

        for lat, lon in coordinates:
            result.append(
                self.convert(
                    lat,
                    lon,
                )
            )

        return result

    # ------------------------------------------------------------------
    # Linie 3D
    # ------------------------------------------------------------------

    def line_3d(
        self,
        coordinates,
        z=0.0,
    ):
        """
        Konvertiert eine komplette Linie
        in TPF2-3D-Koordinaten.

        Die Höhe wird für alle Punkte
        auf z gesetzt.
        """

        if not coordinates:
            return []

        result = []

        for lat, lon in coordinates:
            result.append(
                self.convert_3d(
                    lat,
                    lon,
                    z,
                )
            )

        return result

    # ------------------------------------------------------------------
    # Mehrere Linien
    # ------------------------------------------------------------------

    def lines(
        self,
        geometries,
    ):
        """
        Konvertiert mehrere Linien.

        Eingabe:

            [
                [(lat, lon), ...],
                [(lat, lon), ...],
            ]

        Ausgabe:

            [
                [(x, y), ...],
                [(x, y), ...],
            ]
        """

        if not geometries:
            return []

        return [
            self.line(
                geometry
            )
            for geometry in geometries
        ]

    # ------------------------------------------------------------------
    # Entfernung
    # ------------------------------------------------------------------

    @staticmethod
    def distance(
        point_a,
        point_b,
    ):
        """
        Berechnet die Entfernung zwischen
        zwei lokalen TPF2-Punkten in Metern.

        Eingabe:

            (x1, y1)
            (x2, y2)
        """

        x1, y1 = point_a
        x2, y2 = point_b

        return math.hypot(
            x2 - x1,
            y2 - y1,
        )

    # ------------------------------------------------------------------
    # Tangente
    # ------------------------------------------------------------------

    @staticmethod
    def tangent(
        point_a,
        point_b,
    ):
        """
        Erzeugt den Tangentenvektor von
        point_a nach point_b.

        Die Länge der Tangente entspricht
        der Länge des Linienabschnitts.

        Das entspricht der Verwendung von
        Positions- und Tangentenvektoren
        innerhalb einer TPF2-edgeList.
        """

        x1, y1 = point_a
        x2, y2 = point_b

        return [
            float(x2 - x1),
            float(y2 - y1),
            0.0,
        ]

    # ------------------------------------------------------------------
    # Ursprung
    # ------------------------------------------------------------------

    def get_origin(
        self,
    ):
        """
        Gibt den geografischen Ursprung
        des aktuellen Exporters zurück.
        """

        return (
            self.origin_lat,
            self.origin_lon,
        )

    # ------------------------------------------------------------------
    # Eigenschaften
    # ------------------------------------------------------------------

    @property
    def origin_latitude(
        self,
    ):
        """
        Ursprung Breitengrad.
        """

        return self.origin_lat

    @property
    def origin_longitude(
        self,
    ):
        """
        Ursprung Längengrad.
        """

        return self.origin_lon

    @property
    def longitude_scale(
        self,
    ):
        """
        Aktueller Meterfaktor für einen
        Längengrad am Exportursprung.
        """

        return self._lon_scale

    @property
    def right_vector(
        self,
    ):
        """
        (Ost-, Nord-Anteil) der lokalen X-Achse
        (bereits um rotation_deg gedreht).
        """

        return self._right

    @property
    def up_vector(
        self,
    ):
        """
        (Ost-, Nord-Anteil) der lokalen Y-Achse
        (bereits um rotation_deg gedreht).
        """

        return self._up

    @property
    def latitude_scale(
        self,
    ):
        """
        Meterfaktor für einen Breitengrad.
        """

        return self.METERS_PER_DEGREE_LAT