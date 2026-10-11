# HDB lease and resale charts

Open `index.html` in a modern browser for five English charts and the complete searchable ledger. GitHub displays HTML source; download the ZIP and extract it to view the charts locally.

- `transactions.csv`: unchanged user-supplied CSV, 242,259 records.
- `01-*.html` through `05-*.html`: individual interactive charts.
- `.png`: article-ready chart exports with explanatory notes.
- `.svg`: vector chart geometry; notes remain in HTML and PNG exports.
- `chart-data.json`: computed summary statistics.
- `methodology.md`: definitions, limitations and template audit.
- `build_charts.py`: regenerates HTML and summary data; PNG/SVG exports were produced with Chromium.

## Rebuild

Clone this repository with `git clone --recurse-submodules https://github.com/wengshi10/practice.git`, or run `git submodule update --init --recursive` in an existing checkout. The Lieflat Charts skill is pinned at `.codex/skills/lieflat-charts`.

Install pandas and numpy in your Python environment, then run `python charts/hdb/build_charts.py` from the repository root. Browser files embed the monochrome tokens; only the optional Inter font needs Internet access.

## Template license

Template-derived rendering and tokens come from [Lieflat Charts](https://github.com/larashero3-dotcom/lieflat-charts), under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0). A copy is included as `LIEFLAT-LICENSE.md`. This notice covers template-derived software; it does not establish ownership or licensing of the supplied transaction data.
