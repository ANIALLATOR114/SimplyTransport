/**
 * MapLibre stop map: loads /api/v1/map/stop/{id} and renders routes, vehicles, stops.
 * Depends on global maplibregl (loaded from CDN before this script).
 */
(function () {
	"use strict";

	/** Vehicle route labels appear first; stop codes require zooming in one step further. */
	/** Match fonts bundled at demotiles.maplibre.org (see MapLibre demo style). */
	const VEHICLE_LABEL_MIN_ZOOM = 14;
	const STOP_LABEL_MIN_ZOOM = 15;
	const LABEL_FONT = ["Open Sans Semibold"];
	/** Matches --bg-color-bump-border in style.css. MapLibre has no text-background; thick blurred halo ≈ rounded pill. */
	const MAP_LABEL_BADGE_PAINT = {
		"text-color": "#ffffff",
		"text-halo-color": "#313b46",
		"text-halo-width": 3.5,
		"text-halo-blur": 0.9,
	};
	/** Ems below anchor (larger Y = label further from the point). */
	const VEHICLE_LABEL_TEXT_OFFSET = [0, 1.95];
	const STOP_LABEL_TEXT_OFFSET = [0, 1.65];

	/**
	 * Animate halo circles under vehicle markers (realtime “live” cue).
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

	/** OpenStreetMap raster tiles (same idea as classic OSM web maps). */
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
							stop_code: s.code != null && s.code !== "" ? s.code : s.stop_id,
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
				panel.className =
					"maplibre-layer-panel maplibre-layer-panel--routes-scroll";

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
							vehiclePulse: vehiclesGeojson
								? `vehicle-pulse-${route.route_id}`
								: null,
							vehicleLabel: vehiclesGeojson
								? `vehicle-label-${route.route_id}`
								: null,
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
							const pid = `vehicle-pulse-${route.route_id}`;
							map.addLayer({
								id: pid,
								type: "circle",
								source: "vehicles-src",
								filter: ["==", ["get", "route_id"], route.route_id],
								paint: {
									"circle-radius": 12,
									"circle-color": ["get", "color"],
									"circle-opacity": 0.2,
									"circle-blur": 0.35,
								},
							});
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
							map.addLayer({
								id: `vehicle-label-${route.route_id}`,
								type: "symbol",
								source: "vehicles-src",
								minzoom: VEHICLE_LABEL_MIN_ZOOM,
								filter: ["==", ["get", "route_id"], route.route_id],
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
						});
						startVehiclePulseAnimation(map, () =>
							payload.routes
								.map((r) => `vehicle-pulse-${r.route_id}`)
								.filter((id) => map.getLayer(id)),
						);
					}

					map.addLayer({
						id: "stops-labels-focus",
						type: "symbol",
						source: "stops-src",
						minzoom: STOP_LABEL_MIN_ZOOM,
						filter: ["==", ["get", "is_focus"], true],
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
					map.addLayer({
						id: "stops-labels-other",
						type: "symbol",
						source: "stops-src",
						minzoom: STOP_LABEL_MIN_ZOOM,
						filter: ["==", ["get", "is_focus"], false],
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
							const vLabelId = `vehicle-label-${route.route_id}`;
							if (!map.getLayer(vid)) {
								return;
							}
							function onVehicleClick(e) {
								popup.remove();
								const f = e.features[0];
								const p = f.properties;
								vehiclePopup
									.setLngLat(f.geometry.coordinates)
									.setHTML(window.StopMapPopup.buildVehiclePopupHtml(p))
									.addTo(map);
							}
							map.on("click", vid, onVehicleClick);
							if (map.getLayer(vLabelId)) {
								map.on("click", vLabelId, onVehicleClick);
								map.on("mouseenter", vLabelId, () => {
									map.getCanvas().style.cursor = "pointer";
								});
								map.on("mouseleave", vLabelId, () => {
									map.getCanvas().style.cursor = "";
								});
							}
							map.on("mouseenter", vid, () => {
								map.getCanvas().style.cursor = "pointer";
							});
							map.on("mouseleave", vid, () => {
								map.getCanvas().style.cursor = "";
							});
						});
					}

					[
						"stops-focus",
						"stops-other",
						"stops-labels-focus",
						"stops-labels-other",
					].forEach((layerId) => {
						map.on("click", layerId, (e) => {
							vehiclePopup.remove();
							const sid = e.features[0].properties.stop_id;
							openPopupForStopId(sid);
						});
						map.on("mouseenter", layerId, () => {
							map.getCanvas().style.cursor = "pointer";
						});
						map.on("mouseleave", layerId, () => {
							map.getCanvas().style.cursor = "";
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
					if (st.vehicle) {
						setLayerVisibility(map, st.vehicle, allOn);
					}
					if (st.vehiclePulse) {
						setLayerVisibility(map, st.vehiclePulse, allOn);
					}
					if (st.vehicleLabel) {
						setLayerVisibility(map, st.vehicleLabel, allOn);
					}
				}
			});
			setLayerVisibility(map, "stops-other", allOn);
			setLayerVisibility(map, "stops-labels-other", allOn);
			panel.querySelectorAll('input[type="checkbox"]').forEach((el) => {
				el.checked = allOn;
			});
		});
		panel.appendChild(btn);

		const scroll = document.createElement("div");
		scroll.className = "maplibre-layer-panel-scroll";
		scroll.setAttribute("role", "group");
		scroll.setAttribute("aria-label", "Map layers");

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
					if (st.vehiclePulse) {
						setLayerVisibility(map, st.vehiclePulse, vis);
					}
					if (st.vehicleLabel) {
						setLayerVisibility(map, st.vehicleLabel, vis);
					}
				}
			});
			scroll.appendChild(row);
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
			setLayerVisibility(map, "stops-labels-other", vis);
		});
		scroll.appendChild(stopsRow);
		panel.appendChild(scroll);
	}

	window.initStopMap = initStopMap;
})();
