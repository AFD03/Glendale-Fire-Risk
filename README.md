# Glendale Fire Risk Interactive Visualization

## Overview
This project visualizes wildfire risk in Glendale, California using GIS data, a weighted risk model, and an interactive Plotly Dash web dashboard. It aims to help city planners, emergency services, and residents understand spatial patterns of fire vulnerability at the building level.

## Team – STA160 (Team 3)
| Name | Major | Role |
|------|-------|------|
| Ruhi Aggarwal | Data Science | Risk Model, Integration |
| **Alexander Davis*** | Statistics | Team Lead, GIS Dev, 3D Scene, Website Build |
| Alyssa Chau | Statistics/Mgmt Econ | Risk Model, Integration |
| YiChun Chen | Data Science | 2D plotly charts |
| Odin Nielsen | Statistics | 2D plotly sharts |
| Zhichu Zheng | Statistics | GIS Data & Terrain Analysis |

\*Team Leader

---

## Deliverables
- Interactive **2D dashboard** showing building-level fire risk  
- Embedded **3D QGIS scene** (terrain, extruded buildings, risk overlay)  
- Full data pipeline documentation & final report  
- Supplemental 2D charts for contextualizing fire risk in Glendale, CA

---

## Repository Structure

```
Glendale-Fire-Risk/
│
├── README.md
├── .gitignore
├── LICENSE
├── index.html            # base page for website
├── analysis.html         # analysis page for website
├── interactive.html      # 3D map page for website
├── dashboard.html        # 2D map page for website
│
├── data_raw/                 # Unmodified source datasets
│   ├── buildings/
│   ├── dem/
│   ├── vegetation/
│   ├── fhsz/
│   └── boundary/
│
├── data_processed/           # Clipped, cleaned, reprojected, and merged datasets
│   ├── geojson/
│   └── raster/
│
├── qgis_project/             # .qgz project file + related styles, exports
│   └── exports_3d/           # qgis2threejs outputs here
│
├── visualization/                 # 2D visuals
│   ├── interactive.html          
│   └── data/                 # Processed GeoJSON for loading into Dash
│
├── docs/                     # Final report, proposal, project documentation
    ├── project_plan.pdf
    ├── final_report/
    └── presentation/
```

---

## Data Sources
| Dataset | Source |
|---------|--------|
| Building Footprints | LA County GIS Data Portal |
| Digital Elevation Model (DEM, 10m) | USGS National Map |
| Vegetation / Fuel (FRAP) | CalFire Fire and Resource Assessment Program |
| Fire Hazard Severity Zones | CalFire |
| Glendale City Boundary | LA County GIS Portal |

All data is public, government-sourced, and contains no personal or identifying information.

---

## Technology Stack
| Category | Tool |
|----------|------|
| GIS Processing | QGIS (Slope, Aspect, Reclassification) |
| 3D Visualization | QGIS + qgis2threejs Plugin |
| Web App | Python, Leaflet |
| Version Control | Git / GitHub |
| Languages | Python, HTML/CSS |
| Reproducibility | Saved QGIS project file + documented workflow |

---

## Fire Risk Modeling
A weighted overlay model using:
- **Slope** (derived from DEM)  
- **Vegetation / Fuel Type**  
- **Aspect (sun/wind influence)** 

Final risk score formula:
Risk = w₁ * Slope + w₂ * Vegetation + w₃ * Aspect

Weights determined from CalFire research + sensitivity analysis.

---

## Timeline
| Week | Task |
|------|------|
| Week 4 | Download & preprocess GIS data |
| Week 5 | GIS analysis (slope, aspect, vegetation classification) |
| Week 6 | Build and validate risk model |
| Week 7 | Finalize GeoJSON + begin 2D visuals |
| Week 8 | Complete 2D dashboard + 3D scene |
| Week 9 | Integration + report writing |
| Week 10 | Final testing & presentation |

---

## License
This project uses only public data and is licensed under the MIT License.

## Contact
If you have questions or feedback:

Email: alfdavis.ucdavis.edu (Project Lead)

GitHub Issues: Open a ticket in this repository

---
