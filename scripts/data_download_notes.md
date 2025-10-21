# Data Download Instructions

This document provides detailed instructions for acquiring all necessary GIS data for the Glendale Fire Risk project.

## Required Datasets

### 1. Glendale City Boundary
**Status**: ✓ Already downloaded
- **Source**: LA County GIS Data Portal
- **Location**: `data_raw/Glendale_boundary.*`
- **Format**: Shapefile
- **Usage**: Clipping boundary for all other datasets

### 2. Building Footprints
**Status**: ✓ Already processed
- **Source**: LA County GIS Data Portal (https://egis-lacounty.hub.arcgis.com/)
- **Location**: `data_processed/LA_buildings_glendale.gpkg`
- **Format**: GeoPackage
- **Usage**: Building-level fire risk assessment

### 3. Digital Elevation Model (DEM)
**Status**: Needs download
- **Source**: USGS National Map (https://apps.nationalmap.gov/downloader/)
- **Resolution**: 10m
- **Format**: GeoTIFF (.tif)
- **Target Location**: `data_raw/dem/`
- **Steps**:
  1. Go to USGS National Map Downloader
  2. Search for "Glendale, California"
  3. Select "Elevation Products (3DEP)"
  4. Choose "1/3 arc-second DEM" (approximately 10m resolution)
  5. Download tiles covering Glendale area
  6. Save to `data_raw/dem/`

### 4. Vegetation / Fuel Data (FRAP)
**Status**: Needs download
- **Source**: CalFire Fire and Resource Assessment Program (https://frap.fire.ca.gov/mapping/gis-data/)
- **Dataset**: Fire Hazard Severity Zones or Vegetation/Fuel Rank
- **Format**: Shapefile or GeoTIFF
- **Target Location**: `data_raw/vegetation/`
- **Steps**:
  1. Visit CalFire FRAP GIS Data page
  2. Download "Vegetation" or "Fire Threat" dataset
  3. Extract and save to `data_raw/vegetation/`

### 5. Fire Hazard Severity Zones (FHSZ)
**Status**: Needs download
- **Source**: CalFire (https://osfm.fire.ca.gov/divisions/community-wildfire-preparedness-and-mitigation/wildland-hazards-building-codes/fire-hazard-severity-zones-maps/)
- **Format**: Shapefile
- **Target Location**: `data_raw/fhsz/`
- **Steps**:
  1. Visit CalFire FHSZ Maps page
  2. Download FHSZ data for Los Angeles County
  3. Save to `data_raw/fhsz/`

## Data Organization

After downloading, organize files as follows:

```
data_raw/
├── boundary/
│   └── Glendale_boundary.shp (and associated files)
├── buildings/
│   └── LA_County_Buildings.shp (raw, before clipping)
├── dem/
│   └── glendale_dem_10m.tif
├── vegetation/
│   └── frap_vegetation.shp
└── fhsz/
    └── LA_fhsz.shp
```

## Coordinate Reference System (CRS)

All datasets should be reprojected to a common CRS:
- **Target CRS**: EPSG:2229 (NAD83 / California zone 5, US Survey Feet)
- **Alternative**: EPSG:26911 (NAD83 / UTM zone 11N, meters)

## Next Steps

After downloading all data:
1. Run `clip_and_reproject.py` to clip and reproject data to Glendale boundary
2. Run `derive_terrain.py` to calculate slope and aspect from DEM
3. Run `build_risk_model.py` to create the risk classification layers
