#!/usr/bin/env python3
"""
Build Fire Risk Model
=====================

This script reclassifies slope, aspect, and vegetation layers into standardized
risk categories (1-5 scale) and combines them using a weighted overlay model.

Risk Categories:
    1 = Very Low
    2 = Low
    3 = Moderate
    4 = High
    5 = Very High

Usage:
    python build_risk_model.py

Requirements:
    - rasterio, numpy, geopandas
    - Processed terrain and vegetation data

Author: Glendale Fire Risk Team
"""

import os
import sys
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
import geopandas as gpd
import warnings

warnings.filterwarnings('ignore')

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data_processed"
RASTER_DIR = DATA_PROCESSED / "raster"
VECTOR_DIR = DATA_PROCESSED / "geojson"

# Risk model weights (must sum to 1.0)
WEIGHTS = {
    'slope': 0.45,      # Slope is critical for fire spread
    'aspect': 0.25,     # South/Southwest aspects are higher risk
    'vegetation': 0.30  # Fuel load matters significantly
}


def reclassify_slope(slope_path, output_path):
    """
    Reclassify slope into risk categories.
    
    Classification based on California fire research:
    - 0-5°: Very Low (1)
    - 5-15°: Low (2)
    - 15-25°: Moderate (3)
    - 25-35°: High (4)
    - >35°: Very High (5)
    """
    print("\n📊 Reclassifying slope...")
    
    with rasterio.open(slope_path) as src:
        slope = src.read(1)
        profile = src.meta.copy()
        
        # Create risk array
        slope_risk = np.zeros_like(slope, dtype=np.uint8)
        
        # Apply classification
        slope_risk[slope < 5] = 1
        slope_risk[(slope >= 5) & (slope < 15)] = 2
        slope_risk[(slope >= 15) & (slope < 25)] = 3
        slope_risk[(slope >= 25) & (slope < 35)] = 4
        slope_risk[slope >= 35] = 5
        
        # Handle NoData
        slope_risk[np.isnan(slope)] = 0
        
        print(f"  Slope risk distribution:")
        for risk_level in range(1, 6):
            count = np.sum(slope_risk == risk_level)
            pct = (count / slope_risk.size) * 100
            print(f"    Level {risk_level}: {count:,} cells ({pct:.2f}%)")
        
        # Save reclassified slope
        profile.update(dtype=rasterio.uint8, nodata=0)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(slope_risk, 1)
            dst.set_band_description(1, "Slope Risk (1-5)")
        
        print(f"  ✓ Saved to {output_path.name}")
        return slope_risk


def reclassify_aspect(aspect_path, output_path):
    """
    Reclassify aspect into risk categories.
    
    Classification based on solar exposure and prevailing winds:
    - Flat areas (-1): Low (2)
    - North (315-45°): Low (2)
    - East (45-135°): Moderate (3)
    - South (135-225°): Very High (5)
    - West (225-315°): High (4)
    
    South and Southwest facing slopes receive more sun and dry out faster.
    """
    print("\n🧭 Reclassifying aspect...")
    
    with rasterio.open(aspect_path) as src:
        aspect = src.read(1)
        profile = src.meta.copy()
        
        # Create risk array
        aspect_risk = np.zeros_like(aspect, dtype=np.uint8)
        
        # Apply classification
        # Flat areas
        aspect_risk[aspect == -1] = 2
        
        # North (315-360 and 0-45)
        aspect_risk[((aspect >= 315) | (aspect < 45)) & (aspect != -1)] = 2
        
        # East (45-135)
        aspect_risk[(aspect >= 45) & (aspect < 135)] = 3
        
        # South (135-225) - HIGHEST RISK
        aspect_risk[(aspect >= 135) & (aspect < 225)] = 5
        
        # West (225-315)
        aspect_risk[(aspect >= 225) & (aspect < 315)] = 4
        
        # Handle NoData
        aspect_risk[np.isnan(aspect)] = 0
        
        print(f"  Aspect risk distribution:")
        for risk_level in range(1, 6):
            count = np.sum(aspect_risk == risk_level)
            pct = (count / aspect_risk.size) * 100
            print(f"    Level {risk_level}: {count:,} cells ({pct:.2f}%)")
        
        # Save reclassified aspect
        profile.update(dtype=rasterio.uint8, nodata=0)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(aspect_risk, 1)
            dst.set_band_description(1, "Aspect Risk (1-5)")
        
        print(f"  ✓ Saved to {output_path.name}")
        return aspect_risk


def reclassify_vegetation(reference_raster_path, output_path):
    """
    Reclassify vegetation into risk categories.
    
    This is a placeholder that creates a moderate risk layer.
    In practice, this would use actual vegetation/fuel data.
    
    Classification would be based on fuel models:
    - Urban/Barren: Very Low (1)
    - Grass: Moderate (3)
    - Shrub: High (4)
    - Forest/Heavy Fuel: Very High (5)
    """
    print("\n🌿 Creating vegetation risk layer...")
    
    with rasterio.open(reference_raster_path) as src:
        profile = src.meta.copy()
        shape = (src.height, src.width)
        
        # Create a default moderate risk layer
        # In production, this would be based on actual vegetation data
        veg_risk = np.full(shape, 3, dtype=np.uint8)
        
        print(f"  ⚠️  Using default moderate risk (level 3) for all areas")
        print(f"  ℹ️  To improve accuracy, add vegetation data to data_raw/vegetation/")
        
        # Save vegetation risk
        profile.update(dtype=rasterio.uint8, nodata=0)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(veg_risk, 1)
            dst.set_band_description(1, "Vegetation Risk (1-5)")
        
        print(f"  ✓ Saved to {output_path.name}")
        return veg_risk


def calculate_weighted_risk(slope_risk, aspect_risk, veg_risk, 
                           reference_path, output_path):
    """
    Calculate final weighted fire risk score.
    
    Final Risk = (w_slope × slope_risk) + (w_aspect × aspect_risk) + 
                 (w_veg × veg_risk)
    """
    print("\n🔥 Calculating weighted fire risk...")
    print(f"  Weights: Slope={WEIGHTS['slope']}, " +
          f"Aspect={WEIGHTS['aspect']}, Vegetation={WEIGHTS['vegetation']}")
    
    # Calculate weighted risk
    weighted_risk = (
        WEIGHTS['slope'] * slope_risk +
        WEIGHTS['aspect'] * aspect_risk +
        WEIGHTS['vegetation'] * veg_risk
    )
    
    # Round to nearest integer and convert to 1-5 scale
    final_risk = np.round(weighted_risk).astype(np.uint8)
    final_risk = np.clip(final_risk, 1, 5)
    
    # Handle NoData (where any input is 0)
    nodata_mask = (slope_risk == 0) | (aspect_risk == 0) | (veg_risk == 0)
    final_risk[nodata_mask] = 0
    
    print(f"\n  Final risk distribution:")
    for risk_level in range(1, 6):
        count = np.sum(final_risk == risk_level)
        pct = (count / final_risk[final_risk > 0].size) * 100 if np.any(final_risk > 0) else 0
        risk_label = ['', 'Very Low', 'Low', 'Moderate', 'High', 'Very High'][risk_level]
        print(f"    Level {risk_level} ({risk_label:>10}): {count:,} cells ({pct:.2f}%)")
    
    # Save final risk
    with rasterio.open(reference_path) as src:
        profile = src.meta.copy()
        profile.update(dtype=rasterio.uint8, nodata=0)
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(final_risk, 1)
            dst.set_band_description(1, "Fire Risk Score (1-5)")
    
    print(f"\n  ✓ Saved to {output_path.name}")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("  GLENDALE FIRE RISK - RISK MODEL CLASSIFICATION")
    print("="*60)
    
    # Check for required inputs
    slope_path = RASTER_DIR / "slope.tif"
    aspect_path = RASTER_DIR / "aspect.tif"
    
    if not slope_path.exists():
        print(f"\n❌ Error: Slope raster not found!")
        print(f"   Expected: {slope_path}")
        print("   Please run derive_terrain.py first.")
        sys.exit(1)
    
    if not aspect_path.exists():
        print(f"\n❌ Error: Aspect raster not found!")
        print(f"   Expected: {aspect_path}")
        print("   Please run derive_terrain.py first.")
        sys.exit(1)
    
    # Define output paths
    slope_risk_path = RASTER_DIR / "slope_risk.tif"
    aspect_risk_path = RASTER_DIR / "aspect_risk.tif"
    veg_risk_path = RASTER_DIR / "vegetation_risk.tif"
    final_risk_path = RASTER_DIR / "fire_risk.tif"
    
    try:
        # Reclassify each layer
        slope_risk = reclassify_slope(slope_path, slope_risk_path)
        aspect_risk = reclassify_aspect(aspect_path, aspect_risk_path)
        veg_risk = reclassify_vegetation(slope_path, veg_risk_path)
        
        # Calculate final weighted risk
        calculate_weighted_risk(slope_risk, aspect_risk, veg_risk,
                              slope_path, final_risk_path)
        
        print("\n" + "="*60)
        print("  RISK MODEL COMPLETE")
        print("="*60)
        print(f"\nRisk layers saved to: {RASTER_DIR}")
        print(f"  - Slope Risk: {slope_risk_path.name}")
        print(f"  - Aspect Risk: {aspect_risk_path.name}")
        print(f"  - Vegetation Risk: {veg_risk_path.name}")
        print(f"  - Final Fire Risk: {final_risk_path.name}")
        print("\n✓ Risk model ready for visualization in QGIS and Dash app!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
