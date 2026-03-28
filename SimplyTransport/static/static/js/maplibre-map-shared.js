/**
 * Shared MapLibre map constants and helpers for stop-map, route-map, nearby-map,
 * static-stop-map, and agency-map. Loaded before those scripts.
 */
(function (global) {
	"use strict";

	function getMaplibre() {
		return global.maplibregl;
	}

	/**
	 * OpenStreetMap raster base style. Symbol layers need glyphs; line-only maps can omit them.
	 * @param {{ includeGlyphs?: boolean }} [opts]
	 */
	function createOsmRasterStyle(opts) {
		const includeGlyphs = !opts || opts.includeGlyphs !== false;
		const style = {
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
		if (includeGlyphs) {
			style.glyphs =
				"https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf";
		}
		return style;
	}

	const LABEL_FONT = ["Open Sans Semibold"];

	const MAP_LABEL_BADGE_PAINT = {
		"text-color": "#ffffff",
		"text-halo-color": "#313b46",
		"text-halo-width": 3.5,
		"text-halo-blur": 0.9,
	};

	const VEHICLE_LABEL_MIN_ZOOM = 14;
	const STOP_LABEL_MIN_ZOOM = 15;
	const VEHICLE_LABEL_TEXT_OFFSET = [0, 1.95];
	const STOP_LABEL_TEXT_OFFSET = [0, 1.65];

	function addDefaultMapControls(map) {
		const m = getMaplibre();
		if (!m) {
			return;
		}
		map.addControl(new m.NavigationControl(), "top-left");
		map.addControl(new m.FullscreenControl(), "top-left");
	}

	function setLayerVisibility(map, id, visible) {
		if (!map.getLayer(id)) {
			return;
		}
		map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
	}

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

	global.MapLibreMapShared = {
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
	};
})(window);
