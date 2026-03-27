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

                const tooltip = new maplibregl.Popup({
                    closeButton: false,
                    closeOnClick: false,
                    className: "maplibre-stop-tooltip",
                    anchor: "bottom",
                    offset: [0, -12],
                    maxWidth: "none",
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

                    function openPopupForStopId(sid) {
                        tooltip.remove();
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

                    map.on("click", "stops-nearby", (e) => {
                        const sid = e.features[0].properties.stop_id;
                        openPopupForStopId(sid);
                    });
                    map.on("mouseenter", "stops-nearby", (e) => {
                        map.getCanvas().style.cursor = "pointer";
                        const sid = e.features[0].properties.stop_id;
                        const stop = payload.stops.find((s) => s.stop_id === sid);
                        if (!stop) {
                            return;
                        }
                        tooltip
                            .setLngLat([stop.lon, stop.lat])
                            .setHTML(window.StopMapPopup.buildStopTooltipHtml(stop))
                            .addTo(map);
                    });
                    map.on("mouseleave", "stops-nearby", () => {
                        map.getCanvas().style.cursor = "";
                        tooltip.remove();
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
})();
