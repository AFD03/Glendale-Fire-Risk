#!/usr/bin/env python3
"""
Generate Sample DEM for Testing
================================

This script generates a synthetic DEM for testing the GIS processing pipeline
when real DEM data is not available.

The synthetic DEM creates a realistic terrain with:
- Elevation variation
- Valleys and ridges
- Smooth transitions

Usage:
    python generate_sample_dem.py

Note: This is for testing only. Use real DEM data for production analysis.

Author: Glendale Fire Risk Team
"""

import sys
from pathlib import Path

try:
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds
    import geopandas as gpd
except ImportError as e:
    print(f"Error: Required library not installed: {e}")
    print("\nPlease install dependencies:")
    print("  pip install numpy rasterio geopandas")
    sys.exit(1)


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data_raw"
BOUNDARY_PATH = DATA_RAW / "Glendale_boundary.shp"
OUTPUT_PATH = DATA_RAW / "dem" / "sample_dem.tif"
TARGET_CRS = "EPSG:2229"


def create_synthetic_terrain(width, height, base_elevation=300, variation=100):
    """
    Create a synthetic terrain using Perlin-like noise.
    
    Args:
        width: Width of the DEM in pixels
        height: Height of the DEM in pixels
        base_elevation: Base elevation in meters
        variation: Maximum elevation variation in meters
        
    Returns:
        numpy.ndarray: Synthetic elevation data
    """
    print(f"  Generating {width}x{height} elevation grid...")
    
    # Create coordinate grids
    x = np.linspace(0, 10, width)
    y = np.linspace(0, 10, height)
    X, Y = np.meshgrid(x, y)
    
    # Combine multiple sine waves to create terrain-like variation
    # This creates hills, valleys, and ridges
    terrain = (
        np.sin(X * 1.5) * np.cos(Y * 1.2) * 30 +
        np.sin(X * 3.0 + Y * 2.5) * 15 +
        np.cos(X * 0.8 - Y * 1.5) * 25 +
        np.sin(X * 4.2) * np.cos(Y * 3.8) * 10
    )
    
    # Add some random noise for realism
    np.random.seed(42)
    noise = np.random.randn(height, width) * 5
    terrain = terrain + noise
    
    # Normalize to desired range
    terrain = terrain - terrain.min()
    terrain = terrain / terrain.max() * variation
    terrain = terrain + base_elevation
    
    print(f"  Elevation range: {terrain.min():.1f} to {terrain.max():.1f} meters")
    
    return terrain


def main():
    """Generate sample DEM."""
    print("\n" + "="*60)
    print("  GENERATE SAMPLE DEM FOR TESTING")
    print("="*60)
    
    # Check for boundary
    if not BOUNDARY_PATH.exists():
        print(f"\n❌ Error: Boundary file not found!")
        print(f"   Expected: {BOUNDARY_PATH}")
        sys.exit(1)
    
    # Load boundary
    print(f"\n📍 Loading boundary from {BOUNDARY_PATH.name}...")
    boundary = gpd.read_file(BOUNDARY_PATH)
    boundary = boundary.to_crs(TARGET_CRS)
    
    # Get bounds
    minx, miny, maxx, maxy = boundary.total_bounds
    print(f"  Bounds: ({minx:.1f}, {miny:.1f}) to ({maxx:.1f}, {maxy:.1f})")
    
    # Calculate dimensions for ~10m resolution
    resolution = 10.0  # meters per pixel
    width = int((maxx - minx) / resolution)
    height = int((maxy - miny) / resolution)
    
    print(f"\n📐 DEM specifications:")
    print(f"  Resolution: {resolution}m")
    print(f"  Dimensions: {width} x {height} pixels")
    print(f"  Coverage: {(width*resolution/1000):.2f} x {(height*resolution/1000):.2f} km")
    
    # Generate terrain
    print("\n🏔️  Generating synthetic terrain...")
    terrain = create_synthetic_terrain(width, height)
    
    # Create transform
    transform = from_bounds(minx, miny, maxx, maxy, width, height)
    
    # Create output directory
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save DEM
    print(f"\n💾 Saving DEM to {OUTPUT_PATH}...")
    
    profile = {
        'driver': 'GTiff',
        'dtype': 'float32',
        'width': width,
        'height': height,
        'count': 1,
        'crs': TARGET_CRS,
        'transform': transform,
        'nodata': -9999,
        'compress': 'lzw'
    }
    
    with rasterio.open(OUTPUT_PATH, 'w', **profile) as dst:
        dst.write(terrain.astype(np.float32), 1)
        dst.set_band_description(1, "Elevation (meters)")
    
    print("  ✓ Sample DEM created successfully!")
    
    print("\n" + "="*60)
    print("  SAMPLE DEM GENERATION COMPLETE")
    print("="*60)
    print(f"\nOutput: {OUTPUT_PATH}")
    print("\n⚠️  WARNING: This is a SYNTHETIC DEM for TESTING only!")
    print("For production analysis, download real DEM data from USGS.")
    print("\nNext steps:")
    print("  python clip_and_reproject.py")
    print("  python derive_terrain.py")
    print("  python build_risk_model.py")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
