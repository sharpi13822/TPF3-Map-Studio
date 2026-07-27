class PolygonMatcher:
    """
    Ordnet Innenringe den passenden Außenringen zu.

    Rückgabe:

        [
            [outer, inner1, inner2],
            [outer2],
            ...
        ]
    """

    # ------------------------------------------------------------------
    # Öffentlich
    # ------------------------------------------------------------------

    def assign(self, outers, inners):

        polygons = []

        for outer in outers:
            polygons.append([outer])

        for inner in inners:

            best_polygon = None
            best_area = None

            for polygon in polygons:

                outer = polygon[0]

                if not self._ring_inside(inner, outer):
                    continue

                area = self._ring_area(outer)

                if best_area is None or area < best_area:
                    best_area = area
                    best_polygon = polygon

            if best_polygon is not None:
                best_polygon.append(inner)

        return polygons

    # ------------------------------------------------------------------
    # Ring liegt innerhalb eines anderen Rings
    # ------------------------------------------------------------------

    def _ring_inside(self, inner, outer):

        if len(inner) < 3 or len(outer) < 3:
            return False

        return self._point_in_polygon(inner[0], outer)

    # ------------------------------------------------------------------
    # Ray Casting
    # ------------------------------------------------------------------

    def _point_in_polygon(self, point, polygon):

        y, x = point

        inside = False

        j = len(polygon) - 1

        for i in range(len(polygon)):

            yi, xi = polygon[i]
            yj, xj = polygon[j]

            if ((xi > x) != (xj > x)):

                cross = (
                    (yj - yi)
                    * (x - xi)
                    / (xj - xi)
                    + yi
                )

                if y < cross:
                    inside = not inside

            j = i

        return inside

    # ------------------------------------------------------------------
    # Shoelace-Fläche
    # ------------------------------------------------------------------

    def _ring_area(self, ring):

        area = 0.0

        n = len(ring)

        if n < 3:
            return 0.0

        for i in range(n):

            y1, x1 = ring[i]
            y2, x2 = ring[(i + 1) % n]

            area += x1 * y2 - x2 * y1

        return abs(area) * 0.5