# Weighted Redistribution of Passively Georeferenced Point Data

Python implementation of the weighted redistribution algorithm proposed by Huck, Whyatt and Coulton (2015) for disaggregating passively geocoded spatial data from administrative centroids to more spatially representative locations.

Completed as part of the GEOG3/70551 Understanding GIS module, MSc Geographical Information Science, University of Manchester.

---

## Overview

Passively georeferenced data — such as social media posts geocoded from place names — is typically generalised to the centroid of an administrative area. This creates false hotspots in heatmaps and obscures real spatial patterns, particularly when data spans multiple scales.

This project implements the algorithm from Huck et al. (2015), which redistributes points from centroids to more plausible locations within each polygon using a population density weighting surface. Rather than recovering the true location (which is unknowable), the algorithm produces a likelihood region around a weighted seed point, yielding a more realistic spatial distribution for downstream analysis.

---

## Dataset

- **1,023 tweets** relating to the Royal Wedding, geocoded to districts in Greater Manchester (level 3 administrative areas)
- **Weighting surface**: population density raster for Greater Manchester
- All vector data reprojected to British National Grid (EPSG:27700) for topological operations

---

## Algorithm Summary

For each administrative polygon:
1. Identify all data points (tweets) within the polygon
2. For each point, generate random candidate locations within the polygon's bounding box
3. Query the weighting surface (population density raster) at each candidate location
4. Select the candidate with the highest weight as the **seed location**
5. Calculate a likelihood region radius using:

   `r = s * sqrt(A / π)`

   where `A` is the polygon area and `s` is the user-defined spatial ambiguity parameter
6. Create a disk around the seed location using `skimage.draw.disk`; assign probability values across the disk using a distance-decay function from the seed centre

**Parameters used:**
- Weighting influence (`w`): 20
- Spatial ambiguity (`s`): 0.01

---

## Files

| File | Description |
|------|-------------|
| `weighted_disaggregation.py` | Full Python implementation of the Huck et al. (2015) algorithm |

---

## Dependencies

```python
import geopandas as gpd
import rasterio
import numpy as np
from numpy.random import uniform
from skimage.draw import disk
import matplotlib.pyplot as plt
```

---

## Data Sources

- Tweet dataset — provided as part of GEOG3/70551 coursework
- Population density raster — derived from ONS Census data for Greater Manchester
- Administrative boundaries — ONS Open Geography Portal


---

## Limitations

- Implementation operates at a single administrative level (level 3); multi-scale disaggregation across a hierarchy of levels is not implemented
- Random point generation produces a different distribution on each run, so outputs are not deterministic
- Redistributed points represent a more plausible spatial arrangement than centroid-generalised data but do not reflect actual locations
- Population density is used as the sole weighting surface; other surfaces (land use, road density) could be substituted depending on the nature of the data

---

## Reference

Huck, J., Whyatt, D. and Coulton, P. (2015). Visualizing patterns in spatially ambiguous point data. *Journal of Spatial Information Science*, 2015(10), pp.47–66.
