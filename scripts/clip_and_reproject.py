#!/usr/bin/env python3
"""
Clip and Reproject GIS Data
============================

This script clips all input datasets to the Glendale boundary and reprojects
them to a common coordinate reference system (CRS).

Usage:
    python clip_and_reproject.py

Requirements:
    - geopandas, rasterio, fiona
    - Input data in data_raw/ directories
    - Glendale boundary shapefile

Author: Glendale Fire Risk Team
"""

import os
import sys
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import mapping
import warnings

warnings.filterwarnings('ignore')

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data_raw"
DATA_PROCESSED = PROJECT_ROOT / "data_processed"
TARGET_CRS = "EPSG:2229"  # NAD83 / California zone 5


def ensure_directories():
    """Create necessary output directories."""
    directories = [
        DATA_PROCESSED / "geojson",
        DATA_PROCESSED / "raster"
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    print("✓ Output directories created")


def load_boundary():
    """Load and reproject Glendale boundary to target CRS."""
    print("\n📍 Loading Glendale boundary...")
    boundary_files = list(DATA_RAW.glob("**/Glendale_boundary.shp"))
    
    if not boundary_files:
        raise FileNotFoundError(
            "Glendale_boundary.shp not found in data_raw/. "
            "Please ensure boundary shapefile is present."
        )
    
    boundary = gpd.read_file(boundary_files[0])
    boundary = boundary.to_crs(TARGET_CRS)
    print(f"  Boundary CRS: {boundary.crs}")
    print(f"  Boundary bounds: {boundary.total_bounds}")
    return boundary


def clip_vector_data(input_path, boundary, output_name):
    """
    Clip vector data to boundary and save as GeoJSON.
    
    Args:
        input_path: Path to input vector file
        boundary: GeoDataFrame with clipping boundary
        output_name: Name for output file (without extension)
    """
    print(f"\n✂️  Clipping {input_path.name}...")
    
    try:
        # Read input data
        gdf = gpd.read_file(input_path)
        print(f"  Original CRS: {gdf.crs}")
        print(f"  Original features: {len(gdf)}")
        
        # Reproject to target CRS
        gdf = gdf.to_crs(TARGET_CRS)
        
        # Clip to boundary
        gdf_clipped = gpd.clip(gdf, boundary)
        print(f"  Clipped features: {len(gdf_clipped)}")
        
        # Save as GeoJSON
        output_path = DATA_PROCESSED / "geojson" / f"{output_name}.geojson"
        gdf_clipped.to_file(output_path, driver="GeoJSON")
        print(f"  ✓ Saved to {output_path}")
        
        return gdf_clipped
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def clip_raster_data(input_path, boundary, output_name):
    """
    Clip raster data to boundary and save as GeoTIFF.
    
    Args:
        input_path: Path to input raster file
        boundary: GeoDataFrame with clipping boundary
        output_name: Name for output file (without extension)
    """
    print(f"\n✂️  Clipping {input_path.name}...")
    
    try:
        with rasterio.open(input_path) as src:
            print(f"  Original CRS: {src.crs}")
            print(f"  Original bounds: {src.bounds}")
            print(f"  Resolution: {src.res}")
            
            # Reproject boundary to raster CRS for clipping
            boundary_raster_crs = boundary.to_crs(src.crs)
            
            # Get geometry for masking
            geoms = [mapping(geom) for geom in boundary_raster_crs.geometry]
            
            # Clip raster
            out_image, out_transform = mask(src, geoms, crop=True)
            out_meta = src.meta.copy()
            
            # Update metadata
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
            
            # If CRS needs reprojection, do it
            if src.crs != TARGET_CRS:
                print(f"  Reprojecting to {TARGET_CRS}...")
                # Calculate transform for target CRS
                transform, width, height = calculate_default_transform(
                    src.crs, TARGET_CRS, 
                    out_image.shape[2], out_image.shape[1],
                    *rasterio.transform.array_bounds(
                        out_image.shape[1], out_image.shape[2], out_transform
                    )
                )
                
                # Create output array
                out_image_reprojected = rasterio.warp.reproject(
                    out_image,
                    destination=rasterio.band(src, 1),
                    src_transform=out_transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=TARGET_CRS,
                    resampling=Resampling.bilinear
                )
                
                out_meta.update({
                    "crs": TARGET_CRS,
                    "transform": transform,
                    "width": width,
                    "height": height
                })
                out_image = out_image_reprojected[0]
            
            # Save clipped raster
            output_path = DATA_PROCESSED / "raster" / f"{output_name}.tif"
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(out_image)
            
            print(f"  ✓ Saved to {output_path}")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")


def process_all_data():
    """Process all available data files."""
    print("\n" + "="*60)
    print("  GLENDALE FIRE RISK - DATA CLIPPING & REPROJECTION")
    print("="*60)
    
    # Create directories
    ensure_directories()
    
    # Load boundary
    boundary = load_boundary()
    
    # Process vector data
    print("\n" + "-"*60)
    print("VECTOR DATA")
    print("-"*60)
    
    # Buildings (if in raw format)
    buildings_raw = list(DATA_RAW.glob("**/buildings/*.shp"))
    if buildings_raw:
        clip_vector_data(buildings_raw[0], boundary, "buildings_clipped")
    else:
        print("\n⚠️  No raw building shapefiles found in data_raw/buildings/")
        print("   If buildings are already processed, this is OK.")
    
    # Vegetation/Fuel
    vegetation_files = list(DATA_RAW.glob("**/vegetation/*.shp"))
    if vegetation_files:
        clip_vector_data(vegetation_files[0], boundary, "vegetation_clipped")
    else:
        print("\n⚠️  No vegetation shapefiles found in data_raw/vegetation/")
    
    # Fire Hazard Severity Zones
    fhsz_files = list(DATA_RAW.glob("**/fhsz/*.shp"))
    if fhsz_files:
        clip_vector_data(fhsz_files[0], boundary, "fhsz_clipped")
    else:
        print("\n⚠️  No FHSZ shapefiles found in data_raw/fhsz/")
    
    # Process raster data
    print("\n" + "-"*60)
    print("RASTER DATA")
    print("-"*60)
    
    # DEM
    dem_files = list(DATA_RAW.glob("**/dem/*.tif")) + \
                list(DATA_RAW.glob("**/dem/*.tiff"))
    if dem_files:
        clip_raster_data(dem_files[0], boundary, "dem_clipped")
    else:
        print("\n⚠️  No DEM files found in data_raw/dem/")
    
    print("\n" + "="*60)
    print("  PROCESSING COMPLETE")
    print("="*60)
    print(f"\nProcessed data saved to: {DATA_PROCESSED}")
    print(f"  - Vector data: {DATA_PROCESSED / 'geojson'}")
    print(f"  - Raster data: {DATA_PROCESSED / 'raster'}")


if __name__ == "__main__":
    try:
        process_all_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
