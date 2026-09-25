import requests

from src.map.objects.selection import Selection
from src.osm.osm_parser import OSMParser
from src.osm.objects.osm_data import OSMData
from src.osm.overpass_query_builder import OverpassQueryConfig, build_query


class OverpassClient:
    """
    Overpass-Client mit Fallback auf mehrere Server.
    """

    SERVERS = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
    ]

    def __init__(self):

        self.timeout = 60
        self.parser = OSMParser()

    # ---------------------------------------------------------

    def download(
        self,
        selection: Selection,
        config: OverpassQueryConfig | None = None,
    ) -> OSMData:

        query = build_query(selection, config)

        print("Overpass-Abfrage:")
        print(query)

        last_exception = None

        for server in self.SERVERS:

            print()
            print("=" * 60)
            print("Versuche Server:", server)

            try:

                response = requests.post(
                    server,
                    data={"data": query},
                    headers={
                        "User-Agent": "TPF3-Map-Studio",
                        "Accept": "application/json",
                    },
                    timeout=self.timeout,
                )

                print("HTTP:", response.status_code)

                response.raise_for_status()

                json_data = response.json()

                print("JSON erfolgreich empfangen.")

                osm = self.parser.parse(json_data)

                print()
                print("Download erfolgreich.")
                print(f"Nodes     : {osm.node_count}")
                print(f"Ways      : {osm.way_count}")
                print(f"Relations : {osm.relation_count}")

                return osm

            except requests.RequestException as exc:

                last_exception = exc

                print(type(exc).__name__)

                if hasattr(exc, "response") and exc.response is not None:

                    print("HTTP:", exc.response.status_code)

                    try:
                        print(exc.response.text)
                    except Exception:
                        pass

                else:
                    print(exc)

        raise RuntimeError(
            "Keiner der Overpass-Server war erreichbar."
        ) from last_exception