class InfoPanel {

    constructor() {

        this.object = null;

        this.create();

    }

    create() {

        this.createPanel();

        this.cacheElements();

        this.bindEvents();

    }

    createPanel() {

        const panel =
            document.createElement("div");

        panel.id = "info-panel";

        panel.innerHTML =
            this.getPanelHtml();

        document.body.appendChild(panel);

        this.panel = panel;

    }

    getPanelHtml() {

        return `

            <div class="info-title">

                Objekt Information

            </div>

            <div id="info-content">

                Kein Objekt ausgewählt

            </div>

            <button id="edit-object">

                Bearbeiten

            </button>

            <button id="delete-object">

                Löschen

            </button>

        `;

    }

    cacheElements() {

        this.content =
            this.panel.querySelector(
                "#info-content"
            );

        this.editButton =
            this.panel.querySelector(
                "#edit-object"
            );

        this.deleteButton =
            this.panel.querySelector(
                "#delete-object"
            );

    }

    bindEvents() {

        this.editButton.onclick = () => {

            this.edit();

        };

        this.deleteButton.onclick = () => {

            this.delete();

        };

    }

    // ===== weitere Methoden folgen =====



    //====================================================
    // Objekt anzeigen
    //====================================================

    show(object) {

        this.object = object;

        if (!object) {

            this.content.innerHTML =
                "Kein Objekt ausgewählt";

            return;

        }

        this.ensureProperties();

        const properties =
            this.getPropertiesHtml(
                this.object.properties
            );

        this.content.innerHTML = `

            <b>ID:</b>

            ${this.object.id}

            <br>

            <b>Layer:</b>

            ${this.translateLayer(
                this.object.layer
            )}

            <br>

            <b>Typ:</b>

            ${this.translateValue(
                "type",
                this.object.type
            )}

            <br>

            <b>Punkte:</b>

            ${
                this.object.geometry
                    ? this.object.geometry.length
                    : 0
            }

            <br><br>

            <b>Eigenschaften:</b>

            <br><br>

            ${properties}

        `;

    }

    //====================================================
    // Eigenschaften als HTML erzeugen
    //====================================================

    getPropertiesHtml(properties) {

        if (
            !properties ||
            Object.keys(properties).length === 0
        ) {

            return "Keine Eigenschaften";

        }

        const order =
            this.getPropertyOrder();

        const labels =
            this.getPropertyLabels();

        return Object.entries(properties)

            .sort(([a], [b]) => {

                const ia =
                    order.indexOf(a);

                const ib =
                    order.indexOf(b);

                if (
                    ia === -1 &&
                    ib === -1
                ) {

                    return a.localeCompare(b);

                }

                if (ia === -1) {

                    return 1;

                }

                if (ib === -1) {

                    return -1;

                }

                return ia - ib;

            })

            .map(([key, value]) => {

                return `

                    <div class="property-row">

                        <b>${labels[key] ?? key}:</b>

                        <br>

                        ${this.translateValue(
                            key,
                            value
                        )}

                    </div>

                `;

            })

            .join("");

}
    //====================================================
    // Eigenschaften sicherstellen
    //====================================================

    ensureProperties() {

        if (!this.object.properties) {

            this.object.properties = {};

        }

    }

    //====================================================
    // Eigenschaften bearbeiten
    //====================================================

    edit() {

        if (!this.object) {

            return;

        }

        this.ensureProperties();

        const properties =
            this.object.properties;

        const fields =
            this.getPropertyOrder();

        const labels =
            this.getPropertyLabels();

        let html = `

            <b>Eigenschaften bearbeiten</b>

            <br><br>

        `;

        for (const field of fields) {

            let value =
                properties[field] ?? "";

            if (field === "type") {

                value = this.translateValue(
                    field,
                    value
                );

            }

            html += `

                <label>

                    ${labels[field]}

                    <br>

                    <input
                        id="edit-${field}"
                        value="${value}"
                    >

                </label>

                <br><br>

            `;

        }

        html += `

            <button id="save-properties">

                Speichern

            </button>

        `;

        this.content.innerHTML = html;

        this.bindSaveButton(
            fields,
            properties
        );

    }

    //====================================================
    // Speichern
    //====================================================

    bindSaveButton(fields, properties) {

        const button =
            this.content.querySelector(
                "#save-properties"
            );

        button.onclick = () => {

            for (const field of fields) {

                const input =
                    this.content.querySelector(
                        "#edit-" + field
                    );

                if (!input) {

                    continue;

                }

                properties[field] =
                    this.reverseTranslateValue(
                        field,
                        input.value
                    );

            }

            if (
                window.geometryManager &&
                typeof window.geometryManager.updateProperties === "function"
            ) {

                window.geometryManager.updateProperties(
                    this.object,
                    properties
                );

            }
                
            this.show(
                this.object
            );

        };

    }

    //====================================================
    // Objekt löschen
    //====================================================

        delete() {

        if (!this.object) {

            return;

        }

        if (!confirm("Objekt wirklich löschen?")) {

            return;

        }

        console.log(
            "DELETE:",
            this.object
        );

        window.geometryManager.remove(
            this.object.layer,
            this.object.id
        );

        this.object = null;

        this.content.innerHTML =
            "Kein Objekt ausgewählt";

}

    //====================================================
    // Wert übersetzen
    //====================================================

    translateValue(key, value) {

        if (key !== "type") {

            return value;

        }

        return this.getTypeTranslations()[value] ?? value;

    }

    //====================================================
    // Übersetzung rückgängig machen
    //====================================================

    reverseTranslateValue(key, value) {

        if (key !== "type") {

            return value;

        }

        const translations =
            this.getTypeTranslations();

        for (const [internal, display] of Object.entries(translations)) {

            if (display === value) {

                return internal;

            }

        }

        return value;

    }

    //====================================================
    // Layer übersetzen
    //====================================================

    translateLayer(layer) {

        return this.getLayerTranslations()[layer] ?? layer;

    }

    //====================================================
    // Typübersetzungen
    //====================================================

    getTypeTranslations() {

        return {

            polyline: "Linie",

            polygon: "Polygon",

            multipolygon: "Multipolygon",

            rectangle: "Rechteck",

            circle: "Kreis"

        };
    }


    //====================================================
    // Layerübersetzungen
    //====================================================

    getLayerTranslations() {

        return {

            roads: "Straßen",

            railways: "Bahnstrecken",

            buildings: "Gebäude",

            water: "Gewässer",

            waterways: "Flüsse",

            parks: "Parks",

            landuse: "Landnutzung",

            vegetation: "Vegetation",

            selection: "Auswahl"

        };
    }


    //====================================================
    // Reihenfolge der Eigenschaften
    //====================================================

    getPropertyOrder() {

        return [

            "name",

            "type",

            "ref",

            "maxspeed",

            "oneway",

            "bridge",

            "tunnel",

            "surface",

            "lanes"

        ];

    }

    //====================================================
    // Bezeichnungen der Eigenschaften
    //====================================================

    getPropertyLabels() {

    return {

        name: "Name",

        type: "Typ",

        ref: "Referenz",

        maxspeed: "Höchstgeschwindigkeit",

        oneway: "Einbahnstraße",

        bridge: "Brücke",

        tunnel: "Tunnel",

        surface: "Oberfläche",

        lanes: "Fahrstreifen"

    };

}

}