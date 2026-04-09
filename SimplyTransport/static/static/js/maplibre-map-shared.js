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

	/** Route number drawn on top of the vehicle icon (lighter halo than stop badges). */
	const VEHICLE_INLINE_LABEL_PAINT = {
		"text-color": "#ffffff",
		"text-halo-color": "rgba(17,24,39,0.75)",
		"text-halo-width": 1.25,
		"text-halo-blur": 0.35,
	};

	const STOP_LABEL_MIN_ZOOM = 15;
	/** Ems: route number centered on the vehicle icon anchor (same point as the chevron). */
	const VEHICLE_INLINE_LABEL_OFFSET = [0, 0];
	const STOP_LABEL_TEXT_OFFSET = [0, 1.65];

	/** Shared image id for mono-marker.svg (focus stop, user location). */
	const MONO_MARKER_IMAGE_ID = "mono-marker";
	const MONO_MARKER_IMAGE_URL = "/static/mono-marker.svg";

	/** Baseline layout icon-size for solid vehicle chevrons. */
	const VEHICLE_MAIN_ICON_SIZE = 0.64;

	/** Show pulse only if `time_of_update` is newer than this (ms). */
	const VEHICLE_PULSE_MAX_AGE_MS = 180_000;

	/**
	 * @param {string | null | undefined} timeOfUpdate — ISO datetime from API
	 * @returns {boolean}
	 */
	function vehiclePulseIsActive(timeOfUpdate) {
		if (timeOfUpdate == null || timeOfUpdate === "") {
			return false;
		}
		const ms = new Date(timeOfUpdate).getTime();
		if (Number.isNaN(ms)) {
			return false;
		}
		return Date.now() - ms < VEHICLE_PULSE_MAX_AGE_MS;
	}

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

	/**
	 * Rasterize mono-marker.svg to ImageData. MapLibre's loadImage often fails on SVG
	 * (InvalidStateError: The source image could not be decoded) when uploading to WebGL.
	 */
	function drawImageToMarkerImageData(img, size, callback) {
		try {
			const canvas = document.createElement("canvas");
			canvas.width = size;
			canvas.height = size;
			const ctx = canvas.getContext("2d");
			if (!ctx) {
				callback(null);
				return;
			}
			ctx.drawImage(img, 0, 0, size, size);
			callback(ctx.getImageData(0, 0, size, size));
		} catch (_e) {
			callback(null);
		}
	}

	function rasterizeMonoMarkerForMap(callback) {
		const size = 128;
		const img = new Image();
		img.onload = function () {
			drawImageToMarkerImageData(img, size, callback);
		};
		img.onerror = function () {
			if (!global.fetch) {
				callback(null);
				return;
			}
			fetch(MONO_MARKER_IMAGE_URL)
				.then((r) => {
					if (!r.ok) {
						throw new Error("fetch failed");
					}
					return r.blob();
				})
				.then((blob) => {
					const objectUrl = URL.createObjectURL(blob);
					const img2 = new Image();
					img2.onload = function () {
						drawImageToMarkerImageData(img2, size, (data) => {
							URL.revokeObjectURL(objectUrl);
							callback(data);
						});
					};
					img2.onerror = function () {
						URL.revokeObjectURL(objectUrl);
						callback(null);
					};
					img2.src = objectUrl;
				})
				.catch(() => {
					callback(null);
				});
		};
		img.src = MONO_MARKER_IMAGE_URL;
	}

	/**
	 * @param {*} map — MapLibre map instance
	 * @param {(ok: boolean) => void} onDone — ok true if image registered
	 */
	function loadMonoMarkerImage(map, onDone) {
		if (map.hasImage(MONO_MARKER_IMAGE_ID)) {
			onDone(true);
			return;
		}
		rasterizeMonoMarkerForMap((imageData) => {
			if (!imageData) {
				onDone(false);
				return;
			}
			if (!map.hasImage(MONO_MARKER_IMAGE_ID)) {
				map.addImage(MONO_MARKER_IMAGE_ID, imageData);
			}
			onDone(true);
		});
	}

	/**
	 * @param {string | number} routeId
	 * @returns {string}
	 */
	function sanitizeRouteIdForImageKey(routeId) {
		return String(routeId).replace(/[^a-zA-Z0-9_-]/g, "_");
	}

	/**
	 * Draw a route-colored chevron (rounded body + triangle) pointing east; returns ImageData for MapLibre.
	 * @param {string} fillColor — hex or css color
	 * @returns {ImageData}
	 */
	function createVehicleChevronImageData(fillColor) {
		const size = 64;
		const canvas = document.createElement("canvas");
		canvas.width = size;
		canvas.height = size;
		const ctx = canvas.getContext("2d");
		if (!ctx) {
			throw new Error("2d context unavailable");
		}
		ctx.clearRect(0, 0, size, size);

		/* Rectangle body (2× prior 26px width) + short triangle. */
		const bodyX = 4;
		const bodyY = 16;
		const bodyW = 52;
		const bodyH = 30;
		const br = 6;
		const tipX = 65;
		const midY = size / 2;

		function fillRoundBody() {
			ctx.beginPath();
			if (typeof ctx.roundRect === "function") {
				ctx.roundRect(bodyX, bodyY, bodyW, bodyH, br);
			} else {
				ctx.rect(bodyX, bodyY, bodyW, bodyH);
			}
		}

		const baseLeft = bodyX + bodyW;
		const triInset = 5;

		ctx.fillStyle = fillColor;
		fillRoundBody();
		ctx.fill();

		ctx.beginPath();
		ctx.moveTo(baseLeft, bodyY + triInset);
		ctx.lineTo(tipX, midY);
		ctx.lineTo(baseLeft, bodyY + bodyH - triInset);
		ctx.closePath();
		ctx.fill();

		ctx.strokeStyle = "#ffffff";
		ctx.lineWidth = 2.5;
		ctx.lineJoin = "round";
		ctx.lineCap = "round";
		fillRoundBody();
		ctx.stroke();
		ctx.beginPath();
		ctx.moveTo(baseLeft, bodyY + triInset);
		ctx.lineTo(tipX, midY);
		ctx.lineTo(baseLeft, bodyY + bodyH - triInset);
		ctx.stroke();

		return ctx.getImageData(0, 0, size, size);
	}

	/**
	 * Register a chevron bitmap for this route id + color (idempotent per map).
	 * @returns {string} MapLibre image id
	 */
	function registerVehicleIconForRoute(map, routeId, color) {
		const key = sanitizeRouteIdForImageKey(routeId);
		const id = `vehicle-icon-${key}`;
		if (map.hasImage(id)) {
			return id;
		}
		const imageData = createVehicleChevronImageData(color);
		map.addImage(id, imageData);
		return id;
	}

	/**
	 * Animates vehicle pulse layers: blurred circle (circle-blur) uses radius + opacity wave.
	 */
	function startVehiclePulseAnimation(map, getPulseLayerIds) {
		let raf = 0;
		function tick() {
			const wave = Math.sin((Date.now() / 2000) * Math.PI * 2) * 0.5 + 0.5;
			const opacity = 0.22 + wave * 0.38;
			const radius = 11 + wave * 10;
			for (const lid of getPulseLayerIds()) {
				const layer = map.getLayer(lid);
				if (!layer || layer.type !== "circle") {
					continue;
				}
				map.setPaintProperty(lid, "circle-opacity", opacity);
				map.setPaintProperty(lid, "circle-radius", radius);
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
		VEHICLE_INLINE_LABEL_PAINT,
		STOP_LABEL_MIN_ZOOM,
		VEHICLE_INLINE_LABEL_OFFSET,
		STOP_LABEL_TEXT_OFFSET,
		MONO_MARKER_IMAGE_ID,
		MONO_MARKER_IMAGE_URL,
		VEHICLE_MAIN_ICON_SIZE,
		VEHICLE_PULSE_MAX_AGE_MS,
		vehiclePulseIsActive,
		addDefaultMapControls,
		setLayerVisibility,
		loadMonoMarkerImage,
		sanitizeRouteIdForImageKey,
		registerVehicleIconForRoute,
		startVehiclePulseAnimation,
	};
})(window);
