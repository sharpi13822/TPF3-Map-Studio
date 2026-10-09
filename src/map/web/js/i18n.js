// Uebersetzung der Kartenoberflaeche (Deutsch / English).
//
// Prinzip wie in Python (src/i18n.py): Der deutsche Originaltext ist der
// Schluessel. Das Woerterbuch kommt vom lokalen Server (i18n_data.js, von
// src/core/server.py erzeugt) und ist bei Deutsch leer.
//
//   t("Alle")                                   -> "All"
//   tf("Eckpunkte: {count}", { count: 5 })      -> "Vertices: 5"
//
// Die festen Texte aus index.html werden beim Laden automatisch ersetzt
// (Textknoten sowie title-/alt-Attribute). Fehlt ein Eintrag, bleibt der
// deutsche Text stehen.

(function () {

    const dictionary = window.TPF_I18N || {};

    const has = (key) =>
        Object.prototype.hasOwnProperty.call(dictionary, key);

    function t(text) {

        return has(text) ? dictionary[text] : text;

    }

    function tf(text, values) {

        return t(text).replace(
            /\{(\w+)\}/g,
            (match, name) =>
                values && Object.prototype.hasOwnProperty.call(values, name)
                    ? String(values[name])
                    : match
        );

    }

    // Whitespace so zusammenfassen wie in den Schluesseln (Umbrueche und
    // Einrueckung im HTML spielen keine Rolle).
    const normalize = (text) => text.replace(/\s+/g, " ").trim();

    function translateTextNode(node) {

        const original = node.nodeValue;

        const plain = normalize(original);

        if (!plain) {
            return;
        }

        // data-i18n am umgebenden Element legt einen eigenen Schluessel fest,
        // wenn derselbe deutsche Text je nach Stelle verschieden heissen soll.
        const holder = node.parentElement;

        const key =
            (holder && holder.getAttribute("data-i18n")) || plain;

        if (!has(key)) {
            return;
        }

        const start = original.length - original.trimStart().length;

        const end = original.trimEnd().length;

        node.nodeValue =
            original.slice(0, start) +
            dictionary[key] +
            original.slice(end);

    }

    function translateDom(root) {

        if (!root || Object.keys(dictionary).length === 0) {
            return;
        }

        const walker = document.createTreeWalker(
            root,
            NodeFilter.SHOW_TEXT
        );

        const nodes = [];

        while (walker.nextNode()) {
            nodes.push(walker.currentNode);
        }

        nodes.forEach(translateTextNode);

        const elements =
            root.nodeType === 1
                ? [root, ...root.querySelectorAll("[title], [alt]")]
                : [...root.querySelectorAll("[title], [alt]")];

        for (const element of elements) {

            for (const attribute of ["title", "alt"]) {

                const value = element.getAttribute(attribute);

                if (value && has(normalize(value))) {

                    element.setAttribute(
                        attribute,
                        dictionary[normalize(value)]
                    );

                }

            }

        }

    }

    window.t = t;

    window.tf = tf;

    window.translateDom = translateDom;

    document.documentElement.lang = window.TPF_LANG || "de";

    translateDom(document.body);

})();
