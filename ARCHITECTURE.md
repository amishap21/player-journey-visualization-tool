# Architecture Document

## What I Built

A web-based visualization tool for LILA BLACK game event data that enables Level Designers to analyze player behavior, combat patterns, and map usage. The tool provides:

- **Player Path Visualization**: Renders human (green) and bot (red) movement paths on game minimaps
- **Event Markers**: Displays kill, death, loot, and storm events with distinct colors
- **Timeline Playback**: Timeline replay of player movement and event markers on the minimap frame by frame
- **Heatmaps**: Density maps for kill zones, death zones, and player traffic
- **Interactive Filtering**: Filter by date, map, and match for both Player Path and Heatmaps

## Tech Stack Selection

**Python + Streamlit** was chosen for this project because:

- **Beginner-friendly**: Simple syntax and minimal boilerplate
- **Built-in deployment**: Streamlit Cloud offers free, one-click deployment
- **Data visualization**: Excellent integration with pandas, matplotlib, and seaborn
- **Rapid prototyping**: UI components (sliders, checkboxes, buttons) are built-in
- **Caching**: `@st.cache_data` decorator handles data loading efficiently

**Alternatives considered**:
- React + Node.js: More flexible but higher complexity and longer development time
- Dash (Python): More powerful but steeper learning curve
- Jupyter Notebooks: Good for analysis but not suitable for interactive tools

## Data Flow

```
player_data.zip (if not extracted)
    ↓
data_loader.py (ensure_data_available - extracts zip if needed)
    ↓
Parquet Files (player_data/February_XX/)
    ↓
data_loader.py (load_day_data)
    ↓
Pandas DataFrame (decoded events, timestamp conversion)
    ↓
Global Data Caching (@st.cache_resource)
    ↓
Pre-processed Nested Structure {date: {map_id: {match_id: DataFrame}}}
    ↓
Map Pre-aggregation {map_id: DataFrame} for heatmaps
    ↓
User Selection (date → map → match) + View Mode (Player Paths/Heatmap)
    ↓
Dictionary Lookup (instant O(1) access)
    ↓
coordinate_mapper.py (world_to_pixel)
    ↓
visualizations.py (matplotlib rendering with caching)
    ↓
Streamlit Display (st.pyplot or st.image for playback)
```

### Data Loading Pipeline

1. **Zip Extraction**: `ensure_data_available()` extracts `player_data.zip` if `player_data/` folder doesn't exist (Did this to avoid cluttering the repository with large data files)
2. **File Discovery**: `get_available_dates()` scans `player_data/` for date folders (of format: `February_XX/`)
3. **Parquet Reading**: `load_day_data()` uses PyArrow to read all `.nakama-0` files
4. **Event Decoding**: Binary event column decoded to UTF-8 strings
5. **Timestamp Conversion**: `ts` column converted to numeric milliseconds
6. **Global Caching**: All data loaded once at startup into nested dictionary structure `{date: {map_id: {match_id: DataFrame}}}`
7. **Instant Lookup**: Data access uses dictionary lookups (O(1)) instead of DataFrame filtering (O(n))
8. **Map Data Pre-aggregation**: Heatmap data pre-aggregated by map at startup for instant access

### Rendering Pipeline

1. **Coordinate Conversion**: World (x, z) → pixel coordinates using map-specific scale/origin - 1024x1024 (Scaled down the images to 1024x1024 for faster rendering from higher resolution images provided)
2. **Minimap Caching**: Minimap images loaded once and cached to avoid repeated disk I/O
3. **Path Rendering**: Group by user_id, collect line segments, render using LineCollection (batch rendering)
4. **Event Rendering**: Scatter plot markers for Kill, Killed, Loot, KilledByStorm events
5. **Heatmap Generation**: 2D histogram with Gaussian interpolation for density visualization
6. **Minimap Overlay**: Base minimap image (1024x1024) displayed as background
7. **Frame Pre-computation** (for playback): Divide match into time intervals, render minimap for each interval, convert to PIL images for display

## Coordinate Mapping Approach

The README.md provided the formula for converting world coordinates to minimap pixels:

```
u = (x - origin_x) / scale
v = (z - origin_z) / scale
pixel_x = u * image_size
pixel_y = (1 - v) * image_size
```

### Implementation Details

**Initial Challenge**: The README stated minimaps are 1024x1024 pixels, but actual images varied:
- AmbroseValley: 4320x4320
- GrandRift: 2160x2158
- Lockdown: 9000x9000

**Performance Issue**: Large minimap images caused slow rendering (matplotlib had to process 4320x4320 and 9000x9000 images)

**Solution**: Resized all minimap images to 1024x1024 using high-quality LANCZOS resampling:
- All minimaps now 1024x1024 pixels
- Coordinate mapper updated to use `image_size: 1024` for all maps
- Significantly improved rendering performance while maintaining quality for level designers

```python
# Current implementation
image_size = 1024  # Standardized for all maps
ax.imshow(minimap, extent=[0, image_size, image_size, 0])
```

This ensures coordinates map correctly across all maps with consistent performance.

## Assumptions Made

1. **Data Scope**: Implementation and testing are specific to the provided dataset format and structure. May not work with different data formats without modification.

## Tradeoffs

| Decision | Alternative | Tradeoff |
|----------|-------------|----------|
| Global data caching at startup | On-demand data loading | Global caching has 5-10s initial load but instant access thereafter |
| LineCollection for paths | Individual plot calls | LineCollection is faster but less flexible per-path customization |
| Minimap resize to 1024x1024 | Keep original sizes | Resize improves performance but reduces maximum resolution |
| On-demand frame pre-computation | Pre-compute all frames | On-demand saves time when playback disabled but adds delay when enabled |
| Per-match frame caching | Global frame cache | Per-match prevents conflicts but uses more memory for multiple matches |
| Matplotlib for rendering | Plotly/Bokeh | Matplotlib is simpler but less interactive (no zoom/pan) |
| 2D histogram for heatmaps | Kernel Density Estimation (KDE) | Histogram is faster but KDE is smoother |
| Streamlit session state for playback | JavaScript animation | Session state works but has slight delay vs JS |
| Single-page app | Multi-page app | Single page is simpler but could be organized better with pages |

## Performance Considerations

After performance optimizations:

- **Initial Data Load**: ~5-10 seconds (one-time global data caching with nested dictionary structure)
- **Match Selection**: Instant (O(1) dictionary lookup)
- **Map Selection**: Instant (dictionary lookup from pre-aggregated map data)
- **Rendering**: ~0.5-1 second to render a match with all paths and events (LineCollection, cached minimaps, 1024x1024 images)
- **Heatmap Generation**: ~0.3 seconds for 2D histogram (pre-aggregated map data)
- **Playback Enablement**: ~3-5 seconds (on-demand frame pre-computation with 30 frames)
- **Frame Navigation**: Instant (cached per match)
- **Memory**: ~50-100MB for global data cache (acceptable for modern machines)

**Key Optimizations:**
- Global data caching with nested dictionary structure eliminates repeated parquet file reads
- Dictionary lookups (O(1)) replace DataFrame filtering (O(n))
- Minimap images resized to 1024x1024 for faster rendering
- LineCollection for batch path rendering instead of individual plot calls
- Minimap image caching to avoid repeated disk I/O
- On-demand frame pre-computation only when playback is enabled
- Per-match frame caching prevents conflicts when switching matches

## Deployment Architecture

**Live Deployment**: https://player-journey-visualization-tool.streamlit.app/

**Local Development**:
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Environment Variables**: None required (all paths are relative)
