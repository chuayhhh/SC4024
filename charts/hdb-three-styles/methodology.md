# Three HDB chart styles: definitions and template audit

This delivery uses the same unchanged user-supplied CSV as the original HDB charts: 242,259 transactions, 2017-01 to 2026-10. No original record is removed, deduplicated, invented, winsorised or corrected. The full CSV accompanies the charts; the original `../hdb/index.html` also provides the complete searchable ledger. This is chart mode, not a report-template layout. All text is English.

## Statistical definitions

- Remaining lease is stated years plus stated months divided by 12; no month component means zero months. Registration month is not necessarily contract month.
- Per-sale unit price = resale price / floor area in m². Displayed medians are medians of these ratios, not ratios of aggregate medians.
- The bands are [0,50), [50,60), [60,70), [70,80), [80,100). Observed leases range from 39 years 4 months to 97 years 9 months.
- 2025 is the latest complete calendar year supplied. The extraction date is unknown; 2026 through October is partial. All prices are nominal SGD, not inflation adjusted.
- The six-town comparison selects towns with at least 30 transactions in both <60-year and ≥80-year bands, then takes the six with the greatest total 2025 transaction count. Town selection is based on volume, not gap magnitude. The matrix includes all five bands for these towns, even cells with fewer than 30 sales; counts appear on hover. A missing cell means no transactions.
- Signed gap = (median S$/m² for <60 years / median S$/m² for ≥80 years − 1) × 100. It is not a yearly rate. It does not control for size beyond dividing price by area, flat type, model, storey or micro-location.
- The scatter uses 20 towns with the most 2025 transactions. Its two coordinates are separate town medians, not one real or synthetic representative home. It has no fitted trend or causal inference.
- Million-dollar threshold includes prices equal to S$1,000,000. Waffle circles are percentage points, not homes. The final black share of a dot preserves the fractional percentage without rounding in an extra fictitious home.

## Candidate audit

The full catalog was inspected in the required order: Lupi Editorial, Lupi Basics, then Glance. The user explicitly requested all three families, so Glance is an authorized comparison output rather than a fallback claimed to be necessary. The sets intentionally share one lease-price topic for style comparison and add distinct evidence elsewhere. No template repeats within the nine-chart batch.

Editorial candidates that do not match the data contract: L1 birth/current-size fan, L6 network, L7 bipolar scores, L10 time-of-day, L11 life-history events and L13 funnel lack matching source fields; L5/L12 cannot legibly list 242,259 records. L14 composition is valid for shares but redundant with the chosen Glance share chart. L15 ballots is not an exclusive transaction distribution. L2 integer dot units are poor for continuous median prices. L8 adds a 3D-looking grid without an explanatory dimension. Reserve L16/L19/L20 are unnecessary for the selected matrix, distributions and price comparisons. Basics candidates F4/F7/F10/F11/F13 do not match the selected continuous-price or before/after findings; reserve templates are unnecessary here.

| Output | Source gallery and card | Preserved structure and candidate comparison |
|---|---|---|
| Editorial 01: L3 Barcode Lollipop | `templates/lupi-gallery.html`: Ninety days as a barcode | Full-height period guides, capped stems, lollipop marks, spaced annotations. Period changed explicitly from days to 12 months. F2 would be clearer for connected trend but gives a Basics comparison rather than the requested editorial time texture; F3 area emphasizes integral/volume unnecessarily. |
| Editorial 02: L4 Arc Matrix | `templates/lupi-gallery.html`: Eight products land in twelve cities | Curved row guides, categorical matrix, circle area proportional to median price; fixed sqrt radius scale. L9 better fits years but repeats the mix chart; F10's repeated hour/week grid is not the right contract. L16 heat is unnecessary for 30 cells. |
| Editorial 03: L9 Bubble Almanac | `templates/lupi-gallery.html`: Eight years of tickets, one almanac | Year rows, ledger hairlines, seeded blobs, area=count, marginal notes; outline denotes partial 2026 rather than demo beta status. L4 handles cells but gives less temporal context; F7 cannot carry ten years and five bands under its small-series contract. |
| Basics 01: F5 Tick Rows | `templates/basics-gallery.html`: Six teams, shipped and counted | Horizontal tick queues, guide lines and every-fifth dots. Tick=S$100/m² with fractional last tick. L2 crowds category names; F1 vertical ladders offer less room for band labels. |
| Basics 02: F8 Plumb Scatter | `templates/basics-gallery.html`: Price against satisfaction | Barcode floor, vertical plumb lines, actual x/y values, extreme labels, one town per dot (20 maximum). F5 loses the joint relation; L4 requires binned categories; no artificial random transaction sample is introduced. |
| Basics 03: F6 Paired Rungs | `templates/basics-gallery.html`: This year against last, plan by plan | Two ladders per common flat type, light/black periods, zero baseline, S$25k units, fractional final rungs. F12 could carry endpoints but changes the silhouette; F2 duplicates the time overview. Rare types remain in source and all-record charts. |
| Glance 01: G3 Chunky Bars | `templates/glance-gallery.html`: Revenue by plan | Chart.js canvas, capsule tops, common zero baseline, quartic entry, staggered bars, top value labels. F5/L2 considered first; G3 is included because the user requested a fast-read alternative. |
| Glance 02: G10 Diverging Bar | `templates/glance-gallery.html`: Where we gained, where we bled | ECharts bars with rounded outside ends, signed values and zero markLine. All selected observed gaps are negative; no fictitious positive category is added. F5 is unsigned unit magnitude; F9 is a change decomposition, not separate town contrasts. |
| Glance 03: G4 Dot Waffle | `templates/glance-gallery.html`: Where sign-ups come from | 10×10 dot field, categorical lightness and side legend; one percentage point per dot with fractional final sector. L14/F4 are valid composition alternatives, but G4 fulfills the requested fast-read set and avoids duplicating a donut outline. |

## Shared visual and delivery rules

Mono is used throughout: dense town and lease data do not have a shared categorical color mapping that warrants another palette. Actual gallery structures and inlined MONO tokens are used, with English labels, side notes, source lines, reveal/replay and reduced-motion handling. G3 uses pinned Chart.js 4.5.1; G10 uses pinned ECharts 6.0.0. Both dependencies are embedded in HTML so offline rendering does not rely on a CDN. Inter font can load online; system sans-serif is the offline fallback. Templates are attributed under the included PolyForm Noncommercial license; vendor licenses accompany embedded libraries.

PNG exports include titles, legends and caveats. SVG exports preserve the chart geometry (eight SVG files); G3 is canvas-based and has a PNG rather than a native SVG. Interpretation depends on the explanatory notes as well as geometry.

## Supported observations

- Across pooled 2025 transactions, the ≥80-year band has a higher median S$/m² than the shorter bands; medians below 80 years are not monotonic.
- For the six selected towns, <60-year median S$/m² is 11.4%–26.3% below the ≥80-year median. These are cross-sectional associations.
- Town-level price differences persist beyond lease length alone; scatter summaries are descriptive and are not a controlled model.
- 1,593 of 25,084 transactions in 2025 (6.3507%) cost at least S$1m. Of these, 126 had <60 lease years. That is compatible with location and property attributes influencing prices; it does not prove which factor caused an individual price.

No unique property identifier is available to establish matched repeat sales. A defensible causal depreciation curve would require a separate modeling task with suitable controls, identification assumptions and uncertainty estimates. No such curve or annual percentage is asserted by these charts.
