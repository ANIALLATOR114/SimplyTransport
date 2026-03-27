/**
 * MapLibre agency routes: GET /api/v1/map/route/{agency_id}
 */
(function () {
    "use strict";

    const OSM_RASTER_STYLE = {
        version: 8,
        sources: {
            osm: {
                type: "raster",
                tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                tileSize: 256,
                attribution:
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            },
        },
        layers: [
            {
                id: "osm",
                type: "raster",
                source: "osm",
                minzoom: 0,
                maxzoom: 19,
            },
        ],
    };

    function setLayerVisibility(map, id, visible) {
        if (!map.getLayer(id)) {
            return;
        }
        map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
    }

    function buildLayerPanel(panel, payload, layerState, map) {
        const routes = payload.routes;

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "maplibre-toggle-all maplibre-toggle-all--panel-top";
        btn.textContent = "Toggle all off";
        let allOn = true;
        btn.addEventListener("click", () => {
            allOn = !allOn;
            btn.textContent = allOn ? "Toggle all off" : "Toggle all on";
            routes.forEach((route) => {
                const st = layerState.routes[route.route_id];
                if (st) {
                    setLayerVisibility(map, st.line, allOn);
                }
            });
            panel.querySelectorAll('input[type="checkbox"]').forEach((el) => {
                el.checked = allOn;
            });
        });
        panel.appendChild(btn);

        const scroll = document.createElement("div");
        scroll.className = "maplibre-layer-panel-scroll";
        scroll.setAttribute("role", "group");
        scroll.setAttribute("aria-label", "Route layers");

        routes.forEach((route) => {
            const row = document.createElement("label");
            row.className = "maplibre-layer-row";
            const cb = document.createElement("input");
            cb.type = "checkbox";
            cb.checked = true;
            cb.dataset.routeId = route.route_id;
            const swatch = document.createElement("span");
            swatch.className = "maplibre-color-swatch";
            swatch.style.backgroundColor = route.color;
            swatch.setAttribute("aria-hidden", "true");
            row.appendChild(cb);
            row.appendChild(swatch);
            row.appendChild(document.createTextNode(` ${route.short_name}`));
            cb.addEventListener("change", () => {
                const vis = cb.checked;
                const st = layerState.routes[route.route_id];
                if (st) {
                    setLayerVisibility(map, st.line, vis);
                }
            });
            scroll.appendChild(row);
        });
        panel.appendChild(scroll);
    }

    function initAgencyMap(agencyId, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !window.maplibregl) {
            return;
        }

        const loader = container.parentElement
            ? container.parentElement.querySelector(".map-loader")
            : null;

        const url = `/api/v1/map/route/${encodeURIComponent(agencyId)}`;

        fetch(url)
            .then((r) => {
                if (!r.ok) {
                    throw new Error("Map data not available");
                }
                return r.json();
            })
            .then((payload) => {
                if (loader) {
                    loader.style.display = "none";
                }

                const map = new maplibregl.Map({
                    container: containerId,
                    style: OSM_RASTER_STYLE,
                    center: payload.center,
                    zoom: payload.zoom,
                });

                map.addControl(new maplibregl.NavigationControl(), "top-left");
                map.addControl(new maplibregl.FullscreenControl(), "top-left");

                const layerState = {
                    routes: {},
                };

                const panel = document.createElement("div");
                panel.className =
                    "maplibre-layer-panel maplibre-layer-panel--routes-scroll";

                map.on("load", () => {
                    payload.routes.forEach((route) => {
                        const lid = `agency-route-line-${route.route_id}`;
                        const srcId = `agency-route-src-${route.route_id}`;
                        map.addSource(srcId, {
                            type: "geojson",
                            data: {
                                type: "Feature",
                                properties: {},
                                geometry: route.line,
                            },
                        });
                        map.addLayer({
                            id: lid,
                            type: "line",
                            source: srcId,
                            layout: {
                                visibility: "visible",
                                "line-join": "round",
                                "line-cap": "round",
                            },
                            paint: {
                                "line-color": route.color,
                                "line-width": 5,
                                "line-opacity": 0.9,
                            },
                        });
                        layerState.routes[route.route_id] = { line: lid };
                    });

                    buildLayerPanel(panel, payload, layerState, map);
                    const panelHost = container.parentElement;
                    if (panelHost) {
                        panelHost.appendChild(panel);
                    }
                });
            })
            .catch(() => {
                if (loader) {
                    loader.style.display = "none";
                }
                container.innerHTML =
                    '<p class="map-error">Map could not be loaded. Try again later.</p>';
            });
    }

    window.initAgencyMap = initAgencyMap;

    function bindAgencyMapEmbed() {
        const wrap = document.querySelector(
            ".map-container--maplibre[data-agency-id]",
        );
        if (!wrap || wrap.dataset.agencymapEmbedInit === "1") {
            return;
        }
        if (!window.initAgencyMap) {
            return;
        }
        if (!wrap.dataset.agencyId || !document.getElementById("map-element")) {
            return;
        }
        function doInit() {
            if (wrap.dataset.agencymapEmbedInit === "1") {
                return;
            }
            if (!window.initAgencyMap || !window.maplibregl) {
                return;
            }
            wrap.dataset.agencymapEmbedInit = "1";
            initAgencyMap(wrap.dataset.agencyId, "map-element");
        }
        if (window.whenMapLibreReady) {
            window.whenMapLibreReady(doInit);
        } else {
            function fallback() {
                if (wrap.dataset.agencymapEmbedInit === "1") {
                    return;
                }
                if (!window.maplibregl) {
                    const n = Number(wrap.dataset.embedWaitDeps || 0) + 1;
                    if (n > 120) {
                        return;
                    }
                    wrap.dataset.embedWaitDeps = String(n);
                    requestAnimationFrame(fallback);
                    return;
                }
                delete wrap.dataset.embedWaitDeps;
                doInit();
            }
            fallback();
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindAgencyMapEmbed);
    } else {
        bindAgencyMapEmbed();
    }
    window.addEventListener("load", bindAgencyMapEmbed);
    if (!window.__agencyMapEmbedHtmxBound) {
        window.__agencyMapEmbedHtmxBound = true;
        document.body.addEventListener("htmx:afterSwap", bindAgencyMapEmbed);
        document.body.addEventListener("htmx:afterSettle", bindAgencyMapEmbed);
    }
})();
