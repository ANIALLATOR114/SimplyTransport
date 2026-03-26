/**
 * MapLibre static stop maps: GET /api/v1/map/stop/aggregated/{map_type}
 */
(function () {
    "use strict";

    function escapeHtml(s) {
        if (s === null || s === undefined) {
            return "";
        }
        return String(s)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function buildStopPopupHtml(stop) {
        const direction = 0;
        const code = stop.code || "";
        const title = `${code} - ${stop.name}`.trim();
        const routes = stop.routes || [];
        const routesHtml = routes
            .map(
                (r) =>
                    `<a href="/realtime/route/${escapeHtml(r.route_id)}/${direction}">${escapeHtml(r.short_name)}</a> — ${escapeHtml(r.long_name)}`,
            )
            .join("<br>");

        let featuresHtml = "";
        if (stop.stop_features) {
            const sf = stop.stop_features;
            featuresHtml = `<p class="map-popup-block map-popup-muted">Wheelchair accessible: ${escapeHtml(sf.wheelchair_accessible)}<br>
Bus Shelter: ${escapeHtml(sf.shelter_active)}<br>
Realtime display: ${escapeHtml(sf.rtpi_active)}</p>`;
        }

        return (
            `<div class="map-popup-inner">` +
            `<h4 class="map-popup-title"><a href="/realtime/stop/${escapeHtml(stop.stop_id)}">${escapeHtml(title)}</a></h4>` +
            `<p class="map-popup-block">` +
            `<a class="map-popup-link" href="${escapeHtml(stop.street_view_url)}" target="_blank" rel="noopener noreferrer">Street view</a><br>` +
            `<span class="map-popup-muted">Lat: ${escapeHtml(stop.lat)}<br>Lon: ${escapeHtml(stop.lon)}</span></p>` +
            featuresHtml +
            `<p class="map-popup-block map-popup-routes-head"><strong>${routes.length} Routes</strong></p>` +
            `<p class="map-popup-routes">${routesHtml}</p>` +
            `</div>`
        );
    }

    function buildStopTooltipHtml(stop) {
        const code = stop.code || "";
        const title = `${code} - ${stop.name}`.trim();
        return `<div class="map-stop-tooltip-inner">${escapeHtml(title)}</div>`;
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

    function initStaticStopMap(mapType, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !window.maplibregl) {
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
                        popup
                            .setLngLat([stop.lon, stop.lat])
                            .setHTML(buildStopPopupHtml(stop))
                            .addTo(map);
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
                            .setHTML(buildStopTooltipHtml(stop))
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
