# 🏢 SC4024 Data Visualization & Visual Analytics Project
## **Singapore HDB Resale Market Visual Analytics Dashboard (2017 – Present)**

> **Course:** NTU SC4024 Data Visualization & Visual Analytics  
> **Topic:** Multi-Attribute Trade-off & Spatial Dynamics of Singapore HDB Resale Flats  
> **Tech Stack:** Python 3.11, Streamlit, Plotly Express/Graph Objects, Pandas, Statsmodels, Geopy, OpenStreetMap/OneMap API

---

## 📌 Executive Overview & Core Problem Statement

Singapore’s public housing market, managed by the Housing & Development Board (HDB), presents a complex high-dimensional decision matrix for buyers, urban planners, and policy analysts. Public flat valuations are governed by competing structural and spatial forces:

1. **Spatial Convenience vs. Distance Decay:** Proximity to Mass Rapid Transit (MRT) stations and the Central Business District (CBD) commands a steep valuation premium.
2. **Leasehold Depreciation (99-Year Lease Decay):** As public flats age, Bala’s Curve dictates non-linear lease decay, which competes against capital appreciation.
3. **Macroeconomic Monetary Pressures:** Rising benchmark mortgage rates (such as the 3-Month SORA) alter housing demand and affordability.

This interactive Visual Analytics application equips stakeholders with high-dimensional brushing, spatial exploration tools, and real-time trade-off modeling to analyze how these factors interact across Singapore's 26 HDB towns.

---

## 🛠️ Repository Architecture

```text
SC4024/
├── app.py                          # Main Streamlit Application Orchestrator
├── README.md                       # Comprehensive Project & Dashboard Guide
├── sc4024_project_report.pdf       # System Architecture & Analytical Report
├── data/                           # Data Storage Layer
│   ├── resale_flat_prices.csv      # Primary Raw Ingestion Dataset (HDB Resale Transactions)
│   ├── hdb_coordinates.csv         # Geocoded Lat/Lon Registry (OneMap/Nominatim)
│   └── hdb_spatial_features.csv    # Computed Spatial Features (MRT/CBD Haversine Distances)
└── src/                            # Modular Analytics & Engine Codebase
    ├── __init__.py                 # Module Initializer
    ├── data_loader.py              # Data Pipeline (Ingestion, Cleaning, Spatial Left-Joins)
    ├── geocode_hdb.py              # Parallel Multi-Threaded OneMap/Nominatim Geocoding Engine
    ├── repair_coordinates.py       # Automated Address Repair & Retry Engine
    ├── mrt_distance.py             # Vectorized Spatial Haversine Distance Engine (MRT/LRT)
    ├── school_cbd_distance.py      # Spatial Proximity Engine (CBD & Key Regional Hubs)
    └── visual_components.py        # Standardized Dark-Theme Plotly Visual Components
└── archive_notebooks/              # Old Project Reference
    └── old_project.ipynb           # Old project .ipynb file
```

## ⚡ Quickstart & Local Installation Guide

Follow these steps to set up a clean, isolated environment and launch the local dashboard server.

### 1. Repository Setup & Virtual Environment

Open your terminal in the project directory:

```bash
# Clone or navigate to project directory
cd SC4024

# Create an isolated Python 3.11 virtual environment
python3 -m venv venv

# Activate the virtual environment
# macOS / Linux:
source venv/bin/activate
# Windows (Command Prompt):
venv\Scripts\activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

Install the pinned requirements to prevent binary C-extension conflicts between NumPy 2.x and Pandas/Statsmodels:

```bash
pip install --upgrade pip
pip install streamlit plotly pandas "numpy<2.0.0" statsmodels requests geopy
```

### 3. Launch the Application

```bash
streamlit run app.py

The application will launch automatically in your browser at `http://localhost:8501`.
```

---


## 📖 Dashboard User Guide & Interpretive Framework

The dashboard is structured into **5 Analytical Tabs**, accompanied by a **Sidebar Multi-Select Filter Panel** and a **Live Flat Holding Cost Simulator**.

---

### 🎛️ Sidebar Utilities & Live Simulator

* **Multi-Attribute Filters:** Filter the global dataset by Town, Flat Type, Remaining Lease Range, and Transaction Date Range.
* **Filter-Sensitive Statistics:** All 5 analytical tabs dynamically calculate statistics based strictly on your active sidebar filter selection.
* **Valuation & Holding Cost Simulator:**
  * **Inputs:** Select **Flat Type**, **Purchase Town**, **Holding Horizon (Years)**, and **Target Floor Area**.
  * **Outputs:** Computes projected annualized lease decay using Bala's Curve dynamics and estimates projected total holding depreciation.

---

### 🗺️ Tab 1: Geospatial Scatter Map

* **Objective:** Map spatial valuation trends across the island.
* **Visual Encoding:**
  * **Latitude / Longitude:** Flat physical location.
  * **Color Scale (Viridis):** Price per Square Meter (SGD $/sqm). Dark purple indicates affordable suburban flats (\~$3,000/sqm); bright yellow highlights high-value central flats (\~$10,000+/sqm).

  * **Bubble Size:** Floor area in square meters.
* **How to Read & Interact:**
  * Zoom and pan across specific neighborhoods (e.g., Central Area vs. Woodlands).
  * Hover over points to view exact address, flat type, remaining lease, and nearest MRT station.
  * Use the dynamic insight block below the map to observe the price-per-sqm gap between the highest and lowest valued towns in your current selection.

---

### 🚆 Tab 2: MRT & Location Impact (Proximity vs. Valuation)

* **Objective:** Quantify the price premium paid for proximity to MRT/LRT networks.
* **Visual Encoding:**
  * **X-Axis:** Distance to Nearest MRT Station (km).
  * **Y-Axis:** Price per Square Meter (SGD $/sqm).
  * **Color Scale:** Remaining Lease (Years).
  * **Red OLS Line:** Ordinary Least Squares trendline capturing valuation decay rate over distance.
  * **Yellow Dashed Line:** 500m Walkable Zone Reference Line.
* **How to Read & Interact:**
  * Compare points to the left of the 500m line versus points to the right.
  * Observe the slope of the red OLS line to measure distance decay.
  * The dynamic insight block calculates the exact **% price premium per sqm** for flats within 500m of an MRT relative to flats >1km away within your active filter selection.

---

### 🔀 Tab 3: Multi-Attribute Parallel Coordinates (High-Dimensional Brushing)

* **Objective:** Enable high-dimensional trade-off exploration across 5 continuous variables simultaneously.
* **Visual Encoding:**
  * **Vertical Axes:** Remaining Lease (Yrs), Floor Area (Sqm), MRT Distance (km), CBD Distance (km), Resale Price ($).
  * **Line Color (Tealrose Scale):** Encoded by Resale Price ($).
* **How to Read & Interact (Interactive Brushing):**
  * **Click and Drag Vertically** along any axis line to create a selection box (e.g., drag on *Resale Price* between $400k and $500k).
  * The chart isolates lines passing through that constraint, highlighting trade-offs (e.g., to stay under $500k near the CBD, buyers must accept smaller floor area or shorter remaining lease).
  * Drag selection boxes across multiple axes to perform multi-variable filtering.

---

### 📊 Tab 4: Town Depreciation Spread (Boxplot Analysis)

* **Objective:** Evaluate town-level depreciation risk and annual holding costs.
* **Visual Encoding:**
  * **X-Axis:** HDB Towns (Sorted in ascending order of median annual depreciation).
  * **Y-Axis:** Annual Depreciation Rate (SGD $/year).
  * **Box Elements:** Interquartile Range (IQR, 25th to 75th percentile) and median line per town.
  * **Red Dashed Line:** National Median Depreciation Rate Benchmark.
* **How to Read & Interact:**
  * Towns below the national benchmark line represent higher capital preservation efficiency.
  * Wide box distributions (e.g., Queenstown, Kallang/Whampoa) indicate wide price variance driven by premium sub-clusters (such as DBSS or Pinnacle@Duxton).

---

### 📈 Tab 5: Macro Benchmark (Resale Prices vs. 3-Month SORA Interest Rates)

* **Objective:** Compare public housing price trajectory against macroeconomic monetary conditions.
* **Visual Encoding:**
  * **Primary Y-Axis (Blue Line):** Median Resale Price per Sqm ($/sqm) over time.
  * **Secondary Y-Axis (Red Dashed Line):** Simulated 3-Month SORA (Singapore Overnight Rate Average) interest rate (%).
* **How to Read & Interact:**
  * Trace the price curve during low-interest periods (2020–2021) versus rate-hiking cycles (2022–2023).
  * Use the dynamic insight block to evaluate total percentage price growth over your selected transaction timeframe.

---

## ⚙️ Data Ingestion & Spatial Feature Engineering Pipeline

The spatial feature pipeline generates geocodes and distance measurements using vectorization:

```text
                                +---------------------------+
                                | resale_flat_prices.csv    |
                                +-------------+-------------+
                                              |
                                              v
                                +---------------------------+
                                |    src/data_loader.py     |
                                +-------------+-------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
        +--------------------------+                      +--------------------------+
        |   src/geocode_hdb.py     |                      |   src/mrt_distance.py    |
        | Parallel OneMap API      |                      | Vectorized Haversine     |
        | & Nominatim Fallback     |                      | Distance to 160+ MRTs    |
        +------------+-------------+                      +------------+-------------+
                     |                                                 |
                     +------------------------+------------------------+
                                              |
                                              v
                                +---------------------------+
                                | hdb_spatial_features.csv  |
                                +-------------+-------------+
                                              |
                                              v
                                +---------------------------+
                                |  Streamlit Analytics App  |
                                +---------------------------+
```

1. **Parallel Geocoding Engine (`src/geocode_hdb.py`):** Uses Python's `ThreadPoolExecutor` to query OneMap's REST API across unique physical block addresses, with Nominatim API as a fallback.
2. **Automated Coordinates Repair (`src/repair_coordinates.py`):** Retries missing address records to ensure complete coverage.
3. **Vectorized Haversine Engine (`src/mrt_distance.py`):** Computes minimum distance from every flat block to 160+ operational MRT/LRT station coordinates in Singapore.

---

### ⚠️ Troubleshooting Common Setup Issues

* **`ValueError: numpy.dtype size changed...`**  
  This indicates a C-extension binary conflict between NumPy 2.x and Pandas/Statsmodels.  
  **Fix:** Ensure your virtual environment is active (`source venv/bin/activate`), then run:
```bash
  pip install "numpy<2.0.0" --force-reinstall
```

---

## 🎓 Academic Rubric Alignment (NTU SC4024)

| Grading Criteria | Applied Implementation |
| :--- | :--- |
| **Visual Appropriateness & Design Variety** | Integrates Scatter Maps, OLS Regression Scatters, Parallel Coordinates, Sorted Boxplots, and Dual-Axis Line Subplots formatted in dark theme (`plotly_dark`). |
| **High-Dimensional Brushing** | Implements interactive multi-axis brushing on Tab 3 (Parallel Coordinates), allowing cross-variable trade-off isolation. |
| **Spatial Feature Enrichment** | Enriches flat transactions with OneMap lat/lon geocodes, Haversine MRT proximity, and CBD distance calculations. |
| **Filter-Sensitive Storytelling** | Contextual `st.info()` blocks recalculate localized metrics dynamically based on user sidebar filters. |
| **Code Modularity & Cleanliness** | Enforces separation of concerns (`app.py` for UI layout, `src/data_loader.py` for data transformation, `src/visual_components.py` for chart rendering). |

---

## 📄 License & Course Attribution

Developed for **SC4024 Data Visualization & Visual Analytics** at **Nanyang Technological University (NTU), Singapore**. Dataset sourced from [Data.gov.sg](https://data.gov.sg/) (HDB Resale Flat Prices).
