/**
 * MapLibre nearby stops: GET /api/v1/map/stop/nearby?latitude=&longitude=
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
        if (!container || !window.maplibregl) {
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
                        popup
                            .setLngLat([stop.lon, stop.lat])
                            .setHTML(buildStopPopupHtml(stop))
                            .addTo(map);
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
                            .setHTML(buildStopTooltipHtml(stop))
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
