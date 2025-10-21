#!/usr/bin/env python3
"""
Derive Terrain Analysis Products
=================================

This script derives slope and aspect from a Digital Elevation Model (DEM).

Slope: The rate of change of elevation, measured in degrees (0-90°)
Aspect: The compass direction of the slope, measured in degrees (0-360°)
       where 0° = North, 90° = East, 180° = South, 270° = West

Usage:
    python derive_terrain.py

Requirements:
    - rasterio, numpy, scipy
    - Clipped DEM in data_processed/raster/

Author: Glendale Fire Risk Team
"""

import os
import sys
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage
from rasterio.transform import Affine
import warnings

warnings.filterwarnings('ignore')

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data_processed" / "raster"


def calculate_slope_aspect(dem_path, output_slope_path, output_aspect_path):
    """
    Calculate slope and aspect from DEM.
    
    Args:
        dem_path: Path to input DEM file
        output_slope_path: Path for output slope raster
        output_aspect_path: Path for output aspect raster
    """
    print(f"\n📐 Calculating slope and aspect from {dem_path.name}...")
    
    with rasterio.open(dem_path) as src:
        dem = src.read(1)
        profile = src.meta.copy()
        
        # Get cell size (assuming square cells)
        cell_size = src.res[0]
        print(f"  DEM shape: {dem.shape}")
        print(f"  Cell size: {cell_size}")
        print(f"  Elevation range: {np.nanmin(dem):.2f} to {np.nanmax(dem):.2f}")
        
        # Calculate gradients using Sobel filters
        # These approximate the rate of change in x and y directions
        print("  Computing gradients...")
        
        # Sobel kernels for gradient calculation
        # Using Horn's method (commonly used in GIS)
        kernel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]]) / (8 * cell_size)
        
        kernel_y = np.array([[1, 2, 1],
                            [0, 0, 0],
                            [-1, -2, -1]]) / (8 * cell_size)
        
        # Calculate gradients
        dz_dx = ndimage.convolve(dem, kernel_x)
        dz_dy = ndimage.convolve(dem, kernel_y)
        
        # Calculate slope in degrees
        print("  Computing slope...")
        slope_radians = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
        slope_degrees = np.degrees(slope_radians)
        
        # Clip slope to valid range
        slope_degrees = np.clip(slope_degrees, 0, 90)
        
        print(f"  Slope range: {np.nanmin(slope_degrees):.2f}° to {np.nanmax(slope_degrees):.2f}°")
        print(f"  Mean slope: {np.nanmean(slope_degrees):.2f}°")
        
        # Calculate aspect in degrees
        print("  Computing aspect...")
        aspect_radians = np.arctan2(dz_dy, -dz_dx)
        aspect_degrees = np.degrees(aspect_radians)
        
        # Convert aspect to compass bearing (0-360°)
        # Where 0° = North, 90° = East, 180° = South, 270° = West
        aspect_degrees = 90 - aspect_degrees
        aspect_degrees = np.where(aspect_degrees < 0, 
                                  aspect_degrees + 360, 
                                  aspect_degrees)
        
        # Set aspect to -1 for flat areas (slope < 1°)
        aspect_degrees = np.where(slope_degrees < 1, -1, aspect_degrees)
        
        print(f"  Aspect range: {np.nanmin(aspect_degrees):.2f}° to {np.nanmax(aspect_degrees):.2f}°")
        
        # Save slope
        print(f"\n💾 Saving slope to {output_slope_path.name}...")
        with rasterio.open(output_slope_path, 'w', **profile) as dst:
            dst.write(slope_degrees.astype(np.float32), 1)
            dst.set_band_description(1, "Slope (degrees)")
        print("  ✓ Slope saved")
        
        # Save aspect
        print(f"💾 Saving aspect to {output_aspect_path.name}...")
        with rasterio.open(output_aspect_path, 'w', **profile) as dst:
            dst.write(aspect_degrees.astype(np.float32), 1)
            dst.set_band_description(1, "Aspect (degrees from North)")
        print("  ✓ Aspect saved")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("  GLENDALE FIRE RISK - TERRAIN ANALYSIS")
    print("="*60)
    
    # Check for DEM
    dem_files = list(DATA_PROCESSED.glob("dem_clipped.tif"))
    
    if not dem_files:
        print("\n❌ Error: No clipped DEM found!")
        print(f"   Expected: {DATA_PROCESSED / 'dem_clipped.tif'}")
        print("   Please run clip_and_reproject.py first.")
        sys.exit(1)
    
    dem_path = dem_files[0]
    output_slope = DATA_PROCESSED / "slope.tif"
    output_aspect = DATA_PROCESSED / "aspect.tif"
    
    # Calculate slope and aspect
    try:
        calculate_slope_aspect(dem_path, output_slope, output_aspect)
        
        print("\n" + "="*60)
        print("  TERRAIN ANALYSIS COMPLETE")
        print("="*60)
        print(f"\nOutputs saved to: {DATA_PROCESSED}")
        print(f"  - Slope: {output_slope.name}")
        print(f"  - Aspect: {output_aspect.name}")
        print("\n✓ Ready for risk model classification!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
