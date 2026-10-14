# 🏢 SC4024 Data Visualization Project

## What Makes an HDB Flat Expensive?

**Exploring Property Characteristics, Location, Accessibility and Neighbourhood Amenities in Singapore**

- **NTU SC4024 Data Visualization & Visual Analytics** 
- **Output:** Self-created HDB Singapore Webpage
- **Coverage:** January 2017–October 2026 in the provided dataset; 2026 data is incomplete.
- **Tools/ Methods Implemented:** HTML, CSS, vanilla JavaScript, SVG and Canvas; Python 3 standard-library preparation scripts; OneMap Search for approved address geocoding.

## Executive Overview & Core Problem Statement

Singapore HDB resale prices vary across property characteristics, location and neighbourhood accessibility. This interactive storytelling webpage explores how remaining lease, floor area, building age, storey, flat type, town and nearby amenities are associated with those differences.

Six connected graphs guide viewers from market-wide trends to property-level trade-offs and neighbourhood comparisons. Coordinated filters, animated charts, map exploration.

The analysis uses the six supplied datasets, while OneMap enriches uploaded addresses with coordinates only. 

Associations are descriptive as the webpage does not estimate causal amenity premiums, predict future prices or model depreciation, mortgage costs or interest rates.

## Repository Architecture

```text
practice/
├── README.md
├── PRESENTATION_GUIDE.md          # Six-minute presentation walkthrough and notes
├── REFINEMENT_NOTES.md
├── .gitignore
├── dist/
│   ├── index.html                # Webpage structure
│   ├── style.css                 # Responsive layout, themes and animations
│   ├── app.js                    # Visualizations, interactions and statistics
│   ├── metadata.json             # Locally generated; excluded from Git
│   ├── transactions.json         # Locally generated; excluded from Git
│   └── accessibility.json        # Locally generated; excluded from Git
├── scripts/
│   ├── prepare_data.py           # Prepare the six uploaded datasets
│   ├── geocode_onemap.py         # Resolve and cache block/school coordinates
│   └── build_accessibility.py    # Compute nearest-amenity distances
├── tests/                        # Optional browser verification scripts
├── datasets/                     # Local source CSV/GeoJSON files; excluded from Git
└── work/                         # Local preparation outputs and coordinate cache
    └── onemap-cache.json         # Preserve this to avoid repeating geocoding
```

The public branch contains code and documentation. Source datasets, generated JSON and geocoding caches are excluded from Git. Run commands from the repository root.

## Quickstart & Local Setup Guide

### 1. Obtain the source code

Open PowerShell in the parent folder where you want the project, then run:

```powershell
git clone --branch BRANCH NAME --single-branch REPOSITORY GIT ADDRESS
cd practice
py --version
```

If you already have the repository, open PowerShell inside your existing folder instead:

```powershell
git switch BRANCHNAME
git pull --ff-only
```

### 2. Add the six source datasets locally

Create a `datasets` folder if needed:

```powershell
New-Item -ItemType Directory -Path datasets -Force
```

Place these dataset files inside the folder:

| File | Purpose |
| --- | --- |
| `resale_flat_prices_based_on_registration_date_from_jan_2017_onwards.csv` | Resale transactions and flat characteristics |
| `HDBPropertyInformation.csv` | Building completion years and property information |
| `Generalinformationofschools.csv` | School addresses and classifications |
| `LTAMRTStationExitGEOJSON.geojson` | MRT exit locations |
| `HawkerCentresGEOJSON.geojson` | Hawker locations and status |
| `MasterPlan2025PlanningAreaBoundaryNoSea.geojson` | Planning-area boundaries |

### 3. Prepare the webpage data

For a fresh setup, run these commands in order:

```powershell
py scripts\prepare_data.py .\datasets
py scripts\geocode_onemap.py --workers 4
py scripts\build_accessibility.py
```

The preparation scripts use Python's standard library; no Streamlit, Plotly, Pandas or npm installation is required. Geocoding needs internet access and can take considerable time because it queries thousands of addresses. 

**IT CAN TAKES UP TO 1.5+ HOUR TO DOWNLOAD FOR GEOCODING!!** So please allocate your time while setting up. :)

It saves progress in `work/onemap-cache.json`; rerunning resumes from saved results. Ambiguous matches are excluded rather than guessed.

If OneMap requires authentication, the script accepts an optional `ONEMAP_TOKEN` environment variable. Keep tokens out of source control.

If all three generated JSON files already exist in `dist`, skip preparation and start the server. Re-running `prepare_data.py` removes the previous accessibility output, so run `build_accessibility.py` afterward to regenerate it using the existing cache.

### 4. Open the webpage

```powershell
py -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open **http://localhost:8000/** in your browser. Keep PowerShell open while viewing; press **Ctrl+C** to stop the server. Use **Ctrl+F5** after an update.

Serve the webpage over HTTP because it fetches local JSON files. Opening `index.html` directly is insufficient. On macOS/Linux, use `python3` in place of `py`.

## Dashboard User Guide & Interpretive Framework

### Shared Controls and Summary Metrics

Select multiple periods, towns and flat types to update coordinated charts and CSV export. The scatterplot also supports horizontal drag selection of a property range. Hover for details, switch between light and dark themes, and use presentation mode for a guided walkthrough.

| Metric | Calculation |
| --- | --- |
| Median resale price | Median transaction resale price among filtered sales |
| Median price / m² | Median of each filtered sale's resale price divided by floor area |
| Median remaining lease | Median recorded lease months divided by 12 |

These summaries use all filtered transactions. Median price/m² is calculated from transaction-level ratios, rather than dividing median price by median area.

### Chapter 1: The Market

Monthly trend lines compare resale price or price/m² across flat categories. Annual bars show percentage change in annual median price relative to 2017; they are not year-on-year growth rates. A dashed 2026 border signals incomplete coverage. Playback progressively reveals the existing trend without changing the selected sales cohort.

### Chapter 2: Location

A planning-area map and linked town ranking compare town-level median prices. A sequential blue palette distinguishes lower and higher values. Unselected towns are grey, while the ranking retains context across towns. Map symbols represent named town aggregates, not individual flat locations.

### Chapter 3: Property Characteristics

The transaction scatterplot explores remaining lease, floor area or building age against price. Drag horizontally to select a range and update linked views. The fitted line and R² use all eligible filtered sales; up to 2,400 transaction dots are displayed for performance. The fitted relationship is descriptive.

### Chapter 4: Storey and Price Distributions

Tukey boxplots compare prices across storey bands, with a building-age selector. Boxes show Q1–Q3 and the median; whiskers end at observed values within 1.5×IQR fences. Points beyond the whiskers are outliers. Distribution overlap helps assess how much variation remains within each group.

### Chapter 5: Town, Flat Type and Model

A town-by-flat-type heatmap compares median values across combinations and highlights the active selection. Two panels keep all 26 towns visible. The flat-model chart ranks median total resale price in SGD for the ten leading eligible models, requiring at least five sales per model.

### Chapter 6: The Neighbourhood

Explore MRT exits, hawker centres and geocoded primary schools on the amenity map. Switch among three related views:

- **Amenity map:** Explore uploaded amenity locations and neighbourhood context.
- **Distance distributions:** Compare price/m² across common nearest-amenity distance bands, switching between MRT exits, primary schools and hawker centres while preserving the same complete-coordinate sales cohort.
- **Ageing and accessibility:** Compare lease groups and distance bands using aggregated price/m² bubbles and a linked block map. Points have equal size by default; optional sizing encodes transaction counts by area.

Accessibility comparisons have their own year and building-age selectors while sharing town, flat type and property-range selections. Distances measure straight-line proximity, not walking routes. Later amenity snapshots cannot reconstruct historical availability, and price differences do not establish causation.

## Data Ingestion & Spatial Feature Engineering Pipeline

```text
Six supplied CSV/GeoJSON datasets
                  |
          prepare_data.py
                  |
      metadata.json + transactions.json
                  |
     geocode_onemap.py + OneMap Search
                  |
       work/onemap-cache.json
                  |
       build_accessibility.py
                  |
          accessibility.json
                  |
    Local HTML/CSS/JavaScript webpage
```

`prepare_data.py` normalizes records, joins building information and records SHA-256 source fingerprints. `geocode_onemap.py` validates address matches and caches coordinates. `build_accessibility.py` computes nearest-amenity distances in Singapore's SVY21 projection and records coordinate coverage. The webpage requires no runtime internet connection once its local data is prepared.

## Data Integrity & Analytical Limitations

- 242,259 transactions, January 2017 to October 2026. 2026 is partial.
- 242,256 records join to building information on normalized block + street. Three unmatched block 82 MacPherson Lane sales remain in price analysis.
- Transaction-level price/m² is calculated before taking medians.
- All summaries use every filtered row. Only scatter dots are sampled, deterministically, to at most 2,400. The displayed denominator and methodology disclose this.
- Building age uses completion year and sale year. Storey groups use the midpoint of the recorded storey range with nonoverlapping thresholds.
- Sparse time-series months are not interpolated across missing observations. Timeline playback animates a reveal clip over a stable full-history path and scale, preserving prior history instead of redrawing it. The monthly axis uses rounded ticks; extrema are annotated. Growth bars show cumulative annual-median change versus 2017, and 2026 has a dashed outline.
- 55 planning polygons retain holes and multipolygons. Price symbols anchor HDB town names to matching planning areas; they do **not** spatially assign sales. Central Area and Kallang/Whampoa remain in the ranking without map symbols.
- 613 MRT exit records and 129 hawker records are assigned to areas by point-in-polygon. Exit counts are not unique station counts; hawkers retain all uploaded statuses.
- 179 primary schools retain their recorded DGP area classification for inventories; verified geocoded addresses provide individual map markers. The school file contains 337 schools overall.
- HDB and school coordinates are absent in the raw uploads. With explicit user approval, OneMap Search resolves their addresses to WGS84 and SVY21 coordinates. Exact block/road matches and school postal-code matches are checked; materially ambiguous addresses are not guessed. All geocoded datasets and caches stay local.
- Nearest-amenity distances are Euclidean in EPSG:3414, not walking routes. The distance selector preserves one common complete-coordinate cohort across MRT exits, primary schools and existing/interim hawkers. Under-construction hawkers are excluded from distance calculations.
- The comparison uses a separate 2017–2026 or all-years selector and building-age selector, while sharing town, flat type and property-range filters with the historical charts. 2026 is partial.
- Tukey boxplots use Q1, median, Q3, and whiskers ending at observed values within 1.5×IQR fences. All outlier counts are exact; at most 160 outlier marks per group are drawn for clarity.
- Lease/accessibility bubbles aggregate 5-year lease groups × distance bands, require at least five sales, use median lease and price/m², and use equal-size points by default, with optional transaction-count sizing by point area.
- The within-comparable-group contrast matches sale year, town, flat type, 10-year building-age bands and 20m² floor-area bands. Strata require at least five near (<400m) and five far (≥1200m) sales. The displayed contrast is exp(weighted average of log near/far median-price ratios) − 1, weighted by the smaller count in each stratum. This is descriptive, not causal.
- Amenities are later snapshots and do not reconstruct historical accessibility.
- No causal effects, inflation adjustment, repeat-sales indices, or predictions are claimed.


## Troubleshooting Common Setup Issues

| Issue | Action |
| --- | --- |
| `py` is not recognized | Install Python 3 and reopen PowerShell, or use `python` if available. |
| Missing transaction data | Confirm source files are in `datasets`, then run `prepare_data.py`. |
| Accessibility views are unavailable | Check `work/onemap-cache.json`, then run `build_accessibility.py` after base preparation. Geocoding is required if no coordinate cache exists. |
| Geocoding stops or the computer sleeps | Rerun the same geocoding command; saved matches are reused. Keep the computer awake during the run. |
| Unmatched or ambiguous addresses remain | Optionally run `py scripts\geocode_onemap.py --workers 4 --retry-unmatched` once, then rebuild accessibility. Repeated retries do not guarantee a valid match. |
| Port 8000 is already in use | Start the server on port 8001 and open `http://localhost:8001/`. |
| Browser shows an older version | Press Ctrl+F5 after updating. |
| Old `hdb-atlas` folder remains | Follow `MIGRATION.md`, verify the webpage works, and remove the folder only after checking that it is empty. |

## Verification

JavaScript syntax can be checked with:

```powershell
node --check dist/app.js
```

Node is optional for verification and is not required to serve the webpage. Optional browser checks in `tests` use Playwright and may need browser/output paths adjusted for your machine.

Existing verification covers median baselines, combined filters, brushing, themes, the methodology dialog, presentation navigation, mobile layout, annual growth, playback stability, Tukey boxplots, school markers and shared amenity cohorts. Nearest distances were independently checked against a KD-tree calculation. Verification results apply to the prepared dataset used for those checks; coordinate coverage on another machine may differ.

## Academic Project Alignment

| Project Area | Implementation |
| --- | --- |
| Visual variety | Animated trends, growth bars, maps, rankings, scatterplots, boxplots, heatmaps and aggregated bubbles |
| Coordinated interaction | Multiple-selection filters, property-range brushing, linked highlighting and amenity selectors |
| Spatial analysis | Validated OneMap coordinates, planning-area inventories and nearest-amenity distances |
| Data storytelling | Six chapters, hover details, timeline playback and presentation controls |
| Reproducibility | Standard-library preparation scripts, cached geocoding and source fingerprints |
| Analytical transparency | Methodology dialog, explicit cohort rules, incomplete-year styling and descriptive limitations |

See [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md) for the six-minute walkthrough. Students should record their own narration; the webpage does not generate a presentation video. This table describes implemented capabilities rather than guaranteeing a rubric score.

## Dataset References & Course Attribution

These links document the uploaded datasets' provenance; no replacement datasets are fetched by the webpage.

- [HDB resale transactions](https://data.gov.sg/datasets?query=resale+flat&resultId=d_8b84c4ee58e3cfc0ece0d773c8ca6abc)
- [HDB Property Information](https://data.gov.sg/datasets?query=hdb+property&resultId=d_17f5382f26140b1fdae0ba2ef6239d2f)
- [MRT station exits](https://data.gov.sg/datasets?query=lta+mrt&resultId=d_b39d3a0871985372d7e1637193335da5)
- [URA planning-area boundaries](https://data.gov.sg/datasets?query=URA+Planning+Area+Boundaries&resultId=d_2cc750190544007400b2cfd5d7f53209)
- [Hawker centres](https://data.gov.sg/datasets?agencies=National+Environment+Agency+(NEA)&resultId=d_4a086da0a5553be1d89383cd90d07ecd)
- [General information of schools](https://data.gov.sg/datasets?query=moe+general+information+of+school&resultId=d_688b934f82c1059ed0a6993d2a829089)
- [OneMap](https://www.onemap.gov.sg/) for address-coordinate lookup only


For SC4024 Data Visualization course at Nanyang Technological University, Singapore. 
Dataset redistribution is subject to the data.gov.sg terms. This README does not grant a separate software or dataset licence.
