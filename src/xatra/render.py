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
      #controls { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; display: flex; align-items: center; gap: 8px; }
      #title { position: fixed; top: 20px; left: 20px; background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; max-width: 360px; z-index: 1000; }
      #layer-selector { position: fixed; top: 20px; right: 20px; background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; }
      #colormap { position: fixed; top: 80px; right: 20px; background: rgba(255,255,255,0.95); padding: 8px 12px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; }
      #layer-selector select { margin-left: 8px; }
      .flag { stroke: #333; stroke-width: 0; } /*fill: rgba(200,0,0,0.3);*/
      .river { stroke: #0066cc; stroke-width: 1; fill: none; }
      .path { stroke: #444; stroke-dasharray: 4 2; }
      .point { background: #000; width: 6px; height: 6px; border-radius: 6px; }
      .text-label { font-size: 16px; font-weight: bold; color: #666666; background: none; border: none; box-shadow: none; }
      .path-label { font-size: 14px; color: #444444; padding: 2px 6px; } /* border-radius: 3px; border: 1px solid #cccccc; background: rgba(255,255,255,0.8); */
      .path-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .river-label { font-size: 14px; color: #0066cc; padding: 2px 6px; }
      .river-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .point-label { font-size: 14px; color: #444444; background: rgba(255,255,255,0.8); padding: 2px 6px; border-radius: 3px; border: 1px solid #cccccc; }
      .flag-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .flag-label { font-size: 14px; font-weight: bold; color: #333; background: none; border: none; box-shadow: none; white-space: nowrap; }
      .admin { stroke: #000; stroke-width: 0.5;  } /* fill: rgba(100,100,100,0.1); */
    .admin-river { stroke: #0066cc; stroke-width: 2; opacity: 0.8; }
      .data { stroke: #333; stroke-width: 1; }
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
    <div id="colormap"></div>
    <div id="controls"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const payload = {{ payload | safe }};
      const map = L.map('map').setView([22, 79], 4);
      
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

      const layers = { flags: [], rivers: [], paths: [], points: [], texts: [], title_boxes: [], admins: [], admin_rivers: [], data: [], dataframes: [] };
      
      // Layer visibility management for dynamic maps
      const layerVisibility = new Map(); // Maps layer objects to their visibility state
      let allLayersCreated = false;

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
      function calculateRiverLabelPosition(geometryOrFeature, label) {
        // Handle both Feature and raw geometry
        let geometry = geometryOrFeature;
        if (geometryOrFeature.type === 'Feature' && geometryOrFeature.geometry) {
          geometry = geometryOrFeature.geometry;
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
        
        // Calculate bounding box center
        let minLat = Infinity, maxLat = -Infinity;
        let minLon = Infinity, maxLon = -Infinity;
        
        for (const lineString of allCoords) {
          for (const coord of lineString) {
            const lon = coord[0];
            const lat = coord[1];
            if (lat < minLat) minLat = lat;
            if (lat > maxLat) maxLat = lat;
            if (lon < minLon) minLon = lon;
            if (lon > maxLon) maxLon = lon;
          }
        }
        
        if (!isFinite(minLat) || !isFinite(maxLat)) return null;
        
        // Center of bounding box
        const center = [(minLat + maxLat) / 2, (minLon + maxLon) / 2];
        
        // Find the nearest point on any LineString to the bounding box center
        let nearestPoint = null;
        let nearestDistance = Infinity;
        let nearestLineString = null;
        let nearestSegmentIndex = -1;
        let nearestT = 0; // Position along the segment (0 to 1)
        
        for (const lineString of allCoords) {
          for (let i = 0; i < lineString.length - 1; i++) {
            const p1 = [lineString[i][1], lineString[i][0]]; // [lat, lon]
            const p2 = [lineString[i+1][1], lineString[i+1][0]]; // [lat, lon]
            
            // Find nearest point on segment p1-p2 to bounding box center
            const result = nearestPointOnSegment(center, p1, p2);
            
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
        
        // Calculate angle based on points at label-length distance from nearest point
        // Estimate label length (roughly 10 pixels per character at default font size)
        const estimatedLabelLength = label.length * 0.15; // in degrees
        
        // Convert LineString to lat/lon format
        const latlngs = nearestLineString.map(coord => [coord[1], coord[0]]);
        
        // Calculate position of nearest point along the LineString
        let distanceToNearest = 0;
        for (let i = 0; i < nearestSegmentIndex; i++) {
          distanceToNearest += Math.sqrt(
            Math.pow(latlngs[i+1][0] - latlngs[i][0], 2) +
            Math.pow(latlngs[i+1][1] - latlngs[i][1], 2)
          );
        }
        // Add the fractional distance within the nearest segment
        distanceToNearest += nearestT * Math.sqrt(
          Math.pow(latlngs[nearestSegmentIndex+1][0] - latlngs[nearestSegmentIndex][0], 2) +
          Math.pow(latlngs[nearestSegmentIndex+1][1] - latlngs[nearestSegmentIndex][1], 2)
        );
        
        // Find points at estimated label distance on either side
        let startPoint = null;
        let endPoint = null;
        
        // Search backwards from nearest point
        let accumulatedDist = 0;
        for (let i = nearestSegmentIndex; i >= 0 && accumulatedDist < estimatedLabelLength; i--) {
          startPoint = latlngs[i];
          if (i > 0) {
            accumulatedDist += Math.sqrt(
              Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
              Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
            );
          }
        }
        
        // Search forwards from nearest point
        accumulatedDist = 0;
        for (let i = nearestSegmentIndex + 1; i < latlngs.length && accumulatedDist < estimatedLabelLength; i++) {
          endPoint = latlngs[i];
          accumulatedDist += Math.sqrt(
            Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
            Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
          );
        }
        
        // Calculate angle between distant points
        let angle = 0;
        if (startPoint && endPoint) {
          const dx = endPoint[1] - startPoint[1]; // longitude difference
          const dy = endPoint[0] - startPoint[0]; // latitude difference
          angle = -Math.atan2(dy, dx) * 180 / Math.PI;
          
          // Normalize angle to keep text readable
          if (angle > 90) angle -= 180;
          if (angle < -90) angle += 180;
        }
        
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

      function createAllLayers() {
        if (allLayersCreated) return;
        
        console.log("Creating all layers for dynamic map...");
        
        // Create all flag layers from all snapshots
        const snapshots = payload.flags.snapshots;
        for (const snapshot of snapshots) {
          for (const f of snapshot.flags) {
            if (!f.geometry) continue;
            
            let className = 'flag';
            if (f.classes) className += ' ' + f.classes;
            const flagStyle = { className: className };
            if (f.color) {
              flagStyle.style = {
                fillColor: f.color,
                fillOpacity: 0.4,
                color: f.color,
                weight: 1
              };
            }
            
            const layer = L.geoJSON(f.geometry, flagStyle);
            layer.bindTooltip(`${f.label}${f.note ? ' — ' + f.note : ''}`, { 
              direction: 'top',
              offset: [0, -10],
              opacity: 0.9,
              interactive: true,
              permanent: false,
              sticky: true
            });
            
            if (f.color) {
              layer.setStyle({
                fillColor: f.color,
                fillOpacity: 0.4,
                color: f.color,
                weight: 1
              });
            }
            
            // Add label at centroid
            const centroid = f.centroid || getCentroid(f.geometry);
            if (centroid && (centroid[0] !== 0 || centroid[1] !== 0)) {
              let labelStyle = '';
              if (f.color) {
                // Convert hex to HSL and reduce luminosity, increase alpha
                const hex = f.color.replace('#', '');
                const r = parseInt(hex.substr(0, 2), 16) / 255;
                const g = parseInt(hex.substr(2, 2), 16) / 255;
                const b = parseInt(hex.substr(4, 2), 16) / 255;
                
                // Convert RGB to HSL
                const max = Math.max(r, g, b);
                const min = Math.min(r, g, b);
                let h, s, l = (max + min) / 2;
                
                if (max === min) {
                  h = s = 0; // achromatic
                } else {
                  const d = max - min;
                  s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
                  switch (max) {
                    case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                    case g: h = (b - r) / d + 2; break;
                    case b: h = (r - g) / d + 4; break;
                  }
                  h /= 6;
                }
                
                // Reduce luminosity and set alpha to 0.9
                l = Math.max(0, l - 0.2);
                const alpha = 0.9;
                
                // Convert back to RGB
                const hue2rgb = (p, q, t) => {
                  if (t < 0) t += 1;
                  if (t > 1) t -= 1;
                  if (t < 1/6) return p + (q - p) * 6 * t;
                  if (t < 1/2) return q;
                  if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                  return p;
                };
                
                let r2, g2, b2;
                if (s === 0) {
                  r2 = g2 = b2 = l; // achromatic
                } else {
                  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
                  const p = 2 * l - q;
                  r2 = hue2rgb(p, q, h + 1/3);
                  g2 = hue2rgb(p, q, h);
                  b2 = hue2rgb(p, q, h - 1/3);
                }
                
                const r3 = Math.round(r2 * 255);
                const g3 = Math.round(g2 * 255);
                const b3 = Math.round(b2 * 255);
                
                labelStyle = `color: rgba(${r3}, ${g3}, ${b3}, ${alpha});`;
              }
              
              let labelClassName = 'flag-label';
              if (f.classes) labelClassName += ' ' + f.classes;
              const labelDiv = L.divIcon({
                html: `<div class="${labelClassName}" style="${labelStyle}">${f.label}</div>`,
                className: 'flag-label-container',
                iconSize: [1, 1],
                iconAnchor: [0, 0]
              });
              const labelLayer = L.marker(centroid, { icon: labelDiv });
              
              // Store metadata for visibility management
              layer._flagData = { label: f.label, snapshot: snapshot.year };
              labelLayer._flagData = { label: f.label, snapshot: snapshot.year };
              
              layers.flags.push(layer, labelLayer);
            }
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
          if (!r.geometry) continue;
          let className = 'river';
          if (r.classes) className += ' ' + r.classes;
          const layer = L.geoJSON(r.geometry, { style: { className } });
          if (!r.show_label) {
            layer.bindTooltip(`${r.label}${r.note ? ' — ' + r.note : ''}`, { 
              direction: 'top',
              offset: [0, -10],
              opacity: 0.9,
              interactive: true,
              permanent: false,
              sticky: true
            });
          }
          layer._riverData = { period: r.period };
          layers.rivers.push(layer);
          
          // Add label if show_label is true
          if (r.show_label) {
            const labelInfo = calculateRiverLabelPosition(r.geometry, r.label);
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

      function createAllPaths() {
        for (const p of payload.paths || []) {
          const latlngs = p.coords.map(([lat, lon]) => [lat, lon]);
          let className = 'path';
          if (p.classes) className += ' ' + p.classes;
          const layer = L.polyline(latlngs, { className });
          if (!p.show_label) {
            layer.bindTooltip(p.label);
          }
          layer._pathData = { period: p.period };
          layers.paths.push(layer);
          
          // Add label at midpoint if show_label is true
          if (p.show_label && latlngs.length > 0) {
            // Calculate midpoint along the path (by distance, not by index)
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
            
            const halfDistance = totalDistance / 2;
            let midpoint = latlngs[0];
            let midpointSegmentIndex = 0;
            
            // Find the segment containing the midpoint
            for (let i = 1; i < distances.length; i++) {
              if (distances[i] >= halfDistance) {
                const segmentStart = distances[i - 1];
                const segmentEnd = distances[i];
                const t = (halfDistance - segmentStart) / (segmentEnd - segmentStart);
                
                // Interpolate between points
                midpoint = [
                  latlngs[i-1][0] + t * (latlngs[i][0] - latlngs[i-1][0]),
                  latlngs[i-1][1] + t * (latlngs[i][1] - latlngs[i-1][1])
                ];
                midpointSegmentIndex = i - 1;
                break;
              }
            }
            
            // Calculate rotation angle based on nearby path segments
            // Estimate label length (roughly 10 pixels per character at default font size)
            const estimatedLabelLength = p.label.length * 0.15; // in degrees (rough estimate)
            
            // Find points within estimated label length of midpoint
            let startPoint = null;
            let endPoint = null;
            
            // Search backwards from midpoint
            let accumulatedDist = 0;
            for (let i = midpointSegmentIndex; i >= 0 && accumulatedDist < estimatedLabelLength; i--) {
              startPoint = latlngs[i];
              if (i > 0) {
                accumulatedDist += Math.sqrt(
                  Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                  Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
                );
              }
            }
            
            // Search forwards from midpoint
            accumulatedDist = 0;
            for (let i = midpointSegmentIndex + 1; i < latlngs.length && accumulatedDist < estimatedLabelLength; i++) {
              endPoint = latlngs[i];
              accumulatedDist += Math.sqrt(
                Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
              );
            }
            
            // Calculate angle between start and end points
            let angle = 0;
            if (startPoint && endPoint) {
              const dx = endPoint[1] - startPoint[1]; // longitude difference
              const dy = endPoint[0] - startPoint[0]; // latitude difference
              angle = -Math.atan2(dy, dx) * 180 / Math.PI;
              
              // Normalize angle to keep text readable (don't flip upside down)
              if (angle > 90) angle -= 180;
              if (angle < -90) angle += 180;
            }
            
            let labelClassName = 'path-label-container';
            let innerClassName = 'text-label path-label';
            if (p.classes) innerClassName += ' ' + p.classes;
            
            // Use divIcon with nested divs for rotation and translation
            // Outer div: rotation (inline), Inner div: translation (CSS customizable)
            const labelDiv = L.divIcon({
              html: `<div style="transform: rotate(${angle}deg);"><div class="${innerClassName}" style="transform: translateY(-8px); white-space: nowrap;">${p.label}</div></div>`,
              className: labelClassName,
              iconSize: [1, 1],
              iconAnchor: [0, 0]
            });
            
            const labelLayer = L.marker(midpoint, { icon: labelDiv });
            labelLayer._pathData = { period: p.period };
            layers.paths.push(labelLayer);
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
          }
          const layer = L.marker([p.position[0], p.position[1]], markerOptions);
          if (!p.show_label) {
            layer.bindTooltip(p.label);
          }
          layer._pointData = { period: p.period };
          layers.points.push(layer);
          
          // Add label next to point if show_label is true
          if (p.show_label) {
            const labelLayer = L.marker([p.position[0], p.position[1]], { opacity: 0.0 });
            labelLayer.bindTooltip(p.label, { 
              permanent: true, 
              direction: 'right', 
              className: 'text-label point-label',
              offset: [10, 0]
            });
            labelLayer._pointData = { period: p.period };
            layers.points.push(labelLayer);
          }
        }
      }

      function createAllTexts() {
        for (const t of payload.texts || []) {
          let className = 'text-label';
          if (t.classes) className += ' ' + t.classes;
          const layer = L.marker([t.position[0], t.position[1]], { opacity: 0.0 });
          layer.bindTooltip(t.label, { 
            permanent: true, 
            direction: 'center', 
            className: className,
            offset: [0, 0]
          });
          layer._textData = { period: t.period };
          layers.texts.push(layer);
        }
      }

      function createAllAdmins() {
        for (const a of payload.admins || []) {
          if (!a.geometry) continue;
          
          let className = 'admin';
          if (a.classes) className += ' ' + a.classes;
          
          const layer = L.geoJSON(a.geometry, {
            style: function(feature) {
              const props = feature.properties || {};
              const color = props._color;
              return {
                className: className,
                fillColor: color || '#cccccc',
                fillOpacity: 0.3,
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
            }
          });
          
          layer._adminData = { period: a.period };
          layers.admins.push(layer);
        }
      }

      function createAllAdminRivers() {
        for (const ar of payload.admin_rivers || []) {
          if (!ar.geometry) continue;
          
          let className = 'admin-river';
          if (ar.classes) className += ' ' + ar.classes;
          
          const layer = L.geoJSON(ar.geometry, {
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
            }
          });
          
          layer._adminRiverData = { period: ar.period };
          layers.admin_rivers.push(layer);
        }
      }

      function createAllData() {
        for (const d of payload.data || []) {
          if (!d.geometry) continue;
          
          let className = 'data';
          if (d.classes) className += ' ' + d.classes;
          
          const layer = L.geoJSON(d.geometry, {
            style: function(feature) {
              const props = feature.properties || {};
              const dataIndex = d.data_index || 0;
              const color = (props._data_colors && props._data_colors[dataIndex]) || d.color || '#cccccc';
              return {
                className: className,
                fillColor: color,
                fillOpacity: 1.0,
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
        if (!df.geometry) return;
        
        let className = 'data';
        if (df.classes) className += ' ' + df.classes;
        
        const layer = L.geoJSON(df.geometry, {
          style: function(feature) {
            const props = feature.properties || {};
            const value = props._dataframe_value;
            const color = getDataColor(value);
            return {
              className: className,
              fillColor: color,
              fillOpacity: 1.0,
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
          }
        });
        
        // Ensure static DataFrame layers are actually shown on static maps
        layer.addTo(map);
        layer._dataframeType = 'static';
        layers.dataframes.push(layer);
      }

      function createDynamicDataframe(df) {
        if (!df.geometry) return;
        
        let className = 'data';
        if (df.classes) className += ' ' + df.classes;
        
        const layer = L.geoJSON(df.geometry, {
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
              fillOpacity: 1.0,
              color: color,
              opacity: 1.0,
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
            
            // Add note for current year if available
            const currentYear = window.currentYear || (df.years && df.years[0]) || 2020;
            const notes = props._dataframe_notes || {};
            if (notes && (currentYear in notes)) {
              tooltip += `Note (${currentYear}): ${notes[currentYear]}<br/>`;
            }
            
            if (tooltip.endsWith('<br/>')) {
              tooltip = tooltip.slice(0, -5);
            }
            
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
          }
        });
        
        layer._dataframeType = 'dynamic';
        layer._dataframeYears = df.years;
        layers.dataframes.push(layer);
      }

      function renderStatic() {
        const flags = payload.flags.flags;
        for (const f of flags) {
          if (!f.geometry) continue;
          
          // Create style with flag color
          let className = 'flag';
          if (f.classes) className += ' ' + f.classes;
          const flagStyle = { className: className };
          if (f.color) {
            flagStyle.style = {
              fillColor: f.color,
              fillOpacity: 0.4,
              color: f.color,
              weight: 1
            };
          }
          
          const layer = addGeoJSON(f.geometry, flagStyle, `${f.label}${f.note ? ' — ' + f.note : ''}`);
          
          // Apply color styling after layer creation
          if (f.color) {
            layer.setStyle({
              fillColor: f.color,
              fillOpacity: 0.4,
              color: f.color,
              weight: 1
            });
          }
          
          layers.flags.push(layer);
          
          // Add label at centroid (use pre-computed centroid if available)
          const centroid = f.centroid || (() => {
            console.warn(`Centroid fallback calculation for flag: ${f.label}`);
            return getCentroid(f.geometry);
          })();
          if (centroid && (centroid[0] !== 0 || centroid[1] !== 0)) {
            // Create custom label element with flag color
            let labelStyle = '';
            if (f.color) {
              // Convert hex to HSL and reduce luminosity, increase alpha
              const hex = f.color.replace('#', '');
              const r = parseInt(hex.substr(0, 2), 16) / 255;
              const g = parseInt(hex.substr(2, 2), 16) / 255;
              const b = parseInt(hex.substr(4, 2), 16) / 255;
              
              // Convert RGB to HSL
              const max = Math.max(r, g, b);
              const min = Math.min(r, g, b);
              let h, s, l = (max + min) / 2;
              
              if (max === min) {
                h = s = 0; // achromatic
              } else {
                const d = max - min;
                s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
                switch (max) {
                  case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                  case g: h = (b - r) / d + 2; break;
                  case b: h = (r - g) / d + 4; break;
                }
                h /= 6;
              }
              
              // Reduce luminosity and set alpha to 0.9
              l = Math.max(0, l - 0.2); // Reduce luminosity
              const alpha = 0.9;
              
              // Convert back to RGB
              const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1/6) return p + (q - p) * 6 * t;
                if (t < 1/2) return q;
                if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
              };
              
              let r2, g2, b2;
              if (s === 0) {
                r2 = g2 = b2 = l; // achromatic
              } else {
                const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
                const p = 2 * l - q;
                r2 = hue2rgb(p, q, h + 1/3);
                g2 = hue2rgb(p, q, h);
                b2 = hue2rgb(p, q, h - 1/3);
              }
              
              const r3 = Math.round(r2 * 255);
              const g3 = Math.round(g2 * 255);
              const b3 = Math.round(b2 * 255);
              
              labelStyle = `color: rgba(${r3}, ${g3}, ${b3}, ${alpha});`;
            }
            
            let labelClassName = 'flag-label';
            if (f.classes) labelClassName += ' ' + f.classes;
            const labelDiv = L.divIcon({
              html: `<div class="${labelClassName}" style="${labelStyle}">${f.label}</div>`,
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
          const layer = addGeoJSON(r.geometry, { style: { className } }, r.show_label ? undefined : `${r.label}${r.note ? ' — ' + r.note : ''}`);
          layers.rivers.push(layer);
          
          // Add label if show_label is true
          if (r.show_label) {
            const labelInfo = calculateRiverLabelPosition(r.geometry, r.label);
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

      function renderPaths(year = null) {
        const paths = year !== null ? filterByPeriod(payload.paths, year) : payload.paths;
        for (const p of paths) {
          const latlngs = p.coords.map(([lat, lon]) => [lat, lon]);
          let className = 'path';
          if (p.classes) className += ' ' + p.classes;
          const layer = L.polyline(latlngs, { className }).addTo(map);
          if (!p.show_label) {
            layer.bindTooltip(p.label);
          }
          layers.paths.push(layer);
          
          // Add label at midpoint if show_label is true
          if (p.show_label && latlngs.length > 0) {
            // Calculate midpoint along the path (by distance, not by index)
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
            
            const halfDistance = totalDistance / 2;
            let midpoint = latlngs[0];
            let midpointSegmentIndex = 0;
            
            // Find the segment containing the midpoint
            for (let i = 1; i < distances.length; i++) {
              if (distances[i] >= halfDistance) {
                const segmentStart = distances[i - 1];
                const segmentEnd = distances[i];
                const t = (halfDistance - segmentStart) / (segmentEnd - segmentStart);
                
                // Interpolate between points
                midpoint = [
                  latlngs[i-1][0] + t * (latlngs[i][0] - latlngs[i-1][0]),
                  latlngs[i-1][1] + t * (latlngs[i][1] - latlngs[i-1][1])
                ];
                midpointSegmentIndex = i - 1;
                break;
              }
            }
            
            // Calculate rotation angle based on nearby path segments
            // Estimate label length (roughly 10 pixels per character at default font size)
            const estimatedLabelLength = p.label.length * 0.15; // in degrees (rough estimate)
            
            // Find points within estimated label length of midpoint
            let startPoint = null;
            let endPoint = null;
            
            // Search backwards from midpoint
            let accumulatedDist = 0;
            for (let i = midpointSegmentIndex; i >= 0 && accumulatedDist < estimatedLabelLength; i--) {
              startPoint = latlngs[i];
              if (i > 0) {
                accumulatedDist += Math.sqrt(
                  Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                  Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
                );
              }
            }
            
            // Search forwards from midpoint
            accumulatedDist = 0;
            for (let i = midpointSegmentIndex + 1; i < latlngs.length && accumulatedDist < estimatedLabelLength; i++) {
              endPoint = latlngs[i];
              accumulatedDist += Math.sqrt(
                Math.pow(latlngs[i][0] - latlngs[i-1][0], 2) +
                Math.pow(latlngs[i][1] - latlngs[i-1][1], 2)
              );
            }
            
            // Calculate angle between start and end points
            let angle = 0;
            if (startPoint && endPoint) {
              const dx = endPoint[1] - startPoint[1]; // longitude difference
              const dy = endPoint[0] - startPoint[0]; // latitude difference
              angle = -Math.atan2(dy, dx) * 180 / Math.PI;
              
              // Normalize angle to keep text readable (don't flip upside down)
              if (angle > 90) angle -= 180;
              if (angle < -90) angle += 180;
            }
            
            let labelClassName = 'path-label-container';
            let innerClassName = 'text-label path-label';
            if (p.classes) innerClassName += ' ' + p.classes;
            
            // Use divIcon with nested divs for rotation and translation
            // Outer div: rotation (inline), Inner div: translation (CSS customizable)
            const labelDiv = L.divIcon({
              html: `<div style="transform: rotate(${angle}deg);"><div class="${innerClassName}" style="transform: translateY(-8px); white-space: nowrap;">${p.label}</div></div>`,
              className: labelClassName,
              iconSize: [1, 1],
              iconAnchor: [0, 0]
            });
            
            const labelLayer = L.marker(midpoint, { icon: labelDiv }).addTo(map);
            layers.paths.push(labelLayer);
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
          }
          const layer = L.marker([p.position[0], p.position[1]], markerOptions).addTo(map);
          if (!p.show_label) {
            layer.bindTooltip(p.label);
          }
          layers.points.push(layer);
          
          // Add label next to point if show_label is true
          if (p.show_label) {
            const labelLayer = L.marker([p.position[0], p.position[1]], { opacity: 0.0 }).addTo(map).bindTooltip(p.label, { 
              permanent: true, 
              direction: 'right', 
              className: 'text-label point-label',
              offset: [10, 0]
            });
            layers.points.push(labelLayer);
          }
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

      function renderAdmins(year = null) {
        const admins = year !== null ? filterByPeriod(payload.admins, year) : payload.admins;
        for (const a of admins) {
          if (!a.geometry) continue;
          
          // Create style for admin regions
          let className = 'admin';
          if (a.classes) className += ' ' + a.classes;
          
          // Add each feature with its own tooltip and color
          const layer = L.geoJSON(a.geometry, {
            style: function(feature) {
              const props = feature.properties || {};
              const color = props._color;
              return {
                className: className,
                fillColor: color || '#cccccc',
                fillOpacity: 0.3,
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
            }
          });
          
          layer.addTo(map);
          layers.admins.push(layer);
        }
      }

      function renderAdminRivers(year = null) {
        const adminRivers = year !== null ? filterByPeriod(payload.admin_rivers, year) : payload.admin_rivers;
        for (const ar of adminRivers) {
          if (!ar.geometry) continue;
          
          // Create style for admin rivers
          let className = 'admin-river';
          if (ar.classes) className += ' ' + ar.classes;
          
          // Add each feature with its own tooltip
          const layer = L.geoJSON(ar.geometry, {
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
            }
          });
          
          layer.addTo(map);
          layers.admin_rivers.push(layer);
        }
      }

      function renderData(year = null) {
        const data = year !== null ? filterByPeriod(payload.data, year) : payload.data;
        for (const d of data) {
          if (!d.geometry) continue;
          
          let className = 'data';
          if (d.classes) className += ' ' + d.classes;
          
          const layer = L.geoJSON(d.geometry, {
            style: function(feature) {
              const props = feature.properties || {};
              const dataIndex = d.data_index || 0;
              const color = (props._data_colors && props._data_colors[dataIndex]) || d.color || '#cccccc';
              return {
                className: className,
                fillColor: color,
                fillOpacity: 1.0,
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
                  fillOpacity: 1.0,
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
                
                // Update tooltip
                feature.setTooltipContent(tooltip);
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
            
            controls.innerHTML = `
              <span id="yearLabel">${min}</span>
              <button id="playPause" style="margin: 0 8px; padding: 4px 8px; border: 1px solid #ccc; background: #f9f9f9; border-radius: 4px; cursor: pointer;">▶</button>
              <span id="startYear" style="margin-right: 8px;">${min}</span>
              <input type="range" id="year" min="${min}" max="${max}" step="1" value="${min}" style="flex: 1; margin: 0 8px;" />
              <span id="endYear" style="margin-left: 8px;">${max}</span>
            `;
            const input = document.getElementById('year');
            const label = document.getElementById('yearLabel');
            const playPauseBtn = document.getElementById('playPause');
            const startYearSpan = document.getElementById('startYear');
            const endYearSpan = document.getElementById('endYear');
            
            let isPlaying = false;
            let playInterval = null;
            
            input.addEventListener('input', () => { 
              label.textContent = input.value; 
              renderDynamic(parseInt(input.value)); 
            });
            
            playPauseBtn.addEventListener('click', () => {
              if (isPlaying) {
                // Pause
                clearInterval(playInterval);
                playPauseBtn.textContent = '▶';
                isPlaying = false;
              } else {
                // Play
                playPauseBtn.textContent = '⏸';
                isPlaying = true;
                playInterval = setInterval(() => {
                  const currentYear = parseInt(input.value);
                  if (currentYear >= max) {
                    // Reached end, stop playing
                    clearInterval(playInterval);
                    playPauseBtn.textContent = '▶';
                    isPlaying = false;
                  } else {
                    const newYear = currentYear + 1;
                    input.value = newYear;
                    label.textContent = newYear;
                    renderDynamic(newYear);
                  }
                }, payload.play_speed || 200); // Use speed from payload or default to 200ms
              }
            });
            
            renderDynamic(min);
          }
        } else {
          // Hide controls for static maps
          controls.style.display = 'none';
        }
      }

      function setupColormap() {
        const colormapDiv = document.getElementById('colormap');
        if (payload.colormap_svg) {
          colormapDiv.innerHTML = payload.colormap_svg;
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
      setupLayerSelector();
      setupControls();
      setupColormap();
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
    html = HTML_TEMPLATE.render(payload=json.dumps(payload, ensure_ascii=False), css=payload.get("css", ""))
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
