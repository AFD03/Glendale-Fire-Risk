# GIS Data Processing Scripts

This directory contains Python scripts for processing GIS data for the Glendale Fire Risk project.

## Overview

The scripts perform the following tasks:
1. **Data Download** - Instructions for acquiring source data
2. **Clipping & Reprojection** - Standardize and clip data to Glendale boundary
3. **Terrain Analysis** - Derive slope and aspect from DEM
4. **Risk Classification** - Reclassify layers and build fire risk model

## Prerequisites

### Install Dependencies

```bash
# From project root directory
pip install -r requirements.txt
```

**Note**: Installing GDAL can be tricky. If you encounter issues:

**On Ubuntu/Debian:**
```bash
sudo apt-get install gdal-bin libgdal-dev
pip install gdal==$(gdal-config --version)
```

**On macOS (with Homebrew):**
```bash
brew install gdal
pip install gdal==$(gdal-config --version)
```

**Using Conda (recommended):**
```bash
conda install -c conda-forge gdal rasterio geopandas
```

## Workflow

### Step 1: Data Acquisition

Follow instructions in `data_download_notes.md` to download required datasets:
- Digital Elevation Model (DEM) from USGS
- Vegetation/Fuel data from CalFire
- Fire Hazard Severity Zones from CalFire

Required data structure:
```
data_raw/
├── boundary/          # ✓ Already present
│   └── Glendale_boundary.shp
├── buildings/         # Optional: raw buildings before clipping
├── dem/              # Download required
│   └── *.tif
├── vegetation/       # Download optional (defaults to moderate risk)
│   └── *.shp
└── fhsz/            # Download optional
    └── *.shp
```

### Step 2: Clip and Reproject Data

Standardizes all data to a common CRS and clips to Glendale boundary:

```bash
python scripts/clip_and_reproject.py
```

**Output:**
- `data_processed/geojson/` - Clipped vector data
- `data_processed/raster/dem_clipped.tif` - Clipped DEM

### Step 3: Derive Terrain Products

Calculates slope and aspect from the DEM:

```bash
python scripts/derive_terrain.py
```

**Output:**
- `data_processed/raster/slope.tif` - Slope in degrees (0-90°)
- `data_processed/raster/aspect.tif` - Aspect in degrees (0-360°, -1 for flat)

### Step 4: Build Risk Model

Reclassifies layers into 1-5 risk categories and creates weighted overlay:

```bash
python scripts/build_risk_model.py
```

**Output:**
- `data_processed/raster/slope_risk.tif` - Reclassified slope (1-5)
- `data_processed/raster/aspect_risk.tif` - Reclassified aspect (1-5)
- `data_processed/raster/vegetation_risk.tif` - Reclassified vegetation (1-5)
- `data_processed/raster/fire_risk.tif` - Final fire risk score (1-5)

## Risk Model Details

### Risk Categories
- **1** - Very Low
- **2** - Low
- **3** - Moderate
- **4** - High
- **5** - Very High

### Slope Classification
- 0-5°: Very Low (1)
- 5-15°: Low (2)
- 15-25°: Moderate (3)
- 25-35°: High (4)
- >35°: Very High (5)

### Aspect Classification
- Flat: Low (2)
- North (315-45°): Low (2)
- East (45-135°): Moderate (3)
- South (135-225°): Very High (5) ⚠️ Highest risk
- West (225-315°): High (4)

*South-facing slopes receive more direct sunlight and dry out faster, increasing fire risk.*

### Vegetation Classification
Currently uses default moderate risk (3) for all areas. When vegetation data is added:
- Urban/Barren: Very Low (1)
- Grass: Moderate (3)
- Shrub: High (4)
- Forest/Heavy Fuel: Very High (5)

### Weighted Overlay Model

Final Risk = (0.45 × Slope) + (0.25 × Aspect) + (0.30 × Vegetation)

**Weights:**
- Slope: 45% - Most critical for fire spread rate
- Aspect: 25% - Solar exposure and prevailing wind
- Vegetation: 30% - Fuel availability and type

## Troubleshooting

### "DEM not found" error
Make sure you've downloaded DEM data and placed it in `data_raw/dem/`. Then run `clip_and_reproject.py`.

### GDAL import errors
Try installing with conda:
```bash
conda create -n glendale-fire python=3.11
conda activate glendale-fire
conda install -c conda-forge gdal rasterio geopandas
```

### Memory issues with large rasters
If processing large DEMs causes memory errors, consider:
- Using a smaller DEM resolution
- Processing in tiles
- Increasing available RAM

## Next Steps

After running these scripts:
1. Open `qgis_project/glendale_fire_risk.qgz` in QGIS
2. Load the generated risk layers
3. Style and visualize the data
4. Export for use in the Dash web application

## Script Details

### clip_and_reproject.py
- Loads Glendale boundary
- Clips all vector and raster data to boundary
- Reprojects to EPSG:2229 (NAD83 California Zone 5)
- Saves processed data

### derive_terrain.py
- Reads clipped DEM
- Calculates slope using Horn's method
- Calculates aspect (compass bearing)
- Saves slope and aspect rasters

### build_risk_model.py
- Reclassifies slope into 5 risk categories
- Reclassifies aspect into 5 risk categories
- Reclassifies vegetation into 5 risk categories
- Combines using weighted overlay
- Produces final fire risk map

## References

- CalFire Fire Hazard Severity Zones: https://osfm.fire.ca.gov/divisions/community-wildfire-preparedness-and-mitigation/wildland-hazards-building-codes/fire-hazard-severity-zones-maps/
- USGS National Map: https://apps.nationalmap.gov/downloader/
- Horn, B.K.P. (1981). "Hill shading and the reflectance map"
