# Supply Chain Uncertainty Decision System

**Live Demo:** [baselstrase-sc-opt.streamlit.app](https://baselstrase-sc-opt.streamlit.app/)

An end-to-end supply chain analytics portfolio for turning demand uncertainty into better inventory, service, and financial decisions.

## Core Question
How do we improve service at the lowest total cost under demand uncertainty?

## What This Repository Does
This repository connects six decision layers that are often handled separately:

1. Forecast accuracy
2. Safety stock sizing
3. Reorder point design
4. Fill rate and service simulation
5. Shortage versus excess cost monetization
6. ROI comparison of improvement levers

Together, they form a single decision system rather than a set of isolated analyses.

## Why It Matters
Uncertainty in demand and supply typically shows up in two expensive ways:

- too much inventory
- too little availability

That leads to:

- stockouts
- excess inventory
- expediting costs
- unstable replenishment decisions
- trapped working capital

The goal of this project is not to optimize one metric in isolation. It is to improve customer service while minimizing the total cost of uncertainty.

## Portfolio Modules

### 1. Forecast Accuracy Improvement Engine
Answers: How good is our demand signal?

Focus:
- forecast error diagnostics
- bias detection
- forecastability segmentation
- demand signal improvement opportunities

### 2. Safety Stock Classification Engine
Answers: How much uncertainty buffer do we need?

Focus:
- service-driven safety stock sizing
- ABC and XYZ segmentation
- working capital impact of policy changes

### 3. Reorder Point Classification Engine
Answers: When should we replenish?

Focus:
- reorder point logic
- review policy design
- replenishment trigger sensitivity

### 4. Fill Rate and Service-Level Simulator
Answers: What service outcome will the current policy deliver?

Focus:
- fill rate estimation
- cycle service performance
- Monte Carlo style policy evaluation

### 5. Shortage vs Excess Monetization Engine
Answers: What is the financial risk of shortage versus excess?

Focus:
- expected shortage cost
- expected excess cost
- service-cost trade-off visibility

### 6. ROI Comparator
Answers: Which uncertainty-reduction lever gives the best return?

Focus:
- ROI by lever
- payback comparison
- prioritization of operational improvements

## System Flow
```text
Forecast Accuracy -> Safety Stock -> Reorder Point -> Fill Rate -> Risk Monetization -> ROI Comparison
```

## Repository Structure
```text
.
|-- README.md
|-- app.py
|-- requirements.txt
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- sample/
|-- notebooks/
|   |-- 01_forecast_accuracy.ipynb
|   |-- 02_safety_stock.ipynb
|   |-- 03_reorder_point.ipynb
|   |-- 04_fill_rate.ipynb
|   |-- 05_monetization.ipynb
|   `-- 06_roi_compare.ipynb
|-- src/
|   |-- forecasting.py
|   |-- inventory.py
|   |-- monetization.py
|   |-- scenarios.py
|   |-- service.py
|   `-- utils.py
|-- outputs/
|   |-- figures/
|   |-- tables/
|   `-- reports/
|-- 01_forecast_accuracy_engine/
|-- 02_safety_stock_classification/
|-- 03_reorder_point_classification/
|-- 04_fill_rate_service_simulator/
|-- 05_shortage_excess_monetization/
`-- 06_roi_comparator/
```

## Data
The project is set up to work with either:

- sample or synthetic data in `data/sample/`
- processed real data in `data/processed/`

Large raw files and generated outputs are intentionally excluded from Git through `.gitignore`.

Typical fields used across the modules include:

- `sku`, `location`, `date`
- `actual_demand`, `forecast`
- `lead_time`, `lead_time_variability`
- `order_quantity`, `review_period`, `service_target`
- `unit_cost`, `holding_cost_rate`, `shortage_cost`
- `on_hand`, `on_order`
- `abc_class`, `xyz_class`

## Methods and Techniques
- baseline forecasting
- moving averages and smoothing approaches
- forecast error diagnostics such as MAE, RMSE, bias, and WAPE
- ABC and XYZ segmentation
- safety stock and reorder point calculations
- fill rate and cycle service evaluation
- scenario comparison
- financial risk monetization
- ROI analysis

## Quick Start

### 1. Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```powershell
pip install -r requirements.txt
```

### 3. Explore the notebooks
```powershell
jupyter notebook
```

### 4. Run the Streamlit app
```powershell
streamlit run app.py
```

The app reads from `data/processed/master_data.csv` when available and falls back to `data/sample/master_data.csv` otherwise.

## Outputs
Expected outputs include:

- results tables in `outputs/tables/`
- charts in `outputs/figures/`
- summary artifacts in `outputs/reports/`
- module-level insights from each notebook

## Who This Is For
- supply chain analysts
- planners and buyers
- inventory managers
- finance and S&OP teams
- operations leaders evaluating improvement priorities

## Project Positioning
This repository is designed as a portfolio-grade supply chain decision platform that links operational analytics to financial trade-offs and investment choices.

## Notes
- sample data is included for demonstration
- raw uploads and generated result files are not committed
- each module folder contains a project-specific README with more detail
