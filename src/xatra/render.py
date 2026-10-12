"""
Xatra HTML Rendering Module

This module provides HTML template and JavaScript logic for rendering interactive
maps using Leaflet.js. It supports both static and dynamic maps with time-based
filtering, base layer selection, and various map elements.

The module generates self-contained HTML files that can be opened in any web browser
without requiring a web server.

If period flags are present, the map is a *dynamic* map, and there should be a slider 
at the bottom: whenever the slider passes a breakpoint year (a start or end year of any 
flag), we change the displayed map to only display the united flags active at that time. 
The labels of the flags are placed at the centroid of their geometries (at any given year), 
and both labels and notes are shown in the hover tooltips.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from jinja2 import Template

from .debug_utils import time_debug


HTML_TEMPLATE = Template(
    r"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet-control-geocoder@2.4.0/dist/Control.Geocoder.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet-search@4.0.0/dist/leaflet-search.min.css" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..700;1,400..700&family=Inter:wght@400..650&display=swap" />
    <style>
      /* ── Design tokens (override any of these in your own CSS) ── */
      :root {
        --xatra-ui-font: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        --xatra-map-font: "EB Garamond", "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
        --xatra-ink: #2f2a26;
        --xatra-muted: #6b6560;
        --xatra-water: #3a76b0;
        --xatra-water-ink: #24598c;
        --xatra-route: #7a5a3a;
        --xatra-panel-bg: rgba(255, 255, 255, 0.9);
        --xatra-panel-border: rgba(30, 25, 20, 0.08);
        --xatra-panel-shadow: 0 1px 2px rgba(20, 15, 10, 0.06), 0 8px 28px rgba(20, 15, 10, 0.14);
        --xatra-accent: #8b2f2f;
        --xatra-halo: 0 0 1px rgba(255,255,255,0.95), 0 0 2px rgba(255,255,255,0.95), 0 0 4px rgba(255,255,255,0.8), 0 0 8px rgba(255,255,255,0.45);
      }
      html, body, #map { height: 100%; margin: 0; padding: 0; }
      body { font-family: var(--xatra-ui-font); color: #1f1c19; -webkit-font-smoothing: antialiased; }
      #map { background: #dfe5e8; }
      .leaflet-container { font-family: var(--xatra-ui-font); font-size: 12px; }

      /* ── Panels ── */
      #title { position: fixed; top: calc(16px + var(--xatra-inset-top, 0px)); left: 16px; max-width: min(340px, calc(100% - 32px - var(--xatra-inset-right, 0px))); box-sizing: border-box; z-index: 1000; padding: 14px 16px 12px; background: var(--xatra-panel-bg); -webkit-backdrop-filter: blur(10px) saturate(1.3); backdrop-filter: blur(10px) saturate(1.3); border: 1px solid var(--xatra-panel-border); border-radius: 12px; box-shadow: var(--xatra-panel-shadow); font-size: 13.5px; line-height: 1.45; cursor: move; user-select: none; scrollbar-width: thin; }
      #title-content > .title-box { margin-bottom: 8px; }
      #title.dragging { opacity: 0.85; }
      #title-toggle { position: absolute; top: 6px; right: 6px; width: 24px; height: 24px; padding: 0; border: none; border-radius: 6px; background: transparent; color: var(--xatra-muted); cursor: pointer; font-size: 0; line-height: 0; }
      #title-toggle::before { content: ""; display: inline-block; width: 7px; height: 7px; border-right: 1.6px solid currentColor; border-bottom: 1.6px solid currentColor; transform: translateY(-2px) rotate(-135deg); }
      #title-toggle:hover { background: rgba(0,0,0,0.06); color: var(--xatra-ink); }
      #title.collapsed #title-toggle::before { transform: translateY(1px) rotate(45deg); }
      #title-content { padding-right: 18px; }
      #title.collapsed { padding-top: 10px; padding-bottom: 10px; }
      #title.collapsed #title-search-wrapper,
      #title.collapsed #title-content > :not(.title-box),
      #title.collapsed #title-content > .title-box ~ .title-box { display: none; }
      /* Collapsed: just the first lines of the title. */
      #title.collapsed #title-content > .title-box:not(.title-box ~ .title-box) { margin: 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
      #title.collapsed #title-content > .title-box:not(.title-box ~ .title-box) :is(h1, h2, h3) { font-size: 17px; margin: 0; }
      #title.collapsed #title-content > .title-box:not(.title-box ~ .title-box) :is(p, ul, ol, br ~ *) { display: inline; }
      #title-content > .title-box:empty { display: none; }
      #title .title-box h1, #title .title-box h2, #title .title-box h3 { font-family: var(--xatra-map-font); font-weight: 600; line-height: 1.15; margin: 0 0 6px; letter-spacing: 0.01em; }
      #title .title-box h1 { font-size: 24px; }
      #title .title-box h2 { font-size: 20px; }
      #title .title-box h3 { font-size: 17px; }
      #title .title-box p { margin: 0 0 6px; }
      #title .title-box ul, #title .title-box ol { margin: 4px 0 6px; padding-left: 18px; }
      #title a { color: var(--xatra-accent); }
      #title .xatra-credit { font-size: 11px; color: var(--xatra-muted); }
      #title .xatra-credit a { color: inherit; }
      #title input, #title select, #title button, #title textarea { cursor: auto; }
      #controls { position: fixed; bottom: 22px; left: 50%; transform: translateX(-50%); max-width: calc(100% - 32px); box-sizing: border-box; background: var(--xatra-panel-bg); -webkit-backdrop-filter: blur(10px) saturate(1.3); backdrop-filter: blur(10px) saturate(1.3); padding: 8px 14px; border: 1px solid var(--xatra-panel-border); border-radius: 999px; box-shadow: var(--xatra-panel-shadow); z-index: 1000; display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--xatra-muted); font-variant-numeric: tabular-nums; }
      #controls:has(#year) { width: min(640px, calc(100% - 32px)); }
      #controls button[id^="musicPlayPause"] { width: auto; padding: 0 12px; border-radius: 999px; }
      #controls #yearLabel { font-family: var(--xatra-map-font); font-size: 20px; font-weight: 600; color: var(--xatra-ink); min-width: 92px; text-align: center; white-space: nowrap; }
      #controls button { flex: 0 0 auto; display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; padding: 0; border: none; border-radius: 50%; background: var(--xatra-ink); color: #fff; font-size: 13px; cursor: pointer; transition: transform 0.12s ease, background 0.12s ease; }
      #controls button:hover { background: #000; transform: scale(1.06); }
      #controls input[type="range"] { flex: 1; min-width: 60px; accent-color: var(--xatra-ink); cursor: pointer; }
      #controls #startYear, #controls #endYear { white-space: nowrap; }
      #coordinate-display { margin-top: 10px; font-size: 11px; color: var(--xatra-muted); order: 9; }
      #coordinate-label { font-weight: 500; }
      #coordinates { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; color: var(--xatra-muted); }
      /* Scroll long titles inside the panel; the search row stays outside so its dropdown isn't clipped. */
      #title-content { display: flex; flex-direction: column; max-height: calc(100vh - 190px - var(--xatra-inset-top, 0px)); overflow-y: auto; scrollbar-width: thin; }
      #layer-selector { margin-top: 6px; display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--xatra-muted); }
      #layer-selector select { margin-left: 0; flex: 1; min-width: 0; font: inherit; color: var(--xatra-ink); padding: 4px 8px; border: 1px solid rgba(0,0,0,0.12); border-radius: 7px; background: rgba(255,255,255,0.8); }
      #colormap { margin-top: 10px; cursor: crosshair; }
      #colormap svg { max-width: 100%; height: auto; }
      #colormap-tooltip { position: fixed; background: #fff; border: 1px solid var(--xatra-panel-border); padding: 6px 10px; border-radius: 8px; box-shadow: var(--xatra-panel-shadow); z-index: 1001; pointer-events: none; display: none; font-size: 12.5px; }
      #colormap-tooltip .color-sample { width: 14px; height: 14px; border: 1px solid rgba(0,0,0,0.2); display: inline-block; vertical-align: middle; margin-right: 8px; border-radius: 3px; }
      #multi-tooltip { position: fixed; background: rgba(255,255,255,0.97); border: 1px solid var(--xatra-panel-border); padding: 8px 12px; border-radius: 10px; box-shadow: var(--xatra-panel-shadow); z-index: 1002; pointer-events: none; display: none; font-size: 13px; line-height: 1.4; max-width: 340px; color: var(--xatra-ink); }
      #multi-tooltip .tooltip-item { margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px solid rgba(0,0,0,0.07); }
      #multi-tooltip .tooltip-item:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
      #multi-tooltip .tooltip-type { font-weight: 600; color: var(--xatra-muted); font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2px; }
      #multi-tooltip .tooltip-content { color: var(--xatra-ink); }

      /* ── Map features ── */
      .flag { transition: fill-opacity 0.15s ease, stroke-width 0.15s ease; }
      .flag:hover { fill-opacity: 0.62; stroke-width: 2; }
      .river { stroke: var(--xatra-water); stroke-width: 1.4; stroke-opacity: 0.9; stroke-linecap: round; stroke-linejoin: round; fill: none; }
      .path { stroke: var(--xatra-route); stroke-width: 1.6; stroke-opacity: 0.9; stroke-dasharray: 6 4; stroke-linecap: round; stroke-linejoin: round; fill: none; }
      .point { background: none; }
      .point-dot { display: block; width: 100%; height: 100%; box-sizing: border-box; border-radius: 50%; background: var(--xatra-ink); border: 2px solid #fff; box-shadow: 0 0 0 1px rgba(0,0,0,0.25), 0 1px 3px rgba(0,0,0,0.3); }
      .text-label { font-family: var(--xatra-map-font); font-size: 17px; font-weight: 500; font-variant: small-caps; letter-spacing: 0.22em; color: rgba(60, 50, 42, 0.78); background: none; border: none; box-shadow: none; text-shadow: var(--xatra-halo); }
      .path-label { font-family: var(--xatra-map-font); font-size: 14px; font-style: italic; letter-spacing: 0.03em; color: var(--xatra-route); padding: 2px 6px; text-shadow: var(--xatra-halo); }
      .path-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .river-label { font-family: var(--xatra-map-font); font-size: 14px; font-style: italic; letter-spacing: 0.04em; color: var(--xatra-water-ink); padding: 2px 6px; text-shadow: var(--xatra-halo); }
      .river-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .admin-river-label { font-family: var(--xatra-map-font); font-size: 12px; font-style: italic; color: var(--xatra-water-ink); padding: 1px 4px; text-shadow: var(--xatra-halo); }
      .admin-river-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .point-label { font-family: var(--xatra-map-font); font-size: 14px; font-weight: 500; font-variant: normal; letter-spacing: 0.01em; color: var(--xatra-ink); background: none; padding: 0; border: none; text-shadow: var(--xatra-halo); }
      .point-label-container { background: none; border: none; display: flex; justify-content: flex-start; align-items: center; }
      .text-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .flag-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; pointer-events: none; }
      .flag-label { font-family: var(--xatra-map-font); font-size: calc(14px * var(--xatra-label-scale, 1)); font-weight: 600; font-variant: small-caps; letter-spacing: 0.12em; line-height: 1.1; text-align: center; color: var(--xatra-ink); background: none; border: none; box-shadow: none; white-space: nowrap; text-shadow: var(--xatra-halo); }
      .flag-label.vassal, .flag-label.province { font-weight: 500; letter-spacing: 0.08em; }
      .flag-label.xatra-label-hidden { visibility: hidden; }
      .admin { stroke: rgba(40, 35, 30, 0.55); stroke-width: 0.6; }
      .admin-river { stroke: var(--xatra-water); stroke-width: 1.1; stroke-opacity: 0.75; stroke-linecap: round; stroke-linejoin: round; fill: none; }
      .data { stroke: #fff; stroke-width: 0.5; stroke-opacity: 0.8; }

      .xatra-atlas-tiles { filter: saturate(0.72) brightness(1.04); }

      /* ── Leaflet chrome ── */
      .leaflet-top.leaflet-right { top: var(--xatra-inset-controls-top, 0px); }
      .leaflet-bar { border: none !important; border-radius: 10px !important; overflow: hidden; box-shadow: var(--xatra-panel-shadow) !important; }
      .leaflet-bar a, .leaflet-bar a:hover { width: 32px; height: 32px; line-height: 32px; color: var(--xatra-ink); background: var(--xatra-panel-bg); border-bottom-color: rgba(0,0,0,0.08); }
      .leaflet-bar a:hover { background: #fff; }
      .leaflet-control-attribution { background: rgba(255,255,255,0.65) !important; color: #6b6560; font-size: 10px; border-top-left-radius: 6px; }
      .leaflet-control-attribution a { color: #5a544f; }

      /* ── Search ── */
      #title-search-wrapper { margin-top: 10px; display: flex; flex-direction: row; gap: 6px; }
      #title-search-wrapper .leaflet-control { margin: 0; float: none; }
      #title-search-wrapper:has(.search-block:only-child) .search-block { flex-basis: 100%; }
      .search-block { display: flex; flex-direction: column; flex: 1 1 0; min-width: 0; }
      .search-block-label { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
      .search-block:empty, .search-block:has(> div:empty) { display: none; }
      /* Feature search: single row, input + button inline, don't overflow */
      #search-features-container { max-width: 100%; min-width: 0; }
      #search-features-container .leaflet-control-search { display: flex !important; flex-direction: row !important; align-items: stretch; width: 100% !important; max-width: 100%; box-sizing: border-box; background: rgba(255,255,255,0.8); border: 1px solid rgba(0,0,0,0.12); border-radius: 8px; box-shadow: none; }
      #search-features-container .leaflet-control-search label.search-input { display: none !important; }
      #search-features-container .leaflet-control-search input.search-input { display: block !important; order: 2; flex: 1 1 0 !important; min-width: 0 !important; width: 0 !important; height: 28px !important; margin: 0 !important; padding: 0 8px !important; border: none !important; background: transparent !important; font: 12.5px var(--xatra-ui-font) !important; box-sizing: border-box !important; outline: none; }
      #search-features-container .leaflet-control-search .search-button { order: 1; flex: 0 0 28px !important; background-position: 4px 4px !important; width: 28px !important; height: 28px !important; margin: 0 !important; background-color: transparent !important; opacity: 0.6; }
      #search-features-container .leaflet-control-search .search-cancel { right: 4px !important; top: 0 !important; margin: 0 !important; height: 28px !important; }
      #search-features-container .leaflet-control-search .search-tooltip { z-index: 1100; max-height: 240px; left: 0; top: 32px; width: max-content !important; min-width: 100%; max-width: 300px; box-sizing: border-box; background: #fff; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; box-shadow: var(--xatra-panel-shadow); }
      #search-features-container .leaflet-control-search .search-tooltip ul { list-style: none; margin: 0; padding: 2px 0; }
      #search-features-container .leaflet-control-search .search-tip { white-space: normal; margin: 0; padding: 6px 10px; border-radius: 0; background: #fff; border: none; border-bottom: 1px solid #f0eeec; font-size: 12.5px; color: var(--xatra-ink); }
      #search-features-container .leaflet-control-search .search-tip:last-child { border-bottom: none; }
      #search-features-container .leaflet-control-search .search-tip:hover,
      #search-features-container .leaflet-control-search .search-tip-select { background: #f6f3ef; }
      /* Map search (geocoder) */
      #search-geocoder-container { z-index: 400; max-width: 100%; min-width: 0; }
      #title-search-wrapper .leaflet-control-geocoder { width: 100%; max-width: 100%; display: flex; align-items: center; background: rgba(255,255,255,0.8); border: 1px solid rgba(0,0,0,0.12); border-radius: 8px; box-shadow: none; min-height: 30px; box-sizing: border-box; }
      #title-search-wrapper .leaflet-control-geocoder-form { display: block !important; flex: 1; min-width: 0; }
      #title-search-wrapper .leaflet-control-geocoder input { width: 100%; box-sizing: border-box; border: none; background: transparent; font: 12.5px var(--xatra-ui-font); padding: 0 6px; height: 28px; outline: none; }
      #title-search-wrapper .leaflet-control-geocoder-icon { width: 28px; height: 28px; flex: 0 0 28px; background-color: transparent; opacity: 0.6; border-radius: 8px; }
      @media (max-width: 600px) {
        #title { top: calc(10px + var(--xatra-inset-top, 0px)); left: 10px; max-width: calc(100% - 64px - var(--xatra-inset-right, 0px)); padding: 10px 12px; font-size: 12.5px; }
        #controls { bottom: 14px; }
        #controls #startYear, #controls #endYear { display: none; }
      }
      {{ css }}
    </style>
  </head>
  <body>
    <div id="map"></div>
    <div id="title">
      <button id="title-toggle" type="button" aria-expanded="true" title="Hide details" aria-label="Hide details"></button>
      <div id="title-content"></div>
      <div id="title-search-wrapper"><div class="search-block"><label class="search-block-label">Feature search</label><div id="search-features-container"></div></div><div class="search-block"><label class="search-block-label">Map search</label><div id="search-geocoder-container"></div></div></div>
    </div>
    <div id="colormap-tooltip"></div>
    <div id="multi-tooltip"></div>
    <div id="controls"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-control-geocoder@2.4.0/dist/Control.Geocoder.js"></script>
    <script src="https://unpkg.com/leaflet-search@4.0.0/dist/leaflet-search.min.js"></script>
    <script>
      const payload = {{ payload | safe }};
      const geometryRegistry = payload.geometry_registry || {};

      // Hydration helper to resolve geometry from geom_id
      function resolveGeometry(item) {
        if (!item) return null;
        if (item.geometry) return item.geometry;
        if (item.geom_id && geometryRegistry[item.geom_id]) {
          return geometryRegistry[item.geom_id];
        }
        return null;
      }

      const initialFocus = payload.initial_focus || [22, 79];
      const initialZoom = payload.initial_zoom || 4;
      const map = L.map('map', { zoomControl: false }).setView(initialFocus, initialZoom);
      L.control.zoom({ position: 'topright' }).addTo(map);
      
      // Function to initialize coordinate display
      function initializeCoordinateDisplay() {
        const coordinateElement = document.getElementById('coordinates');
        if (coordinateElement) {
          const center = map.getCenter();
          coordinateElement.textContent = `${center.lat.toFixed(4)}, ${center.lng.toFixed(4)}`;
        }
      }
      
      // Add map click event handler
      map.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        const coordinateElement = document.getElementById('coordinates');
        const coordinateLabel = document.getElementById('coordinate-label');
        if (coordinateElement && coordinateLabel) {
          coordinateElement.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
          coordinateLabel.textContent = 'Clicked point: ';
        }
        
        if (window.parent) {
            window.parent.postMessage({
                type: 'mapClick',
                lat: lat,
                lng: lng
            }, '*');
        }
      });
      
      map.on('mousedown', function(e) {
          if ((e.originalEvent && (e.originalEvent.ctrlKey || e.originalEvent.metaKey)) && map && map.dragging) {
              map.dragging.disable();
          }
          if (window.parent) {
              window.parent.postMessage({
                  type: 'mapMouseDown',
                  lat: e.latlng.lat,
                  lng: e.latlng.lng,
                  ctrlKey: !!(e.originalEvent && e.originalEvent.ctrlKey),
                  metaKey: !!(e.originalEvent && e.originalEvent.metaKey),
                  shiftKey: !!(e.originalEvent && e.originalEvent.shiftKey),
              }, '*');
          }
      });
      
      map.on('mousemove', function(e) {
          updateMultiTooltip(e);
          if (map && map.dragging) {
              const modifierHeld = !!(e.originalEvent && (e.originalEvent.ctrlKey || e.originalEvent.metaKey));
              if (modifierHeld && map.dragging.enabled()) map.dragging.disable();
              if (!modifierHeld && !map.dragging.enabled()) map.dragging.enable();
          }
          if (window.parent) {
              window.parent.postMessage({
                  type: 'mapMouseMove',
                  lat: e.latlng.lat,
                  lng: e.latlng.lng,
                  ctrlKey: !!(e.originalEvent && e.originalEvent.ctrlKey),
                  metaKey: !!(e.originalEvent && e.originalEvent.metaKey),
                  shiftKey: !!(e.originalEvent && e.originalEvent.shiftKey),
              }, '*');
          }
      });
      
      map.on('mouseup', function(e) {
          if (map && map.dragging && !map.dragging.enabled()) {
              map.dragging.enable();
          }
          if (window.parent) {
              window.parent.postMessage({
                  type: 'mapMouseUp',
                  lat: e.latlng.lat,
                  lng: e.latlng.lng,
                  ctrlKey: !!(e.originalEvent && e.originalEvent.ctrlKey),
                  metaKey: !!(e.originalEvent && e.originalEvent.metaKey),
                  shiftKey: !!(e.originalEvent && e.originalEvent.shiftKey),
              }, '*');
          }
      });
      
      // Debug mode - set to true to show centroid markers
      const DEBUG_CENTROIDS = false;
      
      // Performance optimization: cache centroids and label styles
      const centroidCache = new Map();
      const labelStyleCache = new Map();
      
      // Base layer management
      const baseLayers = {};
      let currentBaseLayer = null;
      
      // Create base layers
      for (const option of payload.base_options || []) {
        const layerOptions = {
          maxZoom: 18,
          attribution: '&copy; ' + option.name,
          ...(option.options || {}),
        };
        // Providers with limited native zoom are upscaled instead of going blank.
        if (layerOptions.maxNativeZoom === undefined && layerOptions.maxZoom < 18) {
          layerOptions.maxNativeZoom = layerOptions.maxZoom;
          layerOptions.maxZoom = 18;
        }

        const layer = L.tileLayer(option.url, layerOptions);
        baseLayers[option.name] = layer;
      }
      
      // Find default layer - prioritize the one marked as default=True
      const defaultOption = payload.base_options?.find(opt => opt.default === true);
      if (defaultOption) {
        currentBaseLayer = baseLayers[defaultOption.name];
        currentBaseLayer.addTo(map);
      }

      const layers = { flags: [], rivers: [], paths: [], points: [], texts: [], title_boxes: [], admins: [], admin_rivers: [], data: [], dataframes: [] };
      
      // Layer visibility management for dynamic maps
      const layerVisibility = new Map(); // Maps layer objects to their visibility state
      let allLayersCreated = false;

      // Legacy function - no longer used, kept for compatibility
      function addGeoJSON(geojson, options, tooltip) {
        const layer = L.geoJSON(geojson, options);
        // Old tooltip system removed - now using multi-layer tooltips
        layer.addTo(map);
        return layer;
      }

      function filterByPeriod(items, year) {
        return items.filter(item => {
          const period = item.period;
          if (period === null || period === undefined) {
            return true; // No period means always visible
          }
          const start = period[0];
          const end = period[1];
          return year >= start && year < end;
        });
      }

      function setLayerVisibility(layer, visible) {
        if (visible) {
          if (!map.hasLayer(layer)) {
            layer.addTo(map);
          }
        } else {
          if (map.hasLayer(layer)) {
            map.removeLayer(layer);
          }
        }
        layerVisibility.set(layer, visible);
      }

      function isLayerVisible(layer) {
        return layerVisibility.get(layer) || false;
      }

      // Multi-layer tooltip system
      // Maps layer objects to their tooltip metadata: { type: string, content: string, hover_radius: number }
      const layerTooltips = new Map();
      const multiTooltipDiv = document.getElementById('multi-tooltip');
      let lastMouseEvent = null;
      
      // Register a layer with tooltip content and optional hover radius
      function registerLayerTooltip(layer, type, content, hoverRadiusPixels) {
        if (content) {
          layerTooltips.set(layer, { 
            type: type, 
            content: content,
            hover_radius: hoverRadiusPixels // in pixels, will be converted to meters when needed
          });
        }
      }
      
      // Convert pixel distance to meters at the current map center
      function pixelsToMeters(pixels) {
        const zoom = map.getZoom();
        const centerLat = map.getCenter().lat;
        
        // Meters per pixel at this zoom level and latitude
        // At zoom level 0, there are 256 pixels for the entire world (256 * 256 tile)
        // At the equator, the circumference is ~40,075,000 meters
        const metersPerPixelAtEquator = 40075000 / (256 * Math.pow(2, zoom));
        
        // Adjust for latitude (Mercator projection)
        const metersPerPixel = metersPerPixelAtEquator / Math.cos(centerLat * Math.PI / 180);
        
        return pixels * metersPerPixel;
      }
      
      // Check if a point is inside a layer's geometry
      function layerContainsPoint(layer, latlng) {
        if (!layer || !latlng) return false;
        
        // Check bounding box first for performance
        if (layer.getBounds && !layer.getBounds().contains(latlng)) {
          return false;
        }
        
        // Get hover radius from layer metadata (if available)
        const tooltipData = layerTooltips.get(layer);
        const hoverRadiusPixels = tooltipData?.hover_radius;
        
        // Handle Polygon/MultiPolygon layers (individual features from GeoJSON)
        if (layer instanceof L.Polygon) {
          // Use precise point-in-polygon test with ray casting
          const latlngs = layer.getLatLngs();
          return pointInPolygon(latlng, latlngs);
        }
        
        // Handle Path/Polyline layers (rivers, paths, individual line features)
        if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {
          // For lines, check if point is close to any segment
          const latlngs = layer.getLatLngs();
          
          // Use custom hover radius if available, otherwise default to 10 pixels
          const radiusPixels = hoverRadiusPixels !== undefined ? hoverRadiusPixels : 10;
          const maxDistanceMeters = pixelsToMeters(radiusPixels);
          
          // Handle both LineString (flat array) and MultiLineString (array of arrays)
          const lineStrings = Array.isArray(latlngs[0]) ? latlngs : [latlngs];
          
          for (const lineString of lineStrings) {
            for (let i = 0; i < lineString.length - 1; i++) {
              // Check distance to this line segment
              const dist = distanceToLineSegmentLatLng(latlng, lineString[i], lineString[i + 1]);
              if (dist < maxDistanceMeters) {
                return true;
              }
            }
          }
          return false;
        }
        
        // Handle Marker layers (points)
        if (layer instanceof L.Marker) {
          const markerLatLng = layer.getLatLng();
          const distance = map.distance(latlng, markerLatLng);
          
          // Use custom hover radius if available, otherwise default to 20 pixels
          const radiusPixels = hoverRadiusPixels !== undefined ? hoverRadiusPixels : 20;
          const maxDistanceMeters = pixelsToMeters(radiusPixels);
          
          return distance < maxDistanceMeters;
        }
        
        // Handle parent GeoJSON layers (should rarely be called now, but kept for compatibility)
        if (layer instanceof L.GeoJSON) {
          let contains = false;
          layer.eachLayer(function(subLayer) {
            if (layerContainsPoint(subLayer, latlng)) {
              contains = true;
            }
          });
          return contains;
        }
        
        return false;
      }
      
      // Point-in-polygon test using ray casting algorithm
      function pointInPolygon(point, polygonLatlngs) {
        // Handle different polygon structures that Leaflet returns
        // Simple polygon: [{lat, lng}, {lat, lng}, ...]
        // Polygon with holes: [[{lat, lng}, ...], [{lat, lng}, ...]]
        // MultiPolygon: [[[{lat, lng}, ...]], [[{lat, lng}, ...]]]
        
        if (!polygonLatlngs || polygonLatlngs.length === 0) return false;
        
        // Check if it's a simple array of LatLng objects
        if (polygonLatlngs[0].lat !== undefined && polygonLatlngs[0].lng !== undefined) {
          // Simple polygon: [{lat, lng}, {lat, lng}, ...]
          return raycast(point, polygonLatlngs);
        }
        
        // Check if it's a polygon with holes (array of rings)
        if (Array.isArray(polygonLatlngs[0])) {
          if (polygonLatlngs[0].length > 0 && polygonLatlngs[0][0].lat !== undefined) {
            // Polygon with holes: [[exterior ring], [hole1], [hole2], ...]
            // Point must be in exterior ring but not in any holes
            const inExterior = raycast(point, polygonLatlngs[0]);
            if (!inExterior) return false;
            
            // Check holes (if any)
            for (let i = 1; i < polygonLatlngs.length; i++) {
              if (raycast(point, polygonLatlngs[i])) {
                return false; // Point is in a hole
              }
            }
            return true;
          }
          
          // MultiPolygon: [[[{lat, lng}, ...]], [[{lat, lng}, ...]]]
          if (Array.isArray(polygonLatlngs[0][0])) {
            for (const polygon of polygonLatlngs) {
              if (pointInPolygon(point, polygon)) {
                return true;
              }
            }
            return false;
          }
        }
        
        return false;
      }
      
      // Ray casting algorithm for point-in-polygon test
      function raycast(point, ring) {
        if (!ring || ring.length < 3) return false;
        
        let inside = false;
        const x = point.lng;
        const y = point.lat;
        
        for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
          const xi = ring[i].lng;
          const yi = ring[i].lat;
          const xj = ring[j].lng;
          const yj = ring[j].lat;
          
          const intersect = ((yi > y) !== (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
          
          if (intersect) inside = !inside;
        }
        
        return inside;
      }
      
      // Distance from point to line segment (in meters)
      function distanceToLineSegmentLatLng(point, lineStart, lineEnd) {
        // Project point onto line segment
        const x0 = point.lat;
        const y0 = point.lng;
        const x1 = lineStart.lat;
        const y1 = lineStart.lng;
        const x2 = lineEnd.lat;
        const y2 = lineEnd.lng;
        
        const dx = x2 - x1;
        const dy = y2 - y1;
        
        if (dx === 0 && dy === 0) {
          // Line segment is a point
          return map.distance(point, lineStart);
        }
        
        // Calculate projection parameter
        const t = Math.max(0, Math.min(1, ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)));
        
        // Calculate nearest point on segment
        const nearestLat = x1 + t * dx;
        const nearestLng = y1 + t * dy;
        const nearestPoint = L.latLng(nearestLat, nearestLng);
        
        // Return distance in meters
        return map.distance(point, nearestPoint);
      }
      
      // Distance from point to line segment
      function distanceToSegment(p, v, w) {
        const l2 = Math.pow(v.x - w.x, 2) + Math.pow(v.y - w.y, 2);
        if (l2 === 0) return Math.sqrt(Math.pow(p.x - v.x, 2) + Math.pow(p.y - v.y, 2));
        let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
        t = Math.max(0, Math.min(1, t));
        const projX = v.x + t * (w.x - v.x);
        const projY = v.y + t * (w.y - v.y);
        return Math.sqrt(Math.pow(p.x - projX, 2) + Math.pow(p.y - projY, 2));
      }
      
      // Find all layers at a given point
      function getLayersAtPoint(latlng) {
        const foundLayers = [];
        
        // Check all layer types
        for (const layerType of Object.keys(layers)) {
          for (const layer of layers[layerType]) {
            // Skip if layer is not visible
            if (!map.hasLayer(layer)) continue;
            
            // For GeoJSON layers (admins, admin_rivers, data, dataframes), check sublayers
            if (layer instanceof L.GeoJSON) {
              layer.eachLayer(function(subLayer) {
                // Check if this sublayer has tooltip metadata
                if (layerTooltips.has(subLayer)) {
                  // Check if point is inside this sublayer
                  if (layerContainsPoint(subLayer, latlng)) {
                    foundLayers.push(subLayer);
                  }
                }
              });
            } else {
              // For simple layers (flags, rivers, paths, points), check directly
              if (layerTooltips.has(layer)) {
                if (layerContainsPoint(layer, latlng)) {
                  foundLayers.push(layer);
                }
              }
            }
          }
        }
        
        return foundLayers;
      }
      
      // Update multi-tooltip display
      function updateMultiTooltip(e) {
        if (!e) return;
        
        lastMouseEvent = e;
        const latlng = e.latlng;
        const foundLayers = getLayersAtPoint(latlng);
        
        if (foundLayers.length === 0) {
          multiTooltipDiv.style.display = 'none';
          return;
        }
        
        // Build tooltip HTML
        let html = '';
        for (let i = 0; i < foundLayers.length; i++) {
          const layer = foundLayers[i];
          const tooltipData = layerTooltips.get(layer);
          if (tooltipData && tooltipData.content) {
            html += '<div class="tooltip-item">';
            html += `<div class="tooltip-type">${tooltipData.type}</div>`;
            html += `<div class="tooltip-content">${tooltipData.content}</div>`;
            html += '</div>';
          }
        }
        
        if (html) {
          multiTooltipDiv.innerHTML = html;
          multiTooltipDiv.style.display = 'block';
          multiTooltipDiv.style.left = (e.containerPoint.x + 15) + 'px';
          multiTooltipDiv.style.top = (e.containerPoint.y + 15) + 'px';
        } else {
          multiTooltipDiv.style.display = 'none';
        }
      }
      
      // Hide tooltip when mouse leaves map
      map.on('mouseout', function() {
        multiTooltipDiv.style.display = 'none';
      });
      
      // Update tooltip on mousemove
      map.on('mousemove', updateMultiTooltip);

      // Listener for parent window messages (Studio integration)
      let draftLayer = null;
      const highlightedLayers = new Map();
      const highlightedLabelLayers = new Map();
      function normalizeGadmCode(code) {
        if (!code || typeof code !== 'string') return '';
        return code.replace(/_\d+$/, '');
      }
      function getFeatureGidFromProps(props) {
        if (!props) return '';
        return normalizeGadmCode(props.GID_3 || props.GID_2 || props.GID_1 || props.GID_0 || '');
      }
      function resetSelectionOverlay() {
        highlightedLayers.forEach((original, layer) => {
          if (!layer || !layer.setStyle) return;
          layer.setStyle(original);
        });
        highlightedLayers.clear();
      }
      function applySelectionOverlay(groups) {
        resetSelectionOverlay();
        if (!Array.isArray(groups) || groups.length === 0) return;
        const styles = {
          union: { color: '#16a34a', fillColor: '#16a34a', fillOpacity: 0.2, weight: 3 },
          difference: { color: '#e11d48', fillColor: '#e11d48', fillOpacity: 0.2, weight: 3 },
          intersection: { color: '#4f46e5', fillColor: '#4f46e5', fillOpacity: 0.2, weight: 3 },
          pending: { color: '#0ea5e9', fillColor: '#0ea5e9', fillOpacity: 0.2, weight: 3, dashArray: '6,6' },
        };
        const gidToStyle = new Map();
        groups.forEach((group) => {
          const op = (group && group.op) ? String(group.op) : 'pending';
          const style = styles[op] || styles.pending;
          (group && Array.isArray(group.gids) ? group.gids : []).forEach((gid) => {
            gidToStyle.set(normalizeGadmCode(gid), style);
          });
        });
        if (gidToStyle.size === 0) return;
        layers.admins.forEach((adminLayer) => {
          if (!adminLayer || !adminLayer.eachLayer) return;
          adminLayer.eachLayer((subLayer) => {
            const props = subLayer?.feature?.properties || {};
            const gid = getFeatureGidFromProps(props);
            if (!gid || !gidToStyle.has(gid) || !subLayer.setStyle) return;
            if (!highlightedLayers.has(subLayer)) {
              highlightedLayers.set(subLayer, {
                color: subLayer.options?.color,
                fillColor: subLayer.options?.fillColor,
                fillOpacity: subLayer.options?.fillOpacity,
                weight: subLayer.options?.weight,
                dashArray: subLayer.options?.dashArray,
              });
            }
            subLayer.setStyle(gidToStyle.get(gid));
          });
        });
      }
      function resetLabelSelectionOverlay() {
        highlightedLabelLayers.forEach((original, layer) => {
          if (!layer) return;
          if (layer.setStyle && original.style) {
            layer.setStyle(original.style);
          }
          if (typeof layer.setOpacity === 'function' && original.opacity != null) {
            layer.setOpacity(original.opacity);
          }
        });
        highlightedLabelLayers.clear();
      }
      function applyLabelSelectionOverlay(groups) {
        resetLabelSelectionOverlay();
        if (!Array.isArray(groups) || groups.length === 0) return;
        const styles = {
          union: { color: '#16a34a', fillColor: '#16a34a', fillOpacity: 0.2, weight: 3, opacity: 1.0 },
          difference: { color: '#e11d48', fillColor: '#e11d48', fillOpacity: 0.2, weight: 3, opacity: 1.0 },
          intersection: { color: '#4f46e5', fillColor: '#4f46e5', fillOpacity: 0.2, weight: 3, opacity: 1.0 },
          pending: { color: '#0ea5e9', fillColor: '#0ea5e9', fillOpacity: 0.2, weight: 3, opacity: 1.0 },
        };
        const labelToStyle = new Map();
        groups.forEach((group) => {
          const op = (group && group.op) ? String(group.op) : 'pending';
          const style = styles[op] || styles.pending;
          (group && Array.isArray(group.names) ? group.names : []).forEach((name) => {
            labelToStyle.set(String(name), style);
          });
        });
        if (labelToStyle.size === 0) return;
        layers.flags.forEach((layer) => {
          const label = layer?._flagData?.label;
          if (!label || !labelToStyle.has(label)) return;
          const style = labelToStyle.get(label);
          if (layer.setStyle) {
            if (!highlightedLabelLayers.has(layer)) {
              highlightedLabelLayers.set(layer, {
                style: {
                  color: layer.options?.color,
                  fillColor: layer.options?.fillColor,
                  fillOpacity: layer.options?.fillOpacity,
                  weight: layer.options?.weight,
                  dashArray: layer.options?.dashArray,
                },
                opacity: null,
              });
            }
            layer.setStyle(style);
          } else if (typeof layer.setOpacity === 'function') {
            if (!highlightedLabelLayers.has(layer)) {
              highlightedLabelLayers.set(layer, {
                style: null,
                opacity: layer.options?.opacity ?? 1.0,
              });
            }
            layer.setOpacity(1.0);
          }
        });
      }
      function extractRiverIdFromProps(props) {
        if (!props) return null;
        if (props._source === 'naturalearth' && props._ne_id != null) return String(props._ne_id);
        if (props._source === 'overpass') {
          if (props._id != null) return String(props._id);
          const filename = props._filename ? String(props._filename) : '';
          const match = filename.match(/(\d+)/);
          if (match) return match[1];
        }
        return null;
      }
      // Tell an embedding page the map is listening (it may reply with setPanelInsets).
      setTimeout(function() {
        if (window.parent && window.parent !== window) window.parent.postMessage({ type: 'mapReady' }, '*');
      }, 0);
      window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'setPanelInsets') {
          // An embedding page (e.g. xatra-gui) can push the title panel down to
          // clear its own overlays: { type: 'setPanelInsets', top, right, controlsTop }
          // (pixels, or null to reset). `top`/`right` keep the title panel clear;
          // `controlsTop` moves the zoom buttons down.
          const setInset = (name, value) => {
            const px = Number(value);
            if (Number.isFinite(px) && px > 0) document.documentElement.style.setProperty(name, px + 'px');
            else document.documentElement.style.removeProperty(name);
          };
          setInset('--xatra-inset-top', event.data.top);
          setInset('--xatra-inset-controls-top', event.data.controlsTop);
          setInset('--xatra-inset-right', event.data.right);
          return;
        }
        if (event.data === 'getCurrentView') {
          const center = map.getCenter();
          const zoom = map.getZoom();
          window.parent.postMessage({
            type: 'mapViewUpdate',
            center: [center.lat, center.lng],
            zoom: zoom
          }, '*');
        } else if (event.data && event.data.type === 'setDraft') {
            if (draftLayer) { map.removeLayer(draftLayer); draftLayer = null; }
            const { points, shapeType } = event.data;
            if (!points || points.length === 0) return;
            const t = shapeType || event.data.type;
            if (t === 'point' || t === 'text') {
                const pt = points[0];
                draftLayer = L.circleMarker(Array.isArray(pt) ? pt : [pt.lat, pt.lng], { color: 'red', radius: 8, weight: 2, fillOpacity: 0.7 }).addTo(map);
            } else if (t === 'path' || t === 'polygon') {
                const latlngs = points.map(p => Array.isArray(p) ? p : [p.lat, p.lng]);
                const group = L.layerGroup();
                if (t === 'path') {
                    group.addLayer(L.polyline(latlngs, { color: '#dc2626', weight: 4, dashArray: '8, 8', opacity: 0.9 }));
                } else {
                    group.addLayer(L.polygon(latlngs, { color: '#dc2626', weight: 3, fillColor: '#dc2626', fillOpacity: 0.25, dashArray: '6, 6' }));
                }
                latlngs.forEach(function(ll) {
                    group.addLayer(L.circleMarker(ll, { color: '#dc2626', radius: 5, weight: 2, fillColor: '#fff', fillOpacity: 1 }));
                });
                draftLayer = group.addTo(map);
            }
        } else if (event.data && event.data.type === 'setSelectionOverlay') {
            applySelectionOverlay(event.data.groups || []);
        } else if (event.data && event.data.type === 'setLabelSelectionOverlay') {
            applyLabelSelectionOverlay(event.data.groups || []);
        }
      });

      // Forward key events to parent so picker shortcuts work when map iframe has focus
      document.addEventListener('keydown', function(e) {
        if (!window.parent) return;
        if ((e.ctrlKey || e.metaKey) && (e.key === ' ' || e.code === 'Space')) {
          e.preventDefault();
          window.parent.postMessage({ type: 'mapShortcut', shortcut: 'updatePickerMap' }, '*');
        }
        if ((e.key === 'Control' || e.key === 'Meta') && map && map.dragging) {
          map.dragging.disable();
        }
        if (e.key === 'Backspace' || e.key === 'Escape' || e.key === 'Control' || e.key === 'Meta') {
          e.preventDefault();
          window.parent.postMessage({ type: 'mapKeyDown', key: e.key, repeat: e.repeat === true }, '*');
        }
        // Forward modifier+key combos so global shortcuts work when the map iframe has focus
        if ((e.ctrlKey || e.metaKey) && e.key !== 'Control' && e.key !== 'Meta' && e.key !== ' ' && e.code !== 'Space') {
          e.preventDefault();
          window.parent.postMessage({
            type: 'mapKeyDown',
            key: e.key,
            ctrlKey: !!e.ctrlKey,
            metaKey: !!e.metaKey,
            shiftKey: !!e.shiftKey,
            altKey: !!e.altKey,
            repeat: e.repeat === true
          }, '*');
        }
      });
      document.addEventListener('keyup', function(e) {
        if (!window.parent) return;
        if ((e.key === 'Control' || e.key === 'Meta') && map && map.dragging) {
          map.dragging.enable();
          e.preventDefault();
          window.parent.postMessage({ type: 'mapKeyUp', key: e.key }, '*');
        }
      });
      window.addEventListener('blur', function() {
        if (map && map.dragging) {
          map.dragging.enable();
        }
        if (window.parent) {
          window.parent.postMessage({ type: 'mapKeyUp', key: 'Control' }, '*');
          window.parent.postMessage({ type: 'mapKeyUp', key: 'Meta' }, '*');
        }
      });
      document.addEventListener('visibilitychange', function() {
        if (document.hidden && map && map.dragging) {
          map.dragging.enable();
        }
      });
      document.addEventListener('keyup', function(e) {
        if (!window.parent) return;
        if (e.key === 'Backspace' || e.key === 'Escape') {
          e.preventDefault();
          window.parent.postMessage({ type: 'mapKeyUp', key: e.key }, '*');
        }
      });

      function getCentroid(geometry) {
        // Proper geometric centroid calculation
        if (geometry.type === 'Polygon') {
          const coords = geometry.coordinates[0]; // Exterior ring
          if (coords.length < 3) return [0, 0];
          
          let area = 0;
          let cx = 0, cy = 0;
          
          for (let i = 0; i < coords.length - 1; i++) {
            const x1 = coords[i][0];
            const y1 = coords[i][1];
            const x2 = coords[i + 1][0];
            const y2 = coords[i + 1][1];
            
            const cross = x1 * y2 - x2 * y1;
            area += cross;
            cx += (x1 + x2) * cross;
            cy += (y1 + y2) * cross;
          }
          
          area *= 0.5;
          if (Math.abs(area) < 1e-10) return [0, 0];
          
          cx /= (6 * area);
          cy /= (6 * area);
          
          return [cy, cx]; // [lat, lng]
        } else if (geometry.type === 'MultiPolygon') {
          // Calculate weighted centroid for all polygons
          let totalArea = 0;
          let weightedX = 0, weightedY = 0;
          
          for (const polygon of geometry.coordinates) {
            const coords = polygon[0]; // Exterior ring
            if (coords.length < 3) continue;
            
            let area = 0;
            let cx = 0, cy = 0;
            
            for (let i = 0; i < coords.length - 1; i++) {
              const x1 = coords[i][0];
              const y1 = coords[i][1];
              const x2 = coords[i + 1][0];
              const y2 = coords[i + 1][1];
              
              const cross = x1 * y2 - x2 * y1;
              area += cross;
              cx += (x1 + x2) * cross;
              cy += (y1 + y2) * cross;
            }
            
            area *= 0.5;
            if (Math.abs(area) > 1e-10) {
              cx /= (6 * area);
              cy /= (6 * area);
              
              weightedX += cx * Math.abs(area);
              weightedY += cy * Math.abs(area);
              totalArea += Math.abs(area);
            }
          }
          
          if (totalArea < 1e-10) return [0, 0];
          
          return [weightedY / totalArea, weightedX / totalArea]; // [lat, lng]
        }
        return [0, 0]; // Fallback
      }

      // Helper function to calculate river label position and rotation
      function calculateRiverLabelPosition(geometryOrFeature, label, fraction = 0.5) {
        // Handle Feature, FeatureCollection, and raw geometry
        let geometry = geometryOrFeature;
        if (geometryOrFeature.type === 'Feature' && geometryOrFeature.geometry) {
          geometry = geometryOrFeature.geometry;
        } else if (geometryOrFeature.type === 'FeatureCollection' && geometryOrFeature.features) {
          // For FeatureCollection, combine all features' geometries
          let allCoords = [];
          for (const feature of geometryOrFeature.features) {
            if (feature.geometry) {
              if (feature.geometry.type === 'LineString') {
                allCoords.push(feature.geometry.coordinates);
              } else if (feature.geometry.type === 'MultiLineString') {
                allCoords = allCoords.concat(feature.geometry.coordinates);
              }
            }
          }
          
          // If we found coordinates, proceed with the algorithm
          if (allCoords.length > 0) {
            return processCoordinates(allCoords, label, fraction);
          }
          return null;
        }
        
        // Extract all coordinates from the geometry
        let allCoords = [];
        
        if (geometry.type === 'LineString') {
          allCoords = [geometry.coordinates];
        } else if (geometry.type === 'MultiLineString') {
          allCoords = geometry.coordinates;
        } else {
          return null; // Unsupported geometry type
        }
        
        return processCoordinates(allCoords, label, fraction);
      }
      
      // Helper function to find two most distant points in a geometry
      function findDistantPoints(geometry) {
        // Extract all coordinates from the geometry
        let allCoords = [];
        
        if (geometry.type === 'FeatureCollection' && geometry.features) {
          // Handle FeatureCollection
          for (const feature of geometry.features) {
            if (feature.geometry) {
              allCoords = allCoords.concat(extractCoordinatesFromGeometry(feature.geometry));
            }
          }
        } else if (geometry.type === 'Feature' && geometry.geometry) {
          // Handle Feature
          allCoords = extractCoordinatesFromGeometry(geometry.geometry);
        } else {
          // Handle raw geometry
          allCoords = extractCoordinatesFromGeometry(geometry);
        }
        
        if (allCoords.length === 0) return null;
        
        // For performance, sample points if there are too many
        const maxSampleSize = 200;
        let sampledPoints = allCoords;
        if (allCoords.length > maxSampleSize) {
          const step = Math.floor(allCoords.length / maxSampleSize);
          sampledPoints = [];
          for (let i = 0; i < allCoords.length; i += step) {
            sampledPoints.push(allCoords[i]);
          }
          // Always include the last point
          if (sampledPoints[sampledPoints.length - 1] !== allCoords[allCoords.length - 1]) {
            sampledPoints.push(allCoords[allCoords.length - 1]);
          }
        }
        
        // Find the two most distant points
        let maxDistance = 0;
        let point1 = null;
        let point2 = null;
        
        for (let i = 0; i < sampledPoints.length; i++) {
          for (let j = i + 1; j < sampledPoints.length; j++) {
            const dist = Math.sqrt(
              Math.pow(sampledPoints[j][0] - sampledPoints[i][0], 2) +
              Math.pow(sampledPoints[j][1] - sampledPoints[i][1], 2)
            );
            if (dist > maxDistance) {
              maxDistance = dist;
              point1 = sampledPoints[i];
              point2 = sampledPoints[j];
            }
          }
        }
        
        if (!point1 || !point2) return null;
        
        // Calculate angle based on the line between the two distant points
        const dx = point2[1] - point1[1]; // longitude difference
        const dy = point2[0] - point1[0]; // latitude difference
        let angle = -Math.atan2(dy, dx) * 180 / Math.PI;
        
        // Normalize angle to keep text readable
        if (angle > 90) angle -= 180;
        if (angle < -90) angle += 180;
        
        return { point1: point1, point2: point2, angle: angle };
      }
      
      // Helper function to extract coordinates from various geometry types
      function extractCoordinatesFromGeometry(geometry) {
        let allCoords = [];
        
        switch (geometry.type) {
          case 'Point':
            allCoords.push([geometry.coordinates[1], geometry.coordinates[0]]); // [lat, lon]
            break;
          case 'LineString':
            for (const coord of geometry.coordinates) {
              allCoords.push([coord[1], coord[0]]); // Convert to [lat, lon]
            }
            break;
          case 'MultiLineString':
            for (const lineString of geometry.coordinates) {
              for (const coord of lineString) {
                allCoords.push([coord[1], coord[0]]); // Convert to [lat, lon]
              }
            }
            break;
          case 'Polygon':
            for (const ring of geometry.coordinates) {
              for (const coord of ring) {
                allCoords.push([coord[1], coord[0]]); // Convert to [lat, lon]
              }
            }
            break;
          case 'MultiPolygon':
            for (const polygon of geometry.coordinates) {
              for (const ring of polygon) {
                for (const coord of ring) {
                  allCoords.push([coord[1], coord[0]]); // Convert to [lat, lon]
                }
              }
            }
            break;
        }
        
        return allCoords;
      }
      
      // Helper function to process coordinates (extracted for reuse)
      function processCoordinates(allCoords, label, fraction) {
        
        // Collect all points from all LineStrings
        let allPoints = [];
        for (const lineString of allCoords) {
          for (const coord of lineString) {
            allPoints.push([coord[1], coord[0]]); // Convert to [lat, lon]
          }
        }
        
        if (allPoints.length === 0) return null;
        
        // For performance, sample points if there are too many
        const maxSampleSize = 200;
        let sampledPoints = allPoints;
        if (allPoints.length > maxSampleSize) {
          const step = Math.floor(allPoints.length / maxSampleSize);
          sampledPoints = [];
          for (let i = 0; i < allPoints.length; i += step) {
            sampledPoints.push(allPoints[i]);
          }
          // Always include the last point
          if (sampledPoints[sampledPoints.length - 1] !== allPoints[allPoints.length - 1]) {
            sampledPoints.push(allPoints[allPoints.length - 1]);
          }
        }
        
        // Find the two most distant points along the river
        let maxDistance = 0;
        let point1 = null;
        let point2 = null;
        
        for (let i = 0; i < sampledPoints.length; i++) {
          for (let j = i + 1; j < sampledPoints.length; j++) {
            const dist = Math.sqrt(
              Math.pow(sampledPoints[j][0] - sampledPoints[i][0], 2) +
              Math.pow(sampledPoints[j][1] - sampledPoints[i][1], 2)
            );
            if (dist > maxDistance) {
              maxDistance = dist;
              point1 = sampledPoints[i];
              point2 = sampledPoints[j];
            }
          }
        }
        
        if (!point1 || !point2) return null;
        
        // Interpolate position along the line between the two distant points
        const targetLat = point1[0] + fraction * (point2[0] - point1[0]);
        const targetLon = point1[1] + fraction * (point2[1] - point1[1]);
        const targetPoint = [targetLat, targetLon];
        
        // Find the nearest point on the actual river geometry to the target point
        let nearestPoint = null;
        let nearestDistance = Infinity;
        let nearestLineString = null;
        let nearestSegmentIndex = -1;
        let nearestT = 0;
        
        for (const lineString of allCoords) {
          for (let i = 0; i < lineString.length - 1; i++) {
            const p1 = [lineString[i][1], lineString[i][0]]; // [lat, lon]
            const p2 = [lineString[i+1][1], lineString[i+1][0]]; // [lat, lon]
            
            // Find nearest point on segment p1-p2 to target point
            const result = nearestPointOnSegment(targetPoint, p1, p2);
            
            if (result.distance < nearestDistance) {
              nearestDistance = result.distance;
              nearestPoint = result.point;
              nearestLineString = lineString;
              nearestSegmentIndex = i;
              nearestT = result.t;
            }
          }
        }
        
        if (!nearestPoint || !nearestLineString) return null;
        
        // Calculate angle based on the line between the two distant points
        const dx = point2[1] - point1[1]; // longitude difference
        const dy = point2[0] - point1[0]; // latitude difference
        let angle = -Math.atan2(dy, dx) * 180 / Math.PI;
        
        // Normalize angle to keep text readable
        if (angle > 90) angle -= 180;
        if (angle < -90) angle += 180;
        
        return { position: nearestPoint, angle: angle };
      }
      
      function nearestPointOnSegment(point, segmentStart, segmentEnd) {
        // Calculate nearest point on line segment to a given point
        const dx = segmentEnd[1] - segmentStart[1];
        const dy = segmentEnd[0] - segmentStart[0];
        
        if (dx === 0 && dy === 0) {
          // Degenerate segment
          const dist = Math.sqrt(
            Math.pow(point[0] - segmentStart[0], 2) +
            Math.pow(point[1] - segmentStart[1], 2)
          );
          return { point: segmentStart, distance: dist, t: 0 };
        }
        
        // Calculate projection parameter t
        const t = Math.max(0, Math.min(1,
          ((point[1] - segmentStart[1]) * dx + (point[0] - segmentStart[0]) * dy) /
          (dx * dx + dy * dy)
        ));
        
        // Calculate nearest point
        const nearest = [
          segmentStart[0] + t * dy,
          segmentStart[1] + t * dx
        ];
        
        // Calculate distance
        const dist = Math.sqrt(
          Math.pow(point[0] - nearest[0], 2) +
          Math.pow(point[1] - nearest[1], 2)
        );
        
        return { point: nearest, distance: dist, t: t };
      }

      // Default point marker: a small ink dot with a white ring (an atlas-style
      // city marker). Restyle via `.point-dot` in CSS, or pass an Icon.
      function defaultPointIcon(classes) {
        return L.divIcon({
          html: '<span class="point-dot"></span>',
          className: 'point' + (classes ? ' ' + classes : ''),
          iconSize: [11, 11],
          iconAnchor: [5.5, 5.5]
        });
      }

      // ── Flag styling ─────────────────────────────────────────────────────────
      function parseColorToHsl(color) {
        if (!color || typeof color !== 'string') return null;
        const c = color.trim();
        let m = c.match(/^hsla?\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%/i);
        if (m) return { h: parseFloat(m[1]) / 360, s: parseFloat(m[2]) / 100, l: parseFloat(m[3]) / 100 };
        if (!c.startsWith('#')) return null;
        let hex = c.slice(1);
        if (hex.length === 3) hex = hex.split('').map(ch => ch + ch).join('');
        if (hex.length < 6) return null;
        const r = parseInt(hex.substr(0, 2), 16) / 255;
        const g = parseInt(hex.substr(2, 2), 16) / 255;
        const b = parseInt(hex.substr(4, 2), 16) / 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h = 0, s = 0;
        const l = (max + min) / 2;
        if (max !== min) {
          const d = max - min;
          s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
          if (max === r) h = (g - b) / d + (g < b ? 6 : 0);
          else if (max === g) h = (b - r) / d + 2;
          else h = (r - g) / d + 4;
          h /= 6;
        }
        return { h, s, l };
      }

      function hslCss(hsl, alpha = 1) {
        const h = Math.round(hsl.h * 3600) / 10;
        const s = Math.round(Math.max(0, Math.min(1, hsl.s)) * 1000) / 10;
        const l = Math.round(Math.max(0, Math.min(1, hsl.l)) * 1000) / 10;
        return alpha >= 1 ? `hsl(${h}, ${s}%, ${l}%)` : `hsla(${h}, ${s}%, ${l}%, ${alpha})`;
      }

      // Deep ink of the same hue, for labels drawn on a pale fill.
      function labelInkColor(color) {
        const hsl = parseColorToHsl(color);
        if (!hsl) return '#2f2a26';
        return hslCss({ h: hsl.h, s: Math.min(Math.max(hsl.s, 0.2), 0.5), l: Math.min(hsl.l * 0.42, 0.3) });
      }

      // A darker, slightly desaturated shade of the fill, for borders.
      function borderShadeColor(color) {
        const hsl = parseColorToHsl(color);
        if (!hsl) return '#555';
        return hslCss({ h: hsl.h, s: hsl.s * 0.7, l: Math.max(hsl.l - 0.28, 0.12) });
      }

      function geometryLatLngBounds(geometry) {
        let minLat = Infinity, maxLat = -Infinity, minLng = Infinity, maxLng = -Infinity;
        const visit = (coords) => {
          if (typeof coords[0] === 'number') {
            if (coords[1] < minLat) minLat = coords[1];
            if (coords[1] > maxLat) maxLat = coords[1];
            if (coords[0] < minLng) minLng = coords[0];
            if (coords[0] > maxLng) maxLng = coords[0];
            return;
          }
          for (const c of coords) visit(c);
        };
        const visitGeom = (g) => {
          if (!g) return;
          if (g.type === 'FeatureCollection') { for (const f of g.features || []) visitGeom(f.geometry); return; }
          if (g.type === 'Feature') { visitGeom(g.geometry); return; }
          if (g.type === 'GeometryCollection') { for (const gg of g.geometries || []) visitGeom(gg); return; }
          if (g.coordinates) visit(g.coordinates);
        };
        visitGeom(geometry);
        if (!isFinite(minLat)) return null;
        return L.latLngBounds([minLat, minLng], [maxLat, maxLng]);
      }

      // Label size follows the territory's on-screen size, so empires get
      // big, airy labels and small principalities get modest ones.
      const flagLabelMarkers = new Set();
      function flagLabelScale(marker) {
        const info = marker._xatraLabel;
        if (!info || !info.bounds) return info ? info.depthScale : 1;
        const zoom = map.getZoom();
        const nw = map.project(info.bounds.getNorthWest(), zoom);
        const se = map.project(info.bounds.getSouthEast(), zoom);
        const sizePx = Math.sqrt(Math.max(1, Math.abs(se.x - nw.x)) * Math.max(1, Math.abs(se.y - nw.y)));
        const scale = Math.max(0.9, Math.min(1.7, Math.pow(sizePx / 180, 0.5)));
        marker._xatraSizePx = sizePx;
        return scale * info.depthScale;
      }
      function applyFlagLabelScale(marker) {
        const el = marker.getElement && marker.getElement();
        if (!el) return;
        const inner = el.querySelector('.flag-label');
        if (inner) inner.style.setProperty('--xatra-label-scale', flagLabelScale(marker).toFixed(3));
      }
      function updateFlagLabelScales() {
        for (const marker of flagLabelMarkers) {
          if (map.hasLayer(marker)) applyFlagLabelScale(marker);
        }
        declutterFlagLabels();
      }
      map.on('zoomend', updateFlagLabelScales);
      map.on('moveend', () => scheduleDeclutter());

      // Hide flag labels that would collide with a bigger territory's label (or
      // with point/text labels); zooming in reveals them. Labels are compared as
      // rotated rectangles, so tilted ones only claim the space they cover.
      function labelBox(cx, cy, hw, hh, angle) {
        const c = Math.cos(angle), s = Math.sin(angle);
        const ac = Math.abs(c), as = Math.abs(s);
        return { cx, cy, hw, hh, c, s, rx: hw * ac + hh * as, ry: hw * as + hh * ac };
      }
      function elementAngle(el) {
        let angle = 0;
        for (let node = el; node; node = node.parentElement) {
          const t = getComputedStyle(node).transform;
          if (t && t !== 'none') {
            const m = new DOMMatrixReadOnly(t);
            angle += Math.atan2(m.b, m.a);
          }
          if (node.classList.contains('leaflet-marker-icon')) break;
        }
        return angle;
      }
      function elementBox(el, pad) {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return null;
        const w = el.offsetWidth, h = el.offsetHeight;
        const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        if (!w || !h) return labelBox(cx, cy, r.width / 2 + pad, r.height / 2 + pad, 0);
        return labelBox(cx, cy, w / 2 + pad, h / 2 + pad, elementAngle(el));
      }
      function boxesOverlap(a, b) {
        const dx = b.cx - a.cx, dy = b.cy - a.cy;
        if (Math.abs(dx) >= a.rx + b.rx || Math.abs(dy) >= a.ry + b.ry) return false;
        for (const [x, y] of [[a.c, a.s], [-a.s, a.c], [b.c, b.s], [-b.s, b.c]]) {
          const ra = a.hw * Math.abs(a.c * x + a.s * y) + a.hh * Math.abs(-a.s * x + a.c * y);
          const rb = b.hw * Math.abs(b.c * x + b.s * y) + b.hh * Math.abs(-b.s * x + b.c * y);
          if (Math.abs(dx * x + dy * y) >= ra + rb) return false;
        }
        return true;
      }
      function flagContainsPoint(marker, latlng) {
        const polygon = marker._xatraPolygon;
        if (!polygon) return true;
        let inside = false;
        polygon.eachLayer((sub) => {
          if (!inside && sub instanceof L.Polygon) {
            const b = sub.getBounds();
            if (b.contains(latlng) && pointInPolygon(latlng, sub.getLatLngs())) inside = true;
          }
        });
        return inside;
      }

      // A territory whose label spot is off-screen still gets a label when
      // enough of it is in view: the roomiest visible point (farthest from its
      // edges and from the screen's), found on a coarse grid and then refined.
      function visibleLabelSpot(marker, view, overlays, halfW, halfH) {
        const polygon = marker._xatraPolygon;
        if (!polygon) return null;
        const rings = [];
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        polygon.eachLayer((sub) => {
          if (!(sub instanceof L.Polygon) || !sub._parts) return;
          for (const part of sub._parts) {
            if (part.length < 3) continue;
            const ring = part.map((pt) => map.layerPointToContainerPoint(pt));
            for (const pt of ring) {
              if (pt.x < minX) minX = pt.x;
              if (pt.y < minY) minY = pt.y;
              if (pt.x > maxX) maxX = pt.x;
              if (pt.y > maxY) maxY = pt.y;
            }
            rings.push(ring);
          }
        });
        minX = Math.max(minX, view.left); minY = Math.max(minY, view.top);
        maxX = Math.min(maxX, view.right); maxY = Math.min(maxY, view.bottom);
        if (!rings.length || maxX - minX < 4 || maxY - minY < 4) return null;
        const room = (x, y) => {
          let inside = false;
          let d2 = Infinity;
          for (const ring of rings) {
            for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
              const a = ring[j], b = ring[i];
              if ((a.y > y) !== (b.y > y) && x < ((b.x - a.x) * (y - a.y)) / (b.y - a.y) + a.x) inside = !inside;
              const ex = b.x - a.x, ey = b.y - a.y;
              const len2 = ex * ex + ey * ey;
              const t = len2 ? Math.max(0, Math.min(1, ((x - a.x) * ex + (y - a.y) * ey) / len2)) : 0;
              const qx = a.x + t * ex - x, qy = a.y + t * ey - y;
              const q2 = qx * qx + qy * qy;
              if (q2 < d2) d2 = q2;
            }
          }
          if (!inside) return -1;
          let d = Math.min(Math.sqrt(d2), x - view.left, view.right - x, y - view.top, view.bottom - y);
          for (const o of overlays) {
            const ox = Math.max(o.left - x, 0, x - o.right), oy = Math.max(o.top - y, 0, y - o.bottom);
            if (!ox && !oy) return -1;
            d = Math.min(d, Math.hypot(ox, oy));
          }
          return d;
        };
        let step = Math.max(6, Math.sqrt(((maxX - minX) * (maxY - minY)) / 300));
        let best = null;
        for (let y = minY + step / 2; y < maxY; y += step) {
          for (let x = minX + step / 2; x < maxX; x += step) {
            const d = room(x, y);
            if (d > 0 && (!best || d > best.room)) best = { x, y, room: d };
          }
        }
        if (!best) return null;
        for (let pass = 0; pass < 3; pass++) {
          step /= 2;
          const cx = best.x, cy = best.y;
          for (let ky = -2; ky <= 2; ky++) {
            for (let kx = -2; kx <= 2; kx++) {
              const d = room(cx + kx * step, cy + ky * step);
              if (d > best.room) best = { x: cx + kx * step, y: cy + ky * step, room: d };
            }
          }
        }
        // Keep the whole label on screen when the territory allows it.
        const x = Math.max(view.left + halfW, Math.min(view.right - halfW, best.x));
        const y = Math.max(view.top + halfH, Math.min(view.bottom - halfH, best.y));
        if ((x !== best.x || y !== best.y) && room(x, y) > 0) {
          best.x = x;
          best.y = y;
        }
        best.size = Math.sqrt((maxX - minX) * (maxY - minY));
        return best;
      }

      // Nudges tried when a label's own spot is taken, in label-sized steps
      // (dx in label widths, dy in text lines), nearest first.
      const FLAG_LABEL_NUDGES = [[0, 0], [0, -1], [0, 1], [-0.3, 0], [0.3, 0], [-0.3, -1], [0.3, -1], [-0.3, 1], [0.3, 1], [0, -2], [0, 2], [-0.6, 0], [0.6, 0]];
      function declutterFlagLabels() {
        const mapEl = map.getContainer();
        const mapRect = mapEl.getBoundingClientRect();
        const pad = 2;
        const taken = [];
        for (const el of mapEl.querySelectorAll('.text-label, .point-label')) {
          const box = elementBox(el, 0);
          if (box) taken.push(box);
        }
        // Point markers are dodged when possible but never hide a label.
        const markers = [];
        for (const el of mapEl.querySelectorAll('.point-dot, .leaflet-marker-icon:not(.leaflet-div-icon):not(.flag-label-container)')) {
          const r = el.getBoundingClientRect();
          if (r.width && r.height) markers.push(labelBox(r.left + r.width / 2, r.top + r.height / 2, r.width / 2, r.height / 2, 0));
        }
        // The title panel and map controls cover the map: labels under them
        // look for a visible spot instead.
        const overlays = [];
        for (const el of document.querySelectorAll('#title, #controls, .leaflet-control-container .leaflet-control')) {
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height || r.right <= mapRect.left || r.left >= mapRect.right || r.bottom <= mapRect.top || r.top >= mapRect.bottom) continue;
          overlays.push({ left: r.left - mapRect.left - pad, right: r.right - mapRect.left + pad, top: r.top - mapRect.top - pad, bottom: r.bottom - mapRect.top + pad });
          taken.push(labelBox(r.left + r.width / 2, r.top + r.height / 2, r.width / 2, r.height / 2, 0));
        }
        const view = { left: 0, top: 0, right: mapRect.width, bottom: mapRect.height };
        // Reset every label before measuring any (one layout, not one per label).
        const labels = [];
        for (const marker of flagLabelMarkers) {
          if (!map.hasLayer(marker)) continue;
          const el = marker.getElement && marker.getElement();
          const inner = el && el.querySelector('.flag-label');
          if (!inner) continue;
          const rotor = el.querySelector('.flag-label-rotor') || inner;
          inner.classList.remove('xatra-label-hidden');
          inner.style.translate = '';
          rotor.style.translate = '';
          rotor.style.scale = '';
          labels.push({ marker, inner, rotor });
        }
        const items = [];
        for (const { marker, inner, rotor } of labels) {
          const r = inner.getBoundingClientRect();
          if (!r.width || !r.height) continue;
          const w = inner.offsetWidth || r.width, h = inner.offsetHeight || r.height;
          const item = { inner, rotor, marker, w, h, width: r.width, cx: r.left + r.width / 2, cy: r.top + r.height / 2, fit: 1 };
          let priority = (marker._xatraSizePx || 0) * (marker._xatraLabel ? marker._xatraLabel.depthScale : 1);
          const fullyInView = r.left >= mapRect.left && r.right <= mapRect.right && r.top >= mapRect.top && r.bottom <= mapRect.bottom
            && !overlays.some((o) => r.left - mapRect.left < o.right && o.left < r.right - mapRect.left && r.top - mapRect.top < o.bottom && o.top < r.bottom - mapRect.top);
          if (!fullyInView) {
            const spot = visibleLabelSpot(marker, view, overlays, r.width / 2 + pad, r.height / 2 + pad);
            if (spot && spot.room >= Math.max(h, w / 5)) {
              // Shrink a big territory's label to what is actually in view.
              item.fit = Math.max(0.7, Math.min(1, Math.sqrt(spot.size / Math.max(1, marker._xatraSizePx || spot.size))));
              item.cx = spot.x + mapRect.left;
              item.cy = spot.y + mapRect.top;
              item.moved = true;
              priority = Math.min(priority, spot.size);
            } else if (r.right < mapRect.left || r.left > mapRect.right || r.bottom < mapRect.top || r.top > mapRect.bottom) {
              continue;
            }
          }
          item.x0 = r.left + r.width / 2;
          item.y0 = r.top + r.height / 2;
          item.priority = priority;
          items.push(item);
        }
        items.sort((a, b) => b.priority - a.priority);
        for (const item of items) {
          const { w, h, cx, cy } = item;
          const angle = ((item.marker._xatraLabel && item.marker._xatraLabel.angle) || 0) * Math.PI / 180;
          // Try the anchor first, then nearby spots that are still inside the
          // territory; if nothing fits, a slightly smaller label gets the same
          // chance before it waits for a zoom-in.
          let placed = false;
          for (const [shrink, avoidMarkers] of [[1, true], [1, false], [0.85, true], [0.85, false]]) {
            const scale = shrink * item.fit;
            for (const [kx, ky] of FLAG_LABEL_NUDGES) {
              const dx = kx * item.width * scale, dy = ky * 1.1 * h * scale;
              const box = labelBox(cx + dx, cy + dy, (w * scale) / 2 + pad, (h * scale) / 2 + pad, angle);
              if (taken.some((t) => boxesOverlap(box, t))) continue;
              if (avoidMarkers && markers.some((t) => boxesOverlap(box, t))) continue;
              if (dx || dy) {
                const center = L.point(cx + dx - mapRect.left, cy + dy - mapRect.top);
                if (!flagContainsPoint(item.marker, map.containerPointToLatLng(center))) continue;
              }
              const tx = cx + dx - item.x0, ty = cy + dy - item.y0;
              if (tx || ty) item.rotor.style.translate = `${tx.toFixed(1)}px ${ty.toFixed(1)}px`;
              if (scale !== 1) item.rotor.style.scale = scale.toFixed(3);
              taken.push(box);
              placed = true;
              break;
            }
            if (placed) break;
          }
          if (!placed) item.inner.classList.add('xatra-label-hidden');
        }
      }

      let declutterPending = false;
      function scheduleDeclutter() {
        if (declutterPending) return;
        declutterPending = true;
        requestAnimationFrame(() => {
          declutterPending = false;
          declutterFlagLabels();
        });
      }
      // Web fonts change label widths once they load.
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => scheduleDeclutter());

      // Rotate labels only for clearly elongated territories, and gently.
      function flagLabelAngle(geometry) {
        const distant = findDistantPoints(geometry);
        if (!distant) return 0;
        const [lat1, lng1] = distant.point1;
        const [lat2, lng2] = distant.point2;
        const len = Math.hypot(lat2 - lat1, lng2 - lng1);
        if (len < 1e-9) return 0;
        const ux = (lng2 - lng1) / len, uy = (lat2 - lat1) / len;
        let minW = Infinity, maxW = -Infinity;
        for (const [lat, lng] of extractCoordinatesFromGeometry(geometry.type === 'Feature' ? geometry.geometry : geometry)) {
          const w = (lng - lng1) * -uy + (lat - lat1) * ux;
          if (w < minW) minW = w;
          if (w > maxW) maxW = w;
        }
        const width = Math.max(maxW - minW, 1e-9);
        if (len / width < 2.2) return 0;
        return Math.max(-35, Math.min(35, distant.angle));
      }

      function flagTooltipText(f) {
        let text = f.display_label || f.label;
        if (f.parent) {
          const relation = f.type || 'vassal';
          const parentLabel = f.parent.includes('/') ? f.parent.split('/').slice(-1)[0] : f.parent;
          text += ` (${relation} of ${parentLabel})`;
        }
        if (f.note) text += ' — ' + f.note;
        return text;
      }

      // Builds the polygon layer (and label marker, if any) for one flag.
      // Layers are returned un-added; `flagData` is attached for dynamic maps.
      function buildFlagLayers(f, geometry, flagData) {
        let className = (f.type === 'province') ? 'province' : 'flag';
        if (f.type === 'vassal') className += ' vassal';
        if (f.classes) className += ' ' + f.classes;
        const baseColor = f.root_parent_color || f.color;

        let style;
        if (f.type === 'province') {
          style = {
            className,
            fill: false,
            stroke: true,
            color: borderShadeColor(baseColor || '#888'),
            opacity: 0.75,
            weight: 1,
            dashArray: '4 3',
            lineJoin: 'round'
          };
        } else if (f.color) {
          style = {
            className,
            fillColor: f.color,
            fillOpacity: f.type === 'vassal' ? 0.6 : 0.5,
            color: borderShadeColor(f.type === 'vassal' ? (baseColor || f.color) : f.color),
            opacity: 0.7,
            weight: f.type === 'vassal' ? 0.9 : 1.1,
            lineJoin: 'round'
          };
        } else {
          style = { className };
        }

        const flagTooltip = flagTooltipText(f);
        const layer = L.geoJSON(geometry, {
          style: () => style,
          onEachFeature: function(feature, subLayer) {
            registerLayerTooltip(subLayer, 'Flag', flagTooltip);
            subLayer.on('click', function() {
              if (!window.parent) return;
              window.parent.postMessage({
                type: 'mapFeaturePick',
                featureType: 'territory',
                name: f.label || ''
              }, '*');
            });
          }
        });
        layer._flagData = flagData;
        const built = [layer];

        const anchor = f.centroid || getCentroid(geometry);
        if (anchor && (anchor[0] !== 0 || anchor[1] !== 0)) {
          let labelClassName = 'flag-label';
          if (f.type === 'vassal') labelClassName += ' vassal';
          if (f.type === 'province') labelClassName += ' province';
          if (f.classes) labelClassName += ' ' + f.classes;
          const labelStyle = baseColor ? `color: ${labelInkColor(baseColor)};` : '';
          const rotationAngle = flagLabelAngle(geometry);
          const labelDiv = L.divIcon({
            html: `<div class="flag-label-rotor" style="transform: rotate(${rotationAngle}deg);"><div class="${labelClassName}" style="${labelStyle}">${f.display_label || f.label}</div></div>`,
            className: 'flag-label-container',
            iconSize: [0, 0],
            iconAnchor: [0, 0]
          });
          const labelLayer = L.marker(anchor, { icon: labelDiv, interactive: false, keyboard: false });
          labelLayer._flagData = flagData;
          labelLayer._xatraPolygon = layer;
          labelLayer._xatraLabel = {
            bounds: geometryLatLngBounds(geometry),
            angle: rotationAngle,
            depthScale: Math.pow(0.85, f.vassal_depth || 0)
          };
          labelLayer.on('add', () => {
            applyFlagLabelScale(labelLayer);
            scheduleDeclutter();
          });
          flagLabelMarkers.add(labelLayer);
          built.push(labelLayer);
        }
        return built;
      }

      function createAllLayers() {
        if (allLayersCreated) return;
        
        console.log("Creating all layers for dynamic map...");
        
        // Create all flag layers from all snapshots
        const snapshots = payload.flags.snapshots;
        for (const snapshot of snapshots) {
          for (const f of snapshot.flags) {
            const geometry = resolveGeometry(f);
            if (!geometry) continue;
            
            const built = buildFlagLayers(f, geometry, { label: f.label, snapshot: snapshot.year });
            layers.flags.push(...built);
          }
        }
        
        // Create all other layer types
        createAllRivers();
        createAllPaths();
        createAllPoints();
        createAllTexts();
        createAllAdmins();
        createAllAdminRivers();
        createAllData();
        createAllDataframes();
        
        allLayersCreated = true;
        console.log("All layers created for dynamic map");
      }

      function createAllRivers() {
        for (const r of payload.rivers || []) {
          const geometry = resolveGeometry(r);
          if (!geometry) continue;
          let className = 'river';
          if (r.classes) className += ' ' + r.classes;
          const riverTooltip = `${r.label}${r.note ? ' — ' + r.note : ''}`;
          const layer = L.geoJSON(geometry, { 
            style: { className },
            onEachFeature: function(feature, subLayer) {
              // Register each sublayer with multi-tooltip system
              registerLayerTooltip(subLayer, 'River', riverTooltip, r.hover_radius);
            }
          });
          
          layer._riverData = { period: r.period };
          layers.rivers.push(layer);
          
          // Add labels if show_label is true
          if (r.show_label) {
            const nLabels = r.n_labels || 1;
            
            // Create labels at positions k/(n+1) where k = 1, 2, ..., n
            for (let k = 1; k <= nLabels; k++) {
              const fraction = k / (nLabels + 1);
              const labelInfo = calculateRiverLabelPosition(geometry, r.label, fraction);
              
              if (labelInfo) {
                let labelClassName = 'river-label-container';
                let innerClassName = 'text-label river-label';
                if (r.classes) innerClassName += ' ' + r.classes;
                
                // Use divIcon with nested divs for rotation and translation
                // Outer div: rotation (inline), Inner div: translation (CSS customizable)
                const labelDiv = L.divIcon({
                  html: `<div style="transform: rotate(${labelInfo.angle}deg);"><div class="${innerClassName}" style="transform: translateY(-12px); white-space: nowrap;">${r.label}</div></div>`,
                  className: labelClassName,
                  iconSize: [1, 1],
                  iconAnchor: [0, 0]
                });
                
                const labelLayer = L.marker([labelInfo.position[0], labelInfo.position[1]], { icon: labelDiv });
                labelLayer._riverData = { period: r.period };
                layers.rivers.push(labelLayer);
              }
            }
          }
        }
      }

      function createAllPaths() {
        for (const p of payload.paths || []) {
          const latlngs = p.coords.map(([lat, lon]) => [lat, lon]);
          let className = 'path';
          if (p.classes) className += ' ' + p.classes;
          const layer = L.polyline(latlngs, { className });
          // Register with multi-tooltip system
          const pathTooltip = `${p.label}${p.note ? ' — ' + p.note : ''}`;
          registerLayerTooltip(layer, 'Path', pathTooltip, p.hover_radius);
          layer._pathData = { period: p.period };
          layers.paths.push(layer);
          
          // Add labels if show_label is true
          if (p.show_label && latlngs.length > 0) {
            // Calculate total distance along the path
            let totalDistance = 0;
            const distances = [0];
            for (let i = 1; i < latlngs.length; i++) {
              const d = Math.sqrt(
                Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
              );
              totalDistance += d;
              distances.push(totalDistance);
            }
            
            const nLabels = p.n_labels || 1;
            
            // Create labels at positions k/(n+1) where k = 1, 2, ..., n
            for (let k = 1; k <= nLabels; k++) {
              const targetDistance = (k / (nLabels + 1)) * totalDistance;
              
              let labelPoint = latlngs[0];
              let labelSegmentIndex = 0;
              
              // Find the segment containing this position
              for (let i = 1; i < distances.length; i++) {
                if (distances[i] >= targetDistance) {
                  const segmentStart = distances[i - 1];
                  const segmentEnd = distances[i];
                  const t = (targetDistance - segmentStart) / (segmentEnd - segmentStart);
                  
                  // Interpolate between points
                  labelPoint = [
                    latlngs[i-1][0] + t * (latlngs[i][0] - latlngs[i-1][0]),
                    latlngs[i-1][1] + t * (latlngs[i][1] - latlngs[i-1][1])
                  ];
                  labelSegmentIndex = i - 1;
                  break;
                }
              }
              
              // Calculate rotation angle based on nearby path segments
              const estimatedLabelLength = p.label.length * 0.15;
              
              let startPoint = null;
              let endPoint = null;
              
              // Search backwards
              let accumulatedDist = 0;
              for (let i = labelSegmentIndex; i >= 0 && accumulatedDist < estimatedLabelLength; i--) {
                startPoint = latlngs[i];
                if (i > 0) {
                  accumulatedDist += Math.sqrt(
                    Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                    Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
                  );
                }
              }
              
              // Search forwards
              accumulatedDist = 0;
              for (let i = labelSegmentIndex + 1; i < latlngs.length && accumulatedDist < estimatedLabelLength; i++) {
                endPoint = latlngs[i];
                accumulatedDist += Math.sqrt(
                  Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                  Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
                );
              }
              
              // Calculate angle
              let angle = 0;
              if (startPoint && endPoint) {
                const dx = endPoint[1] - startPoint[1];
                const dy = endPoint[0] - startPoint[0];
                angle = -Math.atan2(dy, dx) * 180 / Math.PI;
                
                if (angle > 90) angle -= 180;
                if (angle < -90) angle += 180;
              }
              
              let labelClassName = 'path-label-container';
              let innerClassName = 'text-label path-label';
              if (p.classes) innerClassName += ' ' + p.classes;
              
              const labelDiv = L.divIcon({
                html: `<div style="transform: rotate(${angle}deg);"><div class="${innerClassName}" style="transform: translateY(-8px); white-space: nowrap;">${p.label}</div></div>`,
                className: labelClassName,
                iconSize: [1, 1],
                iconAnchor: [0, 0]
              });
              
              const labelLayer = L.marker(labelPoint, { icon: labelDiv });
              labelLayer._pathData = { period: p.period };
              layers.paths.push(labelLayer);
            }
          }
        }
      }

      function createAllPoints() {
        for (const p of payload.points || []) {
          let markerOptions = {};
          if (p.icon) {
            const iconOptions = {
              iconUrl: p.icon.iconUrl,
              iconSize: p.icon.iconSize,
              iconAnchor: p.icon.iconAnchor,
              popupAnchor: p.icon.popupAnchor
            };
            if (p.icon.shadowUrl) iconOptions.shadowUrl = p.icon.shadowUrl;
            if (p.icon.shadowSize) iconOptions.shadowSize = p.icon.shadowSize;
            if (p.icon.shadowAnchor) iconOptions.shadowAnchor = p.icon.shadowAnchor;
            markerOptions.icon = L.icon(iconOptions);
          } else {
            markerOptions.icon = defaultPointIcon(p.classes);
          }
          
          // Apply classes to marker if present
          let className = 'point';
          if (p.classes) className += ' ' + p.classes;
          markerOptions.className = className;
          
          const layer = L.marker([p.position[0], p.position[1]], markerOptions);
          // Register with multi-tooltip system
          const pointTooltip = `${p.label}${p.note ? ' — ' + p.note : ''}`;
          registerLayerTooltip(layer, 'Point', pointTooltip, p.hover_radius);
          layer._pointData = { period: p.period };
          layers.points.push(layer);
          
          // Add label next to point if show_label is true
          if (p.show_label) {
            // Apply classes to label if present
            let labelClassName = 'point-label-container';
            let innerClassName = 'text-label point-label';
            if (p.classes) innerClassName += ' ' + p.classes;
            
            // Use divIcon with nested divs for rotation and translation
            // Outer div: rotation (inline, can be customized), Inner div: translation (CSS customizable)
            const rotationAngle = p.rotation || 0; // Default to 0 degrees if no rotation specified
            const labelDiv = L.divIcon({
              html: `<div style="transform: rotate(${rotationAngle}deg);"><div class="${innerClassName}" style="transform: translateX(9px); white-space: nowrap;">${p.label}</div></div>`,
              className: labelClassName,
              iconSize: [1, 1],
              iconAnchor: [0, 0]
            });
            
            const labelLayer = L.marker([p.position[0], p.position[1]], { icon: labelDiv });
            labelLayer._pointData = { period: p.period };
            layers.points.push(labelLayer);
          }
        }
      }

      function createAllTexts() {
        for (const t of payload.texts || []) {
          let labelClassName = 'text-label-container';
          let innerClassName = 'text-label';
          if (t.classes) innerClassName += ' ' + t.classes;
          
          // Use divIcon with nested divs for rotation and translation
          // Outer div: rotation (inline, can be customized), Inner div: translation (CSS customizable)
          const rotationAngle = t.rotation || 0; // Default to 0 degrees if no rotation specified
          const labelDiv = L.divIcon({
            html: `<div style="transform: rotate(${rotationAngle}deg);"><div class="${innerClassName}" style="transform: translateY(0px); white-space: nowrap;">${t.label}</div></div>`,
            className: labelClassName,
            iconSize: [1, 1],
            iconAnchor: [0, 0]
          });
          
          const layer = L.marker([t.position[0], t.position[1]], { icon: labelDiv });
          // Register with multi-tooltip system if note is present
          if (t.note) {
            const textTooltip = `${t.label} — ${t.note}`;
            registerLayerTooltip(layer, 'Text', textTooltip);
          }
          layer._textData = { period: t.period };
          layers.texts.push(layer);
        }
      }

      function createAllAdmins() {
        for (const a of payload.admins || []) {
          const geometry = resolveGeometry(a);
          if (!geometry) continue;
          let className = 'admin';
          if (a.classes) className += ' ' + a.classes;
          const layer = L.geoJSON(geometry, {

            style: function(feature) {
              const props = feature.properties || {};
              const color = props._color;
              return {
                className: className,
                fillColor: color || '#cccccc',
                fillOpacity: 0.35,
                color: color || '#666666',
                weight: 1
              };
            },
            onEachFeature: function(feature, layer) {
              const props = feature.properties || {};
              
              let tooltip = '';
              let topName = '';
              if (props.NAME_3) topName = props.NAME_3;
              else if (props.NAME_2) topName = props.NAME_2;
              else if (props.NAME_1) topName = props.NAME_1;
              else if (props.COUNTRY) topName = props.COUNTRY;
              
              if (topName) tooltip += `<b>${topName}</b><br/>`;
              
              if (props.GID_0) tooltip += `GID_0: ${props.GID_0}<br/>`;
              if (props.COUNTRY) tooltip += `COUNTRY: ${props.COUNTRY}<br/>`;
              if (props.GID_1) tooltip += `GID_1: ${props.GID_1}<br/>`;
              if (props.NAME_1) tooltip += `NAME_1: ${props.NAME_1}<br/>`;
              if (props.VARNAME_1 && props.VARNAME_1 !== 'NA') tooltip += `VARNAME_1: ${props.VARNAME_1}<br/>`;
              if (props.GID_2) tooltip += `GID_2: ${props.GID_2}<br/>`;
              if (props.NAME_2) tooltip += `NAME_2: ${props.NAME_2}<br/>`;
              if (props.VARNAME_2 && props.VARNAME_2 !== 'NA') tooltip += `VARNAME_2: ${props.VARNAME_2}<br/>`;
              if (props.GID_3) tooltip += `GID_3: ${props.GID_3}<br/>`;
              if (props.NAME_3) tooltip += `NAME_3: ${props.NAME_3}<br/>`;
              if (props.VARNAME_3 && props.VARNAME_3 !== 'NA') tooltip += `VARNAME_3: ${props.VARNAME_3}<br/>`;
              
              // Add DataFrame value for current year
              if (props._dataframe_data) {
                const currentYear = window.currentYear || (df.years && df.years[0]) || 2020;
                
                // Find the closest available year
                let closestYear = null;
                let closestDistance = Infinity;
                
                for (const year of Object.keys(props._dataframe_data)) {
                  const distance = Math.abs(parseInt(year) - currentYear);
                  if (distance < closestDistance) {
                    closestDistance = distance;
                    closestYear = parseInt(year);
                  }
                }
                
                if (closestYear !== null) {
                  const value = props._dataframe_data[closestYear];
                  tooltip += `Value (${closestYear}): ${value}<br/>`;
                }
              }
              
              if (tooltip.endsWith('<br/>')) {
                tooltip = tooltip.slice(0, -5);
              }
              
              // Register with multi-tooltip system
              if (tooltip) {
                registerLayerTooltip(layer, 'Admin Region', tooltip);
              }

              layer.on('mousemove', function(e) {
                if (!window.parent) return;
                const originalEvent = (e && e.originalEvent) ? e.originalEvent : {};
                const isAddSweep = !!(originalEvent.ctrlKey || originalEvent.metaKey);
                const isRemoveSweep = !!originalEvent.altKey;
                if (!isAddSweep && !isRemoveSweep) return;
                const pickedGid = normalizeGadmCode(
                  props.GID_3 || props.GID_2 || props.GID_1 || props.GID_0 || ''
                );
                if (!pickedGid) return;
                const pickedName = props.NAME_3 || props.NAME_2 || props.NAME_1 || props.COUNTRY || '';
                window.parent.postMessage({
                  type: 'mapFeaturePick',
                  featureType: 'gadm',
                  gid: pickedGid,
                  name: pickedName,
                  hoverMode: isRemoveSweep ? 'remove' : 'add'
                }, '*');
              });

              layer.on('click', function(e) {
                if (!window.parent) return;
                const pickedGid = normalizeGadmCode(
                  props.GID_3 || props.GID_2 || props.GID_1 || props.GID_0 || ''
                );
                if (!pickedGid) return;
                const pickedName = props.NAME_3 || props.NAME_2 || props.NAME_1 || props.COUNTRY || '';
                const originalEvent = (e && e.originalEvent) ? e.originalEvent : {};
                window.parent.postMessage({
                  type: 'mapFeaturePick',
                  featureType: 'gadm',
                  gid: pickedGid,
                  name: pickedName,
                  shiftKey: !!originalEvent.shiftKey,
                  ctrlKey: !!originalEvent.ctrlKey,
                  metaKey: !!originalEvent.metaKey,
                  altKey: !!originalEvent.altKey,
                  multiSelect: !!(originalEvent.shiftKey || originalEvent.ctrlKey || originalEvent.metaKey),
                }, '*');
              });
            }
          });
          
          layer._adminData = { period: a.period };
          layers.admins.push(layer);
        }
      }

      function createAllAdminRivers() {
        for (const ar of payload.admin_rivers || []) {
          const geometry = resolveGeometry(ar);
          if (!geometry) continue;
          let className = 'admin-river';

          if (ar.classes) className += ' ' + ar.classes;
          
          const layer = L.geoJSON(geometry, {
            style: function(feature) {
              const props = feature.properties || {};
              const source = props._source;
              let color = '#0066cc';
              if (source === 'naturalearth') color = '#0066cc';
              else if (source === 'overpass') color = '#cc6600';
              
              return {
                className: className,
                color: color,
                weight: 2,
                opacity: 0.8
              };
            },
            onEachFeature: function(feature, layer) {
              const props = feature.properties || {};
              
              let tooltip = '';
              const source = props._source;
              if (source === 'naturalearth') {
                tooltip += `<b>Natural Earth River</b><br/>`;
                if (props._ne_id) tooltip += `NE ID: ${props._ne_id}<br/>`;
              } else if (source === 'overpass') {
                tooltip += `<b>Overpass River</b><br/>`;
                if (props._filename) tooltip += `File: ${props._filename}<br/>`;
              }
              
              if (props.name) tooltip += `Name: ${props.name}<br/>`;
              if (props.NAME) tooltip += `NAME: ${props.NAME}<br/>`;
              if (props.NAME_EN) tooltip += `NAME_EN: ${props.NAME_EN}<br/>`;
              if (props.NAME_LOC) tooltip += `NAME_LOC: ${props.NAME_LOC}<br/>`;
              if (props.NAME_ALT) tooltip += `NAME_ALT: ${props.NAME_ALT}<br/>`;
              if (props.NAME_OTHER) tooltip += `NAME_OTHER: ${props.NAME_OTHER}<br/>`;
              
              if (props.scalerank) tooltip += `Scale Rank: ${props.scalerank}<br/>`;
              if (props.featurecla) tooltip += `Feature Class: ${props.featurecla}<br/>`;
              if (props.min_zoom) tooltip += `Min Zoom: ${props.min_zoom}<br/>`;
              
              if (tooltip.endsWith('<br/>')) {
                tooltip = tooltip.slice(0, -5);
              }
              
              // Register with multi-tooltip system (default hover radius for admin rivers)
              if (tooltip) {
                registerLayerTooltip(layer, 'Admin River', tooltip, 10);
              }

              layer.on('click', function() {
                if (!window.parent) return;
                const riverId = extractRiverIdFromProps(props);
                if (!riverId) return;
                window.parent.postMessage({
                  type: 'mapFeaturePick',
                  featureType: 'river',
                  id: riverId,
                  source_type: props._source || 'naturalearth',
                  name: props.name || props.NAME || ''
                }, '*');
              });
            }
          });
          
          layer._adminRiverData = { period: ar.period };
          layers.admin_rivers.push(layer);
          
          // Add labels if requested
          if (ar.show_label && ar.n_labels > 0) {
            const nLabels = ar.n_labels || 1;
            
            for (let k = 1; k <= nLabels; k++) {
              const fraction = k / (nLabels + 1);
              
              // Calculate label position and rotation for each river feature
              if (geometry.features) {
                for (const feature of geometry.features) {
                  const labelInfo = calculateRiverLabelPosition(feature, feature.properties?.name || 'River', fraction);
                  if (labelInfo && labelInfo.position) {
                    const innerClassName = 'admin-river-label';
                    const labelDiv = L.divIcon({
                      html: `<div style="transform: rotate(${labelInfo.angle}deg);"><div class="${innerClassName}" style="transform: translateY(-12px); white-space: nowrap;">${feature.properties?.name || 'River'}</div></div>`,
                      className: 'admin-river-label-container',
                      iconSize: [1, 1],
                      iconAnchor: [0, 0]
                    });
                    
                    const labelLayer = L.marker(labelInfo.position, { icon: labelDiv });
                    labelLayer._adminRiverData = { period: ar.period };
                    layers.admin_rivers.push(labelLayer);
                  }
                }
              }
            }
          }
        }
      }

      function createAllData() {
        for (const d of payload.data || []) {
          const geometry = resolveGeometry(d);
          if (!geometry) continue;
          let className = 'data';
          if (d.classes) className += ' ' + d.classes;

          const layer = L.geoJSON(geometry, {

            style: function(feature) {
              const props = feature.properties || {};
              const dataIndex = d.data_index || 0;
              const color = (props._data_colors && props._data_colors[dataIndex]) || d.color || '#cccccc';
              return {
                className: className,
                fillColor: color,
                fillOpacity: 0.85,
                color: color,
                weight: 1
              };
            },
            onEachFeature: function(feature, layer) {
              const props = feature.properties || {};
              const dataIndex = d.data_index || 0;
              
              let tooltip = '';
              let topName = '';
              if (props.NAME_3) topName = props.NAME_3;
              else if (props.NAME_2) topName = props.NAME_2;
              else if (props.NAME_1) topName = props.NAME_1;
              else if (props.COUNTRY) topName = props.COUNTRY;
              
              if (topName) tooltip += `<b>${topName}</b><br/>`;
              
              if (props.GID_0) tooltip += `GID_0: ${props.GID_0}<br/>`;
              if (props.COUNTRY) tooltip += `COUNTRY: ${props.COUNTRY}<br/>`;
              if (props.GID_1) tooltip += `GID_1: ${props.GID_1}<br/>`;
              if (props.NAME_1) tooltip += `NAME_1: ${props.NAME_1}<br/>`;
              if (props.VARNAME_1 && props.VARNAME_1 !== 'NA') tooltip += `VARNAME_1: ${props.VARNAME_1}<br/>`;
              if (props.GID_2) tooltip += `GID_2: ${props.GID_2}<br/>`;
              if (props.NAME_2) tooltip += `NAME_2: ${props.NAME_2}<br/>`;
              if (props.VARNAME_2 && props.VARNAME_2 !== 'NA') tooltip += `VARNAME_2: ${props.VARNAME_2}<br/>`;
              if (props.GID_3) tooltip += `GID_3: ${props.GID_3}<br/>`;
              if (props.NAME_3) tooltip += `NAME_3: ${props.NAME_3}<br/>`;
              if (props.VARNAME_3 && props.VARNAME_3 !== 'NA') tooltip += `VARNAME_3: ${props.VARNAME_3}<br/>`;
              
              // Get the specific value for this data element
              const value = (props._data_values && props._data_values[dataIndex]) || d.value;
              if (value !== undefined) tooltip += `Value: ${value}<br/>`;
              
              if (tooltip.endsWith('<br/>')) {
                tooltip = tooltip.slice(0, -5);
              }
              
              // Register with multi-tooltip system
              if (tooltip) {
                registerLayerTooltip(layer, 'Data', tooltip);
              }
            }
          });
          
          layer._dataData = { period: d.period };
          layers.data.push(layer);
        }
      }

      function createAllDataframes() {
        for (const df of payload.dataframes || []) {
          if (df.type === 'static') {
            // Static DataFrame - create simple data layers
            createStaticDataframe(df);
          } else if (df.type === 'dynamic') {
            // Dynamic DataFrame - create time-series data layers
            createDynamicDataframe(df);
          }
        }
      }

      function createStaticDataframe(df) {
        const geometry = resolveGeometry(df);
        if (!geometry) return;
        
        let className = 'data';
        if (df.classes) className += ' ' + df.classes;
        
        const layer = L.geoJSON(geometry, {
          style: function(feature) {
            const props = feature.properties || {};
            const value = props._dataframe_value;
            const color = getDataColor(value);
            return {
              className: className,
              fillColor: color,
              fillOpacity: 0.85,
              color: color,
              weight: 1
            };
          },
          onEachFeature: function(feature, layer) {
            const props = feature.properties || {};
            
            let tooltip = '';
            let topName = '';
            if (props.NAME_3) topName = props.NAME_3;
            else if (props.NAME_2) topName = props.NAME_2;
            else if (props.NAME_1) topName = props.NAME_1;
            else if (props.COUNTRY) topName = props.COUNTRY;
            
            if (topName) tooltip += `<b>${topName}</b><br/>`;
            
            // Add GADM properties
            if (props.GID_0) tooltip += `GID_0: ${props.GID_0}<br/>`;
            if (props.COUNTRY) tooltip += `COUNTRY: ${props.COUNTRY}<br/>`;
            if (props.GID_1) tooltip += `GID_1: ${props.GID_1}<br/>`;
            if (props.NAME_1) tooltip += `NAME_1: ${props.NAME_1}<br/>`;
            if (props.VARNAME_1 && props.VARNAME_1 !== 'NA') tooltip += `VARNAME_1: ${props.VARNAME_1}<br/>`;
            if (props.GID_2) tooltip += `GID_2: ${props.GID_2}<br/>`;
            if (props.NAME_2) tooltip += `NAME_2: ${props.NAME_2}<br/>`;
            if (props.VARNAME_2 && props.VARNAME_2 !== 'NA') tooltip += `VARNAME_2: ${props.VARNAME_2}<br/>`;
            if (props.GID_3) tooltip += `GID_3: ${props.GID_3}<br/>`;
            if (props.NAME_3) tooltip += `NAME_3: ${props.NAME_3}<br/>`;
            if (props.VARNAME_3 && props.VARNAME_3 !== 'NA') tooltip += `VARNAME_3: ${props.VARNAME_3}<br/>`;
            
            // Add DataFrame value
            if (props._dataframe_value !== undefined) tooltip += `Value: ${props._dataframe_value}<br/>`;
            if (props._dataframe_note !== undefined) tooltip += `Note: ${props._dataframe_note}<br/>`;
            
            if (tooltip.endsWith('<br/>')) {
              tooltip = tooltip.slice(0, -5);
            }
            
            // Register with multi-tooltip system
            if (tooltip) {
              registerLayerTooltip(layer, 'DataFrame', tooltip);
            }
          }
        });
        
        // Ensure static DataFrame layers are actually shown on static maps
        layer.addTo(map);
        layer._dataframeType = 'static';
        layers.dataframes.push(layer);
      }

      function createDynamicDataframe(df) {
        const geometry = resolveGeometry(df);
        if (!geometry) return;
        
        let className = 'data';
        if (df.classes) className += ' ' + df.classes;
        
        const layer = L.geoJSON(geometry, {
          style: function(feature) {
            const props = feature.properties || {};
            const dataframeData = props._dataframe_data;
            const currentYear = window.currentYear || (df.years && df.years[0]) || 2020;
            
            // Use only exact year; if missing, render fully transparent
            let value = null;
            if (dataframeData && (currentYear in dataframeData)) {
              value = dataframeData[currentYear];
            }
            
            if (value === null || value === undefined) {
              return {
                className: className,
                fillColor: '#000000',
                fillOpacity: 0.0,
                color: '#000000',
                opacity: 0.0,
                weight: 0
              };
            }
            
            const color = getDataColor(value);
            return {
              className: className,
              fillColor: color,
              fillOpacity: 0.85,
              color: color,
              opacity: 1.0,
              weight: 1
            };
          },
          onEachFeature: function(feature, layer) {
            const props = feature.properties || {};
            
            // For dynamic DataFrames, get the initial year's value
            const currentYear = window.currentYear || (df.years && df.years[0]) || 2020;
            const dataframeData = props._dataframe_data;
            let value = null;
            if (dataframeData && (currentYear in dataframeData)) {
              value = dataframeData[currentYear];
            }
            
            let tooltip = '';
            let topName = '';
            if (props.NAME_3) topName = props.NAME_3;
            else if (props.NAME_2) topName = props.NAME_2;
            else if (props.NAME_1) topName = props.NAME_1;
            else if (props.COUNTRY) topName = props.COUNTRY;
            
            if (topName) tooltip += `<b>${topName}</b><br/>`;
            
            // Add GADM properties
            if (props.GID_0) tooltip += `GID_0: ${props.GID_0}<br/>`;
            if (props.COUNTRY) tooltip += `COUNTRY: ${props.COUNTRY}<br/>`;
            if (props.GID_1) tooltip += `GID_1: ${props.GID_1}<br/>`;
            if (props.NAME_1) tooltip += `NAME_1: ${props.NAME_1}<br/>`;
            if (props.VARNAME_1 && props.VARNAME_1 !== 'NA') tooltip += `VARNAME_1: ${props.VARNAME_1}<br/>`;
            if (props.GID_2) tooltip += `GID_2: ${props.GID_2}<br/>`;
            if (props.NAME_2) tooltip += `NAME_2: ${props.NAME_2}<br/>`;
            if (props.VARNAME_2 && props.VARNAME_2 !== 'NA') tooltip += `VARNAME_2: ${props.VARNAME_2}<br/>`;
            if (props.GID_3) tooltip += `GID_3: ${props.GID_3}<br/>`;
            if (props.NAME_3) tooltip += `NAME_3: ${props.NAME_3}<br/>`;
            if (props.VARNAME_3 && props.VARNAME_3 !== 'NA') tooltip += `VARNAME_3: ${props.VARNAME_3}<br/>`;
            
            // Add DataFrame value for the initial year
            if (value !== null && value !== undefined) {
              tooltip += `Value (${currentYear}): ${value}<br/>`;
            }
            
            // Add note for current year if available
            const notes = props._dataframe_notes || {};
            if (notes && (currentYear in notes)) {
              tooltip += `Note (${currentYear}): ${notes[currentYear]}<br/>`;
            }
            
            if (tooltip.endsWith('<br/>')) {
              tooltip = tooltip.slice(0, -5);
            }
            
            // Register with multi-tooltip system
            if (tooltip) {
              registerLayerTooltip(layer, 'DataFrame', tooltip);
            }
          }
        });
        
        layer._dataframeType = 'dynamic';
        layer._dataframeYears = df.years;
        layers.dataframes.push(layer);
      }

      function renderStatic() {
        const flags = payload.flags.flags;
        for (const f of flags) {
          const geometry = resolveGeometry(f);
          if (!geometry) continue;
          
          const built = buildFlagLayers(f, geometry, { label: f.label });
          for (const l of built) {
            l.addTo(map);
            layers.flags.push(l);
          }
          if (DEBUG_CENTROIDS && f.centroid) {
            const debugMarker = L.circleMarker(f.centroid, {
              radius: 8,
              color: 'red',
              fillColor: 'yellow',
              fillOpacity: 0.8,
              weight: 2
            }).addTo(map).bindTooltip(`Centroid: ${f.label}<br>Lat: ${f.centroid[0].toFixed(4)}<br>Lng: ${f.centroid[1].toFixed(4)}`);
            layers.flags.push(debugMarker);
          }
        }
        updateFlagLabelScales();
      }

      function renderRivers(year = null) {
        const rivers = year !== null ? filterByPeriod(payload.rivers, year) : payload.rivers;
        for (const r of rivers) {
          const geometry = resolveGeometry(r);
          if (!geometry) continue;
          let className = 'river';
          if (r.classes) className += ' ' + r.classes;
          const riverTooltip = `${r.label}${r.note ? ' — ' + r.note : ''}`;
          
          const layer = L.geoJSON(geometry, {
            style: { className },
            onEachFeature: function(feature, subLayer) {
              // Register each sublayer with multi-tooltip system
              registerLayerTooltip(subLayer, 'River', riverTooltip, r.hover_radius);
            }
          }).addTo(map);
          
          layers.rivers.push(layer);
          
          // Add labels if show_label is true
          if (r.show_label) {
            const nLabels = r.n_labels || 1;
            
            // Create labels at positions k/(n+1) where k = 1, 2, ..., n
            for (let k = 1; k <= nLabels; k++) {
              const fraction = k / (nLabels + 1);
              const labelInfo = calculateRiverLabelPosition(geometry, r.label, fraction);
              
              if (labelInfo) {
                let labelClassName = 'river-label-container';
                let innerClassName = 'text-label river-label';
                if (r.classes) innerClassName += ' ' + r.classes;
                
                // Use divIcon with nested divs for rotation and translation
                // Outer div: rotation (inline), Inner div: translation (CSS customizable)
                const labelDiv = L.divIcon({
                  html: `<div style="transform: rotate(${labelInfo.angle}deg);"><div class="${innerClassName}" style="transform: translateY(-12px); white-space: nowrap;">${r.label}</div></div>`,
                  className: labelClassName,
                  iconSize: [1, 1],
                  iconAnchor: [0, 0]
                });
                
                const labelLayer = L.marker([labelInfo.position[0], labelInfo.position[1]], { icon: labelDiv }).addTo(map);
                layers.rivers.push(labelLayer);
              }
            }
          }
        }
      }

      function renderPaths(year = null) {
        const paths = year !== null ? filterByPeriod(payload.paths, year) : payload.paths;
        for (const p of paths) {
          const latlngs = p.coords.map(([lat, lon]) => [lat, lon]);
          let className = 'path';
          if (p.classes) className += ' ' + p.classes;
          const layer = L.polyline(latlngs, { className }).addTo(map);
          // Register with multi-tooltip system
          const pathTooltip = `${p.label}${p.note ? ' — ' + p.note : ''}`;
          registerLayerTooltip(layer, 'Path', pathTooltip, p.hover_radius);
          layers.paths.push(layer);
          
          // Add labels if show_label is true
          if (p.show_label && latlngs.length > 0) {
            // Calculate total distance along the path
            let totalDistance = 0;
            const distances = [0];
            for (let i = 1; i < latlngs.length; i++) {
              const d = Math.sqrt(
                Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
              );
              totalDistance += d;
              distances.push(totalDistance);
            }
            
            const nLabels = p.n_labels || 1;
            
            // Create labels at positions k/(n+1) where k = 1, 2, ..., n
            for (let k = 1; k <= nLabels; k++) {
              const targetDistance = (k / (nLabels + 1)) * totalDistance;
              
              let labelPoint = latlngs[0];
              let labelSegmentIndex = 0;
              
              // Find the segment containing this position
              for (let i = 1; i < distances.length; i++) {
                if (distances[i] >= targetDistance) {
                  const segmentStart = distances[i - 1];
                  const segmentEnd = distances[i];
                  const t = (targetDistance - segmentStart) / (segmentEnd - segmentStart);
                  
                  // Interpolate between points
                  labelPoint = [
                    latlngs[i-1][0] + t * (latlngs[i][0] - latlngs[i-1][0]),
                    latlngs[i-1][1] + t * (latlngs[i][1] - latlngs[i-1][1])
                  ];
                  labelSegmentIndex = i - 1;
                  break;
                }
              }
              
              // Calculate rotation angle based on nearby path segments
              const estimatedLabelLength = p.label.length * 0.15;
              
              let startPoint = null;
              let endPoint = null;
              
              // Search backwards
              let accumulatedDist = 0;
              for (let i = labelSegmentIndex; i >= 0 && accumulatedDist < estimatedLabelLength; i--) {
                startPoint = latlngs[i];
                if (i > 0) {
                  accumulatedDist += Math.sqrt(
                    Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                    Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
                  );
                }
              }
              
              // Search forwards
              accumulatedDist = 0;
              for (let i = labelSegmentIndex + 1; i < latlngs.length && accumulatedDist < estimatedLabelLength; i++) {
                endPoint = latlngs[i];
                accumulatedDist += Math.sqrt(
                  Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                  Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
                );
              }
              
              // Calculate angle
              let angle = 0;
              if (startPoint && endPoint) {
                const dx = endPoint[1] - startPoint[1];
                const dy = endPoint[0] - startPoint[0];
                angle = -Math.atan2(dy, dx) * 180 / Math.PI;
                
                if (angle > 90) angle -= 180;
                if (angle < -90) angle += 180;
              }
              
              let labelClassName = 'path-label-container';
              let innerClassName = 'text-label path-label';
              if (p.classes) innerClassName += ' ' + p.classes;
              
              const labelDiv = L.divIcon({
                html: `<div style="transform: rotate(${angle}deg);"><div class="${innerClassName}" style="transform: translateY(-8px); white-space: nowrap;">${p.label}</div></div>`,
                className: labelClassName,
                iconSize: [1, 1],
                iconAnchor: [0, 0]
              });
              
              const labelLayer = L.marker(labelPoint, { icon: labelDiv }).addTo(map);
              layers.paths.push(labelLayer);
            }
          }
        }
      }

      function renderPoints(year = null) {
        const points = year !== null ? filterByPeriod(payload.points, year) : payload.points;
        for (const p of points) {
          let markerOptions = {};
          if (p.icon) {
            const iconOptions = {
              iconUrl: p.icon.iconUrl,
              iconSize: p.icon.iconSize,
              iconAnchor: p.icon.iconAnchor,
              popupAnchor: p.icon.popupAnchor
            };
            if (p.icon.shadowUrl) iconOptions.shadowUrl = p.icon.shadowUrl;
            if (p.icon.shadowSize) iconOptions.shadowSize = p.icon.shadowSize;
            if (p.icon.shadowAnchor) iconOptions.shadowAnchor = p.icon.shadowAnchor;
            markerOptions.icon = L.icon(iconOptions);
          } else {
            markerOptions.icon = defaultPointIcon(p.classes);
          }
          
          // Apply classes to marker if present
          let className = 'point';
          if (p.classes) className += ' ' + p.classes;
          markerOptions.className = className;
          
          const layer = L.marker([p.position[0], p.position[1]], markerOptions).addTo(map);
          // Register with multi-tooltip system
          const pointTooltip = `${p.label}${p.note ? ' — ' + p.note : ''}`;
          registerLayerTooltip(layer, 'Point', pointTooltip, p.hover_radius);
          layers.points.push(layer);
          
          // Add label next to point if show_label is true
          if (p.show_label) {
            // Apply classes to label if present
            let labelClassName = 'point-label-container';
            let innerClassName = 'text-label point-label';
            if (p.classes) innerClassName += ' ' + p.classes;
            
            // Use divIcon with nested divs for rotation and translation
            // Outer div: rotation (inline, can be customized), Inner div: translation (CSS customizable)
            const rotationAngle = p.rotation || 0; // Default to 0 degrees if no rotation specified
            const labelDiv = L.divIcon({
              html: `<div style="transform: rotate(${rotationAngle}deg);"><div class="${innerClassName}" style="transform: translateX(9px); white-space: nowrap;">${p.label}</div></div>`,
              className: labelClassName,
              iconSize: [1, 1],
              iconAnchor: [0, 0]
            });
            
            const labelLayer = L.marker([p.position[0], p.position[1]], { icon: labelDiv }).addTo(map);
            layers.points.push(labelLayer);
          }
        }
      }

      function renderTexts(year = null) {
        const texts = year !== null ? filterByPeriod(payload.texts, year) : payload.texts;
        for (const t of texts) {
          let labelClassName = 'text-label-container';
          let innerClassName = 'text-label';
          if (t.classes) innerClassName += ' ' + t.classes;
          
          // Use divIcon with nested divs for rotation and translation
          // Outer div: rotation (inline, can be customized), Inner div: translation (CSS customizable)
          const rotationAngle = t.rotation || 0; // Default to 0 degrees if no rotation specified
          const labelDiv = L.divIcon({
            html: `<div style="transform: rotate(${rotationAngle}deg);"><div class="${innerClassName}" style="transform: translateY(0px); white-space: nowrap;">${t.label}</div></div>`,
            className: labelClassName,
            iconSize: [1, 1],
            iconAnchor: [0, 0]
          });
          
          const layer = L.marker([t.position[0], t.position[1]], { icon: labelDiv }).addTo(map);
          // Register with multi-tooltip system if note is present
          if (t.note) {
            const textTooltip = `${t.label} — ${t.note}`;
            registerLayerTooltip(layer, 'Text', textTooltip);
          }
          layers.texts.push(layer);
        }
      }

      function renderTitleBoxes(year = null) {
        const titleBoxes = year !== null ? filterByPeriod(payload.title_boxes, year) : payload.title_boxes;
        const titleContent = document.getElementById('title-content');
        
        // Create the content structure (search wrapper is outside title-content so it is not replaced)
        let content = '';
        
        // Add coordinate display first
        content += '<div id="coordinate-display"><span id="coordinate-label">Center: </span><span id="coordinates">Loading...</span></div>';
        
        // Add title boxes
        content += titleBoxes.map(tb => `<div class="title-box">${tb.html}</div>`).join('');
        
        // Add layer selector if there are base options
        if (payload.base_options && payload.base_options.length > 0) {
          content += '<div id="layer-selector"><label for="baseLayer">Basemap</label><select id="baseLayer"></select></div>';
        }
        
        // Add colormap if available
        if (payload.colormap_svg) {
          content += '<div id="colormap"></div>';
        }
        
        titleContent.innerHTML = content;
        
        // Re-setup the layer selector and colormap after updating HTML
        if (payload.base_options && payload.base_options.length > 0) {
          setupLayerSelector();
        }
        if (payload.colormap_svg) {
          setupColormap();
        }
        
        // Initialize coordinate display after title boxes are rendered
        initializeCoordinateDisplay();
      }

      function renderAdmins(year = null) {
        const admins = year !== null ? filterByPeriod(payload.admins, year) : payload.admins;
        for (const a of admins) {
          const geometry = resolveGeometry(a);
          if (!geometry) continue;
          
          // Create style for admin regions
          let className = 'admin';
          if (a.classes) className += ' ' + a.classes;
          
          // Add each feature with its own tooltip and color
          const layer = L.geoJSON(geometry, {
            style: function(feature) {
              const props = feature.properties || {};
              const color = props._color;
              return {
                className: className,
                fillColor: color || '#cccccc',
                fillOpacity: 0.35,
                color: color || '#666666',
                weight: 1
              };
            },
            onEachFeature: function(feature, layer) {
              const props = feature.properties || {};
              
              // Create tooltip with all GADM properties in specified order
              let tooltip = '';
              
              // Find the highest level name to bold at the top
              let topName = '';
              if (props.NAME_3) topName = props.NAME_3;
              else if (props.NAME_2) topName = props.NAME_2;
              else if (props.NAME_1) topName = props.NAME_1;
              else if (props.COUNTRY) topName = props.COUNTRY;
              
              if (topName) tooltip += `<b>${topName}</b><br/>`;
              
              // Add all fields in the specified order
              if (props.GID_0) tooltip += `GID_0: ${props.GID_0}<br/>`;
              if (props.COUNTRY) tooltip += `COUNTRY: ${props.COUNTRY}<br/>`;
              if (props.GID_1) tooltip += `GID_1: ${props.GID_1}<br/>`;
              if (props.NAME_1) tooltip += `NAME_1: ${props.NAME_1}<br/>`;
              if (props.VARNAME_1 && props.VARNAME_1 !== 'NA') tooltip += `VARNAME_1: ${props.VARNAME_1}<br/>`;
              if (props.GID_2) tooltip += `GID_2: ${props.GID_2}<br/>`;
              if (props.NAME_2) tooltip += `NAME_2: ${props.NAME_2}<br/>`;
              if (props.VARNAME_2 && props.VARNAME_2 !== 'NA') tooltip += `VARNAME_2: ${props.VARNAME_2}<br/>`;
              if (props.GID_3) tooltip += `GID_3: ${props.GID_3}<br/>`;
              if (props.NAME_3) tooltip += `NAME_3: ${props.NAME_3}<br/>`;
              if (props.VARNAME_3 && props.VARNAME_3 !== 'NA') tooltip += `VARNAME_3: ${props.VARNAME_3}<br/>`;
              
              // Remove trailing <br/> if present
              if (tooltip.endsWith('<br/>')) {
                tooltip = tooltip.slice(0, -5);
              }
              
              // Register with multi-tooltip system
              if (tooltip) {
                registerLayerTooltip(layer, 'Admin Region', tooltip);
              }

              layer.on('mousemove', function(e) {
                if (!window.parent) return;
                const originalEvent = (e && e.originalEvent) ? e.originalEvent : {};
                const isAddSweep = !!(originalEvent.ctrlKey || originalEvent.metaKey);
                const isRemoveSweep = !!originalEvent.altKey;
                if (!isAddSweep && !isRemoveSweep) return;
                const pickedGid = normalizeGadmCode(
                  props.GID_3 || props.GID_2 || props.GID_1 || props.GID_0 || ''
                );
                if (!pickedGid) return;
                const pickedName = props.NAME_3 || props.NAME_2 || props.NAME_1 || props.COUNTRY || '';
                window.parent.postMessage({
                  type: 'mapFeaturePick',
                  featureType: 'gadm',
                  gid: pickedGid,
                  name: pickedName,
                  hoverMode: isRemoveSweep ? 'remove' : 'add'
                }, '*');
              });

              layer.on('click', function(e) {
                if (!window.parent) return;
                const pickedGid = normalizeGadmCode(
                  props.GID_3 || props.GID_2 || props.GID_1 || props.GID_0 || ''
                );
                if (!pickedGid) return;
                const pickedName = props.NAME_3 || props.NAME_2 || props.NAME_1 || props.COUNTRY || '';
                const originalEvent = (e && e.originalEvent) ? e.originalEvent : {};
                window.parent.postMessage({
                  type: 'mapFeaturePick',
                  featureType: 'gadm',
                  gid: pickedGid,
                  name: pickedName,
                  shiftKey: !!originalEvent.shiftKey,
                  ctrlKey: !!originalEvent.ctrlKey,
                  metaKey: !!originalEvent.metaKey,
                  altKey: !!originalEvent.altKey,
                  multiSelect: !!(originalEvent.shiftKey || originalEvent.ctrlKey || originalEvent.metaKey),
                }, '*');
              });
            }
          });
          
          layer.addTo(map);
          layers.admins.push(layer);
        }
      }

      function renderAdminRivers(year = null) {
        const adminRivers = year !== null ? filterByPeriod(payload.admin_rivers, year) : payload.admin_rivers;
        for (const ar of adminRivers) {
          const geometry = resolveGeometry(ar);
          if (!geometry) continue;
          
          // Create style for admin rivers
          let className = 'admin-river';
          if (ar.classes) className += ' ' + ar.classes;
          
          // Add each feature with its own tooltip
          const layer = L.geoJSON(geometry, {
            style: function(feature) {
              const props = feature.properties || {};
              const source = props._source;
              // Different colors for different sources
              let color = '#0066cc'; // Default blue
              if (source === 'naturalearth') color = '#0066cc'; // Blue for Natural Earth
              else if (source === 'overpass') color = '#cc6600'; // Orange for Overpass
              
              return {
                className: className,
                color: color,
                weight: 2,
                opacity: 0.8
              };
            },
            onEachFeature: function(feature, layer) {
              const props = feature.properties || {};
              
              // Create tooltip with source information and available properties
              let tooltip = '';
              
              // Add source information
              const source = props._source;
              if (source === 'naturalearth') {
                tooltip += `<b>Natural Earth River</b><br/>`;
                if (props._ne_id) tooltip += `NE ID: ${props._ne_id}<br/>`;
              } else if (source === 'overpass') {
                tooltip += `<b>Overpass River</b><br/>`;
                if (props._filename) tooltip += `File: ${props._filename}<br/>`;
              }
              
              // Add name fields if available
              if (props.name) tooltip += `Name: ${props.name}<br/>`;
              if (props.NAME) tooltip += `NAME: ${props.NAME}<br/>`;
              if (props.NAME_EN) tooltip += `NAME_EN: ${props.NAME_EN}<br/>`;
              if (props.NAME_LOC) tooltip += `NAME_LOC: ${props.NAME_LOC}<br/>`;
              if (props.NAME_ALT) tooltip += `NAME_ALT: ${props.NAME_ALT}<br/>`;
              if (props.NAME_OTHER) tooltip += `NAME_OTHER: ${props.NAME_OTHER}<br/>`;
              
              // Add other relevant properties
              if (props.scalerank) tooltip += `Scale Rank: ${props.scalerank}<br/>`;
              if (props.featurecla) tooltip += `Feature Class: ${props.featurecla}<br/>`;
              if (props.min_zoom) tooltip += `Min Zoom: ${props.min_zoom}<br/>`;
              
              // Remove trailing <br/> if present
              if (tooltip.endsWith('<br/>')) {
                tooltip = tooltip.slice(0, -5);
              }
              
              // Register with multi-tooltip system (default hover radius for admin rivers)
              if (tooltip) {
                registerLayerTooltip(layer, 'Admin River', tooltip, 10);
              }

              layer.on('click', function() {
                if (!window.parent) return;
                const riverId = extractRiverIdFromProps(props);
                if (!riverId) return;
                window.parent.postMessage({
                  type: 'mapFeaturePick',
                  featureType: 'river',
                  id: riverId,
                  source_type: props._source || 'naturalearth',
                  name: props.name || props.NAME || ''
                }, '*');
              });
            }
          });
          
          layer.addTo(map);
          layers.admin_rivers.push(layer);
          
          // Add labels if requested
          if (ar.show_label && ar.n_labels > 0) {
            const nLabels = ar.n_labels || 1;
            
            for (let k = 1; k <= nLabels; k++) {
              const fraction = k / (nLabels + 1);
              
              // Calculate label position and rotation for each river feature
              if (geometry.features) {
                for (const feature of geometry.features) {
                  const labelInfo = calculateRiverLabelPosition(feature, feature.properties?.name || 'River', fraction);
                  if (labelInfo && labelInfo.position) {
                    const innerClassName = 'admin-river-label';
                    const labelDiv = L.divIcon({
                      html: `<div style="transform: rotate(${labelInfo.angle}deg);"><div class="${innerClassName}" style="transform: translateY(-12px); white-space: nowrap;">${feature.properties?.name || 'River'}</div></div>`,
                      className: 'admin-river-label-container',
                      iconSize: [1, 1],
                      iconAnchor: [0, 0]
                    });
                    
                    const labelLayer = L.marker(labelInfo.position, { icon: labelDiv }).addTo(map);
                    labelLayer._adminRiverData = { period: ar.period };
                    layers.admin_rivers.push(labelLayer);
                  }
                }
              }
            }
          }
        }
      }

      function renderData(year = null) {
        const data = year !== null ? filterByPeriod(payload.data, year) : payload.data;
        for (const d of data) {
          const geometry = resolveGeometry(d);
          if (!geometry) continue;
          
          let className = 'data';
          if (d.classes) className += ' ' + d.classes;
          
          const layer = L.geoJSON(geometry, {
            style: function(feature) {
              const props = feature.properties || {};
              const dataIndex = d.data_index || 0;
              const color = (props._data_colors && props._data_colors[dataIndex]) || d.color || '#cccccc';
              return {
                className: className,
                fillColor: color,
                fillOpacity: 0.85,
                color: color,
                weight: 1
              };
            },
            onEachFeature: function(feature, layer) {
              const props = feature.properties || {};
              const dataIndex = d.data_index || 0;
              
              let tooltip = '';
              let topName = '';
              if (props.NAME_3) topName = props.NAME_3;
              else if (props.NAME_2) topName = props.NAME_2;
              else if (props.NAME_1) topName = props.NAME_1;
              else if (props.COUNTRY) topName = props.COUNTRY;
              
              if (topName) tooltip += `<b>${topName}</b><br/>`;
              
              if (props.GID_0) tooltip += `GID_0: ${props.GID_0}<br/>`;
              if (props.COUNTRY) tooltip += `COUNTRY: ${props.COUNTRY}<br/>`;
              if (props.GID_1) tooltip += `GID_1: ${props.GID_1}<br/>`;
              if (props.NAME_1) tooltip += `NAME_1: ${props.NAME_1}<br/>`;
              if (props.VARNAME_1 && props.VARNAME_1 !== 'NA') tooltip += `VARNAME_1: ${props.VARNAME_1}<br/>`;
              if (props.GID_2) tooltip += `GID_2: ${props.GID_2}<br/>`;
              if (props.NAME_2) tooltip += `NAME_2: ${props.NAME_2}<br/>`;
              if (props.VARNAME_2 && props.VARNAME_2 !== 'NA') tooltip += `VARNAME_2: ${props.VARNAME_2}<br/>`;
              if (props.GID_3) tooltip += `GID_3: ${props.GID_3}<br/>`;
              if (props.NAME_3) tooltip += `NAME_3: ${props.NAME_3}<br/>`;
              if (props.VARNAME_3 && props.VARNAME_3 !== 'NA') tooltip += `VARNAME_3: ${props.VARNAME_3}<br/>`;
              
              // Get the specific value for this data element
              const value = (props._data_values && props._data_values[dataIndex]) || d.value;
              if (value !== undefined) tooltip += `Value: ${value}<br/>`;
              
              if (tooltip.endsWith('<br/>')) {
                tooltip = tooltip.slice(0, -5);
              }
              
              // Register with multi-tooltip system
              if (tooltip) {
                registerLayerTooltip(layer, 'Data', tooltip);
              }
            }
          });
          
          layer.addTo(map);
          layers.data.push(layer);
        }
      }

      function clearFlagLayers() {
        for (const l of layers.flags) { map.removeLayer(l); }
        layers.flags = [];
      }

      function clearAllLayers() {
        for (const l of layers.flags) { map.removeLayer(l); }
        for (const l of layers.rivers) { map.removeLayer(l); }
        for (const l of layers.paths) { map.removeLayer(l); }
        for (const l of layers.points) { map.removeLayer(l); }
        for (const l of layers.texts) { map.removeLayer(l); }
        for (const l of layers.admins) { map.removeLayer(l); }
        for (const l of layers.admin_rivers) { map.removeLayer(l); }
        for (const l of layers.data) { map.removeLayer(l); }
        for (const l of layers.dataframes) { map.removeLayer(l); }
        layers.flags = [];
        layers.rivers = [];
        layers.paths = [];
        layers.points = [];
        layers.texts = [];
        layers.admins = [];
        layers.admin_rivers = [];
        layers.data = [];
        layers.dataframes = [];
      }

      function renderDynamic(year) {
        // Performance optimization: only update if year actually changed
        if (window.lastRenderedYear === year) return;
        window.lastRenderedYear = year;
        
        // Create all layers on first call
        createAllLayers();
        
        // Find closest snapshot at or before year
        const snapshots = payload.flags.snapshots;
        let current = snapshots[0];
        for (const s of snapshots) {
          if (s.year <= year) current = s;
        }
        
        // Update flag visibility based on current snapshot
        for (const layer of layers.flags) {
          if (layer._flagData) {
            const shouldShow = layer._flagData.snapshot === current.year;
            setLayerVisibility(layer, shouldShow);
          }
        }
        
        // Update other layer types based on period filtering
        updateLayerVisibility(layers.rivers, year, '_riverData');
        updateLayerVisibility(layers.paths, year, '_pathData');
        updateLayerVisibility(layers.points, year, '_pointData');
        updateLayerVisibility(layers.texts, year, '_textData');
        updateLayerVisibility(layers.admins, year, '_adminData');
        updateLayerVisibility(layers.admin_rivers, year, '_adminRiverData');
        updateLayerVisibility(layers.data, year, '_dataData');
        updateDataframeLayers(year);
        
        // Update title boxes
        renderTitleBoxes(year);
        scheduleDeclutter();
      }

      function updateLayerVisibility(layerArray, year, dataProperty) {
        for (const layer of layerArray) {
          const data = layer[dataProperty];
          if (data && data.period) {
            const [start, end] = data.period;
            const shouldShow = year >= start && year < end;
            setLayerVisibility(layer, shouldShow);
          } else {
            // No period means always visible
            setLayerVisibility(layer, true);
          }
        }
      }

      function updateDataframeLayers(year) {
        window.currentYear = year; // Store current year globally
        
        for (const layer of layers.dataframes) {
          if (layer._dataframeType === 'dynamic') {
            // Update colors based on current year by re-styling the layer
            layer.eachLayer(function(feature) {
              const props = feature.feature.properties || {};
              const dataframeData = props._dataframe_data;
              
              if (!dataframeData) return;
              
              // Use only exact year; if missing, render fully transparent
              let value = null;
              if (year in dataframeData) {
                value = dataframeData[year];
              }
              
              if (value === null || value === undefined) {
                feature.setStyle({
                  fillColor: '#000000',
                  fillOpacity: 0.0,
                  color: '#000000',
                  opacity: 0.0,
                  weight: 0
                });
              } else {
                const color = getDataColor(value);
                feature.setStyle({
                  fillColor: color,
                  fillOpacity: 0.85,
                  color: color,
                  opacity: 1.0,
                  weight: 1
                });
              }
              
              // Update tooltip with current year's data if present
              if (value !== null && value !== undefined) {
                let tooltip = '';
                let topName = '';
                if (props.NAME_3) topName = props.NAME_3;
                else if (props.NAME_2) topName = props.NAME_2;
                else if (props.NAME_1) topName = props.NAME_1;
                else if (props.COUNTRY) topName = props.COUNTRY;
                
                if (topName) tooltip += `<b>${topName}</b><br/>`;
                
                // Add GADM properties
                if (props.GID_0) tooltip += `GID_0: ${props.GID_0}<br/>`;
                if (props.COUNTRY) tooltip += `COUNTRY: ${props.COUNTRY}<br/>`;
                if (props.GID_1) tooltip += `GID_1: ${props.GID_1}<br/>`;
                if (props.NAME_1) tooltip += `NAME_1: ${props.NAME_1}<br/>`;
                if (props.VARNAME_1 && props.VARNAME_1 !== 'NA') tooltip += `VARNAME_1: ${props.VARNAME_1}<br/>`;
                if (props.GID_2) tooltip += `GID_2: ${props.GID_2}<br/>`;
                if (props.NAME_2) tooltip += `NAME_2: ${props.NAME_2}<br/>`;
                if (props.VARNAME_2 && props.VARNAME_2 !== 'NA') tooltip += `VARNAME_2: ${props.VARNAME_2}<br/>`;
                if (props.GID_3) tooltip += `GID_3: ${props.GID_3}<br/>`;
                if (props.NAME_3) tooltip += `NAME_3: ${props.NAME_3}<br/>`;
                if (props.VARNAME_3 && props.VARNAME_3 !== 'NA') tooltip += `VARNAME_3: ${props.VARNAME_3}<br/>`;
                
                // Add current year's data value
                tooltip += `Value (${year}): ${value}<br/>`;
                
                // Add note if available for current year
                const notes = props._dataframe_notes || {};
                if (notes && (year in notes)) {
                  tooltip += `Note (${year}): ${notes[year]}<br/>`;
                }
                
                if (tooltip.endsWith('<br/>')) {
                  tooltip = tooltip.slice(0, -5);
                }
                
                // Update the multi-tooltip registration for the current year
                registerLayerTooltip(feature, 'DataFrame', tooltip);
              }
            });
            
            setLayerVisibility(layer, true); // DataFrames are always visible
          }
        }
      }

      function getDataColor(value) {
        // Use colormap info from backend if available
        if (payload.colormap_info && payload.colormap_info.colors && payload.colormap_info.vmin !== null && payload.colormap_info.vmax !== null) {
          const vmin = payload.colormap_info.vmin;
          const vmax = payload.colormap_info.vmax;
          
          let colorIndex;
          if (payload.colormap_info.has_norm && payload.colormap_info.sample_values) {
            // For Normalize objects, find the closest sample value
            const sampleValues = payload.colormap_info.sample_values;
            
            let closestIndex = 0;
            let closestDistance = Math.abs(value - sampleValues[0]);
            for (let i = 1; i < sampleValues.length; i++) {
              const distance = Math.abs(value - sampleValues[i]);
              if (distance < closestDistance) {
                closestDistance = distance;
                closestIndex = i;
              }
            }
            
            colorIndex = closestIndex;
          } else {
            // Linear normalization
            const normalized = Math.min(1, Math.max(0, (value - vmin) / (vmax - vmin)));
            colorIndex = Math.floor(normalized * 255);
          }
          
          // Get color from the user's colormap
          const color = payload.colormap_info.colors[colorIndex];
          
          if (color && color.length >= 3) {
            const r = Math.round(color[0] * 255);
            const g = Math.round(color[1] * 255);
            const b = Math.round(color[2] * 255);
            return `rgb(${r}, ${g}, ${b})`;
          }
        }
        
        // Fallback to default yellow-orange-red colormap
        const normalized = Math.min(1, Math.max(0, value / 300)); // Assume max value of 300
        
        if (normalized < 0.5) {
          // Yellow to orange
          const t = normalized * 2;
          const r = Math.round(255 * (1 - t * 0.5));
          const g = Math.round(255 * (1 - t * 0.2));
          const b = 0;
          return `rgb(${r}, ${g}, ${b})`;
        } else {
          // Orange to red
          const t = (normalized - 0.5) * 2;
          const r = 255;
          const g = Math.round(255 * (0.8 - t * 0.8));
          const b = 0;
          return `rgb(${r}, ${g}, ${b})`;
        }
      }

      function setupLayerSelector() {
        const select = document.getElementById('baseLayer');
        
        // Add "None" option
        const noneOption = document.createElement('option');
        noneOption.value = 'none';
        noneOption.textContent = 'None';
        select.appendChild(noneOption);
        
        // Add base layer options; reflect the layer currently shown (the title
        // panel is rebuilt as the time slider moves).
        for (const option of payload.base_options || []) {
          const optionElement = document.createElement('option');
          optionElement.value = option.name;
          optionElement.textContent = option.name;
          if (currentBaseLayer && baseLayers[option.name] === currentBaseLayer) {
            optionElement.selected = true;
          }
          select.appendChild(optionElement);
        }
        if (!currentBaseLayer) {
          select.selectedIndex = 0; // "None"
        }
        
        // Handle layer changes
        select.addEventListener('change', function() {
          // Remove current layer
          if (currentBaseLayer) {
            map.removeLayer(currentBaseLayer);
            currentBaseLayer = null;
          }
          
          // Add new layer
          if (this.value !== 'none' && baseLayers[this.value]) {
            currentBaseLayer = baseLayers[this.value];
            currentBaseLayer.addTo(map);
          }
        });
      }

      function getCentroidFromCoords(coords, geoJsonOrder) {
        if (!coords || coords.length === 0) return null;
        let lat = 0, lng = 0;
        for (let i = 0; i < coords.length; i++) {
          const c = coords[i];
          if (geoJsonOrder) {
            lng += c[0];
            lat += c[1];
          } else {
            lat += c[0];
            lng += c[1];
          }
        }
        return [lat / coords.length, lng / coords.length];
      }

      function getCentroidFromGeometry(geom) {
        if (!geom || !geom.coordinates) return null;
        const c = geom.coordinates;
        if (geom.type === 'Point') return [c[1], c[0]];
        if (geom.type === 'MultiPoint' || geom.type === 'LineString') {
          return getCentroidFromCoords(c, true);
        }
        if (geom.type === 'MultiLineString') {
          let all = [];
          for (let i = 0; i < c.length; i++) all = all.concat(c[i]);
          return getCentroidFromCoords(all, true);
        }
        if (geom.type === 'Polygon') {
          return getCentroidFromCoords(c[0], true);
        }
        if (geom.type === 'MultiPolygon') {
          return getCentroidFromCoords(c[0][0], true);
        }
        return null;
      }

      function setupSearch() {
        const featuresContainer = document.getElementById('search-features-container');
        const geocoderContainer = document.getElementById('search-geocoder-container');
        if (!featuresContainer && !geocoderContainer) return;

        const searchableFeatures = [];
        const add = (label, lat, lng, type, note) => {
          if (label && lat != null && lng != null) {
            const searchText = note ? (label + ' — ' + note) : label;
            searchableFeatures.push({ label: String(label), lat, lng, type: type || 'Feature', note: note || '', searchText });
          }
        };

        for (const p of payload.points || []) {
          if (p.position) add(p.label, p.position[0], p.position[1], 'Point', p.note);
        }
        for (const t of payload.texts || []) {
          if (t.position) add(t.label, t.position[0], t.position[1], 'Text', t.note);
        }
        for (const p of payload.paths || []) {
          if (p.coords && p.coords.length) {
            const cen = getCentroidFromCoords(p.coords, false);
            if (cen) add(p.label, cen[0], cen[1], 'Path', p.note);
          }
        }
        for (const r of payload.rivers || []) {
          const geometry = resolveGeometry(r);
          if (geometry) {
            const cen = getCentroidFromGeometry(geometry);
            if (cen) add(r.label, cen[0], cen[1], 'River', r.note);
          }
        }
        const flags = payload.flags && payload.flags.flags ? payload.flags.flags : (payload.flags && payload.flags.snapshots && payload.flags.snapshots[0] ? payload.flags.snapshots[0].flags : []);
        for (const f of flags || []) {
          const geometry = resolveGeometry(f);
          if (geometry) {
            const cen = getCentroidFromGeometry(geometry);
            if (cen) add(f.label, cen[0], cen[1], 'Flag', f.note);
          }
        }

        if (featuresContainer && typeof L.Control.Search !== 'undefined' && searchableFeatures.length > 0) {
          const searchLayer = L.layerGroup();
          for (const f of searchableFeatures) {
            const m = L.circleMarker([f.lat, f.lng], { radius: 0, opacity: 0, fillOpacity: 0 });
            m.options.title = f.searchText;
            searchLayer.addLayer(m);
          }
          const searchControl = new L.Control.Search({
            layer: searchLayer,
            propertyName: 'title',
            textPlaceholder: 'Find on map…',
            collapsed: false,
            initial: false,
            hideMarkerOnCollapse: true,
            marker: false
          });
          searchControl.addTo(map);
          const searchEl = searchControl.getContainer();
          if (searchEl && searchEl.parentNode) searchEl.parentNode.removeChild(searchEl);
          featuresContainer.appendChild(searchEl);
        }

        if (geocoderContainer && typeof L.Control !== 'undefined' && L.Control.Geocoder) {
          let geocoderInstance;
          const provider = (payload.geocoder_provider || 'nominatim').toLowerCase();
          const apiKey = payload.geocoder_api_key || '';
          if (provider === 'mapbox' && apiKey) {
            geocoderInstance = L.Control.Geocoder.mapbox({ apiKey: apiKey });
          } else if (provider === 'google' && apiKey) {
            geocoderInstance = L.Control.Geocoder.google({ apiKey: apiKey });
          } else if (provider === 'photon') {
            geocoderInstance = L.Control.Geocoder.photon();
          } else {
            geocoderInstance = new L.Control.Geocoder.Nominatim();
          }
          const geocoderControl = L.Control.geocoder({
            geocoder: geocoderInstance,
            defaultMarkGeocode: true,
            collapsed: false,
            placeholder: 'Find a place…'
          }).addTo(map);
          const geocoderEl = geocoderControl.getContainer();
          if (geocoderEl && geocoderEl.parentNode) geocoderEl.parentNode.removeChild(geocoderEl);
          geocoderContainer.appendChild(geocoderEl);
        }
      }

      function setupDragFunctionality() {
        const titleDiv = document.getElementById('title');
        // Translation applied on top of the panel's CSS position.
        let dx = 0, dy = 0;
        let start = null;
        let dragging = false;

        function point(e) {
          const t = e.touches ? e.touches[0] : e;
          return { x: t.clientX, y: t.clientY };
        }

        function dragStart(e) {
          // Controls inside the panel (search, basemap, links, buttons) keep working.
          if (e.target.closest('input, select, textarea, button, a, label, .search-tooltip, .leaflet-control-geocoder-alternatives')) return;
          const p = point(e);
          const rect = titleDiv.getBoundingClientRect();
          start = { x: p.x, y: p.y, dx, dy, left: rect.left - dx, top: rect.top - dy, width: rect.width, height: rect.height };
          dragging = false;
        }

        function drag(e) {
          if (!start) return;
          const p = point(e);
          const mx = p.x - start.x, my = p.y - start.y;
          // Small movements are taps or text selection, not drags.
          if (!dragging && Math.hypot(mx, my) < 4) return;
          dragging = true;
          e.preventDefault();
          titleDiv.classList.add('dragging');
          dx = Math.max(-start.left, Math.min(start.dx + mx, window.innerWidth - start.width - start.left));
          dy = Math.max(-start.top, Math.min(start.dy + my, window.innerHeight - start.height - start.top));
          titleDiv.style.transform = `translate(${dx}px, ${dy}px)`;
        }

        function dragEnd() {
          if (dragging) scheduleDeclutter();  // labels it uncovered or now covers
          start = null;
          dragging = false;
          titleDiv.classList.remove('dragging');
        }
        if (window.ResizeObserver) new ResizeObserver(() => scheduleDeclutter()).observe(titleDiv);

        titleDiv.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);
        titleDiv.addEventListener('touchstart', dragStart, { passive: true });
        document.addEventListener('touchmove', drag, { passive: false });
        document.addEventListener('touchend', dragEnd);
        titleDiv.addEventListener('dragstart', function(e) {
          e.preventDefault();
        });

        // Collapse toggle: on small screens the panel starts collapsed so the
        // map stays visible; the reader can expand it.
        const toggle = document.getElementById('title-toggle');
        const setCollapsed = (collapsed) => {
          titleDiv.classList.toggle('collapsed', collapsed);
          toggle.setAttribute('aria-expanded', String(!collapsed));
          toggle.title = collapsed ? 'Show details' : 'Hide details';
          toggle.setAttribute('aria-label', toggle.title);
        };
        toggle.addEventListener('click', () => setCollapsed(!titleDiv.classList.contains('collapsed')));
        setCollapsed(window.innerWidth < 600 || window.innerHeight < 500);
      }

      // ── Music player ────────────────────────────────────────────────────────
      // musicAudios is shared between setupMusic() and setupControls() via
      // window._updateMusicForYear so that the slider can drive the audio.
      function setupMusic() {
        if (!payload.musics || payload.musics.length === 0) return;

        const isDynamic = payload.flags.mode === 'dynamic';
        const controls = document.getElementById('controls');
        const musicEntries = [];

        payload.musics.forEach(function(musicData, idx) {
          const audio = new Audio(musicData.data_url);
          audio.preload = 'auto';

          const entry = {
            audio: audio,
            period: musicData.period,           // [y0, y1] or null
            timestamps: musicData.timestamps,   // [t0, t1] or null
            effectiveTimestamps: null,          // resolved after metadata loads
          };

          // Resolve effective timestamps once metadata (duration) is known
          audio.addEventListener('loadedmetadata', function() {
            const t0 = (musicData.timestamps !== null && musicData.timestamps !== undefined)
              ? musicData.timestamps[0] : 0;
            const t1 = (musicData.timestamps !== null && musicData.timestamps !== undefined)
              ? musicData.timestamps[1] : audio.duration;
            entry.effectiveTimestamps = [t0, t1];
            // If already playing (e.g. user clicked play before metadata loaded), seek to t0
            if (!audio.paused && audio.currentTime < t0) {
              audio.currentTime = t0;
            }
          });

          // Loop within the specified segment using timeupdate
          audio.addEventListener('timeupdate', function() {
            if (entry.effectiveTimestamps === null) return;
            const [t0, t1] = entry.effectiveTimestamps;
            if (t1 > t0 && audio.currentTime >= t1 - 0.05) {
              audio.currentTime = t0;
            }
          });

          musicEntries.push(entry);

          if (!isDynamic) {
            // Static map: show a play/pause button in the controls bar
            controls.style.display = 'flex';
            const btn = document.createElement('button');
            btn.id = 'musicPlayPause-' + idx;
            btn.textContent = '\u266a \u25b6';
            btn.title = 'Play / pause music';
            let playing = false;

            btn.addEventListener('click', function() {
              if (playing) {
                audio.pause();
                btn.textContent = '\u266a \u25b6';
                playing = false;
              } else {
                // Start from segment start if not already in the segment
                if (entry.effectiveTimestamps !== null) {
                  const [t0, t1] = entry.effectiveTimestamps;
                  if (audio.currentTime < t0 || audio.currentTime >= t1) {
                    audio.currentTime = t0;
                  }
                }
                audio.play().catch(function() {});
                btn.textContent = '\u266a \u23f8';
                playing = true;
              }
            });

            controls.appendChild(btn);
          }
        });

        if (isDynamic) {
          // Expose a function that setupControls() calls on every slider change.
          // year         – current slider year
          // isSliderPlaying – true while the slider's play interval is active
          window._updateMusicForYear = function(year, isSliderPlaying) {
            const playSpeedMs = payload.play_speed || 200;

            for (const entry of musicEntries) {
              if (entry.effectiveTimestamps === null) continue;

              const [t0, t1] = entry.effectiveTimestamps;
              const segDuration = Math.max(t1 - t0, 0.001);

              // Determine whether the current year falls inside this track's period
              const period = entry.period;
              const inPeriod = (period === null || period === undefined)
                || (year >= period[0] && year < period[1]);

              if (inPeriod) {
                // Compute expected audio position based on real-time elapsed since period start
                const y0 = (period !== null && period !== undefined) ? period[0] : year;
                const elapsedRealSecs = (year - y0) * playSpeedMs / 1000;
                const expectedPos = t0 + (elapsedRealSecs % segDuration);

                // Only seek if the discrepancy is large enough to indicate a manual drag
                // (avoids interrupting smooth natural playback during slider play)
                if (Math.abs(entry.audio.currentTime - expectedPos) > 0.5) {
                  entry.audio.currentTime = expectedPos;
                }

                if (isSliderPlaying) {
                  if (entry.audio.paused) {
                    entry.audio.play().catch(function() {});
                  }
                } else {
                  entry.audio.pause();
                }
              } else {
                if (!entry.audio.paused) {
                  entry.audio.pause();
                }
              }
            }
          };
        }
      }
      // ── End music player ────────────────────────────────────────────────────

      function setupControls() {
        const controls = document.getElementById('controls');
        if (payload.flags.mode === 'dynamic') {
          // Calculate breakpoints from all object types, not just flags
          const allPeriods = [];
          
          // Add flag periods
          if (payload.flags.breakpoints) {
            allPeriods.push(...payload.flags.breakpoints);
          }
          
          // Add periods from other object types
          for (const obj of [...(payload.rivers || []), ...(payload.paths || []), ...(payload.points || []), ...(payload.texts || []), ...(payload.title_boxes || []), ...(payload.admins || []), ...(payload.admin_rivers || []), ...(payload.data || [])]) {
            if (obj.period) {
              allPeriods.push(obj.period[0], obj.period[1]);
            }
          }
          
          // Add DataFrame years
          for (const df of payload.dataframes || []) {
            if (df.type === 'dynamic' && df.years) {
              allPeriods.push(...df.years);
            }
          }
          
          if (allPeriods.length > 0) {
            const uniquePeriods = [...new Set(allPeriods)].sort((a, b) => a - b);
            let min = uniquePeriods[0];
            let max = uniquePeriods[uniquePeriods.length - 1];
            
            // Use map limits if available (without epsilon for slider range)
            if (payload.map_limits) {
              min = payload.map_limits[0];
              max = payload.map_limits[1];
            }
            
            // Show eras only when the range reaches into BCE.
            const useEra = min < 0;
            const formatYear = (y) => {
              y = Number(y);
              if (!useEra) return String(y);
              return y < 0 ? `${-y} BCE` : `${y} CE`;
            };
            controls.innerHTML = `
              <button id="playPause" title="Play / pause" aria-label="Play">▶</button>
              <span id="yearLabel">${formatYear(min)}</span>
              <span id="startYear">${formatYear(min)}</span>
              <input type="range" id="year" min="${min}" max="${max}" step="1" value="${min}" aria-label="Year" />
              <span id="endYear">${formatYear(max)}</span>
            `;
            const input = document.getElementById('year');
            const label = document.getElementById('yearLabel');
            const playPauseBtn = document.getElementById('playPause');
            const startYearSpan = document.getElementById('startYear');
            const endYearSpan = document.getElementById('endYear');
            
            let isPlaying = false;
            let playInterval = null;
            
            input.addEventListener('input', () => {
              label.textContent = formatYear(input.value);
              renderDynamic(parseInt(input.value));
              if (window._updateMusicForYear) window._updateMusicForYear(parseInt(input.value), isPlaying);
            });

            playPauseBtn.addEventListener('click', () => {
              if (isPlaying) {
                // Pause
                clearInterval(playInterval);
                playPauseBtn.textContent = '▶';
                isPlaying = false;
                if (window._updateMusicForYear) window._updateMusicForYear(parseInt(input.value), false);
              } else {
                // Play
                playPauseBtn.textContent = '⏸';
                isPlaying = true;
                if (window._updateMusicForYear) window._updateMusicForYear(parseInt(input.value), true);
                playInterval = setInterval(() => {
                  const currentYear = parseInt(input.value);
                  if (currentYear >= max) {
                    // Reached end, stop playing
                    clearInterval(playInterval);
                    playPauseBtn.textContent = '▶';
                    isPlaying = false;
                    if (window._updateMusicForYear) window._updateMusicForYear(currentYear, false);
                  } else {
                    const newYear = currentYear + 1;
                    input.value = newYear;
                    label.textContent = formatYear(newYear);
                    renderDynamic(newYear);
                    if (window._updateMusicForYear) window._updateMusicForYear(newYear, true);
                  }
                }, payload.play_speed || 200); // Use speed from payload or default to 200ms
              }
            });

            renderDynamic(min);
            if (window._updateMusicForYear) window._updateMusicForYear(min, false);
          }
        } else {
          // Hide controls for static maps
          controls.style.display = 'none';
        }
      }

      function setupColormap() {
        const colormapDiv = document.getElementById('colormap');
        const tooltipDiv = document.getElementById('colormap-tooltip');
        
        if (payload.colormap_svg) {
          colormapDiv.innerHTML = payload.colormap_svg;
          
          // Add interactive tooltip if colormap info is available
          if (payload.colormap_info && payload.colormap_info.vmin !== null && payload.colormap_info.vmax !== null) {
            const svg = colormapDiv.querySelector('svg');
            if (svg) {
              // Find the gradient rect/image in the SVG
              const svgRect = svg.getBoundingClientRect();
              
              colormapDiv.addEventListener('mouseenter', function() {
                // Don't show tooltip on enter - let mousemove handle it
                // This way it only shows when actually over the gradient
              });
              
              colormapDiv.addEventListener('mouseleave', function() {
                tooltipDiv.style.display = 'none';
              });
              
              colormapDiv.addEventListener('mousemove', function(e) {
                const colormapRect = colormapDiv.getBoundingClientRect();
                const svgRect = svg.getBoundingClientRect();
                
                // Find the actual gradient element within the SVG
                const gradientElement = svg.querySelector('image, rect') || svg.querySelector('g');
                if (!gradientElement) return;
                
                const gradientRect = gradientElement.getBoundingClientRect();
                
                // Calculate relative position within the actual gradient bar
                const relX = e.clientX - gradientRect.left;
                const gradientWidth = gradientRect.width;
                
                // Only show tooltip if hovering over the actual gradient
                if (relX < 0 || relX > gradientWidth) {
                  tooltipDiv.style.display = 'none';
                  return;
                }
                
                // Show tooltip when hovering over gradient
                tooltipDiv.style.display = 'block';
                
                // Clamp to valid range
                const normalizedX = Math.max(0, Math.min(1, relX / gradientWidth));
                
                // Calculate value based on position
                const vmin = payload.colormap_info.vmin;
                const vmax = payload.colormap_info.vmax;
                let value;
                
                if (payload.colormap_info.has_norm && payload.colormap_info.sample_values) {
                  // For normalized colormaps, find the closest sample value
                  const sampleValues = payload.colormap_info.sample_values;
                  const sampleIndex = Math.floor(normalizedX * (sampleValues.length - 1));
                  value = sampleValues[Math.max(0, Math.min(sampleValues.length - 1, sampleIndex))];
                } else {
                  // Linear interpolation
                  value = vmin + normalizedX * (vmax - vmin);
                }
                
                // Get color for this value
                const color = getDataColor(value);
                
                // Format value with appropriate precision
                let formattedValue;
                if (Math.abs(value) >= 1000 || (Math.abs(value) < 0.01 && value !== 0)) {
                  formattedValue = value.toExponential(2);
                } else if (Math.abs(value) >= 10) {
                  formattedValue = value.toFixed(1);
                } else {
                  formattedValue = value.toFixed(3);
                }
                
                // Update tooltip content
                tooltipDiv.innerHTML = `<span class="color-sample" style="background-color: ${color};"></span>Value: ${formattedValue}`;
                
                // Position tooltip near the cursor
                tooltipDiv.style.left = (e.clientX + 15) + 'px';
                tooltipDiv.style.top = (e.clientY + 15) + 'px';
              });
            }
          }
        } else {
          colormapDiv.style.display = 'none';
        }
      }

      if (payload.flags.mode === 'static') {
        renderStatic();
        renderRivers();
        renderPaths();
        renderPoints();
        renderTexts();
        renderTitleBoxes();
        renderAdmins();
        renderAdminRivers();
        renderData();
        createAllDataframes();
      } else {
        // For dynamic maps, create all layers and show initial state
        createAllLayers();
        const snapshots = payload.flags.snapshots;
        if (snapshots && snapshots.length > 0) {
          renderDynamic(snapshots[0].year);
        }
      }
      setupControls();
      setupMusic();
      setupDragFunctionality();

      // Frame the content (when the map has no explicit zoom/focus), leaving
      // room for the title panel and the time slider.
      function fitContent(opts = {}) {
        if (!payload.fit_bounds) return;
        const bounds = L.latLngBounds(payload.fit_bounds);
        if (!bounds.isValid()) return;
        // A hidden or not-yet-laid-out frame has no size; framing then would
        // jump to max zoom. The resize handler below frames it once visible.
        const size = map.getSize();
        if (size.x < 50 || size.y < 50) return;
        const width = size.x;
        let left = 24, bottom = 24;
        if (!opts.ignorePanels) {
          const title = document.getElementById('title');
          if (title && title.offsetWidth && width > 760) left = Math.min(title.offsetWidth + 24, width * 0.22);
          const controls = document.getElementById('controls');
          if (controls && controls.style.display !== 'none' && controls.offsetHeight) bottom = controls.offsetHeight + 48;
        }
        // Tiles stay crisp at whole zoom levels, so snap to one: zoom in when
        // the content would only slightly overflow its frame, else zoom out.
        const paddingTL = L.point(left, 24), paddingBR = L.point(24, bottom);
        const snap = map.options.zoomSnap;
        map.options.zoomSnap = 0;
        const exact = map.getBoundsZoom(bounds, false, paddingTL.add(paddingBR));
        map.options.zoomSnap = snap;
        const zoom = Math.min(8, exact - Math.floor(exact) >= 0.8 ? Math.ceil(exact) : Math.floor(exact));
        const offset = paddingBR.subtract(paddingTL).divideBy(2);
        const centerPoint = map.project(bounds.getSouthWest(), zoom).add(map.project(bounds.getNorthEast(), zoom)).divideBy(2).add(offset);
        map.setView(map.unproject(centerPoint, zoom), zoom, { animate: false });
      }
      window.xatraFitContent = fitContent;
      fitContent();
      // Keep the content framed as the frame resizes (or first becomes
      // visible) until the reader moves the map themselves.
      let readerMovedMap = false;
      for (const type of ['pointerdown', 'wheel', 'touchstart', 'keydown']) {
        map.getContainer().addEventListener(type, () => { readerMovedMap = true; }, { passive: true });
      }
      map.on('resize', () => {
        if (!readerMovedMap) fitContent();
        scheduleDeclutter();
      });
      initializeCoordinateDisplay();
      updateFlagLabelScales();
      // NOTE: keep setupSearch() as the script's last line; xatra-gui matches on it.
      setupSearch();
    </script>
  </body>
  </html>
    """
)


def export_html_string(payload: Dict[str, Any] | str, css: Optional[str] = None) -> str:
    """Export map data to HTML string for embedding.

    Args:
        payload: Map data dictionary OR a pre-serialized JSON string.
        css: Optional CSS string (required if payload is a string and has custom styles).

    Returns:
        HTML string containing the complete interactive map.

    Example:
        >>> html = export_html_string(map_data)
        >>> # Use in iframe or embed directly
    """
    if isinstance(payload, str):
        payload_json = payload
        effective_css = css or "" 
    else:
        try:
            import orjson
            # orjson returns bytes
            payload_json = orjson.dumps(payload, option=orjson.OPT_NON_STR_KEYS).decode('utf-8')
        except ImportError:
            import json
            payload_json = json.dumps(payload, ensure_ascii=False)
        effective_css = css if css is not None else payload.get("css", "")
        
    # A "</script>" inside any label would otherwise terminate the inline script.
    payload_json = payload_json.replace("</", "<\\/")
    return HTML_TEMPLATE.render(payload=payload_json, css=effective_css)


@time_debug("Export to HTML")
def export_html(payload: Dict[str, Any] | str, out_html: str, css: Optional[str] = None) -> None:
    """Export map data to an interactive HTML file.

    Args:
        payload: Map data dictionary OR a pre-serialized JSON string.
        out_html: Output path for the HTML file
        css: Optional CSS string.

    Example:
        >>> export_html(payload, "my_map.html")
    """
    html = export_html_string(payload, css=css)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
