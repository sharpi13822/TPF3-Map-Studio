"""Automatisch erzeugt von tools/embed_mod_script.py. Nicht von Hand aendern."""

IMPORT_SCRIPT_TEMPLATE = r"""-- Map Studio: Import von Strassen und Gleisen (erzeugt vom TPF3 Map Studio)
-- Ausloeser per Konsole: makeScriptingSendEventCmd("", "mapstudio", <name>, true)
-- Namen: import_info, import, import_cleanup, import_gitter, import_gitter_flach, import_stop, import_weiter (intern), kreuzung_bauen, pruefen, bauen, kette_pruefen, kette_bauen, gleis_pruefen, gleis_bauen,
--        bruecke_pruefen, bruecke_bauen, tunnel_pruefen, tunnel_bauen,
--        info_res, info_bruecke, info_enum, info_tunnel, info_werte, zaehlen

local TAG = "OSMBAU "
local VERSION = "mapstudio v21 (Gleisbett abgesenkt, kurze Strassenbruecken heben sich ueber Gleise)"

-- v13 (Experiment): Meldet die Pruefung nur NICHT KRITISCHE Meldungen (critical = false), wird trotzdem
-- gebaut (ignoreErrors = true). Bisher galt jede Meldung als Fehler. false = Verhalten wie v10.
local TROTZ_MELDUNGEN = true

-- v16: Gleise, die 1 bis 8 m neben einem parallelen Gleis liegen, holen ihre Hoehe aus dem Gelaende
-- in der MITTE zwischen beiden Gleisen (statt am eigenen Knoten). Am Steilhang lag das Gelaende
-- daneben oft Meter tiefer oder hoeher, und jedes Gleis bekam eine eigene Hoehe (Stufen).
-- false = Verhalten wie v15.
local PARALLELGLEISE = true

-- v17: Das Nachbargleis eines Parallelgleises (der spaetere Weg) uebernimmt waehrend der Glaettung in
-- jedem Durchgang die Hoehe des Hauptgleises (des frueheren Weges) an der gegenueberliegenden Stelle.
-- Die Steigungsgrenze wird nur am Hauptgleis angewendet. v16 setzte nur die Anfangshoehe gleich und
-- die Glaettung trennte beide Gleise wieder (im Test im Mittel 0,6 bis 1,0 m). false = Verhalten wie v16.
-- Wirkt nur, wenn PARALLELGLEISE true ist.
local KOPPLUNG = true

-- v18: Drei Aenderungen an der Paarsuche der Parallelgleise (im Rechner an deinen Netzdaten und dem Gelaende
-- des Spiels geprueft; die Rechnung traf das v17-Log auf Hundertstel genau):
--  PAAR_KLEMMEN: liegt der Fusspunkt knapp ausserhalb eines Streckenstuecks (an einem Knick des
--                Nachbargleises), wird er auf das Streckenende geklemmt statt verworfen.
--  PAAR_WEICHEN: auch Knoten, die in mehreren Gleiswegen vorkommen (Weichen, Wegenden), koppeln
--                an das Nachbargleis. Je Knoten gilt der Partner auf dem fruehesten Weg.
--  PAAR_RADIUS:  Suchradius fuer das Nachbargleis in m (v17: 8).
-- Alle drei auf false bzw. 8 = Verhalten wie v17.
local PAAR_KLEMMEN = true
local PAAR_WEICHEN = true
local PAAR_RADIUS = 6

-- v21: Gleise werden um diesen Betrag UNTER dem Gelaende geplant (in m). Bisher genau auf Gelaendehoehe:
-- Dann steht das Schotterbett als Kante ueber dem Gras. Etwas darunter schneidet das Spiel das Bett ein.
-- Alle Gleisknoten gleich viel (Parallelgleise bleiben gleich hoch, die Steigung aendert sich nicht).
-- Bruecken, die angehoben wurden, bleiben unveraendert. 0 = aus (wie v20).
local GLEIS_ABSENKUNG = 0.4

-- v17d: schreibt zusaetzliche Diagnosezeilen (DIAGGELAENDE, DIAGPAAR) ins Log, aendert nichts am Bau.
local DIAGNOSE_PAARE = true

local STUMM = false
local letzte = {}
local IMPORT = nil -- v11: vorab angelegt, damit auch die Diagnose weiter oben darauf zugreift

local function text(...)
	local t = {}
	for i = 1, select("#", ...) do
		t[#t + 1] = tostring((select(i, ...)))
	end
	return table.concat(t, " ")
end

local function log(...)
	local x = text(...)
	letzte[#letzte + 1] = x
	if #letzte > 6 then table.remove(letzte, 1) end
	if not STUMM then debugPrint(TAG .. x) end
end

-- immer ausgeben (auch waehrend des Imports)
local function logw(...)
	debugPrint(TAG .. text(...))
end

-- Objekt erzeugen (probiert mehrere Pfade)
local function neu(name, versuche)
	for i, f in ipairs(versuche) do
		local ok, obj = pcall(f)
		if ok and obj ~= nil then return obj end
	end
	log("FEHLER: kann nicht erzeugen:", name)
	return nil
end

local function neuKnoten()
	return neu("NodeAndEntity", {
		function() return api.type.NodeAndEntity.new() end,
		function() return api.type.Proposal.NodeAndEntity.new() end,
	})
end

local function neuKante()
	return neu("SegmentAndEntity", {
		function() return api.type.SegmentAndEntity.new() end,
		function() return api.type.Proposal.SegmentAndEntity.new() end,
	})
end

local function zaehle(t)
	local n = 0
	local ok = pcall(function() for _ in ipairs(t) do n = n + 1 end end)
	if not ok then return -1 end
	return n
end

local function findeVorlage(endung)
	local ok, alle = pcall(api.res.streetTemplateRep.getAll, false)
	if not ok then
		log("FEHLER streetTemplateRep.getAll:", alle)
		return nil
	end
	for _, name in pairs(alle) do
		if type(name) == "string" and name:sub(-#endung) == endung then
			return name
		end
	end
	log("FEHLER: keine Vorlage mit Endung", endung)
	return nil
end

local function stand(prop)
	local ok, a, b = pcall(function()
		local sp = prop.streetProposal
		return zaehle(sp.nodesToAdd), zaehle(sp.edgesToAdd)
	end)
	if not ok then return -1, -1 end
	return a, b
end

-- Knoten und Kanten als GANZE Tabellen zuweisen (Einzelzuweisung [i]= landet in einer Kopie)
local function fuelle(prop, nodes, edges)
	local strategien = {
		{ "A", function()
			prop.streetProposal.nodesToAdd = nodes
			prop.streetProposal.edgesToAdd = edges
		end },
		{ "B", function()
			local sp = prop.streetProposal
			sp.nodesToAdd = nodes
			sp.edgesToAdd = edges
			prop.streetProposal = sp
		end },
	}
	for _, st in ipairs(strategien) do
		local ok, err = pcall(st[2])
		local k, e = stand(prop)
		if k == #nodes and e == #edges then
			log("Befuellen", st[1], "ok: Knoten", k, "Kanten", e)
			return true
		end
		log("Befuellen", st[1], "reicht nicht: ok =", ok, "Knoten", k, "Kanten", e, ok and "" or err)
	end
	return false
end

-- Typ in einem Repo finden (Brueckentyp, Tunneltyp); ohne Endung: Eintrag mit kleinster id
local function findeInRep(repName, endung)
	local rep = api.res[repName]
	if not rep then log("FEHLER: api.res." .. repName .. " fehlt") return nil end
	local ok, alle = pcall(rep.getAll)
	if not ok or not alle then log("FEHLER getAll", repName, alle) return nil end
	local erster
	for id, name in pairs(alle) do
		if type(name) == "string" then
			if endung == nil then
				if erster == nil or id < erster[1] then erster = { id, name } end
			elseif name:sub(-#endung) == endung then
				return id, name
			end
		end
	end
	if erster then return erster[1], erster[2] end
	log("FEHLER: kein Typ gefunden in", repName, endung)
	return nil
end

local function enumWert(gruppe, name, ersatz)
	local ok, w = pcall(function() return api.type.enum[gruppe][name] end)
	if ok and w ~= nil then return w, true end
	return ersatz, false
end

-- punkte: Liste von {x, y}, mindestens 2; art: 0 = Strasse, 1 = Gleis
local function baueKette(punkte, art, endung, opts)
	local n = #punkte
	if n < 2 then log("FEHLER: weniger als 2 Punkte") return nil end

	local vorlage = findeVorlage(endung)
	if not vorlage then return nil end

	local okv, tmpl = pcall(function()
		return api.res.streetTemplateRep.get(api.res.streetTemplateRep.find(vorlage))
	end)
	if not okv or tmpl == nil then log("FEHLER: Vorlage nicht lesbar:", tmpl) return nil end
	local nSpuren = zaehle(tmpl.laneConfigs)
	log("Vorlage", vorlage, "Spuren", nSpuren, "roadType", tmpl.roadType)
	if nSpuren <= 0 then log("FEHLER: Vorlage ohne Spuren") return nil end

	local T = api.engine.terrain
	local z = {}
	for i = 1, n do
		z[i] = T.getHeightAt(api.type.Vec2f.new(punkte[i][1], punkte[i][2]))
		if opts and opts.dz then z[i] = z[i] + opts.dz end
	end

	-- Vorhandene Knoten (opts.vorhanden[i] = {entity, z}) behalten ihre Hoehe
	local function fixiere()
		if opts and opts.festZ then
			for i, hz in pairs(opts.festZ) do z[i] = hz end
		end
		if opts and opts.vorhanden then
			for i, v in pairs(opts.vorhanden) do z[i] = v.z end
		end
	end
	fixiere()

	-- Steigung begrenzen (nur wenn opts.maxG gesetzt); Abstand = waagerechte Laenge
	local function abstand(i)
		local dx = punkte[i][1] - punkte[i - 1][1]
		local dy = punkte[i][2] - punkte[i - 1][2]
		return math.sqrt(dx * dx + dy * dy)
	end
	if opts and opts.linear and n >= 3 then
		local summe = { 0 }
		for i = 2, n do summe[i] = summe[i - 1] + abstand(i) end
		if summe[n] > 0 then
			for i = 2, n - 1 do
				z[i] = z[1] + (z[n] - z[1]) * summe[i] / summe[n]
			end
		end
	end
	if opts and opts.maxG then
		for durchgang = 1, 4 do
			for i = 2, n do
				local d = abstand(i) * opts.maxG
				if z[i] > z[i - 1] + d then z[i] = z[i - 1] + d
				elseif z[i] < z[i - 1] - d then z[i] = z[i - 1] - d end
			end
			for i = n - 1, 1, -1 do
				local d = abstand(i + 1) * opts.maxG
				if z[i] > z[i + 1] + d then z[i] = z[i + 1] + d
				elseif z[i] < z[i + 1] - d then z[i] = z[i + 1] - d end
			end
		end
	end
	fixiere()
	do
		local groesste, bei = 0, 0
		for i = 2, n do
			local g = math.abs(z[i] - z[i - 1]) / math.max(abstand(i), 0.001)
			if g > groesste then groesste, bei = g, i - 1 end
		end
		log(string.format("groesste Steigung: %.1f%% (Kante %d), Hoehe Anfang %.1f Ende %.1f", groesste * 100, bei, z[1], z[n]))
	end

	-- Brueckentyp / Tunneltyp bestimmen
	local typWert, typIndex
	if opts and opts.rep then
		local gruppeName = (opts.rep == "bridgeTypeRep") and "BRIDGE" or "TUNNEL"
		local fallback = (opts.rep == "bridgeTypeRep") and 1 or 2
		local w, gef = enumWert("BaseEdgeType", gruppeName, fallback)
		typWert = w
		local id, name = findeInRep(opts.rep, opts.endungTyp)
		if id == nil then return nil end
		typIndex = id
		log("Typ", gruppeName, "Wert", w, gef and "(aus Enum)" or "(Ersatzwert)", "typeIndex", id, name)
	end

	-- Richtung am Knoten i (normiert, aus den Nachbarn): glatte Uebergaenge
	local function richtung(i)
		-- Endknoten, der an GENAU EINE vorhandene Kante anschliesst: glatte Fortsetzung
		local vv = opts and opts.vorhanden and opts.vorhanden[i]
		if vv and vv.tang then
			if i == 1 then return -vv.tang[1], -vv.tang[2], -vv.tang[3] end
			if i == n then return vv.tang[1], vv.tang[2], vv.tang[3] end
		end
		local a, b = math.max(i - 1, 1), math.min(i + 1, n)
		local dx = punkte[b][1] - punkte[a][1]
		local dy = punkte[b][2] - punkte[a][2]
		local dz = z[b] - z[a]
		local l = math.sqrt(dx * dx + dy * dy + dz * dz)
		if l == 0 then return 0, 0, 0 end
		return dx / l, dy / l, dz / l
	end

	local prop = neu("SimpleProposal", { function() return api.type.SimpleProposal.new() end })
	local ctx = neu("Context", { function() return api.type.Context.new() end })
	if not (prop and ctx) then return nil end
	ctx.player = api.engine.util.getPlayer()
	ctx.checkTerrainAlignment = true
	ctx.cleanupStreetGraph = (opts and opts.cleanup) or false
	ctx.gatherBuildings = true
	ctx.gatherFields = true

	local nodes, ids = {}, {}
	for i = 1, n do
		local v = opts and opts.vorhanden and opts.vorhanden[i]
		if v then
			ids[i] = v.entity
		else
			local nd = neuKnoten()
			if not nd then return nil end
			local k = #nodes + 1
			nd.entity = -k
			nd.comp.position = api.type.Vec3f.new(punkte[i][1], punkte[i][2], z[i])
			nodes[k] = nd
			ids[i] = -k
		end
	end
	local nNeu = #nodes

	local edges = {}
	for i = 1, n - 1 do
		local e = neuKante()
		if not e then return nil end
		local sx = punkte[i + 1][1] - punkte[i][1]
		local sy = punkte[i + 1][2] - punkte[i][2]
		local sz = z[i + 1] - z[i]
		local L = math.sqrt(sx * sx + sy * sy + sz * sz)
		local ax, ay, az = richtung(i)
		local bx, by, bz = richtung(i + 1)

		e.entity = -(nNeu + i)
		e.type = art
		e.comp.node0 = ids[i]
		e.comp.node1 = ids[i + 1]
		e.comp.position0 = api.type.Vec3f.new(punkte[i][1], punkte[i][2], z[i])
		e.comp.position1 = api.type.Vec3f.new(punkte[i + 1][1], punkte[i + 1][2], z[i + 1])
		e.comp.tangent0 = api.type.Vec3f.new(ax * L, ay * L, az * L)
		e.comp.tangent1 = api.type.Vec3f.new(bx * L, by * L, bz * L)
		e.comp.roadTemplate = vorlage
		e.comp.laneConfigs = tmpl.laneConfigs
		if tmpl.streetStyle ~= nil then e.comp.roadStyle = tmpl.streetStyle end
		if tmpl.roadType ~= nil then e.comp.roadType = tmpl.roadType end
		if typWert ~= nil then
			e.comp.type = typWert
			e.comp.typeIndex = typIndex
		end
		edges[i] = e
	end

	if not fuelle(prop, nodes, edges) then
		log("FEHLER: Vorschlag bleibt leer, nichts wird gebaut")
		return nil
	end

	-- Schutz: jede Kante muss Spuren haben, sonst bricht das Spiel hart ab
	local okr, spuren = pcall(function()
		local min = 1000000
		for i = 1, #edges do
			local k = prop.streetProposal.edgesToAdd[i]
			min = math.min(min, zaehle(k.comp.laneConfigs))
		end
		return min
	end)
	log("Kontrolle: kleinste Spurenzahl aller Kanten =", okr and spuren or ("nicht lesbar: " .. tostring(spuren)))
	if not okr or spuren <= 0 then
		log("FEHLER: Kanten ohne Spuren, es wird nicht geprueft und nicht gebaut")
		return nil
	end
	return prop, ctx
end

-- Detailtext zum letzten Fehler (Kollisionspartner), wird an die Fehlerliste gehaengt
local detailLetzte = nil

local function entityAus(e)
	if type(e) == "number" then return e end
	for _, f in ipairs({ "entity", "id", "ent", "entityId" }) do
		local ok, v = pcall(function() return e[f] end)
		if ok and type(v) == "number" then return v end
	end
	return nil
end

-- welche Felder hat so ein EntityData-Objekt? (nur zur Diagnose)
local function feldProbe(e)
	local gefunden = {}
	for _, f in ipairs({ "entity", "id", "type", "name", "position", "pos", "kind", "category", "revision", "tag" }) do
		local ok, v = pcall(function() return e[f] end)
		if ok and v ~= nil then gefunden[#gefunden + 1] = f .. "=" .. tostring(v):sub(1, 30) end
	end
	if #gefunden == 0 then return "keine bekannten Felder" end
	return table.concat(gefunden, ",")
end

local function beschreibeEntity(e)
	local ent = entityAus(e)
	if ent then
		local okc, c = pcall(api.engine.getComponent, ent, api.type.ComponentType.BASE_EDGE)
		if okc and c ~= nil then
			local okp, px, py = pcall(function() return c.position0.x, c.position0.y end)
			local tpl = tostring(c.roadTemplate):match("([^/]+)%.street_template$") or tostring(c.roadTemplate)
			return okp and string.format("Kante %s bei %.0f/%.0f", tpl, px, py) or ("Kante " .. tpl)
		end
		local okn, cn = pcall(api.engine.getComponent, ent, api.type.ComponentType.BASE_NODE)
		if okn and cn ~= nil then
			return string.format("Knoten bei %.0f/%.0f", cn.position.x, cn.position.y)
		end
		return "Entity " .. tostring(ent) .. " (weder Kante noch Knoten)"
	end
	return "EntityData " .. feldProbe(e)
end

local function kollisionsInfo(d)
	local ok, res = pcall(function()
		local ci = d.collisionInfo
		if ci == nil then return "keine collisionInfo" end
		local ents = ci.collisionEntities
		if ents == nil then return "collisionInfo ohne collisionEntities" end
		local teile, n = {}, 0
		for _, e in ipairs(ents) do
			n = n + 1
			if n <= 3 then teile[#teile + 1] = beschreibeEntity(e) end
		end
		return n .. " Kollisionen: " .. table.concat(teile, "; ")
	end)
	if ok then return res end
	return "collisionInfo nicht lesbar"
end

local function pruefe(prop, ctx)
	local ok, d = pcall(function() return api.engine.util.proposal.makeProposalData(prop, ctx) end)
	if not ok or d == nil then
		log("Pruefung gescheitert:", d)
		return nil, true
	end
	local es = d.errorState
	local nMsg = es and zaehle(es.messages) or 0
	log("Pruefung: critical =", es and es.critical, "Meldungen:", nMsg)
	if es then
		-- alle Meldungen in EINER Zeile, damit der Grund vollstaendig ist
		local msgs = {}
		pcall(function() for _, m in ipairs(es.messages) do msgs[#msgs + 1] = tostring(m) end end)
		if #msgs > 0 then
			log("messages", 1, table.concat(msgs, " + "))
			for _, m in ipairs(msgs) do
				if m:find("Kollision", 1, true) then
					detailLetzte = kollisionsInfo(d)
					break
				end
			end
		end
		pcall(function()
			for i, m in ipairs(es.warnings) do log("warnings", i, m) end
		end)
		-- v13: Statistik "critical: erste Meldung"
		if #msgs > 0 and IMPORT then
			IMPORT.meldStat = IMPORT.meldStat or {}
			local key = tostring(es.critical) .. ": " .. msgs[1]
			IMPORT.meldStat[key] = (IMPORT.meldStat[key] or 0) + 1
		end
		-- v11: auch bei anderen Meldungen (z.B. "Bau nicht moeglich") Kollisionsdetail, Warnungen und Infos mitschreiben
		if #msgs > 0 then
			if detailLetzte == nil then
				local ki = kollisionsInfo(d)
				if type(ki) == "string" and not ki:find("^0 Kollisionen") then detailLetzte = ki end
			end
			local extra = {}
			pcall(function() for _, m in ipairs(es.warnings) do extra[#extra + 1] = "W:" .. tostring(m) end end)
			pcall(function() for _, m in ipairs(es.infos) do extra[#extra + 1] = "I:" .. tostring(m) end end)
			if #extra > 0 then
				detailLetzte = (detailLetzte and (detailLetzte .. " ") or "") .. "[" .. table.concat(extra, " + ") .. "]"
			end
		end
	end
	return d, ((es and es.critical) or nMsg > 0), (es and es.critical), nMsg
end

-- Knoten (BaseNode) unter den Ergebnis-Entities einer Bauaktion nach Position suchen
local function sucheKnoten(entities, x, y)
	if not entities then return nil end
	for _, eintrag in ipairs(entities) do
		local ent = (type(eintrag) == "table") and eintrag[1] or eintrag
		local ok, c = pcall(api.engine.getComponent, ent, api.type.ComponentType.BASE_NODE)
		if ok and c ~= nil then
			local ok2, px, py, pz = pcall(function() return c.position.x, c.position.y, c.position.z end)
			if ok2 and px and math.abs(px - x) < 1 and math.abs(py - y) < 1 then
				return ent, pz
			end
		end
	end
	return nil
end

-- v11: Diagnose der schon vorhandenen Knoten, an die der Weg anschliesst (Ausnahme beim Bauen, Pruefung gescheitert)
local diagZaehler = 0
local diagPruef = 0
local function diagnoseAnschluss(opts, punkte, endung, anlass)
	if diagZaehler >= 120 then return end
	diagZaehler = diagZaehler + 1
	local nr = (IMPORT and IMPORT.i) or "?"
	local vorlage = tostring(endung):match("([^/]+)%.street_template$") or tostring(endung)
	local n = #punkte
	local karte
	pcall(function() karte = api.engine.system.streetSystem.getNode2SegmentMap() end)
	local gefunden = false
	for k = 1, n do
		local v = opts and opts.vorhanden and opts.vorhanden[k]
		if v then
			gefunden = true
			local ent = v.entity
			local teile = {}
			local pos = (k == 1) and "Anfang" or ((k == n) and "Ende" or ("Mitte " .. k))
			pcall(function()
				local c = api.engine.getComponent(ent, api.type.ComponentType.BASE_NODE)
				local dx, dy = c.position.x - punkte[k][1], c.position.y - punkte[k][2]
				teile[#teile + 1] = string.format("Abstand %.1f m, z Knoten %.1f, z geplant %s", math.sqrt(dx * dx + dy * dy), c.position.z, tostring(v.z))
			end)
			local kanten, anzahl = {}, 0
			local segs = karte and karte[ent]
			if segs then
				for _, seg in pairs(segs) do
					anzahl = anzahl + 1
					pcall(function()
						local c = api.engine.getComponent(seg, api.type.ComponentType.BASE_EDGE)
						local tpl = tostring(c.roadTemplate):match("([^/]+)%.street_template$") or tostring(c.roadTemplate)
						kanten[#kanten + 1] = tpl .. "/Typ" .. tostring(c.type) .. "/" .. tostring(c.roadType)
					end)
				end
			end
			teile[#teile + 1] = "Kanten " .. anzahl .. " [" .. table.concat(kanten, ", ") .. "]"
			pcall(function() teile[#teile + 1] = "Konstruktion " .. tostring(api.engine.system.streetConnectorSystem.getConstructionEntityForNode(ent)) end)
			pcall(function() teile[#teile + 1] = "Bahnuebergang " .. tostring(api.engine.system.railRoadCrossingSystem.getRailroadCrossingForNode(ent)) end)
			pcall(function() teile[#teile + 1] = "Stadtkreuzung " .. tostring(api.engine.system.streetSystem.isTownCrossingNode(ent)) end)
			pcall(function() teile[#teile + 1] = "Knotenkonfig " .. tostring(api.engine.getComponent(ent, api.type.ComponentType.BASE_NODE_CONFIG) ~= nil) end)
			logw("DIAG Weg", nr, anlass, "|", vorlage, "Knoten", k, "von", n, "(" .. pos .. ") entity", ent, "|", table.concat(teile, " | "))
		end
	end
	if not gefunden then logw("DIAG Weg", nr, anlass, "|", vorlage, "kein vorhandener Anschlussknoten") end
end

-- v12: Nach einer Ausnahme beim Bauen pruefen, ob die Kanten des Wegs trotzdem im Spiel stehen.
-- (Im v11-Lauf hatten die Anschlussknoten der 58 "Unknown exception"-Wege schon die neue Kante: der Bau war
-- erfolgt, die Ausnahme kam erst danach, noch vor dem Rueckruf.) Gibt (gefundene Kanten, Soll) zurueck.
local function kantenImSpiel(punkte)
	local n = #punkte
	local karte
	local ok = pcall(function() karte = api.engine.system.streetSystem.getNode2SegmentMap() end)
	if not ok or not karte then return 0, n - 1 end
	local am = {}
	for node, _ in pairs(karte) do
		local okc, c = pcall(api.engine.getComponent, node, api.type.ComponentType.BASE_NODE)
		if okc and c ~= nil then
			local x, y = c.position.x, c.position.y
			for k = 1, n do
				if math.abs(x - punkte[k][1]) < 1.5 and math.abs(y - punkte[k][2]) < 1.5 then
					am[k] = am[k] or {}
					am[k][node] = true
				end
			end
		end
	end
	local gefunden = 0
	for k = 1, n - 1 do
		local gut = false
		if am[k] and am[k + 1] then
			for a in pairs(am[k]) do
				local segs = karte[a]
				if segs then
					for _, seg in pairs(segs) do
						local oks, c = pcall(api.engine.getComponent, seg, api.type.ComponentType.BASE_EDGE)
						if oks and c ~= nil and ((c.node0 == a and am[k + 1][c.node1]) or (c.node1 == a and am[k + 1][c.node0])) then
							gut = true
							break
						end
					end
				end
				if gut then break end
			end
		end
		if gut then gefunden = gefunden + 1 end
	end
	return gefunden, n - 1
end

local STRASSE = "/town/town_new_small.street_template"
local GLEIS = "/track/standard/standard.street_template"

local function baueDann(punkte, art, endung, opts, danach)
	local prop, ctx = baueKette(punkte, art, endung, opts)
	if not prop then return false end
	local pd, kritisch, krit, nMeld = pruefe(prop, ctx)
	local ignorieren = false
	if kritisch and TROTZ_MELDUNGEN and IMPORT and krit == false and (nMeld or 0) > 0 then
		-- v13: nur nicht kritische Meldungen -> trotzdem bauen
		kritisch = false
		ignorieren = true
		IMPORT.trotzMeldung = (IMPORT.trotzMeldung or 0) + 1
	end
	if kritisch then
		log("nicht gebaut: die Pruefung meldet Fehler")
		if IMPORT and opts and opts.vorhanden and next(opts.vorhanden) and diagPruef < 25 then
			diagPruef = diagPruef + 1
			-- v19: auch die Zeilen DAVOR mitschreiben (Pruefung: critical, messages = der Text des Spiels, warnings)
			local zl = {}
			for zi = math.max(1, #letzte - 4), #letzte do zl[#zl + 1] = tostring(letzte[zi]) end
			diagnoseAnschluss(opts, punkte, endung, "Pruefung: " .. table.concat(zl, " // "))
		end
		return false
	end
	local imCallback = false
	local okS, errS = pcall(function()
	api.cmd.sendCommand(
		api.cmd.makeWorldBuildProposalCmd(prop, ctx, ignorieren, true),
		function(d, success, entities)
			imCallback = true
			if ignorieren and success and IMPORT then IMPORT.trotzOk = (IMPORT.trotzOk or 0) + 1 end
			log("Bauen fertig, success =", success, "Entities:", entities and #entities)
			if not success then
				pcall(function()
					local msgs = {}
					for _, m in ipairs(d.resultProposalData.errorState.messages) do msgs[#msgs + 1] = tostring(m) end
					if #msgs > 0 then log("messages", 1, table.concat(msgs, " + ")) end
					for _, m in ipairs(msgs) do
						if m:find("Kollision", 1, true) then
							detailLetzte = kollisionsInfo(d.resultProposalData)
							break
						end
					end
				end)
			end
			if danach then danach(success, entities) end
		end
	)
	end)
	if not okS then
		if not imCallback then
			logw("DIAG sendCommand wirft:", tostring(errS))
			diagnoseAnschluss(opts, punkte, endung, "sendCommand-Ausnahme")
			local gef, ges = kantenImSpiel(punkte)
			local nr = (IMPORT and IMPORT.i) or "?"
			logw("DIAG Weg", nr, "Kanten im Spiel nach der Ausnahme:", gef, "von", ges)
			if ges > 0 and gef == ges and danach then
				logw("DIAG Weg", nr, "Ausnahme trotz fertigem Bau: als gebaut gezaehlt")
				if IMPORT then IMPORT.ausnahmeGebaut = (IMPORT.ausnahmeGebaut or 0) + 1 end
				danach(true, nil)
				return true
			end
		end
		error(errS, 0)
	end
	log("Baubefehl gesendet")
	return true
end

-- Kreuzung: Strasse A (3 Punkte) bauen, dann Strasse B von A's Mittelknoten aus
local function kreuzung()
	local A = { { 0, 400 }, { 80, 400 }, { 160, 400 } }
	baueDann(A, 0, STRASSE, nil, function(ok, entities)
		if not ok then log("Kreuzung: Teil A nicht gebaut") return end
		local ent, pz = sucheKnoten(entities, 80, 400)
		if not ent then log("Kreuzung: Mittelknoten nicht gefunden") return end
		log("Kreuzung: Mittelknoten gefunden, entity", ent, "z", pz)
		local B = { { 80, 400 }, { 80, 470 } }
		baueDann(B, 0, STRASSE, { vorhanden = { [1] = { entity = ent, z = pz } }, maxG = 0.12 }, function(ok2)
			log("Kreuzung: Teil B", ok2 and "gebaut" or "NICHT gebaut")
		end)
	end)
end

-- ===== Import aus der Datendatei =====
local STANDARD_MAXG = { [0] = 0.12, [1] = 0.03 }
local function maxGefaelle(w)
	if w.maxG then return w.maxG end
	if (w.art or 0) == 0 and w.v and w.v:find("highway", 1, true) then return 0.06 end
	return STANDARD_MAXG[w.art or 0]
end

-- Format 2: Knoten und Wege als Text (vermeidet die Konstantengrenze bei grossen Netzen)
--   nodes: eine Zeile je Knoten "x y" (Knoten-id = Zeilennummer)
--   ways:  eine Zeile je Weg "art vorlageIdx t typIdx maxG n1 n2 ..." (maxG "-" = Standard)
local function parseFormat2(d)
	local knoten = {}
	for zeile in string.gmatch(d.nodes, "[^\n]+") do
		local x, y = string.match(zeile, "^%s*(%S+)%s+(%S+)")
		knoten[#knoten + 1] = { tonumber(x), tonumber(y) }
	end
	local wege = {}
	for zeile in string.gmatch(d.ways, "[^\n]+") do
		local tok = {}
		for w in string.gmatch(zeile, "%S+") do tok[#tok + 1] = w end
		-- Format 2: art vorlage t typ maxG n1 n2 ...   Format 3: art vorlage t typ maxG osmId n1 n2 ...
		local ab = (d.format == 3) and 7 or 6
		if #tok >= ab + 1 then
			local weg = { art = tonumber(tok[1]), v = d.templates[tonumber(tok[2])], t = tonumber(tok[3]), n = {} }
			local tpi = tonumber(tok[4])
			if tpi and tpi > 0 then weg.tp = d.types[tpi] end
			if tok[5] ~= "-" then weg.maxG = tonumber(tok[5]) end
			if d.format == 3 then weg.osm = tonumber(tok[6]) end
			for i = ab, #tok do weg.n[#weg.n + 1] = tonumber(tok[i]) end
			wege[#wege + 1] = weg
		end
	end
	return { format = 1, name = d.name, nodes = knoten, ways = wege }
end

local function ladeDaten(datei)
	local ok, res = pcall(function() return ug_require("__MOD_ID__::/" .. datei) end)
	if ok and type(res) == "table" then
		if res.format == 2 or res.format == 3 then
			local ok2, r2 = pcall(parseFormat2, res)
			if ok2 then return r2 end
			logw("Format 2 nicht lesbar:", r2)
			return nil
		end
		return res
	end
	logw("Laden gescheitert:", datei, ok and "(keine Tabelle)" or res)
	return nil
end

IMPORT = nil

local function jetzt()
	local ok, t = pcall(os.clock)
	if ok and type(t) == "number" then return t end
	return 0
end

local function grundAus(zeilen)
	for k = #zeilen, 1, -1 do
		local m = zeilen[k]:match("^messages %d+ (.+)$")
		if m then return m end
	end
	for k = #zeilen, 1, -1 do
		local z = zeilen[k]
		if z:find("^FEHLER") then return z end
		if z:find("success = false", 1, true) then return "Bauen fehlgeschlagen (success = false)" end
	end
	return zeilen[#zeilen] or "unbekannt"
end

local function kurzName(w)
	local n = tostring(w.v or "?"):match("([^/]+)%.street_template$") or tostring(w.v)
	if (w.t or 0) == 1 then n = n .. "+Bruecke" elseif (w.t or 0) == 2 then n = n .. "+Tunnel" end
	return n
end

local function statistik(Z, w, index)
	local kn = kurzName(w)
	local st = Z.statistik[kn]
	if not st then st = { 0, 0 } Z.statistik[kn] = st end
	st[index] = st[index] + 1
	return kn
end

local function merkeFehler(Z, nr, grund, w)
	grund = grund or grundAus(letzte)
	grund = tostring(grund):match("^[^\n]*") or "?"
	if #grund > 140 then grund = grund:sub(1, 140) end
	Z.gruende[grund] = (Z.gruende[grund] or 0) + 1
	local kn = w and statistik(Z, w, 2) or "?"
	Z.ergebnis[nr] = "fehler: " .. grund
	if Z.kk and w then
		local g = (Z.kreuzW[nr] or Z.nahW[nr]) and Z.kk.mit or Z.kk.ohne
		g[2] = g[2] + 1
	end
	if w and w._abw then Z.abwFehler[#Z.abwFehler + 1] = w._abw end
	Z.proGrund = Z.proGrund or {}
	local gz = Z.proGrund[grund] or 0
	if w and #Z.fehlerListe < 600 and gz < 60 then
		Z.proGrund[grund] = gz + 1
		Z.fehlerListe[#Z.fehlerListe + 1] = {
			nr = nr, osm = w.osm, kn = kn, knoten = #w.n, grund = grund,
			info = w._info, detail = detailLetzte,
		}
	end
	detailLetzte = nil
	if Z.gezeigt < 5 then
		Z.gezeigt = Z.gezeigt + 1
		logw("Weg", nr, "nicht gebaut:", grund)
	end
end

local function importEnde(abgebrochen)
	local Z = IMPORT
	STUMM = false
	IMPORT = nil
	if not Z then return end
	logw(abgebrochen and "Import ABGEBROCHEN:" or "Import fertig:", "gebaut", Z.gebaut,
		"Fehler/uebersprungen", Z.fehler, "von", #Z.wege, "Wegen", string.format("(%.1f s)", jetzt() - (Z.start or jetzt())))
	local liste = {}
	for g, n in pairs(Z.gruende) do liste[#liste + 1] = { g, n } end
	table.sort(liste, function(a, b) return a[2] > b[2] end)
	for k = 1, math.min(#liste, 14) do logw("  Grund:", liste[k][1], "x", liste[k][2]) end
	logw("  Knoten wiedergefunden:", Z.wiedergefunden or 0, "verloren:", Z.verloren or 0,
		"veraltete Entities:", Z.veraltet or 0, "| Knotenindex", Z.indexBauten or 0, "x in",
		string.format("%.2f", Z.indexZeit or 0), "s")
	local namen = {}
	for n in pairs(Z.statistik) do namen[#namen + 1] = n end
	table.sort(namen)
	for _, n in ipairs(namen) do
		local st = Z.statistik[n]
		logw("  Art", n, ": gebaut", st[1], "Fehler", st[2])
	end
	local function abwText(liste)
		local n = #liste
		if n == 0 then return "n=0" end
		local summe, max = 0, 0
		for _, v in ipairs(liste) do
			summe = summe + v
			if v > max then max = v end
		end
		return string.format("n=%d Mittel %.1f Grad Max %.1f Grad", n, summe / n, max)
	end
	logw("  Anschluss-Abweichung am Endknoten: gebaut", abwText(Z.abwOk), "| Fehler", abwText(Z.abwFehler))
	logw("  Cleanup im Spiel:", Z.cleanup and "an" or "aus")
	logw("  Ausnahmen mit fertigem Bau (als gebaut gezaehlt):", Z.ausnahmeGebaut or 0)
	logw("  Trotz nicht kritischer Meldung gebaut (Versuche):", Z.trotzMeldung or 0, "| davon success:", Z.trotzOk or 0, "| Schalter TROTZ_MELDUNGEN:", tostring(TROTZ_MELDUNGEN))
	if Z.meldStat then
		local ml = {}
		for k, n in pairs(Z.meldStat) do ml[#ml + 1] = { k, n } end
		table.sort(ml, function(a, b) return a[2] > b[2] end)
		for k = 1, math.min(#ml, 12) do logw("  Meldung", ml[k][1], "x", ml[k][2]) end
	end
	-- eine Zeile je Weg (fuer die Auswertung ausserhalb des Spiels)
	for i = 1, #Z.wege do
		local w = Z.wege[i]
		local e = Z.ergebnis[i]
		if e then
			local nm = Z.nahMin and Z.nahMin[i]
			logw(string.format("WEG %d osm=%s %s W=%.0f ok=%s nv=%s/%s len=%.0f kx=%d nah=%d minV=%s %s",
				i, tostring(w.osm), (tostring(w.v):match("([^/]+)%.street_template$") or "?") .. ((w.t or 0) == 1 and "+B" or (w.t or 0) == 2 and "+T" or ""),
				(Z.breiteW and Z.breiteW[i]) or 0, e == "ok" and "1" or "0", tostring(w._nv), tostring(w._nt), w._len or 0,
				(Z.kreuzW and Z.kreuzW[i]) or 0, (Z.nahW and Z.nahW[i]) or 0, nm and string.format("%.2f", nm) or "-",
				e == "ok" and "" or e))
		end
	end
	if Z.kk then
		logw("  Wege MIT Kreuzung/Naehe ohne Knoten: gebaut", Z.kk.mit[1], "Fehler", Z.kk.mit[2],
			"| OHNE: gebaut", Z.kk.ohne[1], "Fehler", Z.kk.ohne[2])
	end
	for k = 1, math.min(#Z.fehlerListe, 600) do
		local f = Z.fehlerListe[k]
		logw("  Weg", f.nr, "[osm", tostring(f.osm), f.kn .. "]", f.grund,
			f.info and ("(" .. f.info .. ")") or "", f.detail and ("-> " .. f.detail) or "")
	end
	if #Z.fehlerListe >= 600 then logw("  ... (Liste bei 600 Eintraegen abgeschnitten)") end
end

-- Knotenindex: alle Knoten des Strassennetzes im Spiel, in einem Raster von 25 m
local function baueIndex(Z)
	local t0 = jetzt()
	local idx = {}
	local ok, err = pcall(function()
		for node, _ in pairs(api.engine.system.streetSystem.getNode2SegmentMap()) do
			local okc, c = pcall(api.engine.getComponent, node, api.type.ComponentType.BASE_NODE)
			if okc and c ~= nil then
				local x, y, z = c.position.x, c.position.y, c.position.z
				local key = math.floor(x / 25) .. ":" .. math.floor(y / 25)
				local zelle = idx[key]
				if not zelle then zelle = {} idx[key] = zelle end
				zelle[#zelle + 1] = { node, x, y, z }
			end
		end
	end)
	Z.indexBauten = (Z.indexBauten or 0) + 1
	Z.indexZeit = (Z.indexZeit or 0) + (jetzt() - t0)
	if not ok then
		logw("Knotenindex gescheitert:", err)
		return nil
	end
	return idx
end

local function sucheImIndex(idx, x, y)
	local cx, cy = math.floor(x / 25), math.floor(y / 25)
	local best, bd = nil, 5.0
	for gx = cx - 1, cx + 1 do
		for gy = cy - 1, cy + 1 do
			local zelle = idx[gx .. ":" .. gy]
			if zelle then
				for _, e in ipairs(zelle) do
					local dx, dy = e[2] - x, e[3] - y
					local d = math.sqrt(dx * dx + dy * dy)
					if d <= bd then best, bd = e, d end
				end
			end
		end
	end
	return best
end

-- Entity des Knotens id im Spiel: gemerkte Entity pruefen, sonst ueber die Position suchen.
-- Nur Knoten, die schon gebaut wurden, werden gesucht.
local function loeseKnoten(Z, id, x, y)
	local b = Z.bekannt[id]
	if b then
		local okE, ex = pcall(api.engine.entityExists, b.entity)
		if not (okE and ex == false) then
			local ok, c = pcall(api.engine.getComponent, b.entity, api.type.ComponentType.BASE_NODE)
			if ok and c ~= nil then
				local ok2, px, py, pz = pcall(function() return c.position.x, c.position.y, c.position.z end)
				if ok2 and px and math.abs(px - x) < 5 and math.abs(py - y) < 5 then
					b.z = pz
					return b
				end
			end
		end
		Z.bekannt[id] = nil
		Z.veraltet = (Z.veraltet or 0) + 1
	end
	if not Z.gebautId[id] then return nil end
	if Z.indexAlt or not Z.index then
		Z.index = baueIndex(Z)
		Z.indexAlt = false
	end
	if Z.index then
		local e = sucheImIndex(Z.index, x, y)
		if e then
			Z.bekannt[id] = { entity = e[1], z = e[4] }
			Z.wiedergefunden = (Z.wiedergefunden or 0) + 1
			return Z.bekannt[id]
		end
	end
	Z.verloren = (Z.verloren or 0) + 1
	return nil
end

-- Wie weit weicht unsere Richtung am Endknoten von der Fortsetzung der vorhandenen Kante ab?
-- (nur Endknoten, die schon existieren; 0 Grad = glatte Fortsetzung, nur Werte unter 60 Grad zaehlen)
local function anschlussAbweichung(vorhanden, punkte)
	local n = #punkte
	local karte
	pcall(function() karte = api.engine.system.streetSystem.getNode2SegmentMap() end)
	if not karte then return nil end
	local beste = nil
	for _, k in ipairs({ 1, n }) do
		local b = vorhanden[k]
		if b then
			local nachbar = (k == 1) and punkte[2] or punkte[n - 1]
			local ox, oy = nachbar[1] - punkte[k][1], nachbar[2] - punkte[k][2]
			local ol = math.sqrt(ox * ox + oy * oy)
			local segs = karte[b.entity]
			if ol > 0 and segs then
				local minAbw = nil
				for _, seg in pairs(segs) do
					local ok, c = pcall(api.engine.getComponent, seg, api.type.ComponentType.BASE_EDGE)
					if ok and c ~= nil then
						local ok2, ex, ey = pcall(function()
							if c.node0 == b.entity then return c.tangent0.x, c.tangent0.y end
							return -c.tangent1.x, -c.tangent1.y
						end)
						if ok2 and ex then
							local el = math.sqrt(ex * ex + ey * ey)
							if el > 0 then
								local cosw = (ox * -ex + oy * -ey) / (ol * el)
								cosw = math.max(-1, math.min(1, cosw))
								local w = math.deg(math.acos(cosw))
								if minAbw == nil or w < minAbw then minAbw = w end
							end
						end
					end
				end
				if minAbw and minAbw < 60 and (beste == nil or minAbw > beste) then beste = minAbw end
			end
		end
	end
	return beste
end

-- Endknoten, die schon genau eine Kante haben: deren Richtung merken, damit unser Weg glatt
-- anschliesst (Gleise vertragen keinen Knick am Knoten). tang = Richtung vom Knoten in die
-- vorhandene Kante hinein (Einheitsvektor).
local function anschlussTangenten(vorhanden, punkte, art)
	if art ~= 1 then return 0 end -- nur Gleise: bei Strassen erzeugte es zu enge Kurven (Kruemmung zu gross)
	local n = #punkte
	local karte
	pcall(function() karte = api.engine.system.streetSystem.getNode2SegmentMap() end)
	if not karte then return 0 end
	local gesetzt = 0
	for _, k in ipairs({ 1, n }) do
		local b = vorhanden[k]
		if b then
			local liste = {}
			local segs = karte[b.entity]
			if segs then for _, seg in pairs(segs) do liste[#liste + 1] = seg end end
			if #liste == 1 then
				local ok, c = pcall(api.engine.getComponent, liste[1], api.type.ComponentType.BASE_EDGE)
				if ok and c ~= nil then
					local ok2, ox, oy, oz = pcall(function()
						if c.node0 == b.entity then return c.tangent0.x, c.tangent0.y, c.tangent0.z end
						return -c.tangent1.x, -c.tangent1.y, -c.tangent1.z
					end)
					if ok2 and ox then
						local l = math.sqrt(ox * ox + oy * oy + oz * oz)
						if l > 0 then
							vorhanden[k] = { entity = b.entity, z = b.z, tang = { ox / l, oy / l, oz / l } }
							gesetzt = gesetzt + 1
						end
					end
				end
			end
		end
	end
	return gesetzt
end

-- Vorab-Pruefung: Weg im Wasser? (das Spiel meldet "An Land platzieren" erst beim Bauen)
local function wasserPruefung(w, punkte)
	local t = w.t or 0
	if t == 2 then return nil end -- Tunnel liegen unter dem Wasser, nicht pruefen
	local T = api.engine.terrain
	local n = #punkte
	local function nass(x, y)
		local ok, r = pcall(T.isOnWater, api.type.Vec2f.new(x, y))
		return ok and r == true
	end
	for k = 1, n do
		if (t == 0 or k == 1 or k == n) and nass(punkte[k][1], punkte[k][2]) then
			return "Wasser: Knoten im Wasser"
		end
	end
	if t == 0 then
		local nasse, gesamt = 0, 0
		for k = 1, n - 1 do
			local ax, ay, bx, by = punkte[k][1], punkte[k][2], punkte[k + 1][1], punkte[k + 1][2]
			local laenge = math.sqrt((bx - ax) ^ 2 + (by - ay) ^ 2)
			local schritte = math.floor(laenge / 10)
			for s = 1, schritte - 1 do
				gesamt = gesamt + 1
				if nass(ax + (bx - ax) * s / schritte, ay + (by - ay) * s / schritte) then nasse = nasse + 1 end
			end
		end
		if nasse >= 2 then
			w._info = (w._info or "") .. string.format(", %d von %d Stellen im Wasser", nasse, gesamt)
			return "Wasser: Weg quert Wasser"
		end
	end
	return nil
end

-- true: Baubefehl gesendet
local function wegStarten(Z, w, nr)
	local punkte, vorhanden = {}, {}
	for k, id in ipairs(w.n) do
		local p = Z.knoten[id]
		if not p then
			return false, "FEHLER: unbekannter Knoten " .. tostring(id)
		end
		punkte[k] = { p[1], p[2] }
		local b = loeseKnoten(Z, id, p[1], p[2])
		if b then vorhanden[k] = b end
	end
	local nTang = anschlussTangenten(vorhanden, punkte, w.art or 0)
	-- Weginfo fuer die Fehlerliste: Laenge und wie viele Knoten schon existierten
	do
		local laenge, vorh = 0, 0
		for k = 1, #punkte do
			if vorhanden[k] then vorh = vorh + 1 end
			if k > 1 then
				laenge = laenge + math.sqrt((punkte[k][1] - punkte[k - 1][1]) ^ 2 + (punkte[k][2] - punkte[k - 1][2]) ^ 2)
			end
		end
		w._nv, w._nt, w._len = vorh, #punkte, laenge
		w._info = string.format("%d von %d Knoten schon da, %.0f m, von %.0f/%.0f bis %.0f/%.0f%s", vorh, #punkte, laenge,
			punkte[1][1], punkte[1][2], punkte[#punkte][1], punkte[#punkte][2],
			nTang > 0 and (", Tangente angepasst: " .. nTang) or "")
		local kx, nx = Z.kreuzW and Z.kreuzW[nr], Z.nahW and Z.nahW[nr]
		if kx or nx then
			w._info = w._info .. string.format(", Kreuzungen ohne Knoten: %d, zu nah: %d", kx or 0, nx or 0)
		end
	end
	w._abw = nil
	local wasser = wasserPruefung(w, punkte)
	if wasser then
		Z.wasser = (Z.wasser or 0) + 1
		return false, wasser
	end
	w._abw = anschlussAbweichung(vorhanden, punkte)
	if w._abw then w._info = w._info .. string.format(", Anschluss %.0f Grad", w._abw) end
	local t = w.t or 0
	local festZ = {}
	for k, id in ipairs(w.n) do
		if Z.hoehe[id] ~= nil then festZ[k] = Z.hoehe[id] end
	end
	local opts = { vorhanden = vorhanden, festZ = festZ, maxG = maxGefaelle(w), cleanup = Z.cleanup }
	if t == 1 then
		opts.rep = "bridgeTypeRep"
		opts.endungTyp = w.tp or "/trestle.bridge"
		opts.linear = true
	elseif t == 2 then
		opts.rep = "tunnelTypeRep"
		opts.endungTyp = w.tp or (((w.art or 0) == 1) and "/tunnel_a.tunnel" or "/tunnel_a_car.tunnel")
		opts.linear = true
	end
	return baueDann(punkte, w.art or 0, w.v, opts, function(success, ents)
		if success then
			Z.gebaut = Z.gebaut + 1
			statistik(Z, w, 1)
			Z.ergebnis[nr] = "ok"
			if w._abw then Z.abwOk[#Z.abwOk + 1] = w._abw end
			if Z.kk then
				local g = (Z.kreuzW[nr] or Z.nahW[nr]) and Z.kk.mit or Z.kk.ohne
				g[1] = g[1] + 1
			end
			Z.indexAlt = true
			for _, id in ipairs(w.n) do Z.gebautId[id] = true end
		else
			Z.fehler = Z.fehler + 1
			merkeFehler(Z, nr, nil, w)
		end
		Z.wartet = false
	end)
end

-- wird aus update() aufgerufen: einige Wege pro Aufruf (Zeitbudget), keine Verschachtelung
local function importSchritt()
	local Z = IMPORT
	if not Z or Z.wartet then return end
	local start, anzahl = jetzt(), 0
	while true do
		Z.i = Z.i + 1
		local w = Z.wege[Z.i]
		if not w then importEnde(false) return end
		if Z.i % 100 == 0 then
			logw("Fortschritt:", Z.i, "/", #Z.wege, "gebaut", Z.gebaut, "Fehler", Z.fehler)
		end
		Z.wartet = true
		local ok, gestartet, grund = pcall(wegStarten, Z, w, Z.i)
		if not ok or not gestartet then
			Z.wartet = false
			Z.fehler = Z.fehler + 1
			if not ok then
				merkeFehler(Z, Z.i, tostring(gestartet), w)
			else
				merkeFehler(Z, Z.i, grund, w)
			end
		end
		anzahl = anzahl + 1
		if Z.wartet then return end -- asynchron: im naechsten update weiter
		if jetzt() - start > 0.02 or anzahl >= 25 then return end
	end
end

-- Ein Schritt im Ereignis-Handler; danach stoesst sich der Import ueber ein neues Ereignis selbst an
local function importVoran()
	local Z = IMPORT
	if not Z then return end
	if Z.laeuft then return end -- kein Wiedereintritt (Ereignisse werden verschachtelt zugestellt)
	Z.laeuft = true
	Z.start = jetzt()
	-- Eine flache Schleife in EINEM Aufruf: Die Rueckmeldungen des Spiels kommen synchron.
	-- (Ein Selbst-Ereignis wuerde verschachtelt zugestellt und den Lua-Stapel sprengen.)
	local leer = 0
	while IMPORT do
		local ok, err = pcall(importSchritt)
		if not ok then
			logw("FEHLER im Import:", err)
			importEnde(true)
			return
		end
		if IMPORT then
			if Z.wartet then
				leer = leer + 1
				if leer > 1000 then
					logw("Import abgebrochen: die Rueckmeldung des Spiels kommt nicht synchron")
					importEnde(true)
					return
				end
			else
				leer = 0
			end
		end
	end
end

-- Gemeinsame Hoehenplanung: jeder Knoten bekommt EINMAL seine Hoehe (aus dem Gelaende),
-- danach werden alle Kanten so geglaettet, dass die Steigungsgrenze eingehalten wird.
local function planeHoehen(Z)
	local T = api.engine.terrain
	local hoehe = {}
	local nKnoten = 0
	for _, w in ipairs(Z.wege) do
		for _, id in ipairs(w.n) do
			if hoehe[id] == nil then
				local p = Z.knoten[id]
				if p then
					hoehe[id] = T.getHeightAt(api.type.Vec2f.new(p[1], p[2]))
					nKnoten = nKnoten + 1
				end
			end
		end
	end

	-- v16: Parallelgleise (siehe PARALLELGLEISE oben). Fehler hier duerfen den Import nie stoppen.
	local parPaare = {}
	if PARALLELGLEISE then
		local okPar, errPar = pcall(function()
			local RADIUS, ZELLE = PAAR_RADIUS, 16
			local gitter, nutzung = {}, {}
			for wi, w in ipairs(Z.wege) do
				if (w.art or 0) == 1 then
					local ids = w.n
					for k = 1, #ids do nutzung[ids[k]] = (nutzung[ids[k]] or 0) + 1 end
					for k = 1, #ids - 1 do
						local pa, pb = Z.knoten[ids[k]], Z.knoten[ids[k + 1]]
						if pa and pb then
							local dx, dy = pb[1] - pa[1], pb[2] - pa[2]
							local l = math.sqrt(dx * dx + dy * dy)
							if l > 0 then
								local sg = { pa[1], pa[2], dx, dy, l, wi, ids[k], ids[k + 1] }
								local x0, x1 = math.min(pa[1], pb[1]) - RADIUS, math.max(pa[1], pb[1]) + RADIUS
								local y0, y1 = math.min(pa[2], pb[2]) - RADIUS, math.max(pa[2], pb[2]) + RADIUS
								for cx = math.floor(x0 / ZELLE), math.floor(x1 / ZELLE) do
									for cy = math.floor(y0 / ZELLE), math.floor(y1 / ZELLE) do
										local key = cx .. ":" .. cy
										local c = gitter[key]
										if not c then c = {} gitter[key] = c end
										c[#c + 1] = sg
									end
								end
							end
						end
					end
				end
			end
			local nPar, summe, maxD = 0, 0, 0
			local gesetzt = {}
			for wi, w in ipairs(Z.wege) do
				if (w.art or 0) == 1 then
					local ids = w.n
					for k = 1, #ids do
						local id = ids[k]
						local p = Z.knoten[id]
						if p and (nutzung[id] == 1 or PAAR_WEICHEN) and hoehe[id] ~= nil then
							local na = Z.knoten[ids[k > 1 and k - 1 or k]]
							local nb = Z.knoten[ids[k < #ids and k + 1 or k]]
							local tx, ty = nb[1] - na[1], nb[2] - na[2]
							local tl = math.sqrt(tx * tx + ty * ty)
							if tl > 0 then
								tx, ty = tx / tl, ty / tl
								local bestD, bestSg, bestT = nil, nil, nil
								local key = math.floor(p[1] / ZELLE) .. ":" .. math.floor(p[2] / ZELLE)
								for _, sg in ipairs(gitter[key] or {}) do
									if sg[6] ~= wi then
										local t = ((p[1] - sg[1]) * sg[3] + (p[2] - sg[2]) * sg[4]) / (sg[5] * sg[5])
										if PAAR_KLEMMEN then t = math.max(0, math.min(1, t)) end
										if t >= 0 and t <= 1 then
											local fx, fy = sg[1] + t * sg[3], sg[2] + t * sg[4]
											local d = math.sqrt((p[1] - fx) * (p[1] - fx) + (p[2] - fy) * (p[2] - fy))
											local par = math.abs(tx * sg[3] / sg[5] + ty * sg[4] / sg[5])
											if d >= 1 and d <= RADIUS and par >= 0.94 and (bestD == nil or d < bestD) then
												bestD, bestSg, bestT = d, sg, t
											end
										end
									end
								end
								if bestSg then
									local mx = (p[1] + bestSg[1] + bestT * bestSg[3]) / 2
									local my = (p[2] + bestSg[2] + bestT * bestSg[4]) / 2
									local h = T.getHeightAt(api.type.Vec2f.new(mx, my))
									local diff = math.abs(h - hoehe[id])
									nPar = nPar + 1
									summe = summe + diff
									if diff > maxD then maxD = diff end
									if not gesetzt[id] then
										hoehe[id] = h
										gesetzt[id] = true
									end
									parPaare[#parPaare + 1] = { id, bestSg[7], bestSg[8], bestT, wi, bestSg[6] }
								end
							end
						end
					end
				end
			end
			logw(string.format("Parallelgleise: %d Gleisknoten auf Mittelhoehe gesetzt (Aenderung mittel %.2f m, max %.2f m)", nPar, nPar > 0 and summe / nPar or 0, maxD))
		end)
		if not okPar then logw("FEHLER bei Parallelgleise (ignoriert):", errPar) end
	end

	local function dist(a, b)
		local pa, pb = Z.knoten[a], Z.knoten[b]
		local dx, dy = pa[1] - pb[1], pa[2] - pb[2]
		return math.sqrt(dx * dx + dy * dy)
	end

	-- Segmente: gewoehnliche Wege Kante fuer Kante, Bruecke/Tunnel nur Ende zu Ende
	local segs = {}
	for _, w in ipairs(Z.wege) do
		local ids, g = w.n, maxGefaelle(w)
		if (w.t or 0) == 0 then
			for k = 1, #ids - 1 do
				if hoehe[ids[k]] and hoehe[ids[k + 1]] then
					segs[#segs + 1] = { ids[k], ids[k + 1], dist(ids[k], ids[k + 1]), g }
				end
			end
		elseif #ids >= 2 and hoehe[ids[1]] and hoehe[ids[#ids]] then
			local l = 0
			for k = 1, #ids - 1 do l = l + dist(ids[k], ids[k + 1]) end
			segs[#segs + 1] = { ids[1], ids[#ids], l, g }
		end
	end

	-- Bruecken: Fahrbahn muss ueber Gelaendebuckeln und ueber kreuzenden Wegen liegen.
	-- Beide Brueckenenden werden um "lift" angehoben (die Fahrbahn dazwischen ist linear).
	-- Nur ECHTE Kreuzungen zaehlen: Wege, die die Brueckenlinie schneiden, nicht den
	-- Brueckenknoten teilen und mehr als 12 m vom Brueckenende entfernt kreuzen.
	local fest = {}
	do
		local ZELLE = 20
		local gitter = {}
		for _, w in ipairs(Z.wege) do
			if (w.t or 0) == 0 then
				local ids = w.n
				for k = 1, #ids - 1 do
					local pa, pb = Z.knoten[ids[k]], Z.knoten[ids[k + 1]]
					if pa and pb then
						local sg = { pa[1], pa[2], pb[1], pb[2], (w.art or 0) == 1 and 8.5 or 7, ids[k], ids[k + 1] }
						for cx = math.floor((math.min(pa[1], pb[1]) - 2) / ZELLE), math.floor((math.max(pa[1], pb[1]) + 2) / ZELLE) do
							for cy = math.floor((math.min(pa[2], pb[2]) - 2) / ZELLE), math.floor((math.max(pa[2], pb[2]) + 2) / ZELLE) do
								local key = cx .. ":" .. cy
								local c = gitter[key]
								if not c then c = {} gitter[key] = c end
								c[#c + 1] = sg
							end
						end
					end
				end
			end
		end
		-- Schnittpunkt zweier Strecken: liefert t (0..1 auf P-Q) und den Winkel, sonst nil
		local function schnitt(px, py, qx, qy, sg)
			local rx, ry = qx - px, qy - py
			local sx, sy = sg[3] - sg[1], sg[4] - sg[2]
			local nenner = rx * sy - ry * sx
			if math.abs(nenner) < 1e-9 then return nil end
			local t = ((sg[1] - px) * sy - (sg[2] - py) * sx) / nenner
			local u = ((sg[1] - px) * ry - (sg[2] - py) * rx) / nenner
			if t < 0 or t > 1 or u < 0 or u > 1 then return nil end
			local lr, ls = math.sqrt(rx * rx + ry * ry), math.sqrt(sx * sx + sy * sy)
			if lr == 0 or ls == 0 then return nil end
			local sinus = math.abs(nenner) / (lr * ls)
			if sinus < 0.35 then return nil end -- fast parallel: keine Kreuzung
			return t
		end
		local nBr, nHeb, summeLift, maxLift = 0, 0, 0, 0
		for _, w in ipairs(Z.wege) do
			local ids = w.n
			if (w.t or 0) == 1 and #ids >= 2 and hoehe[ids[1]] and hoehe[ids[#ids]] then
				nBr = nBr + 1
				local eigene = {}
				for _, id in ipairs(ids) do eigene[id] = true end
				local pts, cum, l = {}, { 0 }, 0
				for k, id in ipairs(ids) do
					pts[k] = Z.knoten[id]
					if k > 1 then l = l + dist(ids[k - 1], id) cum[k] = l end
				end
				local za, zb = hoehe[ids[1]], hoehe[ids[#ids]]
				local lift = 0
				-- v20: Abstand vom Brueckenende, ab dem eine Kreuzung zaehlt. Bisher fest 12 m: Eine Strassenbruecke
				-- unter 24 m Laenge (die ueber den Gleisen am Rhein: 21 m) hatte nie eine zaehlende Kreuzung und
				-- wurde nicht angehoben (Log: "angehoben 0"), die Strasse lag dann auf Hoehe der Gleise. Fuer
				-- Strassenbruecken gilt jetzt hoechstens ein Viertel der Laenge. Gleisbruecken bleiben bei 12 m:
				-- Sie wuerden sonst die Hauptstrecke (max. 3 %) um bis zu 7 m anheben.
				local rand = ((w.art or 0) == 0) and math.min(12, l * 0.25) or 12
				if l > 0 then
					-- 1. Gelaendebuckel: Fahrbahn darf nicht unter dem Boden liegen
					local schritt = math.max(4, l / 40)
					local d, k = 0, 1
					while d <= l do
						while k < #ids - 1 and cum[k + 1] < d do k = k + 1 end
						local seg = cum[k + 1] - cum[k]
						local f = seg > 0 and (d - cum[k]) / seg or 0
						local px = pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f
						local py = pts[k][2] + (pts[k + 1][2] - pts[k][2]) * f
						local gel = T.getHeightAt(api.type.Vec2f.new(px, py))
						local lin = za + (zb - za) * d / l
						if gel - lin > lift then lift = gel - lin end
						d = d + schritt
					end
					-- 2. echte Kreuzungen mit anderen Wegen
					for k = 1, #ids - 1 do
						local px, py, qx, qy = pts[k][1], pts[k][2], pts[k + 1][1], pts[k + 1][2]
						local seen = {}
						for cx = math.floor((math.min(px, qx) - 2) / ZELLE), math.floor((math.max(px, qx) + 2) / ZELLE) do
							for cy = math.floor((math.min(py, qy) - 2) / ZELLE), math.floor((math.max(py, qy) + 2) / ZELLE) do
								for _, sg in ipairs(gitter[cx .. ":" .. cy] or {}) do
									if not seen[sg] then
										seen[sg] = true
										if not eigene[sg[6]] and not eigene[sg[7]] then
											local t = schnitt(px, py, qx, qy, sg)
											if t then
												local dc = cum[k] + t * (cum[k + 1] - cum[k])
												if dc > rand and dc < l - rand then
													local cxp, cyp = px + (qx - px) * t, py + (qy - py) * t
													local gel = T.getHeightAt(api.type.Vec2f.new(cxp, cyp))
													local lin = za + (zb - za) * dc / l
													local noetig = gel + sg[5]
													if noetig - lin > lift then lift = noetig - lin end
												end
											end
										end
									end
								end
							end
						end
					end
				end
				if lift > 15 then lift = 15 end
				if lift > 0.3 then
					nHeb = nHeb + 1
					summeLift = summeLift + lift
					if lift > maxLift then maxLift = lift end
					for _, id in ipairs({ ids[1], ids[#ids] }) do
						hoehe[id] = hoehe[id] + lift
						fest[id] = true
					end
				end
			end
		end
		logw(string.format("Bruecken: %d, davon angehoben %d (mittel %.1f m, max %.1f m)", nBr, nHeb, nHeb > 0 and summeLift / nHeb or 0, maxLift))
	end

	-- v17: Folgeknoten der Parallelgleise (siehe KOPPLUNG oben). Fehler hier duerfen nie stoppen:
	-- ohne gueltige Liste bleibt es beim Verhalten von v16.
	local folgerListe, folg = {}, {}
	if KOPPLUNG and PARALLELGLEISE then
		local okF, errF = pcall(function()
			local beste = {}
			for _, e in ipairs(parPaare) do
				if e[5] and e[6] and e[5] > e[6] and not fest[e[1]] then
					local b = beste[e[1]]
					if b == nil or e[6] < b[6] then beste[e[1]] = e end
				end
			end
			for id, e in pairs(beste) do
				folgerListe[#folgerListe + 1] = { id = id, a = e[2], b = e[3], t = e[4], wi = e[5] }
				folg[id] = true
			end
			table.sort(folgerListe, function(x, y)
				if x.wi ~= y.wi then return x.wi < y.wi end
				return x.id < y.id
			end)
		end)
		if not okF then
			logw("FEHLER bei Parallelgleis-Kopplung (ignoriert):", errF)
			folgerListe, folg = {}, {}
		end
		logw("Parallelgleise gekoppelt:", #folgerListe, "Folgeknoten")
	end
	local function folgerAnpassen()
		for _, f in ipairs(folgerListe) do
			local ha, hb = hoehe[f.a], hoehe[f.b]
			if ha and hb then hoehe[f.id] = ha + (hb - ha) * f.t end
		end
	end

	local verletzt, durchgaenge = 0, 0
	for durchgang = 1, 1000 do
		durchgaenge = durchgang
		verletzt = 0
		folgerAnpassen()
		for _, sg in ipairs(segs) do
			local a, b, d, g = sg[1], sg[2], sg[3], sg[4]
			-- Segmente zwischen zwei Folgeknoten erben die Steigung vom Hauptgleis
			if not (folg[a] and folg[b]) then
				local erlaubt = d * g
				local diff = hoehe[b] - hoehe[a]
				local ueber = math.abs(diff) - erlaubt
				if ueber > 0.02 then
					local r = (diff > 0) and 1 or -1
					local fa, fb = fest[a] or folg[a], fest[b] or folg[b]
					if fa and not fb then
						hoehe[b] = hoehe[b] - r * ueber
					elseif fb and not fa then
						hoehe[a] = hoehe[a] + r * ueber
					elseif folg[a] or folg[b] then
						-- beide fest, einer davon Folgeknoten: nichts verschieben
					else
						hoehe[a] = hoehe[a] + r * ueber / 2
						hoehe[b] = hoehe[b] - r * ueber / 2
					end
					verletzt = verletzt + 1
				end
			end
		end
		if verletzt == 0 then break end
	end
	folgerAnpassen()

	-- innere Knoten von Bruecken/Tunneln: linear zwischen den geplanten Enden
	for _, w in ipairs(Z.wege) do
		local ids = w.n
		if (w.t or 0) ~= 0 and #ids >= 3 and hoehe[ids[1]] and hoehe[ids[#ids]] then
			local summe, l = { 0 }, 0
			for k = 2, #ids do
				l = l + dist(ids[k - 1], ids[k])
				summe[k] = l
			end
			if l > 0 then
				for k = 2, #ids - 1 do
					hoehe[ids[k]] = hoehe[ids[1]] + (hoehe[ids[#ids]] - hoehe[ids[1]]) * summe[k] / l
				end
			end
		end
	end

	-- v16: Messung nach der Glaettung: Hoehenunterschied der Parallelgleis-Knoten zum Nachbargleis
	if #parPaare > 0 then
		local okM, errM = pcall(function()
			local n, summe, maxD, ueber = 0, 0, 0, 0
			for _, e in ipairs(parPaare) do
				local h, ha, hb = hoehe[e[1]], hoehe[e[2]], hoehe[e[3]]
				if h and ha and hb then
					local diff = math.abs(h - (ha + (hb - ha) * e[4]))
					n = n + 1
					summe = summe + diff
					if diff > maxD then maxD = diff end
					if diff > 0.5 then ueber = ueber + 1 end
				end
			end
			logw(string.format("Parallelgleise nach Glaettung: %d Knoten, Hoehenunterschied zum Nachbargleis mittel %.2f m, max %.2f m, ueber 0.5 m: %d", n, n > 0 and summe / n or 0, maxD, ueber))
		end)
		if not okM then logw("FEHLER bei Parallelgleis-Messung (ignoriert):", errM) end
	end

	-- v17d: Diagnose (nur Log). Fehler hier duerfen nie stoppen.
	if DIAGNOSE_PAARE then
		local okD, errD = pcall(function()
			-- 1. Kalibrierung: echte Gelaendehoehe des Spiels an jedem 5. Gleisknoten (max. 40 Stueck)
			local gez, zaehler = 0, 0
			for wi, w in ipairs(Z.wege) do
				if (w.art or 0) == 1 then
					for k, id in ipairs(w.n) do
						zaehler = zaehler + 1
						local p = Z.knoten[id]
						if p and gez < 40 and zaehler % 5 == 1 then
							gez = gez + 1
							logw(string.format("DIAGGELAENDE weg %d knoten %d x %.1f y %.1f gelaende %.2f geplant %.2f folger %s",
								wi, id, p[1], p[2], T.getHeightAt(api.type.Vec2f.new(p[1], p[2])), hoehe[id] or -1, tostring(folg[id] == true)))
						end
					end
				end
			end
			-- 2. die zehn groessten Abweichungen zum Nachbargleis
			local liste = {}
			for _, e in ipairs(parPaare) do
				local h, ha, hb = hoehe[e[1]], hoehe[e[2]], hoehe[e[3]]
				if h and ha and hb then
					liste[#liste + 1] = { math.abs(h - (ha + (hb - ha) * e[4])), e, h, ha, hb }
				end
			end
			table.sort(liste, function(x, y) return x[1] > y[1] end)
			for i = 1, math.min(10, #liste) do
				local d, e, h, ha, hb = liste[i][1], liste[i][2], liste[i][3], liste[i][4], liste[i][5]
				local p = Z.knoten[e[1]]
				logw(string.format("DIAGPAAR diff %.2f knoten %d x %.1f y %.1f weg %d partnerweg %d folger %s h %.2f partner %.2f..%.2f t %.2f gelaende %.2f",
					d, e[1], p[1], p[2], e[5], e[6], tostring(folg[e[1]] == true), h, ha, hb, e[4],
					T.getHeightAt(api.type.Vec2f.new(p[1], p[2]))))
			end
		end)
		if not okD then logw("FEHLER bei Diagnose (ignoriert):", errD) end
	end

	-- v21: Gleisbett tiefer. Nach allem anderen, damit Steigungen, Kopplung und Diagnose unberuehrt bleiben.
	if GLEIS_ABSENKUNG and GLEIS_ABSENKUNG > 0 then
		local okA, errA = pcall(function()
			local gesenkt, nAbs = {}, 0
			for _, w in ipairs(Z.wege) do
				if (w.art or 0) == 1 and (w.t or 0) == 0 then
					for _, id in ipairs(w.n) do
						if hoehe[id] and not gesenkt[id] and not fest[id] then
							hoehe[id] = hoehe[id] - GLEIS_ABSENKUNG
							gesenkt[id] = true
							nAbs = nAbs + 1
						end
					end
				end
			end
			logw("Gleisbett abgesenkt:", nAbs, "Knoten um", GLEIS_ABSENKUNG, "m unter das Gelaende")
		end)
		if not okA then logw("FEHLER bei Gleisabsenkung (ignoriert):", errA) end
	end

	logw("Hoehenplanung:", nKnoten, "Knoten,", #segs, "Segmente,", durchgaenge, "Durchgaenge, noch zu steil:", verletzt)
	return hoehe
end

-- Kreuzungsanalyse (nur Messung): Wege, die sich schneiden oder sehr nah liegen, OHNE einen
-- gemeinsamen Knoten. Das sind Stellen, an denen im Spiel Bruecken/Unterfuehrungen noetig waeren.
local function vorlagenBreite(endung)
	local name = findeVorlage(endung)
	if not name then return nil end
	local ok, tmpl = pcall(function()
		return api.res.streetTemplateRep.get(api.res.streetTemplateRep.find(name))
	end)
	if not ok or not tmpl then return nil end
	local summe, n = 0, 0
	local teile = {}
	local ok2 = pcall(function()
		for _, lc in ipairs(tmpl.laneConfigs) do
			summe = summe + lc.width
			n = n + 1
			local modes = {}
			pcall(function()
				for m, v in pairs(lc.transportModes) do
					if v then modes[#modes + 1] = tostring(m) end
				end
			end)
			table.sort(modes)
			teile[#teile + 1] = string.format("%.1f[%s]", lc.width, table.concat(modes, ","))
		end
	end)
	if not ok2 or n == 0 then return nil end
	return summe, n, table.concat(teile, " ")
end

local function kreuzungsAnalyse(Z)
	local ZELLE, RAND = 40, 35
	local breite = {}
	for _, w in ipairs(Z.wege) do
		if w.v and breite[w.v] == nil then
			local b, n, spuren = vorlagenBreite(w.v)
			breite[w.v] = b or false
			if b then
				logw(string.format("  Breite %s: %.1f m (%d Spuren) %s",
					w.v:match("([^/]+)%.street_template$") or w.v, b, n, spuren or ""))
			end
		end
	end
	local segs = {}
	for wi, w in ipairs(Z.wege) do
		local ids = w.n
		for k = 1, #ids - 1 do
			local pa, pb = Z.knoten[ids[k]], Z.knoten[ids[k + 1]]
			if pa and pb then
				segs[#segs + 1] = { wi, ids[k], ids[k + 1], pa[1], pa[2], pb[1], pb[2], w.t or 0, w.art or 0,
					(w.v and breite[w.v]) or 8 }
			end
		end
	end
	local zellen = {}
	for si, sg in ipairs(segs) do
		local x0, x1 = math.min(sg[4], sg[6]) - RAND, math.max(sg[4], sg[6]) + RAND
		local y0, y1 = math.min(sg[5], sg[7]) - RAND, math.max(sg[5], sg[7]) + RAND
		for cx = math.floor(x0 / ZELLE), math.floor(x1 / ZELLE) do
			for cy = math.floor(y0 / ZELLE), math.floor(y1 / ZELLE) do
				local key = cx .. ":" .. cy
				local z = zellen[key]
				if not z then z = {} zellen[key] = z end
				z[#z + 1] = si
			end
		end
	end

	local function ccw(ax, ay, bx, by, cx, cy) return (cy - ay) * (bx - ax) - (by - ay) * (cx - ax) end
	local function schneiden(a, b)
		local d1 = ccw(a[4], a[5], a[6], a[7], b[4], b[5])
		local d2 = ccw(a[4], a[5], a[6], a[7], b[6], b[7])
		local d3 = ccw(b[4], b[5], b[6], b[7], a[4], a[5])
		local d4 = ccw(b[4], b[5], b[6], b[7], a[6], a[7])
		return ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0))
	end
	local function punktSeg(px, py, ax, ay, bx, by)
		local dx, dy = bx - ax, by - ay
		local l2 = dx * dx + dy * dy
		local t = 0
		if l2 > 0 then t = math.max(0, math.min(1, ((px - ax) * dx + (py - ay) * dy) / l2)) end
		local qx, qy = ax + t * dx, ay + t * dy
		return math.sqrt((px - qx) ^ 2 + (py - qy) ^ 2)
	end
	local function abstand(a, b)
		return math.min(
			punktSeg(a[4], a[5], b[4], b[5], b[6], b[7]), punktSeg(a[6], a[7], b[4], b[5], b[6], b[7]),
			punktSeg(b[4], b[5], a[4], a[5], a[6], a[7]), punktSeg(b[6], b[7], a[4], a[5], a[6], a[7]))
	end
	local function ebene(t1, t2)
		if t1 == 0 and t2 == 0 then return "gleiche Ebene" end
		if t1 == t2 then return (t1 == 1) and "Bruecke/Bruecke" or "Tunnel/Tunnel" end
		if t1 == 0 or t2 == 0 then return ((t1 == 1 or t2 == 1) and "Bruecke" or "Tunnel") .. "/normal" end
		return "Bruecke/Tunnel"
	end
	local function artText(a1, a2)
		if a1 == 0 and a2 == 0 then return "Strasse/Strasse" end
		if a1 == 1 and a2 == 1 then return "Gleis/Gleis" end
		return "Strasse/Gleis"
	end

	Z.kreuzW, Z.nahW, Z.nahMin, Z.breiteW = {}, {}, {}, {}
	for wi, w in ipairs(Z.wege) do Z.breiteW[wi] = (w.v and breite[w.v]) or 0 end
	local zaehl, nSchnitt, nNah, gesehen = {}, 0, 0, {}
	for _, liste in pairs(zellen) do
		for i = 1, #liste - 1 do
			for j = i + 1, #liste do
				local si, sj = liste[i], liste[j]
				local a, b = segs[si], segs[sj]
				if a[1] ~= b[1] then
					local key = si * 1000003 + sj
					if not gesehen[key] then
						gesehen[key] = true
						-- gemeinsamer Knoten = verbunden, kein Problem
						if not (a[2] == b[2] or a[2] == b[3] or a[3] == b[2] or a[3] == b[3]) then
							local dd = abstand(a, b)
							local thr = (a[10] + b[10]) / 2
							local ratio = dd / thr
							if ratio < 2 and not schneiden(a, b) then
								if Z.nahMin[a[1]] == nil or ratio < Z.nahMin[a[1]] then Z.nahMin[a[1]] = ratio end
								if Z.nahMin[b[1]] == nil or ratio < Z.nahMin[b[1]] then Z.nahMin[b[1]] = ratio end
							end
							if schneiden(a, b) then
								nSchnitt = nSchnitt + 1
								local k = ebene(a[8], b[8]) .. " " .. artText(a[9], b[9])
								zaehl[k] = (zaehl[k] or 0) + 1
								Z.kreuzW[a[1]] = (Z.kreuzW[a[1]] or 0) + 1
								Z.kreuzW[b[1]] = (Z.kreuzW[b[1]] or 0) + 1
							elseif dd < thr then
								nNah = nNah + 1
								Z.nahW[a[1]] = (Z.nahW[a[1]] or 0) + 1
								Z.nahW[b[1]] = (Z.nahW[b[1]] or 0) + 1
							end
						end
					end
				end
			end
		end
	end
	logw("Kreuzungen ohne gemeinsamen Knoten:", nSchnitt, "| Segmente naeher als die halbe Summe der Fahrbahnbreiten, ohne Kreuzung:", nNah)
	local namen = {}
	for k in pairs(zaehl) do namen[#namen + 1] = k end
	table.sort(namen, function(x, y) return zaehl[x] > zaehl[y] end)
	for i = 1, math.min(#namen, 10) do logw("  Kreuzung", namen[i], ":", zaehl[namen[i]]) end
	Z.kk = { mit = { 0, 0 }, ohne = { 0, 0 } }
end

local function importiere(daten, cleanup)
	if type(daten.nodes) ~= "table" or type(daten.ways) ~= "table" then
		logw("FEHLER: Datei hat keine nodes/ways")
		return
	end
	logw("Import startet:", #daten.nodes, "Knoten,", #daten.ways, "Wege")
	STUMM = true
	IMPORT = {
		knoten = daten.nodes, wege = daten.ways, i = 0, bekannt = {}, gebautId = {}, wartet = false,
		gebaut = 0, fehler = 0, gruende = {}, gezeigt = 0, statistik = {}, fehlerListe = {},
		abwOk = {}, abwFehler = {}, cleanup = cleanup or false, ergebnis = {},
	}
	local okP, hoehe = pcall(planeHoehen, IMPORT)
	if not okP then
		logw("FEHLER in der Hoehenplanung:", hoehe)
		IMPORT.hoehe = {}
	else
		IMPORT.hoehe = hoehe
	end
	local okK, errK = pcall(kreuzungsAnalyse, IMPORT)
	if not okK then
		logw("Kreuzungsanalyse gescheitert:", errK)
		IMPORT.kreuzW, IMPORT.nahW = {}, {}
		IMPORT.kk = { mit = { 0, 0 }, ohne = { 0, 0 } }
	end
	importVoran()
end

-- Flachste Stelle rechts der Kartenmitte suchen (ohne Wasser): Mitte eines Fensters mit kleinster Hoehenspanne
local function findeFlach(groesse)
	local T = api.engine.terrain
	local schritt = 100
	local fenster = math.ceil(groesse / schritt) + 1
	local xs, ys = {}, {}
	for x = 500, 4500, schritt do xs[#xs + 1] = x end
	for y = -4000, 4000, schritt do ys[#ys + 1] = y end
	local H = {}
	for i, x in ipairs(xs) do
		H[i] = {}
		for j, y in ipairs(ys) do
			local v = api.type.Vec2f.new(x, y)
			local ok, hz = pcall(function()
				if not T.isValidCoordinate(v) then return false end
				if T.isOnWater(v) then return false end
				return T.getHeightAt(v)
			end)
			H[i][j] = (ok and hz) or false
		end
	end
	local beste, bi, bj = nil, nil, nil
	for i = 1, #xs - fenster + 1 do
		for j = 1, #ys - fenster + 1 do
			local mn, mx, gut = 1e9, -1e9, true
			for a = 0, fenster - 1 do
				for b = 0, fenster - 1 do
					local h = H[i + a][j + b]
					if not h then gut = false break end
					if h < mn then mn = h end
					if h > mx then mx = h end
				end
				if not gut then break end
			end
			if gut and (beste == nil or (mx - mn) < beste) then beste, bi, bj = mx - mn, i, j end
		end
	end
	if not bi then return nil end
	return xs[bi] + (fenster - 1) * schritt / 2, ys[bj] + (fenster - 1) * schritt / 2, beste
end

local function zaehleKnoten(abfrage)
	local n = 0
	local ok, err = pcall(function()
		for _ in pairs(abfrage()) do n = n + 1 end
	end)
	if not ok then return "Fehler: " .. tostring(err) end
	return n
end

-- Hilfsfunktion: Namen gefiltert und begrenzt in EINER Zeile ausgeben
local function einzeiler(titel, quelle, filter, maximal)
	local namen = {}
	local ok, err = pcall(function()
		for k, v in pairs(quelle) do
			local s = (type(v) == "string") and v or tostring(k)
			if (not filter) or s:lower():find(filter) then
				-- bei Pfaden nur den letzten Teil
				namen[#namen + 1] = (s:match("([^/]+)$") or s)
			end
		end
	end)
	if not ok then logw(titel, "nicht auflistbar:", err) return end
	table.sort(namen)
	local zeige = {}
	for i = 1, math.min(#namen, maximal or 25) do zeige[i] = namen[i] end
	logw(titel, "(" .. #namen .. " gesamt):", table.concat(zeige, ", "))
end

local function infoRes()
	einzeiler("api.res bridge", api.res, "bridge", 10)
	einzeiler("api.res tunnel", api.res, "tunnel", 10)
end

local function infoBruecke()
	local ok, b = pcall(api.res.bridgeTypeRep.getAll)
	if ok and b then
		einzeiler("Brueckentypen", b, nil, 30)
	else
		logw("bridgeTypeRep.getAll gescheitert:", b)
	end
end

local function infoEnum()
	einzeiler("api.type.enum (gefiltert)", api.type.enum, "edge", 15)
	einzeiler("api.type.enum (road/bridge/tunnel)", api.type.enum, "road", 10)
	pcall(function()
		local t = {}
		for k, v in pairs(api.type.enum.BaseEdgeType) do t[#t + 1] = tostring(k) .. "=" .. tostring(v) end
		logw("BaseEdgeType:", table.concat(t, ", "))
	end)
end

local function zaehleKanten()
	local gesehen, nachRoad, nachTyp, gesamt = {}, {}, {}, 0
	local dreier = 0
	local ok, err = pcall(function()
		local m = api.engine.system.streetSystem.getNode2SegmentMap()
		for _, segs in pairs(m) do
			local grad = 0
			for _, seg in pairs(segs) do
				grad = grad + 1
				if not gesehen[seg] then
					gesehen[seg] = true
					gesamt = gesamt + 1
					local c = api.engine.getComponent(seg, api.type.ComponentType.BASE_EDGE)
					local r, t = tostring(c.roadType), tostring(c.type)
					nachRoad[r] = (nachRoad[r] or 0) + 1
					nachTyp[t] = (nachTyp[t] or 0) + 1
				end
			end
			if grad >= 3 then dreier = dreier + 1 end
		end
	end)
	if not ok then logw("Kanten zaehlen gescheitert:", err) return end
	local a, b = {}, {}
	for k, v in pairs(nachRoad) do a[#a + 1] = "roadType " .. k .. ": " .. v end
	for k, v in pairs(nachTyp) do b[#b + 1] = "type " .. k .. ": " .. v end
	table.sort(a) table.sort(b)
	logw("Kanten gesamt:", gesamt, "|", table.concat(a, ", "), "|", table.concat(b, ", "), "| Knoten mit 3+ Kanten:", dreier)
end

-- Testdefinitionen (Koordinaten ab Kartenmitte)
local TESTS = {
	pruefen = { punkte = { { 0, 0 }, { 80, 0 } }, art = 0, endung = STRASSE, bauen = false },
	bauen = { punkte = { { 0, 0 }, { 80, 0 } }, art = 0, endung = STRASSE, bauen = true },
	kette_pruefen = { punkte = { { 0, 100 }, { 60, 100 }, { 120, 130 }, { 180, 130 }, { 240, 100 } }, art = 0, endung = STRASSE, bauen = false },
	kette_bauen = { punkte = { { 0, 100 }, { 60, 100 }, { 120, 130 }, { 180, 130 }, { 240, 100 } }, art = 0, endung = STRASSE, bauen = true },
	gleis_pruefen = { punkte = { { 0, -100 }, { 80, -100 }, { 160, -80 }, { 240, -60 }, { 320, -60 } }, art = 1, endung = GLEIS, bauen = false, opts = { maxG = 0.03 } },
	gleis_bauen = { punkte = { { 0, -100 }, { 80, -100 }, { 160, -80 }, { 240, -60 }, { 320, -60 } }, art = 1, endung = GLEIS, bauen = true, opts = { maxG = 0.03 } },
	-- Bruecke: eine Kante, beide Knoten 8 m ueber dem Gelaende
	bruecke_pruefen = { punkte = { { 0, 250 }, { 70, 250 } }, art = 0, endung = STRASSE, bauen = false,
		opts = { rep = "bridgeTypeRep", endungTyp = "/trestle.bridge", dz = 8 } },
	bruecke_bauen = { punkte = { { 0, 250 }, { 70, 250 } }, art = 0, endung = STRASSE, bauen = true,
		opts = { rep = "bridgeTypeRep", endungTyp = "/trestle.bridge", dz = 8 } },
	-- Tunnel: eine Kante, beide Knoten 8 m unter dem Gelaende (erster Tunneltyp)
	tunnel_pruefen = { punkte = { { 0, -250 }, { 70, -250 } }, art = 0, endung = STRASSE, bauen = false,
		opts = { rep = "tunnelTypeRep", endungTyp = "/tunnel_a_car.tunnel", dz = -8 } },
	tunnel_bauen = { punkte = { { 0, -250 }, { 70, -250 } }, art = 0, endung = STRASSE, bauen = true,
		opts = { rep = "tunnelTypeRep", endungTyp = "/tunnel_a_car.tunnel", dz = -8 } },
	-- Tunnel fuer ein Gleis
	tunnelg_pruefen = { punkte = { { 0, -350 }, { 70, -350 } }, art = 1, endung = GLEIS, bauen = false,
		opts = { rep = "tunnelTypeRep", endungTyp = "/tunnel_a.tunnel", dz = -8, maxG = 0.03 } },
	tunnelg_bauen = { punkte = { { 0, -350 }, { 70, -350 } }, art = 1, endung = GLEIS, bauen = true,
		opts = { rep = "tunnelTypeRep", endungTyp = "/tunnel_a.tunnel", dz = -8, maxG = 0.03 } },
}

-- Diagnose: zu Entity-Nummern (aus den Zeilen "transition not valid: entity N" im Log)
-- ausgeben, welche Kanten an diesen Knoten zusammentreffen (Vorlage, Typ, Winkel).
local function winkelGrad(x, y)
	if math.atan2 then return math.deg(math.atan2(y, x)) end
	return math.deg(math.atan(y, x))
end

local function diagnose(param)
	local ids = {}
	for n in tostring(param):gmatch("%d+") do ids[#ids + 1] = tonumber(n) end
	logw("Diagnose fuer", #ids, "Entities")
	local karte = nil
	pcall(function() karte = api.engine.system.streetSystem.getNode2SegmentMap() end)
	for k = 1, math.min(#ids, 20) do
		local e = ids[k]
		local okE, ex = pcall(api.engine.entityExists, e)
		if okE and ex == false then
			logw("Entity", e, "existiert nicht mehr")
		else
			local okn, cn = pcall(api.engine.getComponent, e, api.type.ComponentType.BASE_NODE)
			if okn and cn ~= nil then
				local px, py, pz = cn.position.x, cn.position.y, cn.position.z
				local teile, winkel = {}, {}
				local segs = karte and karte[e]
				if segs then
					for _, seg in pairs(segs) do
						local okc, c = pcall(api.engine.getComponent, seg, api.type.ComponentType.BASE_EDGE)
						if okc and c ~= nil then
							local tpl = tostring(c.roadTemplate):match("([^/]+)%.street_template$") or tostring(c.roadTemplate)
							local tx, ty
							if c.node0 == e then tx, ty = c.tangent0.x, c.tangent0.y else tx, ty = c.tangent1.x, c.tangent1.y end
							if c.node0 ~= e then tx, ty = -tx, -ty end -- immer vom Knoten weg zeigen
							local w = winkelGrad(tx, ty)
							winkel[#winkel + 1] = w
							local art = (tostring(c.type) == "1" and "Bruecke") or (tostring(c.type) == "2" and "Tunnel") or "normal"
							teile[#teile + 1] = string.format("%s (%s) %.0f Grad", tpl, art, w)
						end
					end
				end
				local klein = 360
				for a = 1, #winkel do
					for b = a + 1, #winkel do
						local d = math.abs(winkel[a] - winkel[b]) % 360
						if d > 180 then d = 360 - d end
						if d < klein then klein = d end
					end
				end
				logw(string.format("Knoten %d bei %.0f/%.0f z %.1f: %d Kanten, kleinster Winkel %s | %s",
					e, px, py, pz, #teile, #winkel > 1 and string.format("%.0f", klein) or "-", table.concat(teile, " | ")))
			else
				local okc, c = pcall(api.engine.getComponent, e, api.type.ComponentType.BASE_EDGE)
				if okc and c ~= nil then
					logw("Entity", e, "ist eine Kante:", tostring(c.roadTemplate), "Typ", tostring(c.type))
				else
					logw("Entity", e, "ist weder Knoten noch Kante")
				end
			end
		end
	end
end

function data()
	local gemeldet = false

	return {
		update = function(userParams, state, dt)
			-- Ereignisse muessen abonniert werden, sonst kommt handleEvent nie an
			local ok, abo = pcall(function() return state:hasEventSubscriptions() end)
			if ok and not abo then
				pcall(function() state:subscribeToAllEvents() end)
			end
			if gemeldet then return end
			gemeldet = true
			log("bereit, Version:", VERSION)
		end,

		handleEvent = function(userParams, state, src, id, name, param)
			if id ~= "mapstudio" then return end
			local ok, err = pcall(function()
				if name == "diagnose" then diagnose(param) return end
				if name == "kreuzung_bauen" then kreuzung() return end
				if name == "import" or name == "import_cleanup" or name == "import_gitter" then
					if IMPORT then logw("Import laeuft schon") return end
					local daten = ladeDaten(name == "import_gitter" and "osmdata_gitter.lua" or "osmdata.lua")
					if daten then importiere(daten, name == "import_cleanup") end
					return
				end
				if name == "import_weiter" then importVoran() return end
				if name == "import_gitter_flach" then
					if IMPORT then logw("Import laeuft schon") return end
					local daten = ladeDaten("osmdata_gitter.lua")
					if not daten then return end
					local cx, cy, spanne = findeFlach(550)
					if not cx then logw("Keine flache Stelle gefunden") return end
					local dx, dy = cx - (-25), cy - (-1025) -- Mitte des Gitters in der Datei: (-25, -1025)
					local neu = { format = daten.format, name = daten.name, ways = daten.ways, nodes = {} }
					for i, p in ipairs(daten.nodes) do neu.nodes[i] = { p[1] + dx, p[2] + dy } end
					logw(string.format("Flachste Stelle: Mitte x=%.0f y=%.0f, Hoehenspanne %.1f m", cx, cy, spanne))
					importiere(neu)
					return
				end
				if name == "import_stop" then
					if IMPORT then importEnde(true) else logw("kein Import aktiv") end
					return
				end
				if name == "import_info" then
					local daten = ladeDaten("osmdata.lua")
					if daten then logw("Datei:", daten.name, "Format", daten.format, "Knoten", daten.nodes and #daten.nodes, "Wege", daten.ways and #daten.ways) end
					return
				end
				if name == "info_res" then infoRes() return end
				if name == "info_bruecke" then infoBruecke() return end
				if name == "info_enum" then infoEnum() return end
				if name == "info_tunnel" then
					local ok, b = pcall(api.res.tunnelTypeRep.getAll)
					if ok and b then einzeiler("Tunneltypen", b, nil, 30) else log("tunnelTypeRep.getAll gescheitert:", b) end
					return
				end
				if name == "info_werte" then
					local t = {}
					for _, p in ipairs({ { "BaseEdgeType", "NONE" }, { "BaseEdgeType", "BRIDGE" }, { "BaseEdgeType", "TUNNEL" },
						{ "RoadType", "STREET" }, { "RoadType", "TRACK" } }) do
						local w, gef = enumWert(p[1], p[2], "?")
						t[#t + 1] = p[1] .. "." .. p[2] .. "=" .. tostring(w) .. (gef and "" or "(nicht gefunden)")
					end
					log("Enum-Werte:", table.concat(t, ", "))
					return
				end
				if name == "zaehlen" then
					logw("Knoten mit Strassenkante:", zaehleKnoten(function() return api.engine.system.streetSystem.getNode2StreetEdgeMap() end))
					zaehleKanten()
					return
				end
				local t = TESTS[name]
				if not t then log("unbekanntes Ereignis:", name, "(Skriptversion:", VERSION .. ")") return end
				log("Ereignis:", name)
				local prop, ctx = baueKette(t.punkte, t.art, t.endung, t.opts)
				if not prop then return end
				local pd, kritisch = pruefe(prop, ctx)
				if not t.bauen then return end
				if kritisch then log("nicht gebaut: die Pruefung meldet Fehler") return end
				api.cmd.sendCommand(
					api.cmd.makeWorldBuildProposalCmd(prop, ctx, false, true),
					function(d, success, entities)
						log("Bauen fertig, success =", success, "Entities:", entities and #entities)
					end
				)
				log("Baubefehl gesendet")
			end)
			if not ok then log("FEHLER im Ereignis:", err) end
		end,
	}
end
"""
