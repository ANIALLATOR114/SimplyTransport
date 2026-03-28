/**
 * MapLibre nearby stops: GET /api/v1/map/stop/nearby?latitude=&longitude=
 */
(function () {
    "use strict";

    function roughCirclePolygon(lon, lat, radiusMeters, steps) {
        const n = steps || 64;
        const ring = [];
        for (let i = 0; i <= n; i++) {
            const ang = (i / n) * 2 * Math.PI;
            const dx =
                (radiusMeters * Math.sin(ang)) / 111320 / Math.cos((lat * Math.PI) / 180);
            const dy = (radiusMeters * Math.cos(ang)) / 110540;
            ring.push([lon + dx, lat + dy]);
        }
        return {
            type: "Feature",
            properties: {},
            geometry: {
                type: "Polygon",
                coordinates: [ring],
            },
        };
    }

    const {
        createOsmRasterStyle,
        LABEL_FONT,
        MAP_LABEL_BADGE_PAINT,
        STOP_LABEL_MIN_ZOOM,
        STOP_LABEL_TEXT_OFFSET,
        addDefaultMapControls,
    } = window.MapLibreMapShared;

    const OSM_RASTER_STYLE = createOsmRasterStyle();

    function initNearbyMap(latitude, longitude, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !window.maplibregl || !window.StopMapPopup) {
            return;
        }

        const loader = container.parentElement
            ? container.parentElement.querySelector(".map-loader")
            : null;

        const q = new URLSearchParams({
            latitude: String(latitude),
            longitude: String(longitude),
        });

        fetch(`/api/v1/map/stop/nearby?${q.toString()}`)
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

                addDefaultMapControls(map);

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

                const userPoint = {
                    type: "FeatureCollection",
                    features: [
                        {
                            type: "Feature",
                            geometry: {
                                type: "Point",
                                coordinates: [payload.user_lon, payload.user_lat],
                            },
                            properties: {},
                        },
                    ],
                };

                const circleFeat = roughCirclePolygon(
                    payload.user_lon,
                    payload.user_lat,
                    payload.radius_meters,
                    64,
                );

                const popup = new maplibregl.Popup({
                    closeButton: true,
                    closeOnClick: true,
                    className: "maplibre-stop-popup",
                    maxWidth: "min(360px, 92vw)",
                });

                map.on("load", () => {
                    map.addSource("radius-src", {
                        type: "geojson",
                        data: circleFeat,
                    });
                    map.addLayer({
                        id: "search-radius",
                        type: "fill",
                        source: "radius-src",
                        paint: {
                            "fill-color": "#2563eb",
                            "fill-opacity": 0.08,
                        },
                    });
                    map.addLayer({
                        id: "search-radius-outline",
                        type: "line",
                        source: "radius-src",
                        paint: {
                            "line-color": "#2563eb",
                            "line-width": 2,
                            "line-opacity": 0.35,
                        },
                    });

                    map.addSource("user-src", {
                        type: "geojson",
                        data: userPoint,
                    });
                    map.addLayer({
                        id: "user-loc",
                        type: "circle",
                        source: "user-src",
                        paint: {
                            "circle-radius": 9,
                            "circle-color": "#dc2626",
                            "circle-stroke-width": 2,
                            "circle-stroke-color": "#ffffff",
                        },
                    });

                    map.addSource("stops-src", {
                        type: "geojson",
                        data: stopsGeojson,
                    });
                    map.addLayer({
                        id: "stops-nearby",
                        type: "circle",
                        source: "stops-src",
                        paint: {
                            "circle-radius": 6,
                            "circle-color": "#ffffff",
                            "circle-stroke-width": 2,
                            "circle-stroke-color": "#333333",
                        },
                    });
                    map.addLayer({
                        id: "stops-labels-nearby",
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

                    function openPopupForStopId(sid) {
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

                    function openStopFromFeature(f) {
                        openPopupForStopId(f.properties.stop_id);
                    }

                    map.on("click", "stops-nearby", (e) => {
                        openStopFromFeature(e.features[0]);
                    });
                    map.on("click", "stops-labels-nearby", (e) => {
                        openStopFromFeature(e.features[0]);
                    });
                    map.on("mouseenter", "stops-nearby", () => {
                        map.getCanvas().style.cursor = "pointer";
                    });
                    map.on("mouseenter", "stops-labels-nearby", () => {
                        map.getCanvas().style.cursor = "pointer";
                    });
                    map.on("mouseleave", "stops-nearby", () => {
                        map.getCanvas().style.cursor = "";
                    });
                    map.on("mouseleave", "stops-labels-nearby", () => {
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

    window.initNearbyMap = initNearbyMap;

    function bindNearbyMapEmbed() {
        const wrap = document.querySelector(
            ".map-container--maplibre[data-latitude][data-longitude]",
        );
        if (!wrap || wrap.dataset.nearbymapEmbedInit === "1") {
            return;
        }
        if (!window.initNearbyMap) {
            return;
        }
        if (!document.getElementById("map-element")) {
            return;
        }
        const lat = Number.parseFloat(wrap.dataset.latitude);
        const lon = Number.parseFloat(wrap.dataset.longitude);
        if (Number.isNaN(lat) || Number.isNaN(lon)) {
            return;
        }
        function doInit() {
            if (wrap.dataset.nearbymapEmbedInit === "1") {
                return;
            }
            if (!window.initNearbyMap || !window.maplibregl || !window.StopMapPopup) {
                return;
            }
            wrap.dataset.nearbymapEmbedInit = "1";
            initNearbyMap(lat, lon, "map-element");
        }
        if (window.whenMapWithPopupReady) {
            window.whenMapWithPopupReady(doInit);
        } else {
            function fallback() {
                if (wrap.dataset.nearbymapEmbedInit === "1") {
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
        document.addEventListener("DOMContentLoaded", bindNearbyMapEmbed);
    } else {
        bindNearbyMapEmbed();
    }
    window.addEventListener("load", bindNearbyMapEmbed);
    if (!window.__nearbyMapEmbedHtmxBound) {
        window.__nearbyMapEmbedHtmxBound = true;
        document.body.addEventListener("htmx:afterSwap", bindNearbyMapEmbed);
        document.body.addEventListener("htmx:afterSettle", bindNearbyMapEmbed);
    }
})();
