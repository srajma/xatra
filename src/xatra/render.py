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
    <style>
      html, body, #map { height: 100%; margin: 0; padding: 0; }
      #controls { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; display: flex; align-items: center; gap: 8px; }
      #title { position: fixed; top: 20px; left: 20px; background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; max-width: 360px; z-index: 1000; }
      #layer-selector { position: fixed; top: 20px; right: 20px; background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; }
      #colormap { position: fixed; top: 80px; right: 20px; background: rgba(255,255,255,0.95); padding: 8px 12px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; cursor: crosshair; }
      #colormap-tooltip { position: fixed; background: rgba(255,255,255,0.98); border: 1px solid #333; padding: 8px 12px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); z-index: 1001; pointer-events: none; display: none; font-size: 13px; }
      #colormap-tooltip .color-sample { width: 20px; height: 20px; border: 1px solid #666; display: inline-block; vertical-align: middle; margin-right: 8px; border-radius: 3px; }
      #multi-tooltip { position: fixed; background: rgba(255,255,255,0.95); border: 2px solid #333; padding: 10px 14px; border-radius: 6px; box-shadow: 0 3px 12px rgba(0,0,0,0.4); z-index: 1002; pointer-events: none; display: none; font-size: 13px; max-width: 400px; }
      #multi-tooltip .tooltip-item { margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #ddd; }
      #multi-tooltip .tooltip-item:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
      #multi-tooltip .tooltip-type { font-weight: bold; color: #0066cc; font-size: 11px; text-transform: uppercase; margin-bottom: 3px; }
      #multi-tooltip .tooltip-content { color: #333; }
      #layer-selector select { margin-left: 8px; }
      .flag { stroke: #333; stroke-width: 0; } /*fill: rgba(200,0,0,0.3);*/
      .flag:hover { stroke-width: 0.7; }
      .river { stroke: #0066cc; stroke-width: 1; fill: none; }
      .path { stroke: #444; stroke-dasharray: 4 2; }
      .point { background: #000; width: 6px; height: 6px; border-radius: 6px; }
      .text-label { font-size: 16px; font-weight: bold; color: #666666; background: none; border: none; box-shadow: none; }
      .path-label { font-size: 14px; color: #444444; padding: 2px 6px; } /* border-radius: 3px; border: 1px solid #cccccc; background: rgba(255,255,255,0.8); */
      .path-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .river-label { font-size: 14px; color: #0066cc; padding: 2px 6px; }
      .river-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
      .admin-river-label { font-size: 12px; color: #0066cc; padding: 1px 4px; }
      .admin-river-label-container { background: none; border: none; display: flex; justify-content: center; align-items: center; }
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
    <div id="colormap-tooltip"></div>
    <div id="multi-tooltip"></div>
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
            
            const flagTooltip = `${f.label}${f.note ? ' — ' + f.note : ''}`;
            const layer = L.geoJSON(f.geometry, {
              ...flagStyle,
              onEachFeature: function(feature, subLayer) {
                // Register with multi-tooltip system
                registerLayerTooltip(subLayer, 'Flag', flagTooltip);
              }
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
              
              // Calculate rotation based on distant points in geometry
              let rotationAngle = 0;
              const distantPoints = findDistantPoints(f.geometry);
              if (distantPoints) {
                rotationAngle = distantPoints.angle;
              }
              
              const labelDiv = L.divIcon({
                html: `<div style="transform: rotate(${rotationAngle}deg);"><div class="${labelClassName}" style="${labelStyle}">${f.label}</div></div>`,
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
          const riverTooltip = `${r.label}${r.note ? ' — ' + r.note : ''}`;
          const layer = L.geoJSON(r.geometry, { 
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
              const labelInfo = calculateRiverLabelPosition(r.geometry, r.label, fraction);
              
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
          registerLayerTooltip(layer, 'Path', p.label, p.hover_radius);
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
          }
          const layer = L.marker([p.position[0], p.position[1]], markerOptions);
          // Register with multi-tooltip system
          registerLayerTooltip(layer, 'Point', p.label, p.hover_radius);
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
              
              // Register with multi-tooltip system
              if (tooltip) {
                registerLayerTooltip(layer, 'Admin Region', tooltip);
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
              
              // Register with multi-tooltip system (default hover radius for admin rivers)
              if (tooltip) {
                registerLayerTooltip(layer, 'Admin River', tooltip, 10);
              }
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
              if (ar.geometry.features) {
                for (const feature of ar.geometry.features) {
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
          
          const flagTooltip = `${f.label}${f.note ? ' — ' + f.note : ''}`;
          const layer = L.geoJSON(f.geometry, {
            ...flagStyle,
            onEachFeature: function(feature, subLayer) {
              // Register with multi-tooltip system
              registerLayerTooltip(subLayer, 'Flag', flagTooltip);
            }
          }).addTo(map);
          
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
            
            // Calculate rotation based on distant points in geometry
            let rotationAngle = 0;
            const distantPoints = findDistantPoints(f.geometry);
            if (distantPoints) {
              rotationAngle = distantPoints.angle;
            }
            
            const labelDiv = L.divIcon({
              html: `<div style="transform: rotate(${rotationAngle}deg);"><div class="${labelClassName}" style="${labelStyle}">${f.label}</div></div>`,
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
          const riverTooltip = `${r.label}${r.note ? ' — ' + r.note : ''}`;
          
          const layer = L.geoJSON(r.geometry, {
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
              const labelInfo = calculateRiverLabelPosition(r.geometry, r.label, fraction);
              
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
          registerLayerTooltip(layer, 'Path', p.label, p.hover_radius);
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
          }
          const layer = L.marker([p.position[0], p.position[1]], markerOptions).addTo(map);
          // Register with multi-tooltip system
          registerLayerTooltip(layer, 'Point', p.label, p.hover_radius);
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
              
              // Register with multi-tooltip system
              if (tooltip) {
                registerLayerTooltip(layer, 'Admin Region', tooltip);
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
              
              // Register with multi-tooltip system (default hover radius for admin rivers)
              if (tooltip) {
                registerLayerTooltip(layer, 'Admin River', tooltip, 10);
              }
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
              if (ar.geometry.features) {
                for (const feature of ar.geometry.features) {
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
      setupLayerSelector();
      setupControls();
      setupColormap();
    </script>
  </body>
  </html>
    """
)


@time_debug("Export to HTML")
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
