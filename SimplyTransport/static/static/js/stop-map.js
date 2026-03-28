/**
 * MapLibre stop map: loads /api/v1/map/stop/{id} and renders routes, vehicles, stops.
 * Depends on global maplibregl (loaded from /static in base.html before this script).
 */
(function () {
	"use strict";

	const {
		createOsmRasterStyle,
		LABEL_FONT,
		MAP_LABEL_BADGE_PAINT,
		VEHICLE_LABEL_MIN_ZOOM,
		STOP_LABEL_MIN_ZOOM,
		VEHICLE_LABEL_TEXT_OFFSET,
		STOP_LABEL_TEXT_OFFSET,
		addDefaultMapControls,
		setLayerVisibility,
		startVehiclePulseAnimation,
	} = window.MapLibreMapShared;

	const OSM_RASTER_STYLE = createOsmRasterStyle();

	function initStopMap(stopId, containerId) {
		const container = document.getElementById(containerId);
		if (!container || !window.maplibregl || !window.StopMapPopup) {
			return;
		}

		const loader = container.parentElement
			? container.parentElement.querySelector(".map-loader")
			: null;

		const wrap = container.closest(
			".map-container--maplibre[data-stop-id]",
		);
		if (wrap && typeof wrap.__stopMapCleanup === "function") {
			wrap.__stopMapCleanup();
		}
		if (loader) {
			loader.style.removeProperty("display");
		}

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

					if (wrap) {
						wrap.__stopMapCleanup = function () {
							map.remove();
							if (panel.parentNode) {
								panel.remove();
							}
							delete wrap.__stopMapCleanup;
						};
					}
					const refBtn = document.getElementById("stop-map-refresh");
					if (refBtn) {
						refBtn.disabled = false;
						refBtn.onclick = function () {
							if (refBtn.disabled) {
								return;
							}
							refBtn.disabled = true;
							initStopMap(stopId, containerId);
						};
					}
				});
			})
			.catch(() => {
				if (loader) {
					loader.style.display = "none";
				}
				const refBtn = document.getElementById("stop-map-refresh");
				if (refBtn) {
					refBtn.disabled = false;
				}
				container.innerHTML =
					'<p class="map-error">Map could not be loaded. Try again later.</p>';
			});
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

	/**
	 * Realtime stop page map: bootstrap lives here (not in the template).
	 * HTMX body swaps do not re-fire DOMContentLoaded; map init is deferred via
	 * whenMapWithPopupReady (see /static/js/maplibre-ready.js in base.html).
	 */
	function bindStopMapRealtimeEmbed() {
		const wrap = document.querySelector(
			".map-container--maplibre[data-stop-id]",
		);
		if (!wrap || wrap.dataset.stopmapEmbedInit === "1") {
			return;
		}
		if (!window.initStopMap) {
			return;
		}
		const stopId = wrap.dataset.stopId;
		if (!stopId || !document.getElementById("map-element")) {
			return;
		}
		function doInit() {
			if (wrap.dataset.stopmapEmbedInit === "1") {
				return;
			}
			if (!window.initStopMap || !window.maplibregl || !window.StopMapPopup) {
				return;
			}
			wrap.dataset.stopmapEmbedInit = "1";
			initStopMap(stopId, "map-element");
		}
		if (window.whenMapWithPopupReady) {
			window.whenMapWithPopupReady(doInit);
		} else {
			function fallback() {
				if (wrap.dataset.stopmapEmbedInit === "1") {
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
		document.addEventListener("DOMContentLoaded", bindStopMapRealtimeEmbed);
	} else {
		bindStopMapRealtimeEmbed();
	}
	window.addEventListener("load", bindStopMapRealtimeEmbed);
	if (!window.__stopMapEmbedHtmxBound) {
		window.__stopMapEmbedHtmxBound = true;
		document.body.addEventListener("htmx:afterSwap", bindStopMapRealtimeEmbed);
		document.body.addEventListener("htmx:afterSettle", bindStopMapRealtimeEmbed);
	}
})();
