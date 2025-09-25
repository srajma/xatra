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
      #fixed { position: fixed; top: 20px; left: 20px; background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; max-width: 360px; z-index: 1000; }
      .flag { stroke: #333; stroke-width: 1; fill: rgba(200,0,0,0.3); }
      .river { stroke: #0066cc; stroke-width: 1; fill: none; }
      .path { stroke: #444; stroke-dasharray: 4 2; }
      .point { background: #000; width: 6px; height: 6px; border-radius: 6px; }
      .text-label { font-size: 16px; font-weight: bold; color: #666666; background: none; border: none; box-shadow: none; }
      {{ css }}
    </style>
  </head>
  <body>
    <div id="map"></div>
    <div id="fixed">{% for html in fixed_texts %}<div class="fixed-box">{{ html | safe }}</div>{% endfor %}</div>
    <div id="controls"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const payload = {{ payload | safe }};
      const map = L.map('map').setView([22, 79], 4);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      const layers = { flags: [], rivers: [], paths: [], points: [], texts: [] };

      function addGeoJSON(geojson, options, tooltip) {
        const layer = L.geoJSON(geojson, options);
        if (tooltip) layer.bindTooltip(tooltip, { 
          direction: 'top',
          offset: [0, -10],
          opacity: 0.9
        });
        layer.addTo(map);
        return layer;
      }

      function renderStatic() {
        const flags = payload.flags.flags;
        for (const f of flags) {
          if (!f.geometry) continue;
          const layer = addGeoJSON(f.geometry, { style: { className: 'flag' } }, `${f.label}${f.note ? ' — ' + f.note : ''}`);
          layers.flags.push(layer);
        }
      }

      function renderRivers() {
        for (const r of payload.rivers) {
          if (!r.geometry) continue;
          let className = 'river';
          if (r.class_name) className += ' ' + r.class_name;
          const layer = addGeoJSON(r.geometry, { style: { className } }, `${r.label}${r.note ? ' — ' + r.note : ''}`);
          layers.rivers.push(layer);
        }
      }

      function renderPaths() {
        for (const p of payload.paths) {
          const latlngs = p.coords.map(([lat, lon]) => [lat, lon]);
          let className = 'path';
          if (p.class_name) className += ' ' + p.class_name;
          const layer = L.polyline(latlngs, { className }).addTo(map).bindTooltip(p.label);
          layers.paths.push(layer);
        }
      }

      function renderPoints() {
        for (const p of payload.points) {
          const layer = L.marker([p.position[0], p.position[1]]).addTo(map).bindTooltip(p.label);
          layers.points.push(layer);
        }
      }

      function renderTexts() {
        for (const t of payload.texts) {
          let className = 'text-label';
          if (t.class_name) className += ' ' + t.class_name;
          const layer = L.marker([t.position[0], t.position[1]], { opacity: 0.0 }).addTo(map).bindTooltip(t.label, { 
            permanent: true, 
            direction: 'center', 
            className: className,
            offset: [0, 0]
          });
          layers.texts.push(layer);
        }
      }

      function clearFlagLayers() {
        for (const l of layers.flags) { map.removeLayer(l); }
        layers.flags = [];
      }

      function renderDynamic(year) {
        clearFlagLayers();
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
        }
      }

      function setupControls() {
        const controls = document.getElementById('controls');
        if (payload.flags.mode === 'dynamic') {
          const min = payload.flags.breakpoints[0];
          const max = payload.flags.breakpoints[payload.flags.breakpoints.length - 1];
          controls.innerHTML = `<input type="range" id="year" min="${min}" max="${max}" step="1" value="${min}" /> <span id="yearLabel">${min}</span>`;
          const input = document.getElementById('year');
          const label = document.getElementById('yearLabel');
          input.addEventListener('input', () => { label.textContent = input.value; renderDynamic(parseInt(input.value)); });
          renderDynamic(min);
        }
      }

      if (payload.flags.mode === 'static') {
        renderStatic();
      }
      renderRivers();
      renderPaths();
      renderPoints();
      renderTexts();
      setupControls();
    </script>
  </body>
  </html>
    """
)


def export_html(payload: Dict[str, Any], out_html: str) -> None:
    html = HTML_TEMPLATE.render(payload=json.dumps(payload), css=payload.get("css", ""), fixed_texts=payload.get("fixed_text_boxes", []))
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
