"""
Coordinate mapping utilities for converting world coordinates to minimap pixel coordinates.
"""

# Map configurations from README.md
# Minimap images resized to 1024x1024 for better performance
MAP_CONFIGS = {
    'AmbroseValley': {
        'scale': 900,
        'origin_x': -370,
        'origin_z': -473,
        'image_size': 1024
    },
    'GrandRift': {
        'scale': 581,
        'origin_x': -290,
        'origin_z': -290,
        'image_size': 1024
    },
    'Lockdown': {
        'scale': 1000,
        'origin_x': -500,
        'origin_z': -500,
        'image_size': 1024
    }
}

def world_to_pixel(x: float, z: float, map_id: str) -> tuple[int, int]:
    """
    Convert world coordinates (x, z) to minimap pixel coordinates.
    
    Formula from README.md:
    Step 1: Convert world coords to UV (0-1 range)
      u = (x - origin_x) / scale
      v = (z - origin_z) / scale
    
    Step 2: Convert UV to pixel coords (1024x1024 image)
      pixel_x = u * 1024
      pixel_y = (1 - v) * 1024    ← Y is flipped (image origin is top-left)
    
    Args:
        x: World X coordinate
        z: World Z coordinate
        map_id: Map identifier (e.g., "AmbroseValley")
    
    Returns:
        Tuple of (pixel_x, pixel_y) as integers
    
    Raises:
        ValueError: If map_id is not recognized
    """
    if map_id not in MAP_CONFIGS:
        raise ValueError(f"Unknown map_id: {map_id}")
    
    config = MAP_CONFIGS[map_id]
    scale = config['scale']
    origin_x = config['origin_x']
    origin_z = config['origin_z']
    image_size = config['image_size']
    
    # Step 1: Convert to UV (0-1 range)
    u = (x - origin_x) / scale
    v = (z - origin_z) / scale
    
    # Step 2: Convert to pixel coordinates
    pixel_x = int(u * image_size)
    pixel_y = int((1 - v) * image_size)
    
    return pixel_x, pixel_y

def pixel_to_world(pixel_x: int, pixel_y: int, map_id: str) -> tuple[float, float]:
    """
    Convert minimap pixel coordinates back to world coordinates.
    
    Args:
        pixel_x: Pixel X coordinate
        pixel_y: Pixel Y coordinate
        map_id: Map identifier
    
    Returns:
        Tuple of (world_x, world_z) as floats
    """
    if map_id not in MAP_CONFIGS:
        raise ValueError(f"Unknown map_id: {map_id}")
    
    config = MAP_CONFIGS[map_id]
    scale = config['scale']
    origin_x = config['origin_x']
    origin_z = config['origin_z']
    image_size = config['image_size']
    
    # Convert pixel to UV
    u = pixel_x / image_size
    v = 1 - (pixel_y / image_size)  # Y is flipped
    
    # Convert UV to world coordinates
    world_x = u * scale + origin_x
    world_z = v * scale + origin_z
    
    return world_x, world_z
