/**
 * MapLibre static stop maps: GET /api/v1/map/stop/aggregated/{map_type}
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
                        },
                    })),
                };

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

                    map.on("click", "stops-static", (e) => {
                        tooltip.remove();
                        const sid = e.features[0].properties.stop_id;
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
                    });
                    map.on("mouseenter", "stops-static", (e) => {
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
                    map.on("mouseleave", "stops-static", () => {
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

    window.initStaticStopMap = initStaticStopMap;
})();
