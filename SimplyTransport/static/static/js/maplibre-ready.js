/**
 * MapLibre is loaded with defer in base.html. Parser-inserted scripts in the body
 * can run before the deferred bundle, so window.maplibregl may be undefined.
 */
(function (global) {
	"use strict";

	function whenMapLibreReady(callback) {
		if (typeof callback !== "function") {
			return;
		}
		var done = false;
		function invoke() {
			if (done) {
				return;
			}
			if (!global.maplibregl) {
				return;
			}
			done = true;
			callback();
		}
		if (global.maplibregl) {
			invoke();
			return;
		}
		function scheduleRaf() {
			var n = 0;
			function tick() {
				if (global.maplibregl) {
					invoke();
					return;
				}
				n += 1;
				if (n > 300) {
					return;
				}
				requestAnimationFrame(tick);
			}
			requestAnimationFrame(tick);
		}
		function onParsingDone() {
			if (global.maplibregl) {
				invoke();
				return;
			}
			scheduleRaf();
		}
		if (global.document.readyState === "loading") {
			global.document.addEventListener("DOMContentLoaded", onParsingDone);
		} else {
			onParsingDone();
		}
		global.addEventListener("load", function () {
			if (global.maplibregl) {
				invoke();
				return;
			}
			scheduleRaf();
		});
	}

	function whenStopMapPopupReady(callback) {
		if (typeof callback !== "function") {
			return;
		}
		var done = false;
		function invoke() {
			if (done) {
				return;
			}
			if (!global.StopMapPopup) {
				return;
			}
			done = true;
			callback();
		}
		if (global.StopMapPopup) {
			invoke();
			return;
		}
		var n = 0;
		function tick() {
			if (global.StopMapPopup) {
				invoke();
				return;
			}
			n += 1;
			if (n > 120) {
				return;
			}
			requestAnimationFrame(tick);
		}
		requestAnimationFrame(tick);
	}

	function whenMapWithPopupReady(callback) {
		whenMapLibreReady(function () {
			whenStopMapPopupReady(callback);
		});
	}

	global.whenMapLibreReady = whenMapLibreReady;
	global.whenStopMapPopupReady = whenStopMapPopupReady;
	global.whenMapWithPopupReady = whenMapWithPopupReady;
})(window);
