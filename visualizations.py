import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
import pandas as pd
import numpy as np
from coordinate_mapper import world_to_pixel, MAP_CONFIGS
from PIL import Image
import os

# Cache for minimap images to avoid reloading
_minimap_cache = {}

def get_minimap_image(map_id: str) -> Image.Image:
    """
    Load the minimap image for a given map with caching.
    
    Args:
        map_id: Map identifier (e.g., "AmbroseValley")
    
    Returns:
        PIL Image object
    """
    # Return cached image if available
    if map_id in _minimap_cache:
        return _minimap_cache[map_id]
    
    # Map filename based on README.md
    if map_id == "AmbroseValley":
        filename = "AmbroseValley_Minimap.png"
    elif map_id == "GrandRift":
        filename = "GrandRift_Minimap.png"
    elif map_id == "Lockdown":
        filename = "Lockdown_Minimap.jpg"
    else:
        raise ValueError(f"Unknown map_id: {map_id}")
    
    # Use absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "player_data", "minimaps", filename)
    if not os.path.exists(image_path):
        # Create a blank image if minimap not found
        blank_image = Image.new('RGB', (1024, 1024), color='gray')
        _minimap_cache[map_id] = blank_image
        return blank_image
    
    # Load and cache the image
    img = Image.open(image_path)
    _minimap_cache[map_id] = img
    return img

def render_minimap_with_paths(
    df: pd.DataFrame,
    map_id: str,
    show_position: bool = True,
    show_kills: bool = True,
    show_deaths: bool = True,
    show_loot: bool = True,
    show_storm: bool = True,
    time_filter: float = None
) -> plt.Figure:
    """
    Render minimap with player paths and event markers.
    
    Args:
        df: DataFrame containing match events
        map_id: Map identifier
        show_position: Whether to show position/botposition events
        show_kills: Whether to show kill events
        show_deaths: Whether to show death events
        show_loot: Whether to show loot events
        show_storm: Whether to show storm deaths
        time_filter: If provided, only show events up to this timestamp
    
    Returns:
        Matplotlib figure
    """
    # Apply time filter if provided
    if time_filter is not None:
        df = df[df['ts'] <= time_filter].copy()
    
    # Load minimap image
    minimap = get_minimap_image(map_id)
    image_size = minimap.size[0]  # Assuming square images
    
    # Create figure with reduced size for better performance
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(minimap, extent=[0, image_size, image_size, 0])
    
    # Separate human and bot data (create a copy to avoid SettingWithCopyWarning)
    df = df.copy()
    df['is_human'] = df['user_id'].apply(lambda x: '-' in str(x))
    
    # Draw player paths using LineCollection for better performance
    if show_position:
        human_segments = []
        bot_segments = []
        
        for user_id, user_data in df.groupby('user_id'):
            is_human = user_data['is_human'].iloc[0]
            
            # Filter for position events only
            pos_data = user_data[user_data['event'].isin(['Position', 'BotPosition'])]
            
            if len(pos_data) < 2:
                continue
            
            # Convert to pixel coordinates
            pixels = pos_data.apply(
                lambda row: world_to_pixel(row['x'], row['z'], map_id),
                axis=1
            ).tolist()
            
            # Create line segments
            points = np.array(pixels)
            segments = np.array([points[:-1], points[1:]]).transpose(1, 0, 2)
            
            if is_human:
                human_segments.extend(segments)
            else:
                bot_segments.extend(segments)
        
        # Draw human paths
        if human_segments:
            human_lc = LineCollection(human_segments, colors='#00ff00', alpha=0.6, linewidths=1.5)
            ax.add_collection(human_lc)
        
        # Draw bot paths
        if bot_segments:
            bot_lc = LineCollection(bot_segments, colors='#ff0000', alpha=0.4, linewidths=1.0)
            ax.add_collection(bot_lc)
    
    # Draw event markers
    event_colors = {
        'Kill': '#ff6600',          # Orange
        'Killed': '#ff0000',        # Red
        'BotKill': '#00ccff',       # Light blue
        'BotKilled': '#cc00ff',     # Purple
        'Loot': '#ffff00',          # Yellow
        'KilledByStorm': '#00ffff'  # Cyan
    }
    
    event_sizes = {
        'Kill': 80,
        'Killed': 80,
        'BotKill': 60,
        'BotKilled': 60,
        'Loot': 40,
        'KilledByStorm': 100
    }
    
    for event_type, show in [
        ('Kill', show_kills),
        ('Killed', show_deaths),
        ('BotKill', show_kills),
        ('BotKilled', show_deaths),
        ('Loot', show_loot),
        ('KilledByStorm', show_storm)
    ]:
        if not show:
            continue
        
        event_data = df[df['event'] == event_type]
        if event_data.empty:
            continue
        
        # Convert to pixel coordinates
        pixels = event_data.apply(
            lambda row: world_to_pixel(row['x'], row['z'], map_id),
            axis=1
        ).tolist()
        
        x_coords = [p[0] for p in pixels]
        y_coords = [p[1] for p in pixels]
        
        ax.scatter(
            x_coords, y_coords,
            c=event_colors[event_type],
            s=event_sizes[event_type],
            marker='o',
            edgecolors='black',
            linewidths=0.5,
            alpha=0.8,
            label=event_type
        )
    
    # Add legend only if there are events to show
    legend_artists = []
    for event_type in event_colors.keys():
        if show_kills and event_type in ['Kill', 'BotKill']:
            legend_artists.append(event_type)
        elif show_deaths and event_type in ['Killed', 'BotKilled']:
            legend_artists.append(event_type)
        elif show_loot and event_type == 'Loot':
            legend_artists.append(event_type)
        elif show_storm and event_type == 'KilledByStorm':
            legend_artists.append(event_type)
    
    if legend_artists:
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
    
    # Set title and labels
    ax.set_title(f"Player Paths & Events - {map_id}", fontsize=14, fontweight='bold')
    ax.set_xlabel("X (pixels)", fontsize=10)
    ax.set_ylabel("Z (pixels)", fontsize=10)
    
    # Remove ticks for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.tight_layout()
    return fig

def render_heatmap(df: pd.DataFrame, map_id: str, heatmap_type: str) -> plt.Figure:
    """
    Render a heatmap for the specified event type.
    
    Args:
        df: DataFrame containing match events
        map_id: Map identifier
        heatmap_type: Type of heatmap ("Kill Zones", "Death Zones", "Traffic (Position)")
    
    Returns:
        Matplotlib figure
    """
    # Load minimap image
    minimap = get_minimap_image(map_id)
    image_size = minimap.size[0]  # Assuming square images
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(minimap, extent=[0, image_size, image_size, 0])
    
    # Filter data based on heatmap type
    if heatmap_type == "Kill Zones":
        event_filter = ['Kill', 'BotKill']
        cmap = 'Reds'
        title = "Kill Zones"
    elif heatmap_type == "Death Zones":
        event_filter = ['Killed', 'BotKilled', 'KilledByStorm']
        cmap = 'Blues'
        title = "Death Zones"
    else:  # Traffic
        event_filter = ['Position', 'BotPosition']
        cmap = 'YlOrRd'
        title = "Player Traffic"
    
    filtered_df = df[df['event'].isin(event_filter)]
    
    if filtered_df.empty:
        ax.text(512, 512, f"No {heatmap_type.lower()} data available", 
                ha='center', va='center', fontsize=16, color='white',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        ax.set_title(f"{title} - {map_id}", fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig
    
    # Convert to pixel coordinates
    pixels = filtered_df.apply(
        lambda row: world_to_pixel(row['x'], row['z'], map_id),
        axis=1
    ).tolist()
    
    x_coords = [p[0] for p in pixels]
    y_coords = [p[1] for p in pixels]
    
    # Create heatmap using 2D histogram
    heatmap, xedges, yedges = np.histogram2d(
        x_coords, y_coords,
        bins=50,
        range=[[0, image_size], [0, image_size]]
    )
    
    # Plot heatmap
    im = ax.imshow(
        heatmap.T,
        extent=[0, image_size, image_size, 0],
        origin='upper',
        cmap=cmap,
        alpha=0.6,
        interpolation='gaussian'
    )
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Event Density', rotation=270, labelpad=20)
    
    # Set title
    ax.set_title(f"{title} - {map_id}", fontsize=14, fontweight='bold')
    
    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.tight_layout()
    return fig
