# Master Data Schema

All projects in this portfolio share a common data structure.
Use this schema when preparing or generating sample data.

## A. Demand and Forecast

| Field | Type | Description |
|---|---|---|
| sku | string | SKU identifier |
| location | string | Warehouse or market |
| date | date | Week or period start date |
| actual_demand | float | Units sold / consumed |
| forecast | float | Forecast for that period |
| forecast_version | string | Forecast run version |
| promo_flag | int | 1 = promotional period |
| holiday_flag | int | 1 = holiday / event period |
| product_family | string | Product group |
| customer | string | Customer or channel (optional) |

## B. Inventory Policy

| Field | Type | Description |
|---|---|---|
| safety_stock | float | Units of safety buffer |
| reorder_point | float | Units — trigger replenishment |
| order_quantity | float | Standard order quantity |
| moq | float | Minimum order quantity |
| review_period | int | Days between review |
| service_target | float | Target CSL, e.g. 0.95 |
| replenishment_type | string | continuous / periodic |

## C. Inventory Position

| Field | Type | Description |
|---|---|---|
| on_hand | float | Units in stock |
| on_order | float | Units ordered, not received |
| backorders | float | Units short / backordered |
| receipts | float | Units received in period |
| stockout_flag | int | 1 = stockout occurred |

## D. Supply

| Field | Type | Description |
|---|---|---|
| supplier | string | Supplier name |
| lead_time | float | Average lead time (days) |
| lead_time_std | float | Std dev of lead time |
| transport_mode | string | Road / sea / air |
| order_frequency | int | Orders per period |

## E. Financial

| Field | Type | Description |
|---|---|---|
| unit_cost | float | Cost per unit (CHF) |
| unit_margin | float | Margin per unit (CHF) |
| holding_cost_rate | float | Annual rate, e.g. 0.20 |
| shortage_cost_per_unit | float | Cost per unit short |
| expedite_cost_per_unit | float | Expedite premium per unit |
| markdown_rate | float | Markdown fraction for excess |

## F. Segmentation

| Field | Type | Description |
|---|---|---|
| abc_class | string | A / B / C |
| xyz_class | string | X / Y / Z |
| criticality | string | High / Medium / Low |
| shelf_life_days | int | 0 = no constraint |
| substitution_flag | int | 1 = substitutable |
