# Data Sources and Licences

This project uses public New Zealand datasets from several organisations.  
Each dataset keeps its **original provider licence**.

| Dataset | Provider | Licence |
|---|---|---|
| Crash Analysis System (CAS) public data | NZ Transport Agency Waka Kotahi | CC BY 4.0 |
| AMDS Network Model | NZ Transport Agency Waka Kotahi | CC BY 4.0 |
| National Road Centreline / RCA data | NZ Transport Agency Waka Kotahi | CC BY 4.0 |
| State Highway Carriageway / RAMM | NZ Transport Agency Waka Kotahi | Check the current NZTA source terms |
| NZDep2023 | University of Otago | CC BY 4.0 |
| 2023 Meshblock geography | Stats NZ | CC BY 4.0 |
| GCH2023 | Centre for Rural Health, University of Otago | CC BY-ND 4.0 |
| LCDB v6.0 | Manaaki Whenua – Landcare Research | CC BY |
| New Zealand LiDAR 1 m DEM | Toitū Te Whenua LINZ | CC BY 4.0 |

## Source Links

- **CAS:** https://www.nzta.govt.nz/partners/data-and-tools/crash-analysis-system/
- **AMDS Network Model:** https://www.arcgis.com/home/item.html?id=dfa1e050f3cd42828f87d67fcff5a4fb
- **National Road Centreline / RCA:** http://catalogue.data.govt.nz/dataset/national-road-centreline-road-controlling-authority-data3
- **State Highway Carriageway:** https://services.arcgis.com/CXBb7LAjgIIdcsPt/arcgis/rest/services/GEO_MASTER_GIS_Carriageway/FeatureServer
- **NZDep2023:** https://www.otago.ac.nz/wellington/research/groups/research-groups-in-the-department-of-public-health/hirp/socioeconomic-deprivation-indexes
- **Stats NZ geographic data:** https://datafinder.stats.govt.nz/
- **GCH2023:** https://www.otago.ac.nz/centre-for-rural-health/research/geographic-classification-for-health
- **LCDB v6.0:** https://lris.scinfo.org.nz/
- **LINZ 1 m DEM:** https://data.linz.govt.nz/layer/121859-new-zealand-lidar-1m-dem/

## GCH2023

GCH2023 is licensed under **CC BY-ND 4.0**. The original GCH source file is kept for the experiment, but the derived `CAS_GCH23_enriched.csv` file is **not included in the public repository**.

This keeps the repository simple and avoids redistributing a modified GCH dataset.

## Attribution

A short acknowledgement for this project is:

> Road-crash and road-network data were sourced from NZ Transport Agency Waka Kotahi. NZDep2023 and GCH2023 were sourced from the University of Otago. Meshblock geography was sourced from Stats NZ. LCDB land-cover data were sourced from Manaaki Whenua – Landcare Research, and elevation data were sourced from Toitū Te Whenua Land Information New Zealand.

## Git LFS

These large files are stored with Git LFS:

- `data/amds_network/AMDS_vehicle_network_2193.gpkg`
- `data/lcdb/LCDB_v6.gpkg`
- `data/nzdep2023/Meshblock_2023_2193.gpkg`

Before cloning the full repository, install Git LFS:

```bash
git lfs install
```

Source terms can change, so check the provider page before redistributing third-party data.
