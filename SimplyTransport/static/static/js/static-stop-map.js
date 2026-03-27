/**
 * MapLibre static stop maps: GET /api/v1/map/stop/aggregated/{map_type}
 */
(function () {
    "use strict";

    const STOP_LABEL_MIN_ZOOM = 15;
    const LABEL_FONT = ["Open Sans Semibold"];
    const MAP_LABEL_BADGE_PAINT = {
        "text-color": "#ffffff",
        "text-halo-color": "#313b46",
        "text-halo-width": 3.5,
        "text-halo-blur": 0.9,
    };
    const STOP_LABEL_TEXT_OFFSET = [0, 1.65];

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

    function initStaticStopMap(mapType, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !window.maplibregl || !window.StopMapPopup) {
            return;
        }

        const loader = container.parentElement
            ? container.parentElement.querySelector(".map-loader")
            : null;

        const url = `/api/v1/map/stop/aggregated/${encodeURIComponent(mapType)}`;

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

                const popup = new maplibregl.Popup({
                    closeButton: true,
                    closeOnClick: true,
                    className: "maplibre-stop-popup",
                    maxWidth: "min(360px, 92vw)",
                });

                map.on("load", () => {
                    map.addSource("stops-src", {
                        type: "geojson",
                        data: stopsGeojson,
                    });
                    map.addLayer({
                        id: "stops-static",
                        type: "circle",
                        source: "stops-src",
                        paint: {
                            "circle-radius": 5,
                            "circle-color": "#2563eb",
                            "circle-stroke-width": 1,
                            "circle-stroke-color": "#ffffff",
                        },
                    });
                    map.addLayer({
                        id: "stops-labels-static",
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

                    function openStopPopupFromFeature(f) {
                        const sid = f.properties.stop_id;
                        const stop = payload.stops.find((s) => s.stop_id === sid);
                        if (!stop) {
                            return;
                        }
                        const P = window.StopMapPopup;
                        const routeDir = 0;
                        popup
                            .setLngLat([stop.lon, stop.lat])
                            .setHTML(P.buildLoadingPopupHtml(stop))
                            .addTo(map);
                        P.fetchStopDetailed(sid)
                            .then((detail) => {
                                popup.setHTML(P.buildPopupHtmlFromDetailed(detail, routeDir));
                            })
                            .catch(() => {
                                popup.setHTML(P.buildErrorPopupHtml(stop));
                            });
                    }

                    map.on("click", "stops-static", (e) => {
                        openStopPopupFromFeature(e.features[0]);
                    });
                    map.on("click", "stops-labels-static", (e) => {
                        openStopPopupFromFeature(e.features[0]);
                    });
                    map.on("mouseenter", "stops-static", () => {
                        map.getCanvas().style.cursor = "pointer";
                    });
                    map.on("mouseenter", "stops-labels-static", () => {
                        map.getCanvas().style.cursor = "pointer";
                    });
                    map.on("mouseleave", "stops-static", () => {
                        map.getCanvas().style.cursor = "";
                    });
                    map.on("mouseleave", "stops-labels-static", () => {
                        map.getCanvas().style.cursor = "";
                    });
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

    window.initStaticStopMap = initStaticStopMap;

    function bindStaticStopMapEmbed() {
        const wrap = document.querySelector(
            ".map-container--maplibre[data-map-type]",
        );
        if (!wrap || wrap.dataset.staticstopmapEmbedInit === "1") {
            return;
        }
        if (!window.initStaticStopMap) {
            return;
        }
        if (!wrap.dataset.mapType || !document.getElementById("map-element")) {
            return;
        }
        function doInit() {
            if (wrap.dataset.staticstopmapEmbedInit === "1") {
                return;
            }
            if (!window.initStaticStopMap || !window.maplibregl || !window.StopMapPopup) {
                return;
            }
            wrap.dataset.staticstopmapEmbedInit = "1";
            initStaticStopMap(wrap.dataset.mapType, "map-element");
        }
        if (window.whenMapWithPopupReady) {
            window.whenMapWithPopupReady(doInit);
        } else {
            function fallback() {
                if (wrap.dataset.staticstopmapEmbedInit === "1") {
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
        document.addEventListener("DOMContentLoaded", bindStaticStopMapEmbed);
    } else {
        bindStaticStopMapEmbed();
    }
    window.addEventListener("load", bindStaticStopMapEmbed);
    if (!window.__staticStopMapEmbedHtmxBound) {
        window.__staticStopMapEmbedHtmxBound = true;
        document.body.addEventListener("htmx:afterSwap", bindStaticStopMapEmbed);
        document.body.addEventListener("htmx:afterSettle", bindStaticStopMapEmbed);
    }
})();
