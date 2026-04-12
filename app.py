import streamlit as st
import pandas as pd
from data_loader import load_day_data, get_available_dates, get_matches_for_date_map
from coordinate_mapper import world_to_pixel
from visualizations import render_minimap_with_paths, render_heatmap
import os

# Page config
st.set_page_config(
    page_title="LILA BLACK - Event Visualizer",
    page_icon="🎮",
    layout="wide"
)

# Custom CSS for tabs
st.markdown("""
<style>
div[data-testid="stTabs"] [data-testid="stTab"] {
    font-size: 24px;
    font-weight: bold;
    padding: 20px;
}
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    background-color: #f0f0f0;
}
</style>
""", unsafe_allow_html=True)

st.title("🎮 LILA BLACK - Player Event Visualizer")
st.markdown("Visualize gameplay data including player paths, combat events, and heatmaps.")

# Load all data globally at startup and pre-process into nested structure
@st.cache_resource
def load_global_data():
    """Load and pre-process all data into nested structure for instant lookups."""
    available_dates = get_available_dates("player_data")
    
    # Structure: {date: {map_id: {match_id: DataFrame}}}
    processed_data = {}
    
    # Pre-aggregate by map for heatmaps: {map_id: DataFrame}
    map_data = {
        "AmbroseValley": [],
        "GrandRift": [],
        "Lockdown": []
    }
    
    for date in available_dates:
        df = load_day_data(f"player_data/{date}")
        if df is None or df.empty:
            continue
        
        df['date_folder'] = date  # Add date folder for reference
        
        # Process into nested structure
        processed_data[date] = {}
        
        for map_id in ["AmbroseValley", "GrandRift", "Lockdown"]:
            map_df = df[df['map_id'] == map_id]
            if map_df.empty:
                processed_data[date][map_id] = {}
                continue
            
            processed_data[date][map_id] = {}
            
            # Group by match_id for instant access
            for match_id, match_df in map_df.groupby('match_id'):
                processed_data[date][map_id][match_id] = match_df.copy()
            
            # Add to map_data for heatmaps
            map_data[map_id].append(map_df)
    
    # Concatenate map data for heatmaps
    for map_id in map_data:
        if map_data[map_id]:
            map_data[map_id] = pd.concat(map_data[map_id], ignore_index=True)
        else:
            map_data[map_id] = pd.DataFrame()
    
    return processed_data, map_data

# Load global data with progress indicator
if 'processed_data' not in st.session_state or 'map_data' not in st.session_state:
    with st.spinner("Loading all game data (this happens once)..."):
        processed_data, map_data = load_global_data()
        st.session_state.processed_data = processed_data
        st.session_state.map_data = map_data

processed_data = st.session_state.processed_data
map_data = st.session_state.map_data

if not processed_data:
    st.error("No data available. Please check the player_data directory.")
    st.stop()

# Sidebar
st.sidebar.header("Filters")

# Date filter
available_dates = get_available_dates("player_data")
selected_date = st.sidebar.selectbox("Select Date", available_dates)

# View mode
view_mode = st.sidebar.radio("View Mode", ["Player Paths", "Heatmap"])

# Event type filters (for Player Paths)
if view_mode == "Player Paths":
    st.sidebar.subheader("Event Filters")
    show_position = st.sidebar.checkbox("Show Position/BotPosition", True)
    show_kills = st.sidebar.checkbox("Show Kills", True)
    show_deaths = st.sidebar.checkbox("Show Deaths", True)
    show_loot = st.sidebar.checkbox("Show Loot", True)
    show_storm = st.sidebar.checkbox("Show KilledByStorm", True)
    
    # Playback controls
    st.sidebar.subheader("Timeline Playback")
    enable_playback = st.sidebar.checkbox("Enable Playback", False)
    
    # Playback navigation buttons (only shown when enabled)
    if enable_playback:
        st.sidebar.subheader("Navigation")
        col1, col2, col3 = st.sidebar.columns(3)
        with col1:
            if st.button("◀", key="prev_frame"):
                frame_index_key = f"current_frame_index_{st.session_state.get('selected_match', '')}"
                if frame_index_key in st.session_state:
                    st.session_state[frame_index_key] = max(0, st.session_state[frame_index_key] - 1)
        with col2:
            if st.button("▶", key="play_frame"):
                frame_index_key = f"current_frame_index_{st.session_state.get('selected_match', '')}"
                frame_cache_key = f"precomputed_frames_{st.session_state.get('selected_match', '')}"
                if frame_index_key in st.session_state and frame_cache_key in st.session_state:
                    st.session_state[frame_index_key] = min(len(st.session_state[frame_cache_key]) - 1, st.session_state[frame_index_key] + 1)
        with col3:
            if st.button("▶▶", key="fast_frame"):
                frame_index_key = f"current_frame_index_{st.session_state.get('selected_match', '')}"
                frame_cache_key = f"precomputed_frames_{st.session_state.get('selected_match', '')}"
                if frame_index_key in st.session_state and frame_cache_key in st.session_state:
                    st.session_state[frame_index_key] = min(len(st.session_state[frame_cache_key]) - 1, st.session_state[frame_index_key] + 5)
        
        # Frame slider in sidebar
        frame_index_key = f"current_frame_index_{st.session_state.get('selected_match', '')}"
        frame_cache_key = f"precomputed_frames_{st.session_state.get('selected_match', '')}"
        if frame_index_key in st.session_state and frame_cache_key in st.session_state:
            current_frame_index = st.sidebar.slider(
                "Frame",
                min_value=0,
                max_value=len(st.session_state[frame_cache_key]) - 1,
                value=st.session_state[frame_index_key],
                step=1,
                key="frame_slider"
            )
            st.session_state[frame_index_key] = current_frame_index
else:
    # Heatmap type
    heatmap_type = st.sidebar.radio(
        "Heatmap Type",
        ["Kill Zones", "Death Zones", "Traffic (Position)"]
    )
    
    # Optional filters for heatmap
    st.sidebar.subheader("Heatmap Filters (Optional)")
    heatmap_filter_date = st.sidebar.selectbox("Filter by Date (Optional)", ["All Dates"] + available_dates)

# Pre-compute frames for playback
@st.cache_data
def precompute_frames(df, map_id, num_frames=50):
    """
    Pre-compute map frames at regular time intervals.
    
    Args:
        df: DataFrame containing match events
        map_id: Map identifier
        num_frames: Number of frames to generate
    
    Returns:
        List of (timestamp, image) tuples
    """
    import io
    from PIL import Image
    import matplotlib.pyplot as plt
    
    min_time = df['ts'].min()
    max_time = df['ts'].max()
    time_step = (max_time - min_time) / num_frames
    
    frames = []
    
    for i in range(num_frames):
        current_time = min_time + (i * time_step)
        filtered_df = df[df['ts'] <= current_time].copy()
        
        # Generate the minimap
        from visualizations import render_minimap_with_paths
        fig = render_minimap_with_paths(
            filtered_df,
            map_id,
            show_position=True,
            show_kills=True,
            show_deaths=True,
            show_loot=True,
            show_storm=True,
            time_filter=None
        )
        
        # Convert figure to image
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        frames.append((current_time, img))
        plt.close(fig)
    
    return frames

# Get data from pre-processed structure (instant dictionary lookup)
def get_data_by_date_map(date, map_id):
    """Get data for specific date and map using dictionary lookup."""
    if date not in processed_data:
        return None
    if map_id not in processed_data[date]:
        return None
    return processed_data[date][map_id]

def get_match_data(date, map_id, match_id):
    """Get data for specific match using dictionary lookup."""
    if date not in processed_data:
        return None
    if map_id not in processed_data[date]:
        return None
    if match_id not in processed_data[date][map_id]:
        return None
    return processed_data[date][map_id][match_id]

def get_map_data(map_id):
    """Get all data for a specific map using dictionary lookup."""
    return map_data.get(map_id, pd.DataFrame())

# Map selector (replaces tabs to only load data for selected map)
map_options = ["AmbroseValley", "GrandRift", "Lockdown"]
selected_map = st.selectbox("Select Map", map_options)

# Only load data for the selected map
if view_mode == "Player Paths":
    # Get data for selected date and map (instant dictionary lookup)
    data = get_data_by_date_map(selected_date, selected_map)
    
    if data is None or not data:
        st.warning(f"No data available for {selected_date} on {selected_map}")
        st.stop()
    
    # Match filter (instant - just get keys from dictionary)
    available_matches = sorted(data.keys())
    selected_match = st.selectbox("Select Match", available_matches)
    
    # Store selected match in session state for sidebar access
    st.session_state.selected_match = selected_match
    
    # Get match data (instant dictionary lookup)
    match_data = get_match_data(selected_date, selected_map, selected_match)
    
    st.subheader(f"Player Paths - {selected_match}")
    
    # Pre-compute frames if not already done for this match (on-demand)
    frame_cache_key = f"precomputed_frames_{selected_match}"
    frame_index_key = f"current_frame_index_{selected_match}"
    
    if enable_playback and frame_cache_key not in st.session_state:
        with st.spinner("Pre-computing frames..."):
            st.session_state[frame_cache_key] = precompute_frames(match_data, selected_map, num_frames=30)
            st.session_state[frame_index_key] = 0
    
    # Initialize frame index if not set
    if frame_index_key not in st.session_state:
        st.session_state[frame_index_key] = 0
    
    if enable_playback:
        # Display current frame (controls are now in sidebar)
        current_frame_index = st.session_state[frame_index_key]
        current_time, current_frame = st.session_state[frame_cache_key][current_frame_index]
        st.image(current_frame)
        st.caption(f"Timestamp: {current_time:.0f} ms | Frame {current_frame_index + 1}/{len(st.session_state[frame_cache_key])}")
    else:
        # Render minimap normally (without pre-computed frames)
        fig = render_minimap_with_paths(
            match_data,
            selected_map,
            show_position,
            show_kills,
            show_deaths,
            show_loot,
            show_storm,
            None
        )
        st.pyplot(fig, use_container_width=True)
    
    # Stats
    st.subheader("Match Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", match_data['user_id'].nunique())
    with col2:
        st.metric("Humans", match_data[match_data['user_id'].str.contains('-')]['user_id'].nunique())
    with col3:
        st.metric("Bots", match_data[~match_data['user_id'].str.contains('-')]['user_id'].nunique())
    with col4:
        st.metric("Total Events", len(match_data))

elif view_mode == "Heatmap":
    st.subheader(f"Event Heatmap - {selected_map}")
    
    # Optional filters for heatmap
    if heatmap_filter_date == "All Dates":
        # Get all data for this map (instant dictionary lookup)
        heatmap_data = get_map_data(selected_map)
        filter_match = "All Matches"
    else:
        # Get data for selected date (instant dictionary lookup)
        data = get_data_by_date_map(heatmap_filter_date, selected_map)
        if data is not None and data:
            available_matches = sorted(data.keys())
            filter_match = st.sidebar.selectbox("Filter by Match (Optional)", ["All Matches"] + available_matches, key="filter_match")
            
            if filter_match != "All Matches":
                heatmap_data = get_match_data(heatmap_filter_date, selected_map, filter_match)
            else:
                # Concatenate all matches for this date/map
                heatmap_data = pd.concat(data.values(), ignore_index=True)
        else:
            heatmap_data = pd.DataFrame()
            filter_match = "All Matches"
    
    if heatmap_data is None or heatmap_data.empty:
        st.warning(f"No data available for {selected_map}")
        st.stop()
    
    # Render heatmap
    fig = render_heatmap(heatmap_data, selected_map, heatmap_type)
    st.pyplot(fig, use_container_width=True)
    
    # Stats
    st.subheader("Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Matches", heatmap_data['match_id'].nunique())
    with col2:
        st.metric("Total Events", len(heatmap_data))
    with col3:
        st.metric("Total Players", heatmap_data['user_id'].nunique())
