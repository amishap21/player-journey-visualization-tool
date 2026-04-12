import pandas as pd
import pyarrow.parquet as pq
import os
import zipfile
from typing import Optional
import streamlit as st

def extract_local_data(zip_path: str = "player_data.zip", extract_to: str = "player_data") -> bool:
    """
    Extract data from local ZIP file.
    
    Args:
        zip_path: Path to local ZIP file containing player_data
        extract_to: Local directory to extract to
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use absolute paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        abs_zip_path = os.path.join(script_dir, zip_path)
        abs_extract_to = os.path.join(script_dir, extract_to)
        
        with st.spinner("Extracting data from local zip file..."):
            with zipfile.ZipFile(abs_zip_path, 'r') as zip_ref:
                zip_ref.extractall(abs_extract_to)
        return True
    except Exception as e:
        st.error(f"Failed to extract data: {e}")
        return False

def ensure_data_available():
    """
    Ensure player_data is available locally, extract from local zip file if needed.
    """
    # Use absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    player_data_path = os.path.join(script_dir, "player_data")
    zip_path = os.path.join(script_dir, "player_data.zip")
    
    # Check if player_data exists locally
    if os.path.exists(player_data_path):
        return
    
    # Check if local zip file exists
    if not os.path.exists(zip_path):
        st.error(f"player_data not found locally and {zip_path} not found in repository")
        st.error(f"Current working directory: {os.getcwd()}")
        st.error(f"Script directory: {script_dir}")
        st.error(f"Files in script directory: {os.listdir(script_dir)}")
        st.stop()
    
    # Extract data from local zip file to script_dir (not player_data subdirectory)
    # This avoids nested player_data/player_data structure
    success = extract_local_data(zip_path, script_dir)
    if not success:
        st.error(f"Failed to extract player_data from {zip_path}")
        st.stop()

def load_day_data(folder_path: str) -> Optional[pd.DataFrame]:
    """
    Load all parquet files from a date folder into a single DataFrame.
    
    Args:
        folder_path: Path to the date folder (e.g., "player_data/February_10")
    
    Returns:
        Combined DataFrame with all events from that day, or None if no data
    """
    # Convert to absolute path if relative
    if not os.path.isabs(folder_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(script_dir, folder_path)
    
    if not os.path.exists(folder_path):
        return None
    
    frames = []
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            try:
                table = pq.read_table(filepath)
                df = table.to_pandas()
                frames.append(df)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue
    
    if not frames:
        return None
    
    combined_df = pd.concat(frames, ignore_index=True)
    
    # Decode event column from bytes to string
    if 'event' in combined_df.columns:
        combined_df['event'] = combined_df['event'].apply(
            lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
        )
    
    # Convert timestamp to numeric milliseconds
    if 'ts' in combined_df.columns:
        combined_df['ts'] = pd.to_numeric(combined_df['ts'], errors='coerce')
    
    return combined_df

def get_available_dates(base_path: str) -> list:
    """
    Get list of available date folders.
    
    Args:
        base_path: Path to player_data directory
    
    Returns:
        List of date folder names sorted chronologically
    """
    # Convert to absolute path if relative
    if not os.path.isabs(base_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(script_dir, base_path)
    
    if not os.path.exists(base_path):
        return []
    
    dates = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and item.startswith("February_"):
            dates.append(item)
    
    return sorted(dates)

def get_matches_for_date_map(folder_path: str, map_id: str) -> list:
    """
    Get list of match IDs for a specific date and map.
    
    Args:
        folder_path: Path to the date folder
        map_id: Map identifier (e.g., "AmbroseValley")
    
    Returns:
        List of unique match IDs
    """
    df = load_day_data(folder_path)
    if df is None:
        return []
    
    matches = df[df['map_id'] == map_id]['match_id'].unique()
    return sorted(matches)

def is_human_user(user_id: str) -> bool:
    """
    Determine if a user_id belongs to a human player or bot.
    
    Args:
        user_id: User identifier from the data
    
    Returns:
        True if human (UUID), False if bot (numeric)
    """
    return '-' in str(user_id)
