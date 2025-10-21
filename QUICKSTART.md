# Quick Start Guide - GIS Data Processing

This guide will help you quickly get started with processing GIS data for the Glendale Fire Risk project.

## Prerequisites

1. **Python 3.8+** installed
2. **GDAL/OGR** libraries (see installation instructions below)
3. **Git** (to clone the repository)

## Quick Installation

### Option 1: Using Conda (Recommended)

```bash
# Create a new conda environment
conda create -n glendale-fire python=3.11 -y
conda activate glendale-fire

# Install GIS dependencies
conda install -c conda-forge gdal rasterio geopandas fiona shapely numpy scipy -y

# Install additional dependencies
pip install plotly dash pandas tqdm
```

### Option 2: Using pip (Advanced)

```bash
# Install GDAL first (system-dependent)
# Ubuntu/Debian:
sudo apt-get install gdal-bin libgdal-dev python3-gdal

# macOS:
brew install gdal

# Then install Python packages
pip install -r requirements.txt
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/AFD03/Glendale-Fire-Risk.git
cd Glendale-Fire-Risk
```

### 2. Download Required Data

The repository already includes:
- ✅ Glendale city boundary
- ✅ Processed building footprints

**You need to download:**
- 🔲 Digital Elevation Model (DEM) - Required for slope/aspect analysis

See `scripts/data_download_notes.md` for detailed download instructions.

Place downloaded DEM files in: `data_raw/dem/`

### 3. Run the Processing Workflow

```bash
cd scripts

# Run all steps automatically
python run_workflow.py
```

Or run steps individually:

```bash
# Step 1: Clip and reproject all data
python clip_and_reproject.py

# Step 2: Calculate slope and aspect from DEM
python derive_terrain.py

# Step 3: Build fire risk model
python build_risk_model.py
```

## Output Files

After running the workflow, you'll have:

```
data_processed/
├── geojson/
│   ├── buildings_clipped.geojson
│   ├── vegetation_clipped.geojson (if vegetation data provided)
│   └── fhsz_clipped.geojson (if FHSZ data provided)
└── raster/
    ├── dem_clipped.tif
    ├── slope.tif
    ├── aspect.tif
    ├── slope_risk.tif
    ├── aspect_risk.tif
    ├── vegetation_risk.tif
    └── fire_risk.tif ← Final output!
```

## Next Steps

1. **Visualize in QGIS:**
   - Open `qgis_project/glendale_fire_risk.qgz`
   - Add layers from `data_processed/raster/`
   - Style the fire risk map

2. **Build Web Dashboard:**
   - Process data for Dash app
   - Develop interactive visualizations
   - Deploy web application

## Troubleshooting

### "ModuleNotFoundError: No module named 'osgeo'"

GDAL is not installed correctly. Try:
```bash
conda install -c conda-forge gdal
```

### "DEM not found" error

You need to download DEM data:
1. Go to https://apps.nationalmap.gov/downloader/
2. Search for "Glendale, California"
3. Download 10m DEM
4. Place in `data_raw/dem/`

### Memory errors with large files

- Use smaller DEM resolution
- Close other applications
- Consider processing in tiles

### Script hangs or runs slowly

This is normal for large raster processing. DEM processing can take several minutes depending on file size.

## Get Help

- Check `scripts/README.md` for detailed documentation
- Review `scripts/data_download_notes.md` for data sources
- Open an issue on GitHub if you encounter problems

## Minimum Working Example

If you just want to test the scripts without full data:

```bash
# 1. Validate scripts
python test_scripts.py

# 2. Try to run with available data (will show warnings for missing data)
python clip_and_reproject.py
```

The scripts are designed to work with whatever data is available and will provide helpful warnings about missing datasets.
