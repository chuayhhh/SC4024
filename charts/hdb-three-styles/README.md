# HDB prices in three visualization styles

Download and extract `../hdb-three-styles.zip`, then open `hdb-three-styles/index.html` in a modern browser. GitHub displays HTML source rather than executing it. Each family has three distinct English charts, with individual HTML and PNG files. SVGs are included for the eight SVG-rendered charts; the Chart.js chart is canvas-based.

The original 242,259-row CSV is included. The original complete searchable ledger is available in `../hdb/index.html` in the repository and in the original `hdb-lupi-charts.zip` bundle. See `methodology.md` for formulas, selection rules and limits of the depreciation interpretation.

Rebuild from the repository checkout: initialize the Lieflat submodule (`git submodule update --init --recursive`), install pandas, then run `python charts/hdb-three-styles/build.py`. The generator also uses existing `charts/hdb/chart-data.json` and the adapted rendering blocks in `charts/hdb/build_charts.py`.

To reproduce browser validation and image exports, install Playwright, provide Chromium at `/usr/bin/chromium`, serve `charts/` locally on port 8877, and run `python charts/hdb-three-styles/verify.py`. `validation.json` records the executed checks. The tests block HTTPS to check that all charts render without external libraries or fonts.

Third-party template-derived software is under `LIEFLAT-LICENSE.md` (PolyForm Noncommercial). Chart.js is MIT; ECharts is Apache-2.0. Their licenses are in `vendor/`. Font files are not bundled. Source transaction data licensing is not established by these software licenses.
