## Current Rendering System Analysis

**Yes, frames are redrawn for every year change even if there are no changes between those years.** Here's how it works:

### 1. **Pax-Max Aggregation (Pre-processing)**
- Creates "snapshots" only at **breakpoint years** (start/end years of any flag)
- Each snapshot contains the union of all active flags at that year
- This is efficient - snapshots are only created when something actually changes

### 2. **Dynamic Rendering (Runtime)**
- **`renderDynamic(year)`** is called for EVERY year change**
- Even though snapshots only exist at breakpoints, `renderDynamic()` is called for every year
- The function finds the "closest snapshot at or before year" 
- **But then it does a FULL re-render every time:**
  - `clearAllLayers()` - removes ALL layers from map
  - Re-renders ALL flags from the snapshot
  - Re-calculates centroids for ALL flags
  - Re-renders ALL other objects (rivers, paths, points, texts, admins, admin_rivers)

### 3. **The Performance Problem**
The issue is that **`renderDynamic()` does a complete re-render even when the year changes but the visual content is identical**. For example:

- Year 100 → Year 101: Full re-render (even if no flags changed)
- Year 101 → Year 102: Full re-render (even if no flags changed)  
- Year 102 → Year 103: Full re-render (even if no flags changed)
- Year 103 → Year 104: Full re-render (even if no flags changed)

**Only when you hit a breakpoint year (like 105) does the content actually change.**

### 4. **Current Optimization**
I added this optimization:
```javascript
if (window.lastRenderedYear === year) return;
window.lastRenderedYear = year;
```

But this only prevents re-rendering the **exact same year**, not years that should have the same visual content.

## The Real Solution

The system should be smarter about when to re-render. It should:

1. **Track the current snapshot** being displayed
2. **Only re-render when the snapshot actually changes**
3. **Skip re-rendering for years that fall between the same breakpoints**

This would dramatically improve performance, especially for maps with long periods between breakpoints!


-----

Do you think it would be possible to re-render only the objects that have changed -- i.e. remove any objects whose periods contained the year but no longer contain the changed year, and draw any objects whose periods did not contain the year but contain the changed year? 