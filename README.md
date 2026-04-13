# LILA BLACK - Player Event Visualizer

A web-based visualization tool for analyzing LILA BLACK game event data. Built for Level Designers to understand player behavior, combat patterns, and map usage through interactive visualizations.

## Features

- **Player Path Visualization**: View human (green) and bot (red) movement paths on game minimaps
- **Event Markers**: Display kill, death, loot, and storm events with distinct colors
- **Timeline Playback**: Timeline replay of player movement and event markers on the minimap frame by frame
- **Heatmaps**: Density maps for kill zones, death zones, and player traffic
- **Interactive Filtering**: Filter by map, date, and match ID for both Player Path and Heatmaps
- **Match Statistics**: View player counts, human/bot distribution, and total events

## Tech Stack

- **Python 3.10+**
- **Streamlit 1.31.0** - Web framework
- **Pandas 2.2.0** - Data manipulation
- **PyArrow 15.0.0** - Parquet file reading
- **Matplotlib 3.8.2** - Visualization
- **Seaborn 0.13.2** - Statistical visualization
- **NumPy 1.24.4** - Numerical computing
- **Pillow 10.2.0** - Image processing

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Local Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd player-journey-visualization-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to `http://localhost:8501`

## Project Structure

```
.
├── app.py                  # Main Streamlit application
├── data_loader.py          # Parquet data loading utilities
├── coordinate_mapper.py    # World-to-pixel coordinate conversion
├── visualizations.py       # Matplotlib rendering functions
├── requirements.txt        # Python dependencies
├── ARCHITECTURE.md         # Architecture documentation
├── INSIGHTS.md             # Data analysis insights
├── README.md               # This file
└── player_data.zip/        # Game event data
    ├── February_10/
    ├── February_11/
    ├── February_12/
    ├── February_13/
    ├── February_14/
    ├── minimaps/
    └── README.md           # Data description
```

## Usage

### Viewing Player Paths

1. Select a date from the sidebar (e.g., February_10)
2. Select a map from the main area (AmbroseValley, GrandRift, or Lockdown)
3. Select a specific match ID
4. Toggle event filters in the sidebar to show/hide specific event types:
   - Show Position/BotPosition
   - Show Kills
   - Show Deaths
   - Show Loot
   - Show KilledByStorm
5. View the minimap with player paths and event markers
6. Match statistics display below the minimap (Total Players, Humans, Bots, Total Events)

### Animated Playback

1. Enable "Enable Playback" checkbox in the sidebar
2. Use navigation buttons to control playback:
   - ◀ Previous frame
   - ▶ Next frame
   - ▶▶ Skip 5 frames
3. Use the frame slider to scrub through the match

### Heatmaps

1. Switch to "Heatmap" view mode in the sidebar
2. Select a map from the main area
3. Select heatmap type from the sidebar:
   - Kill Zones - Where players are getting kills
   - Death Zones - Where players are dying
   - Traffic (Position) - Where players spend most time
4. Optionally filter by date and match from the sidebar
5. View the density overlay on the minimap
6. Statistics display below the heatmap (Total Matches, Total Events, Total Players)

## Data Format

The tool expects Parquet files in the following format:

- **Location**: `player_data/February_XX/`
- **Filename**: `{user_id}_{match_id}.nakama-0`
- **Columns**: user_id, match_id, map_id, x, y, z, ts, event
- **Event Types**: Position, BotPosition, Kill, Killed, BotKill, BotKilled, Loot, KilledByStorm

See `player_data.zip/README.md` for detailed data documentation.

## Deployment

**Live Demo:** [Player Journey Visualization Tool](https://player-journey-visualization-tool.streamlit.app/)

## Environment Variables

No environment variables are required for this application. All configuration is handled through:
- Relative file paths for data loading
- Streamlit's built-in configuration
- Hardcoded map configurations in `coordinate_mapper.py`

The application is designed to work out-of-the-box with the provided `player_data.zip` file.

## Troubleshooting

**Issue**: "ModuleNotFoundError: No module named 'pyarrow'"
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: "FileNotFoundError" when loading data
- **Solution**: Ensure `player_data.zip` file exists in the project directory

**Issue**: Minimap not displaying correctly
- **Solution**: Check that minimap images exist in `player_data/minimaps/`

**Issue**: Slow loading times
- **Solution**: Data is loaded and cached globally at startup. All subsequent interactions are instant.

## Documentation

- **ARCHITECTURE.md**: Detailed architecture documentation, tech stack rationale, data flow, and coordinate mapping approach
- **INSIGHTS.md**: Three data-backed insights about game balance, combat patterns, and map-specific issues

## License

This project was created for the LILA APM Written Test assignment.
