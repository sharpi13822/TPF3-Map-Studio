/**
 * Schattenrelief (Hillshade) als Leaflet-Kachelebene.
 *
 * Rechnet das Relief im Browser aus den frei nutzbaren AWS Terrain Tiles
 * (Terrarium-Format, Mapzen/Tilezen) und legt es halbtransparent ueber
 * Satellitenbild oder Karte. Kein Kartendienst mit Zugangsschluessel noetig.
 * Die Quellen und die vorgeschriebene Namensnennung stehen unter
 * https://github.com/tilezen/joerd/blob/master/docs/attribution.md
 *
 * Terrarium-Kodierung: Hoehe in Metern = R * 256 + G + B / 256 - 32768.
 * Die Kacheln liegen bis Zoomstufe 15 vor, darueber wird vergroessert.
 */

const RELIEF_TILE_URL =
    "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png";

const RELIEF_ATTRIBUTION = t(
    "Relief: AWS Terrain Tiles (Mapzen/Tilezen; Quellen u.a. SRTM, " +
    "Copernicus, siehe github.com/tilezen/joerd)"
);

// Lichtquelle: Nordwest, 45 Grad ueber dem Horizont (klassische Schummerung)
const RELIEF_AZIMUTH_DEG = 315;
const RELIEF_ALTITUDE_DEG = 45;

// Ueberhoehung: macht flache Gelaendeformen besser sichtbar
const RELIEF_Z_FACTOR = 2.0;

let reliefWarned = false;

const ReliefLayer = L.GridLayer.extend({

    options: {
        tileSize: 256,
        maxNativeZoom: 15,
        opacity: 0.65,
        // Staerke der dunklen (Schatten) und hellen (Licht) Seiten
        shadowStrength: 1.0,
        lightStrength: 0.45
    },

    createTile(coords, done) {

        const tile = document.createElement("canvas");

        tile.width = 256;
        tile.height = 256;

        const count = Math.pow(2, coords.z);

        // Ausserhalb der Weltkarte in y-Richtung gibt es keine Kacheln
        if (coords.y < 0 || coords.y >= count) {
            setTimeout(() => done(null, tile), 0);
            return tile;
        }

        // Westen/Osten umbrechen (x kann ausserhalb 0..count-1 liegen)
        const x = ((coords.x % count) + count) % count;

        const url = RELIEF_TILE_URL
            .replace("{z}", coords.z)
            .replace("{x}", x)
            .replace("{y}", coords.y);

        const image = new Image();

        image.crossOrigin = "anonymous";

        image.onload = () => {

            try {

                this._shade(image, tile, coords);

            } catch (error) {

                if (!reliefWarned) {

                    reliefWarned = true;

                    console.warn("Relief nicht berechenbar:", error);

                    if (typeof showToast === "function") {
                        showToast(
                            tf("Relief konnte nicht berechnet werden: {message}", {
                                message: error.message
                            }),
                            true
                        );
                    }

                }

            }

            done(null, tile);

        };

        image.onerror = () => done(null, tile);

        image.src = url;

        return tile;

    },

    _shade(image, tile, coords) {

        const size = 256;

        const source = document.createElement("canvas");

        source.width = size;
        source.height = size;

        const sourceContext = source.getContext("2d", {
            willReadFrequently: true
        });

        sourceContext.drawImage(image, 0, 0);

        const rgba = sourceContext.getImageData(0, 0, size, size).data;

        // Hoehen in Metern
        const elevation = new Float32Array(size * size);

        for (let i = 0; i < size * size; i++) {

            elevation[i] =
                rgba[i * 4] * 256 +
                rgba[i * 4 + 1] +
                rgba[i * 4 + 2] / 256 -
                32768;

        }

        // Zellgroesse in Metern (Web-Mercator, Breite der Kachelmitte)
        const count = Math.pow(2, coords.z);

        const latitude = Math.atan(
            Math.sinh(Math.PI * (1 - 2 * (coords.y + 0.5) / count))
        );

        const cell =
            40075016.686 * Math.cos(latitude) / (size * count);

        // Lichtvektor (x = Osten, y = Norden, z = oben)
        const azimuth = RELIEF_AZIMUTH_DEG * Math.PI / 180;
        const altitude = RELIEF_ALTITUDE_DEG * Math.PI / 180;

        const lightX = Math.sin(azimuth) * Math.cos(altitude);
        const lightY = Math.cos(azimuth) * Math.cos(altitude);
        const lightZ = Math.sin(altitude);

        const context = tile.getContext("2d");

        const output = context.createImageData(size, size);

        const shadow = this.options.shadowStrength;
        const light = this.options.lightStrength;

        const at = (row, col) => {

            const r = Math.min(size - 1, Math.max(0, row));
            const c = Math.min(size - 1, Math.max(0, col));

            return elevation[r * size + c];

        };

        for (let row = 0; row < size; row++) {

            for (let col = 0; col < size; col++) {

                // Steigung nach Osten (Spalten) und nach Sueden (Zeilen)
                const dzdc =
                    (at(row, col + 1) - at(row, col - 1)) / (2 * cell);

                const dzdr =
                    (at(row + 1, col) - at(row - 1, col)) / (2 * cell);

                // Flaechennormale (x = Osten, y = Norden); die Zeilen laufen
                // nach Sueden, deshalb +dz/dr fuer die Nordkomponente.
                const nx = -dzdc * RELIEF_Z_FACTOR;
                const ny = dzdr * RELIEF_Z_FACTOR;

                const shade =
                    (nx * lightX + ny * lightY + lightZ) /
                    Math.sqrt(nx * nx + ny * ny + 1);

                // 1 = ebene Flaeche, < 1 Schattenseite, > 1 Lichtseite
                const k = shade / lightZ;

                const index = (row * size + col) * 4;

                if (k < 1) {

                    output.data[index] = 0;
                    output.data[index + 1] = 0;
                    output.data[index + 2] = 0;
                    output.data[index + 3] =
                        Math.min(255, (1 - k) * shadow * 255);

                } else {

                    output.data[index] = 255;
                    output.data[index + 1] = 255;
                    output.data[index + 2] = 255;
                    output.data[index + 3] =
                        Math.min(255, (k - 1) * light * 255);

                }

            }

        }

        context.putImageData(output, 0, 0);

    }

});
