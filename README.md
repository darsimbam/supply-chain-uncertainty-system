# Supply Chain Uncertainty Decision System

**Live demo:** [baselstrase-sc-opt.streamlit.app](https://baselstrase-sc-opt.streamlit.app/)

An end-to-end supply chain analytics portfolio that links demand uncertainty to inventory policy, service performance, financial risk, and improvement ROI.

## Core Question
How do we improve service at the lowest total cost under demand uncertainty?

## Overview
This repository combines six connected analytics modules that are often treated as separate problems:

1. Forecast accuracy
2. Safety stock sizing
3. Reorder point design
4. Fill rate and service simulation
5. Shortage versus excess monetization
6. ROI comparison of improvement levers

The goal is to move from isolated analysis to a single decision system for planners, inventory teams, and supply chain leaders.

## Why This Matters
Uncertainty creates cost in two directions:

- too much inventory
- too little availability

Those issues show up as:

- stockouts
- excess stock
- expediting
- unstable replenishment
- trapped working capital

This project focuses on improving service without treating inventory growth as the default solution.

## Portfolio Modules

### 1. Forecast Accuracy Improvement Engine
Purpose: measure forecast quality, detect bias, and identify where the demand signal can be improved.

### 2. Safety Stock Classification Engine
Purpose: size uncertainty buffers by item profile and service target.

### 3. Reorder Point Classification Engine
Purpose: determine when replenishment should be triggered under uncertainty.

### 4. Fill Rate and Service Simulator
Purpose: estimate the service outcome delivered by the current policy.

### 5. Shortage vs Excess Monetization Engine
Purpose: translate shortage and excess outcomes into comparable financial risk.

### 6. ROI Comparator
Purpose: rank improvement levers such as forecast improvement, lead-time reduction, or policy change by expected return.

## Decision Flow
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
The project supports two main data modes:

- sample or synthetic data in `data/sample/`
- processed business-ready data in `data/processed/`

Large raw files and generated outputs are excluded from version control through `.gitignore`.

Typical fields used across the modules include:

- `sku`, `location`, `date`
- `actual_demand`, `forecast`
- `lead_time`, `lead_time_variability`
- `review_period`, `order_quantity`, `service_target`
- `unit_cost`, `holding_cost_rate`, `shortage_cost`
- `on_hand`, `on_order`
- `abc_class`, `xyz_class`

## Methods
- forecast diagnostics such as MAE, RMSE, bias, and WAPE
- moving average and smoothing-based forecasting baselines
- ABC and XYZ segmentation
- safety stock and reorder point calculations
- fill rate and cycle service evaluation
- scenario analysis
- expected shortage and excess cost modeling
- ROI comparison of uncertainty-reduction levers

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

### 3. Launch the notebooks
```powershell
jupyter notebook
```

### 4. Run the Streamlit app
```powershell
streamlit run app.py
```

The app loads `data/processed/master_data.csv` when it exists and falls back to `data/sample/master_data.csv` otherwise.

## Outputs
Typical outputs include:

- result tables in `outputs/tables/`
- figures in `outputs/figures/`
- summary artifacts in `outputs/reports/`
- notebook-level analyses for each module

## Intended Audience
- supply chain analysts
- planners and buyers
- inventory managers
- finance and S&OP teams
- operations leaders prioritizing improvement initiatives

## Notes
- sample data is included for demonstration
- raw uploads and generated result files are not committed
- each module folder contains a more detailed project-specific README
