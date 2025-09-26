"""
Xatra HTML Rendering Module

This module provides HTML template and JavaScript logic for rendering interactive
maps using Leaflet.js. It supports both static and dynamic maps with time-based
filtering, base layer selection, and various map elements.

The module generates self-contained HTML files that can be opened in any web browser
without requiring a web server.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from jinja2 import Template


HTML_TEMPLATE = Template(
    r"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
      html, body, #map { height: 100%; margin: 0; padding: 0; }
      #controls { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; }
      #title { position: fixed; top: 20px; left: 20px; background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; max-width: 360px; z-index: 1000; }
      #layer-selector { position: fixed; top: 20px; right: 20px; background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; }
      #layer-selector select { margin-left: 8px; }
      .flag { stroke: #333; stroke-width: 1; fill: rgba(200,0,0,0.3); }
      .river { stroke: #0066cc; stroke-width: 1; fill: none; }
      .path { stroke: #444; stroke-dasharray: 4 2; }
      .point { background: #000; width: 6px; height: 6px; border-radius: 6px; }
      .text-label { font-size: 16px; font-weight: bold; color: #666666; background: none; border: none; box-shadow: none; }
      .flag-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .flag-label { font-size: 14px; font-weight: bold; color: #333; background: none; border: none; box-shadow: none; white-space: nowrap; }
      {{ css }}
    </style>
  </head>
  <body>
    <div id="map"></div>
    <div id="title"></div>
    <div id="layer-selector">
      <label for="baseLayer">Base Layer:</label>
      <select id="baseLayer"></select>
    </div>
    <div id="controls"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const payload = {{ payload | safe }};
      const map = L.map('map').setView([22, 79], 4);
      
      // Debug mode - set to true to show centroid markers
      const DEBUG_CENTROIDS = false;
      
      // Base layer management
      const baseLayers = {};
      let currentBaseLayer = null;
      
      // Create base layers
      for (const option of payload.base_options || []) {
        const layer = L.tileLayer(option.url, {
          maxZoom: 18,
          attribution: '&copy; ' + option.name
        });
        baseLayers[option.name] = layer;
      }
      
      // Find default layer - prioritize the one marked as default=True
      const defaultOption = payload.base_options?.find(opt => opt.default === true);
      if (defaultOption) {
        currentBaseLayer = baseLayers[defaultOption.name];
        currentBaseLayer.addTo(map);
      }

      const layers = { flags: [], rivers: [], paths: [], points: [], texts: [], title_boxes: [] };

      function addGeoJSON(geojson, options, tooltip) {
        const layer = L.geoJSON(geojson, options);
        if (tooltip) {
          layer.bindTooltip(tooltip, { 
            direction: 'top',
            offset: [0, -10],
            opacity: 0.9,
            interactive: true,
            permanent: false,
            sticky: true
          });
        }
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

      function renderStatic() {
        const flags = payload.flags.flags;
        for (const f of flags) {
          if (!f.geometry) continue;
          const layer = addGeoJSON(f.geometry, { style: { className: 'flag' } }, `${f.label}${f.note ? ' — ' + f.note : ''}`);
          layers.flags.push(layer);
          
          // Add label at centroid
          const centroid = getCentroid(f.geometry);
          if (centroid[0] !== 0 || centroid[1] !== 0) {
            // Create custom label element
            const labelDiv = L.divIcon({
              html: `<div class="flag-label">${f.label}</div>`,
              className: 'flag-label-container',
              iconSize: [1, 1],
              iconAnchor: [0, 0]
            });
            const labelLayer = L.marker(centroid, { icon: labelDiv }).addTo(map);
            layers.flags.push(labelLayer);
            
            // Debug: Add visible marker for centroid
            if (DEBUG_CENTROIDS) {
              const debugMarker = L.circleMarker(centroid, {
                radius: 8,
                color: 'red',
                fillColor: 'yellow',
                fillOpacity: 0.8,
                weight: 2
              }).addTo(map).bindTooltip(`Centroid: ${f.label}<br>Lat: ${centroid[0].toFixed(4)}<br>Lng: ${centroid[1].toFixed(4)}`);
              layers.flags.push(debugMarker);
            }
          }
        }
      }

      function renderRivers(year = null) {
        const rivers = year !== null ? filterByPeriod(payload.rivers, year) : payload.rivers;
        for (const r of rivers) {
          if (!r.geometry) continue;
          let className = 'river';
          if (r.classes) className += ' ' + r.classes;
          const layer = addGeoJSON(r.geometry, { style: { className } }, `${r.label}${r.note ? ' — ' + r.note : ''}`);
          layers.rivers.push(layer);
        }
      }

      function renderPaths(year = null) {
        const paths = year !== null ? filterByPeriod(payload.paths, year) : payload.paths;
        for (const p of paths) {
          const latlngs = p.coords.map(([lat, lon]) => [lat, lon]);
          let className = 'path';
          if (p.classes) className += ' ' + p.classes;
          const layer = L.polyline(latlngs, { className }).addTo(map).bindTooltip(p.label);
          layers.paths.push(layer);
        }
      }

      function renderPoints(year = null) {
        const points = year !== null ? filterByPeriod(payload.points, year) : payload.points;
        for (const p of points) {
          const layer = L.marker([p.position[0], p.position[1]]).addTo(map).bindTooltip(p.label);
          layers.points.push(layer);
        }
      }

      function renderTexts(year = null) {
        const texts = year !== null ? filterByPeriod(payload.texts, year) : payload.texts;
        for (const t of texts) {
          let className = 'text-label';
          if (t.classes) className += ' ' + t.classes;
          const layer = L.marker([t.position[0], t.position[1]], { opacity: 0.0 }).addTo(map).bindTooltip(t.label, { 
            permanent: true, 
            direction: 'center', 
            className: className,
            offset: [0, 0]
          });
          layers.texts.push(layer);
        }
      }

      function renderTitleBoxes(year = null) {
        const titleBoxes = year !== null ? filterByPeriod(payload.title_boxes, year) : payload.title_boxes;
        const titleDiv = document.getElementById('title');
        titleDiv.innerHTML = titleBoxes.map(tb => `<div class="title-box">${tb.html}</div>`).join('');
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
        layers.flags = [];
        layers.rivers = [];
        layers.paths = [];
        layers.points = [];
        layers.texts = [];
      }

      function renderDynamic(year) {
        clearAllLayers();
        const snapshots = payload.flags.snapshots;
        // find closest snapshot at or before year
        let current = snapshots[0];
        for (const s of snapshots) {
          if (s.year <= year) current = s;
        }
        for (const f of current.flags) {
          if (!f.geometry) continue;
          const layer = addGeoJSON(f.geometry, { style: { className: 'flag' } }, `${f.label}${f.note ? ' — ' + f.note : ''}`);
          layers.flags.push(layer);
          
          // Add label at centroid
          const centroid = getCentroid(f.geometry);
          if (centroid[0] !== 0 || centroid[1] !== 0) {
            // Create custom label element
            const labelDiv = L.divIcon({
              html: `<div class="flag-label">${f.label}</div>`,
              className: 'flag-label-container',
              iconSize: [1, 1],
              iconAnchor: [0, 0]
            });
            const labelLayer = L.marker(centroid, { icon: labelDiv }).addTo(map);
            layers.flags.push(labelLayer);
            
            // Debug: Add visible marker for centroid
            if (DEBUG_CENTROIDS) {
              const debugMarker = L.circleMarker(centroid, {
                radius: 8,
                color: 'red',
                fillColor: 'yellow',
                fillOpacity: 0.8,
                weight: 2
              }).addTo(map).bindTooltip(`Centroid: ${f.label}<br>Lat: ${centroid[0].toFixed(4)}<br>Lng: ${centroid[1].toFixed(4)}`);
              layers.flags.push(debugMarker);
            }
          }
        }
        
        // Render other object types with period filtering
        renderRivers(year);
        renderPaths(year);
        renderPoints(year);
        renderTexts(year);
        renderTitleBoxes(year);
      }

      function setupLayerSelector() {
        const select = document.getElementById('baseLayer');
        
        // Add "None" option
        const noneOption = document.createElement('option');
        noneOption.value = 'none';
        noneOption.textContent = 'None';
        select.appendChild(noneOption);
        
        // Add base layer options
        let defaultSelected = false;
        for (const option of payload.base_options || []) {
          const optionElement = document.createElement('option');
          optionElement.value = option.name;
          optionElement.textContent = option.name;
          if (option.default === true) {
            optionElement.selected = true;
            defaultSelected = true;
          }
          select.appendChild(optionElement);
        }
        
        // If no default was set, select "None"
        if (!defaultSelected) {
          select.selectedIndex = 0; // Select "None"
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
          for (const obj of [...(payload.rivers || []), ...(payload.paths || []), ...(payload.points || []), ...(payload.texts || []), ...(payload.title_boxes || [])]) {
            if (obj.period) {
              allPeriods.push(obj.period[0], obj.period[1]);
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
            
            controls.innerHTML = `<input type="range" id="year" min="${min}" max="${max}" step="1" value="${min}" /> <span id="yearLabel">${min}</span>`;
            const input = document.getElementById('year');
            const label = document.getElementById('yearLabel');
            input.addEventListener('input', () => { label.textContent = input.value; renderDynamic(parseInt(input.value)); });
            renderDynamic(min);
          }
        } else {
          // Hide controls for static maps
          controls.style.display = 'none';
        }
      }

      if (payload.flags.mode === 'static') {
        renderStatic();
        renderRivers();
        renderPaths();
        renderPoints();
        renderTexts();
        renderTitleBoxes();
      }
      setupLayerSelector();
      setupControls();
    </script>
  </body>
  </html>
    """
)


def export_html(payload: Dict[str, Any], out_html: str) -> None:
    """Export map data to an interactive HTML file.
    
    Args:
        payload: Map data dictionary containing flags, rivers, paths, etc.
        out_html: Output path for the HTML file
        
    Example:
        >>> export_html(map_data, "my_map.html")
    """
    html = HTML_TEMPLATE.render(payload=json.dumps(payload), css=payload.get("css", ""))
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
