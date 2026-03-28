/**
 * MapLibre route map: loads /api/v1/map/route/{id}/{direction}.
 * Depends on global maplibregl (loaded from /static in base.html before this script).
 */
(function () {
    "use strict";

    /** demotiles.maplibre.org fonts (same as MapLibre demo style; Bold is not available). */
    const VEHICLE_LABEL_MIN_ZOOM = 14;
    const STOP_LABEL_MIN_ZOOM = 15;
    const LABEL_FONT = ["Open Sans Semibold"];
    /** Matches --bg-color-bump-border; halo + white text ≈ dark rounded badge (no native text-background in MapLibre). */
    const MAP_LABEL_BADGE_PAINT = {
        "text-color": "#ffffff",
        "text-halo-color": "#313b46",
        "text-halo-width": 3.5,
        "text-halo-blur": 0.9,
    };
    const VEHICLE_LABEL_TEXT_OFFSET = [0, 1.95];
    const STOP_LABEL_TEXT_OFFSET = [0, 1.65];

    /**
     * @param {object} map - maplibregl Map
     * @param {() => string[]} getPulseLayerIds
     */
    function startVehiclePulseAnimation(map, getPulseLayerIds) {
        let raf = 0;
        function tick() {
            const wave = Math.sin((Date.now() / 2000) * Math.PI * 2) * 0.5 + 0.5;
            const opacity = 0.12 + wave * 0.28;
            const radius = 12 + wave * 10;
            for (const lid of getPulseLayerIds()) {
                if (map.getLayer(lid)) {
                    map.setPaintProperty(lid, "circle-opacity", opacity);
                    map.setPaintProperty(lid, "circle-radius", radius);
                }
            }
            raf = requestAnimationFrame(tick);
        }
        raf = requestAnimationFrame(tick);
        map.once("remove", () => {
            cancelAnimationFrame(raf);
        });
    }

    const OSM_RASTER_STYLE = {
        version: 8,
        glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
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

    const LINE_ID = "route-line-main";
    const VEHICLE_PULSE_ID = "vehicle-pulse-main";
    const VEHICLE_ID = "vehicle-main";
    const VEHICLE_LABELS_ID = "vehicle-labels-main";
    const STOPS_ID = "stops-all";
    const STOPS_LABELS_ID = "stops-labels-main";

    function initRouteMap(routeId, direction, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !window.maplibregl || !window.StopMapPopup) {
            return;
        }

        const loader = container.parentElement
            ? container.parentElement.querySelector(".map-loader")
            : null;

        const wrap = container.closest(
            ".map-container--maplibre[data-route-id][data-direction]",
        );
        if (wrap && typeof wrap.__routeMapCleanup === "function") {
            wrap.__routeMapCleanup();
        }
        if (loader) {
            loader.style.removeProperty("display");
        }

        const dir = Number.parseInt(String(direction), 10);
        const url = `/api/v1/map/route/${encodeURIComponent(routeId)}/${Number.isNaN(dir) ? direction : dir}`;

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

                const r = payload.route;
                const stopsGeojson = {
                    type: "FeatureCollection",
                    features: payload.stops.map((s) => ({
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: [s.lon, s.lat],
                        },
                        properties: {
                            stop_id: s.stop_id,
                            stop_code:
                                s.code != null && s.code !== "" ? s.code : s.stop_id,
                        },
                    })),
                };

                const vehiclesGeojson =
                    payload.vehicles.length === 0
                        ? null
                        : {
                              type: "FeatureCollection",
                              features: payload.vehicles.map((v) => ({
                                  type: "Feature",
                                  geometry: {
                                      type: "Point",
                                      coordinates: [v.lon, v.lat],
                                  },
                                  properties: {
                                      route_id: v.route_id,
                                      color: v.color,
                                      vehicle_id: v.vehicle_id,
                                      trip_id: v.trip_id,
                                      route_short_name: v.route_short_name,
                                      agency_name: v.agency_name,
                                      time_of_update: v.time_of_update,
                                      map_direction: payload.direction,
                                  },
                              })),
                          };

                const panel = document.createElement("div");
                panel.className =
                    "maplibre-layer-panel maplibre-layer-panel--routes-scroll";

                map.on("load", () => {
                    map.addSource("route-src-main", {
                        type: "geojson",
                        data: {
                            type: "Feature",
                            properties: {},
                            geometry: r.line,
                        },
                    });
                    map.addLayer({
                        id: LINE_ID,
                        type: "line",
                        source: "route-src-main",
                        layout: {
                            visibility: "visible",
                            "line-join": "round",
                            "line-cap": "round",
                        },
                        paint: {
                            "line-color": r.color,
                            "line-width": 6,
                            "line-opacity": 0.95,
                        },
                    });

                    map.addSource("stops-src", {
                        type: "geojson",
                        data: stopsGeojson,
                    });
                    map.addLayer({
                        id: STOPS_ID,
                        type: "circle",
                        source: "stops-src",
                        paint: {
                            "circle-radius": 5,
                            "circle-color": "#ffffff",
                            "circle-stroke-width": 2,
                            "circle-stroke-color": "#333333",
                        },
                    });

                    if (vehiclesGeojson) {
                        map.addSource("vehicles-src", {
                            type: "geojson",
                            data: vehiclesGeojson,
                        });
                        map.addLayer({
                            id: VEHICLE_PULSE_ID,
                            type: "circle",
                            source: "vehicles-src",
                            filter: ["==", ["get", "route_id"], r.route_id],
                            paint: {
                                "circle-radius": 12,
                                "circle-color": ["get", "color"],
                                "circle-opacity": 0.2,
                                "circle-blur": 0.35,
                            },
                        });
                        map.addLayer({
                            id: VEHICLE_ID,
                            type: "circle",
                            source: "vehicles-src",
                            filter: ["==", ["get", "route_id"], r.route_id],
                            paint: {
                                "circle-radius": 8,
                                "circle-color": ["get", "color"],
                                "circle-stroke-width": 2,
                                "circle-stroke-color": "#111827",
                            },
                        });
                        map.addLayer({
                            id: VEHICLE_LABELS_ID,
                            type: "symbol",
                            source: "vehicles-src",
                            minzoom: VEHICLE_LABEL_MIN_ZOOM,
                            filter: ["==", ["get", "route_id"], r.route_id],
                            layout: {
                                "text-field": [
                                    "to-string",
                                    [
                                        "coalesce",
                                        ["get", "route_short_name"],
                                        ["get", "route_id"],
                                        "",
                                    ],
                                ],
                                "text-size": 12,
                                "text-offset": VEHICLE_LABEL_TEXT_OFFSET,
                                "text-anchor": "top",
                                "text-allow-overlap": true,
                                "text-font": LABEL_FONT,
                            },
                            paint: MAP_LABEL_BADGE_PAINT,
                        });
                        startVehiclePulseAnimation(map, () =>
                            map.getLayer(VEHICLE_PULSE_ID) ? [VEHICLE_PULSE_ID] : [],
                        );
                    }

                    map.addLayer({
                        id: STOPS_LABELS_ID,
                        type: "symbol",
                        source: "stops-src",
                        minzoom: STOP_LABEL_MIN_ZOOM,
                        layout: {
                            "text-field": ["to-string", ["get", "stop_code"]],
                            "text-size": 11,
                            "text-offset": STOP_LABEL_TEXT_OFFSET,
                            "text-anchor": "top",
                            "text-allow-overlap": true,
                            "text-font": LABEL_FONT,
                        },
                        paint: MAP_LABEL_BADGE_PAINT,
                    });

                    buildRouteLayerPanel(panel, map, r, !!vehiclesGeojson);

                    const panelHost = container.parentElement;
                    if (panelHost) {
                        panelHost.appendChild(panel);
                    }

                    const popup = new maplibregl.Popup({
                        closeButton: true,
                        closeOnClick: true,
                        className: "maplibre-stop-popup",
                        maxWidth: "min(360px, 92vw)",
                    });

                    const vehiclePopup = new maplibregl.Popup({
                        closeButton: true,
                        closeOnClick: true,
                        className: "maplibre-stop-popup maplibre-vehicle-popup",
                        maxWidth: "min(360px, 92vw)",
                    });

                    function openPopupForStopId(sid) {
                        vehiclePopup.remove();
                        const stop = payload.stops.find((s) => s.stop_id === sid);
                        if (!stop) {
                            return;
                        }
                        const P = window.StopMapPopup;
                        popup
                            .setLngLat([stop.lon, stop.lat])
                            .setHTML(P.buildLoadingPopupHtml(stop))
                            .addTo(map);
                        P.fetchStopDetailed(sid)
                            .then((detail) => {
                                popup.setHTML(P.buildPopupHtmlFromDetailed(detail, payload.direction));
                            })
                            .catch(() => {
                                popup.setHTML(P.buildErrorPopupHtml(stop));
                            });
                    }

                    function openVehiclePopupFromFeature(f) {
                        popup.remove();
                        vehiclePopup
                            .setLngLat(f.geometry.coordinates)
                            .setHTML(window.StopMapPopup.buildVehiclePopupHtml(f.properties))
                            .addTo(map);
                    }

                    if (vehiclesGeojson && map.getLayer(VEHICLE_ID)) {
                        map.on("click", VEHICLE_ID, (e) => {
                            openVehiclePopupFromFeature(e.features[0]);
                        });
                        map.on("click", VEHICLE_LABELS_ID, (e) => {
                            openVehiclePopupFromFeature(e.features[0]);
                        });
                        map.on("mouseenter", VEHICLE_ID, () => {
                            map.getCanvas().style.cursor = "pointer";
                        });
                        map.on("mouseenter", VEHICLE_LABELS_ID, () => {
                            map.getCanvas().style.cursor = "pointer";
                        });
                        map.on("mouseleave", VEHICLE_ID, () => {
                            map.getCanvas().style.cursor = "";
                        });
                        map.on("mouseleave", VEHICLE_LABELS_ID, () => {
                            map.getCanvas().style.cursor = "";
                        });
                    }

                    function openStopPopupFromFeature(f) {
                        vehiclePopup.remove();
                        const sid = f.properties.stop_id;
                        openPopupForStopId(sid);
                    }

                    map.on("click", STOPS_ID, (e) => {
                        openStopPopupFromFeature(e.features[0]);
                    });
                    map.on("click", STOPS_LABELS_ID, (e) => {
                        openStopPopupFromFeature(e.features[0]);
                    });
                    map.on("mouseenter", STOPS_ID, () => {
                        map.getCanvas().style.cursor = "pointer";
                    });
                    map.on("mouseenter", STOPS_LABELS_ID, () => {
                        map.getCanvas().style.cursor = "pointer";
                    });
                    map.on("mouseleave", STOPS_ID, () => {
                        map.getCanvas().style.cursor = "";
                    });
                    map.on("mouseleave", STOPS_LABELS_ID, () => {
                        map.getCanvas().style.cursor = "";
                    });

                    if (wrap) {
                        wrap.__routeMapCleanup = function () {
                            map.remove();
                            if (panel.parentNode) {
                                panel.remove();
                            }
                            delete wrap.__routeMapCleanup;
                        };
                    }
                    const refBtn = document.getElementById("route-map-refresh");
                    if (refBtn) {
                        refBtn.disabled = false;
                        refBtn.onclick = function () {
                            if (refBtn.disabled) {
                                return;
                            }
                            refBtn.disabled = true;
                            initRouteMap(routeId, direction, containerId);
                        };
                    }
                });
            })
            .catch(() => {
                if (loader) {
                    loader.style.display = "none";
                }
                const refBtn = document.getElementById("route-map-refresh");
                if (refBtn) {
                    refBtn.disabled = false;
                }
                container.innerHTML =
                    '<p class="map-error">Map could not be loaded. Try again later.</p>';
            });
    }

    function setLayerVisibility(map, id, visible) {
        if (!map.getLayer(id)) {
            return;
        }
        map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
    }

    function buildRouteLayerPanel(panel, map, route, hasVehicles) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "maplibre-toggle-all maplibre-toggle-all--panel-top";
        btn.textContent = "Toggle all off";
        let allOn = true;

        const lineRow = document.createElement("label");
        lineRow.className = "maplibre-layer-row";
        const lineCb = document.createElement("input");
        lineCb.type = "checkbox";
        lineCb.checked = true;
        const lineSwatch = document.createElement("span");
        lineSwatch.className = "maplibre-color-swatch";
        lineSwatch.style.backgroundColor = route.color;
        lineSwatch.setAttribute("aria-hidden", "true");
        lineRow.appendChild(lineCb);
        lineRow.appendChild(lineSwatch);
        lineRow.appendChild(document.createTextNode(` ${route.short_name} (line)`));
        lineCb.addEventListener("change", () => {
            setLayerVisibility(map, LINE_ID, lineCb.checked);
        });

        let vehCb = null;
        let vehRow = null;
        if (hasVehicles) {
            vehRow = document.createElement("label");
            vehRow.className = "maplibre-layer-row";
            vehCb = document.createElement("input");
            vehCb.type = "checkbox";
            vehCb.checked = true;
            vehCb.id = "toggle-vehicles-layer";
            vehRow.appendChild(vehCb);
            vehRow.appendChild(document.createTextNode(" Vehicles"));
            vehCb.addEventListener("change", () => {
                const vis = vehCb.checked;
                setLayerVisibility(map, VEHICLE_PULSE_ID, vis);
                setLayerVisibility(map, VEHICLE_ID, vis);
                setLayerVisibility(map, VEHICLE_LABELS_ID, vis);
            });
        }

        const stopsRow = document.createElement("label");
        stopsRow.className = "maplibre-layer-row";
        const stopsCb = document.createElement("input");
        stopsCb.type = "checkbox";
        stopsCb.checked = true;
        stopsCb.id = "toggle-stops-layer";
        stopsRow.appendChild(stopsCb);
        stopsRow.appendChild(document.createTextNode(" Stops"));
        stopsCb.addEventListener("change", () => {
            const vis = stopsCb.checked;
            setLayerVisibility(map, STOPS_ID, vis);
            setLayerVisibility(map, STOPS_LABELS_ID, vis);
        });

        btn.addEventListener("click", () => {
            allOn = !allOn;
            btn.textContent = allOn ? "Toggle all off" : "Toggle all on";
            setLayerVisibility(map, LINE_ID, allOn);
            if (hasVehicles) {
                setLayerVisibility(map, VEHICLE_PULSE_ID, allOn);
                setLayerVisibility(map, VEHICLE_ID, allOn);
                setLayerVisibility(map, VEHICLE_LABELS_ID, allOn);
            }
            setLayerVisibility(map, STOPS_ID, allOn);
            setLayerVisibility(map, STOPS_LABELS_ID, allOn);
            lineCb.checked = allOn;
            if (hasVehicles && vehCb) {
                vehCb.checked = allOn;
            }
            stopsCb.checked = allOn;
        });
        panel.appendChild(btn);

        const scroll = document.createElement("div");
        scroll.className = "maplibre-layer-panel-scroll";
        scroll.setAttribute("role", "group");
        scroll.setAttribute("aria-label", "Map layers");
        scroll.appendChild(lineRow);
        if (hasVehicles && vehRow) {
            scroll.appendChild(vehRow);
        }
        scroll.appendChild(stopsRow);
        panel.appendChild(scroll);
    }

    window.initRouteMap = initRouteMap;

    function bindRouteMapEmbed() {
        const wrap = document.querySelector(
            ".map-container--maplibre[data-route-id][data-direction]",
        );
        if (!wrap || wrap.dataset.routemapEmbedInit === "1") {
            return;
        }
        if (!window.initRouteMap) {
            return;
        }
        if (!wrap.dataset.routeId || !document.getElementById("map-element")) {
            return;
        }
        function doInit() {
            if (wrap.dataset.routemapEmbedInit === "1") {
                return;
            }
            if (!window.initRouteMap || !window.maplibregl || !window.StopMapPopup) {
                return;
            }
            wrap.dataset.routemapEmbedInit = "1";
            initRouteMap(wrap.dataset.routeId, wrap.dataset.direction, "map-element");
        }
        if (window.whenMapWithPopupReady) {
            window.whenMapWithPopupReady(doInit);
        } else {
            function fallback() {
                if (wrap.dataset.routemapEmbedInit === "1") {
                    return;
                }
                if (!window.maplibregl || !window.StopMapPopup) {
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
        document.addEventListener("DOMContentLoaded", bindRouteMapEmbed);
    } else {
        bindRouteMapEmbed();
    }
    window.addEventListener("load", bindRouteMapEmbed);
    if (!window.__routeMapEmbedHtmxBound) {
        window.__routeMapEmbedHtmxBound = true;
        document.body.addEventListener("htmx:afterSwap", bindRouteMapEmbed);
        document.body.addEventListener("htmx:afterSettle", bindRouteMapEmbed);
    }
})();
