/**
 * MapLibre route map: loads /api/v1/map/route/{id}/{direction}.
 * Depends on global maplibregl (loaded from CDN before this script).
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

    const LINE_ID = "route-line-main";
    const VEHICLE_ID = "vehicle-main";
    const STOPS_ID = "stops-all";

    function initRouteMap(routeId, direction, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !window.maplibregl || !window.StopMapPopup) {
            return;
        }

        const loader = container.parentElement
            ? container.parentElement.querySelector(".map-loader")
            : null;

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
                panel.className = "maplibre-layer-panel";

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
                    }

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

                    const tooltip = new maplibregl.Popup({
                        closeButton: false,
                        closeOnClick: false,
                        className: "maplibre-stop-tooltip",
                        anchor: "bottom",
                        offset: [0, -12],
                        maxWidth: "none",
                    });

                    function openPopupForStopId(sid) {
                        vehiclePopup.remove();
                        tooltip.remove();
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

                    if (vehiclesGeojson && map.getLayer(VEHICLE_ID)) {
                        map.on("click", VEHICLE_ID, (e) => {
                            popup.remove();
                            tooltip.remove();
                            const f = e.features[0];
                            vehiclePopup
                                .setLngLat(f.geometry.coordinates)
                                .setHTML(window.StopMapPopup.buildVehiclePopupHtml(f.properties))
                                .addTo(map);
                        });
                        map.on("mouseenter", VEHICLE_ID, (e) => {
                            map.getCanvas().style.cursor = "pointer";
                            const f = e.features[0];
                            const p = f.properties;
                            tooltip
                                .setLngLat(f.geometry.coordinates)
                                .setHTML(window.StopMapPopup.buildVehicleTooltipHtml(p))
                                .addTo(map);
                        });
                        map.on("mouseleave", VEHICLE_ID, () => {
                            map.getCanvas().style.cursor = "";
                            tooltip.remove();
                        });
                    }

                    map.on("click", STOPS_ID, (e) => {
                        vehiclePopup.remove();
                        const sid = e.features[0].properties.stop_id;
                        openPopupForStopId(sid);
                    });
                    map.on("mouseenter", STOPS_ID, (e) => {
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
                    map.on("mouseleave", STOPS_ID, () => {
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

    function setLayerVisibility(map, id, visible) {
        if (!map.getLayer(id)) {
            return;
        }
        map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
    }

    function buildRouteLayerPanel(panel, map, route, hasVehicles) {
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
        panel.appendChild(lineRow);

        if (hasVehicles) {
            const vehRow = document.createElement("label");
            vehRow.className = "maplibre-layer-row";
            const vehCb = document.createElement("input");
            vehCb.type = "checkbox";
            vehCb.checked = true;
            vehCb.id = "toggle-vehicles-layer";
            vehRow.appendChild(vehCb);
            vehRow.appendChild(document.createTextNode(" Vehicles"));
            vehCb.addEventListener("change", () => {
                setLayerVisibility(map, VEHICLE_ID, vehCb.checked);
            });
            panel.appendChild(vehRow);
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
            setLayerVisibility(map, STOPS_ID, stopsCb.checked);
        });
        panel.appendChild(stopsRow);

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "maplibre-toggle-all";
        btn.textContent = "Toggle all off";
        let allOn = true;
        btn.addEventListener("click", () => {
            allOn = !allOn;
            btn.textContent = allOn ? "Toggle all off" : "Toggle all on";
            setLayerVisibility(map, LINE_ID, allOn);
            if (hasVehicles) {
                setLayerVisibility(map, VEHICLE_ID, allOn);
            }
            setLayerVisibility(map, STOPS_ID, allOn);
            lineCb.checked = allOn;
            if (hasVehicles) {
                const v = panel.querySelector("#toggle-vehicles-layer");
                if (v) {
                    v.checked = allOn;
                }
            }
            stopsCb.checked = allOn;
        });
        panel.appendChild(btn);
    }

    window.initRouteMap = initRouteMap;
})();
