## ✂️ Crosscut — targeted test selection

**Running the full suite (160 tests)** — conservative fallback.

**Changed symbols:** `get_cors_origins`, `__init__`, `DashboardLayout`, `LeftPanel`, `RightPanel`, `handleExecute`, `parseInt`, `OperationalMap`, `animate`, `getSeverityClass` (+74 more)

> ℹ️ Changed symbol(s) not found in Orbit graph (LoadedGLTF, LoadedTextureMaterial, SafeGLTF); running full suite (unknown blast radius).
> ℹ️ No covering tests found for changed symbol(s): DashboardLayout, LeftPanel, OperationalMap, RightPanel, SchematicMap, __init__, animate, arc, axis, bColor, band, bandColor, barChart, buildMap, chartLat, chartVar, chartVol, closeDash, dUp, densBand, fireBanner, gaugeSVG, getSeverityClass, get_cors_origins, handleExecute, headers, kc, kpi, makePF, makePlatform, openDash, parseInt, pol, renderDash, renderDetail, renderList, renderMarkers, ringSVG, rng, seg, showPeek, statusLabel, tick, tickRing, usePanZoom; running full suite rather than skipping silently.

---
Not confident in the selection? Add the **`crosscut:full`** label or comment **`/crosscut full`** to run the entire suite.

<sub>Selection computed from Orbit Local (single-repo)'s call graph. Deterministic graph traversal — no LLM in the selection path.</sub>