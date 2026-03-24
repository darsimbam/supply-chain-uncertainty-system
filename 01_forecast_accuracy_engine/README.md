# Project 1 — Forecast Accuracy Improvement Engine

> Improve the demand signal.

## Main Question
How good is our demand signal, and how can we improve it?

## Link to the Big Question
This project improves the quality of the demand signal used in all downstream inventory decisions.

**How do we improve service at the lowest total cost under demand uncertainty?**

It does this by reducing the uncertainty that enters every downstream calculation — safety stock, reorder point, fill rate, and risk monetization all depend on forecast quality.

## Business Problem
What is going wrong today?
- Planners use inaccurate forecasts without knowing it
- Safety stock is sized on faulty error assumptions
- Replenishment reacts to noise, not signal
- No visibility into which SKUs drive the most forecast waste

Who cares?
- Planner
- Buyer
- Inventory manager
- Supply chain manager
- Finance / S&OP / leadership

## 4-Lens View

### Cost
Reduces avoidable inventory, shortages, and expediting caused by forecast error and bias.

### Efficiency
Improves planning stability, reduces firefighting, and increases demand signal visibility.

### Decision-Making
Helps planners decide which SKUs need better forecasting, a different model, or resegmentation.

### KPIs
- RMSE
- WAPE / MAPE
- Bias (mean forecast error)
- Forecast Value Added (FVA)
- SKU-level error distribution

## Objective
Build a tool that measures current forecast quality, identifies the worst-performing SKUs, detects bias, and recommends whether a better model or segmentation would improve outcomes.

## Inputs / Data Needed
- sku
- location
- date / week
- actual demand
- forecast
- promo flag
- calendar variables (holiday, seasonality)
- price / event flags
- product family
- ABC / XYZ class

## Method

### Baseline
Naive, moving average, exponential smoothing — compare against existing forecast.

### Improved Approach
Feature-based forecasting, ABC/XYZ segmentation per method, hierarchical forecasting.

## Outputs
- Error dashboard by SKU and family
- Bias heatmap
- SKU segmentation by forecastability
- Improved forecast recommendations
- Forecast Value Added summary

## Example Use Case
A planner has 200 SKUs. This tool shows that 40 SKUs account for 80% of total forecast error. Of those, 15 are systematically over-forecast (negative bias), leading to excess inventory. A simple model switch on those 15 SKUs reduces WAPE by 12%.

## Folder Structure
```text
.
├── README.md
├── data/
├── notebooks/
│   └── 01_forecast_accuracy.ipynb
├── src/
├── outputs/
└── figures/
```

## Evaluation

### Model Metrics
RMSE, MAE, bias, WAPE, MAPE, FVA

### Business Metrics
Safety stock reduction potential, forecast stability improvement, service improvement potential

## Assumptions
- Forecast errors are approximately normally distributed for continuous demand
- Intermittent SKUs require separate treatment
- Historical actuals are clean (outliers treated upstream)

## Gaps / Future Improvements
- Intermittent demand models (Croston, TSB)
- Promotional uplift modeling
- Hierarchical / reconciled forecasting

## How to Run
```bash
jupyter notebook notebooks/01_forecast_accuracy.ipynb
```

## Expected Deliverables
- Cleaned dataset with error metrics per SKU
- Error and bias plots
- SKU segmentation by forecastability
- Final recommendation table
- README summary

## Portfolio Link
```
[Start] → Project 1 → Project 2 (Safety Stock)
```
Forecast quality feeds directly into safety stock sizing and ROP calculations.
