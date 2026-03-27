/**
 * Shared helpers for map popups: GET /api/v1/stop/{id}/detailed (StopDetailed).
 * Loaded before stop-map.js, nearby-map.js, route-map.js, static-stop-map.js.
 */
(function (global) {
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

    function fetchStopDetailed(stopId) {
        return fetch(`/api/v1/stop/${encodeURIComponent(stopId)}/detailed`).then((r) => {
            if (!r.ok) {
                throw new Error("Stop details not available");
            }
            return r.json();
        });
    }

    /**
     * @param {object} detail - StopDetailed JSON
     * @param {number} directionForRouteLinks - direction segment for /realtime/route/... links
     */
    function buildPopupHtmlFromDetailed(detail, directionForRouteLinks) {
        const stop = detail.stop;
        const code = stop.code || "";
        const title = `${code} - ${stop.name}`.trim();
        const routes = detail.routes || [];
        const dir = Number.isFinite(directionForRouteLinks) ? directionForRouteLinks : 0;
        const routesHtml = routes
            .map(
                (r) =>
                    `<a href="/realtime/route/${escapeHtml(r.route_id)}/${dir}">${escapeHtml(r.short_name)}</a> — ${escapeHtml(r.long_name)}`,
            )
            .join("<br>");

        let featuresHtml = "";
        if (detail.stop_features) {
            const sf = detail.stop_features;
            featuresHtml = `<p class="map-popup-block map-popup-muted">Wheelchair accessible: ${escapeHtml(sf.wheelchair_accessible)}<br>
Bus Shelter: ${escapeHtml(sf.shelter_active)}<br>
Realtime display: ${escapeHtml(sf.rtpi_active)}</p>`;
        }

        const lat = stop.lat != null ? stop.lat : "";
        const lon = stop.lon != null ? stop.lon : "";
        let streetBlock = "";
        const streetUrl = detail.street_view_url || "";
        if (streetUrl) {
            streetBlock =
                `<a class="map-popup-link" href="${escapeHtml(streetUrl)}" target="_blank" rel="noopener noreferrer">Street view</a><br>`;
        }

        return (
            `<div class="map-popup-inner">` +
            `<h4 class="map-popup-title"><a href="/realtime/stop/${escapeHtml(stop.id)}">${escapeHtml(title)}</a></h4>` +
            `<p class="map-popup-block">` +
            streetBlock +
            `<span class="map-popup-muted">Lat: ${escapeHtml(lat)}<br>Lon: ${escapeHtml(lon)}</span></p>` +
            featuresHtml +
            `<p class="map-popup-block map-popup-routes-head"><strong>${routes.length} Routes</strong></p>` +
            `<p class="map-popup-routes">${routesHtml}</p>` +
            `</div>`
        );
    }

    /** @param {object} stop - StopMapStop from map payload */
    function buildLoadingPopupHtml(stop) {
        const code = stop.code || "";
        const title = `${code} - ${stop.name}`.trim();
        return (
            `<div class="map-popup-inner">` +
            `<h4 class="map-popup-title"><a href="/realtime/stop/${escapeHtml(stop.stop_id)}">${escapeHtml(title)}</a></h4>` +
            `<p class="map-popup-muted">Loading routes…</p>` +
            `</div>`
        );
    }

    /** @param {object} stop - StopMapStop from map payload */
    function buildErrorPopupHtml(stop) {
        const code = stop.code || "";
        const title = `${code} - ${stop.name}`.trim();
        return (
            `<div class="map-popup-inner">` +
            `<h4 class="map-popup-title"><a href="/realtime/stop/${escapeHtml(stop.stop_id)}">${escapeHtml(title)}</a></h4>` +
            `<p class="map-popup-muted">Could not load stop details.</p>` +
            `</div>`
        );
    }

    /** @param {object} stop - StopMapStop from map payload */
    function buildStopTooltipHtml(stop) {
        const code = stop.code || "";
        const title = `${code} - ${stop.name}`.trim();
        return `<div class="map-stop-tooltip-inner">${escapeHtml(title)}</div>`;
    }

    global.StopMapPopup = {
        fetchStopDetailed,
        buildPopupHtmlFromDetailed,
        buildLoadingPopupHtml,
        buildErrorPopupHtml,
        buildStopTooltipHtml,
    };
})(window);
