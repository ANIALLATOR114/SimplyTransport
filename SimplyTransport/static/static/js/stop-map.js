/**
 * MapLibre stop map: loads /api/v1/map/stop/{id} and renders routes, vehicles, stops.
 * Depends on global maplibregl (loaded from CDN before this script).
 */
(function () {
	"use strict";

	/** OpenStreetMap raster tiles (same idea as classic OSM web maps). */
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

	function initStopMap(stopId, containerId) {
		const container = document.getElementById(containerId);
		if (!container || !window.maplibregl || !window.StopMapPopup) {
			return;
		}

		const loader = container.parentElement
			? container.parentElement.querySelector(".map-loader")
			: null;

		fetch(`/api/v1/map/stop/${encodeURIComponent(stopId)}`)
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
							is_focus: s.is_focus,
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

				const layerState = {
					routes: {},
					stops: true,
				};

				const panel = document.createElement("div");
				panel.className = "maplibre-layer-panel";

				map.on("load", () => {
					map.addSource("stops-src", {
						type: "geojson",
						data: stopsGeojson,
					});

					// Paint order: route lines → stops → vehicles (top).
					payload.routes.forEach((route) => {
						const lid = `route-line-${route.route_id}`;
						const srcId = `route-src-${route.route_id}`;
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
								"line-width": 6,
								"line-opacity": 0.95,
							},
						});
						layerState.routes[route.route_id] = {
							line: lid,
							vehicle: vehiclesGeojson ? `vehicle-${route.route_id}` : null,
						};
					});

					map.addLayer({
						id: "stops-other",
						type: "circle",
						source: "stops-src",
						filter: ["==", ["get", "is_focus"], false],
						paint: {
							"circle-radius": 5,
							"circle-color": "#ffffff",
							"circle-stroke-width": 2,
							"circle-stroke-color": "#333333",
						},
					});

					map.addLayer({
						id: "stops-focus",
						type: "circle",
						source: "stops-src",
						filter: ["==", ["get", "is_focus"], true],
						paint: {
							"circle-radius": 10,
							"circle-color": "#2563eb",
							"circle-stroke-width": 2,
							"circle-stroke-color": "#ffffff",
						},
					});

					if (vehiclesGeojson) {
						map.addSource("vehicles-src", {
							type: "geojson",
							data: vehiclesGeojson,
						});
						payload.routes.forEach((route) => {
							map.addLayer({
								id: `vehicle-${route.route_id}`,
								type: "circle",
								source: "vehicles-src",
								filter: ["==", ["get", "route_id"], route.route_id],
								paint: {
									"circle-radius": 8,
									"circle-color": ["get", "color"],
									"circle-stroke-width": 2,
									"circle-stroke-color": "#111827",
								},
							});
						});
					}

					buildLayerPanel(panel, payload, layerState, map);
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
								popup.setHTML(
									P.buildPopupHtmlFromDetailed(detail, payload.direction),
								);
							})
							.catch(() => {
								popup.setHTML(P.buildErrorPopupHtml(stop));
							});
					}

					if (vehiclesGeojson) {
						payload.routes.forEach((route) => {
							const vid = `vehicle-${route.route_id}`;
							if (!map.getLayer(vid)) {
								return;
							}
							map.on("click", vid, (e) => {
								popup.remove();
								tooltip.remove();
								const f = e.features[0];
								const p = f.properties;
								vehiclePopup
									.setLngLat(f.geometry.coordinates)
									.setHTML(window.StopMapPopup.buildVehiclePopupHtml(p))
									.addTo(map);
							});
							map.on("mouseenter", vid, (e) => {
								map.getCanvas().style.cursor = "pointer";
								const f = e.features[0];
								const p = f.properties;
								tooltip
									.setLngLat(f.geometry.coordinates)
									.setHTML(window.StopMapPopup.buildVehicleTooltipHtml(p))
									.addTo(map);
							});
							map.on("mouseleave", vid, () => {
								map.getCanvas().style.cursor = "";
								tooltip.remove();
							});
						});
					}

					["stops-focus", "stops-other"].forEach((layerId) => {
						map.on("click", layerId, (e) => {
							vehiclePopup.remove();
							const sid = e.features[0].properties.stop_id;
							openPopupForStopId(sid);
						});
						map.on("mouseenter", layerId, (e) => {
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
						map.on("mouseleave", layerId, () => {
							map.getCanvas().style.cursor = "";
							tooltip.remove();
						});
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

	function buildLayerPanel(panel, payload, layerState, map) {
		const routes = payload.routes;

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
					if (st.vehicle) {
						setLayerVisibility(map, st.vehicle, vis);
					}
				}
			});
			panel.appendChild(row);
		});

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
			layerState.stops = vis;
			setLayerVisibility(map, "stops-other", vis);
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
			routes.forEach((route) => {
				const st = layerState.routes[route.route_id];
				if (st) {
					setLayerVisibility(map, st.line, allOn);
					if (st.vehicle) {
						setLayerVisibility(map, st.vehicle, allOn);
					}
				}
			});
			setLayerVisibility(map, "stops-other", allOn);
			panel.querySelectorAll('input[type="checkbox"]').forEach((el) => {
				el.checked = allOn;
			});
		});
		panel.appendChild(btn);
	}

	window.initStopMap = initStopMap;
})();
