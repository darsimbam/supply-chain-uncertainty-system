# Project 2 — Safety Stock Classification Engine

> Size the uncertainty buffer.

## Main Question
How much uncertainty buffer does each SKU-location need?

## Link to the Big Question
This project converts demand and lead-time uncertainty into buffer stock decisions.

**How do we improve service at the lowest total cost under demand uncertainty?**

It does this by right-sizing the safety buffer per SKU — avoiding both over-investment in low-risk items and under-protection of high-risk ones.

## Business Problem
What is going wrong today?
- Blanket safety stock rules overprotect some items and underprotect others
- No link between forecast error and buffer size
- Buffer is set by gut feel or round numbers
- Working capital is tied up in unnecessary safety stock

Who cares?
- Planner
- Inventory manager
- Supply chain manager
- Finance / S&OP

## 4-Lens View

### Cost
Balances carrying cost against shortage protection. Avoids both excess working capital and stockout losses.

### Efficiency
Right-sizes inventory buffers across the portfolio, releasing working capital where risk is low.

### Decision-Making
Helps planners set safety stock by segment using a transparent, formula-driven approach.

### KPIs
- Safety stock units per SKU
- Days on hand
- Stockout risk by segment
- Working capital in buffer stock

## Objective
Build a tool that calculates recommended safety stock for each SKU using demand uncertainty, lead-time uncertainty, and service targets — segmented by ABC/XYZ class.

## Inputs / Data Needed
- forecast error (sigma demand)
- demand history
- lead time (average and std dev)
- service target (by segment)
- sku criticality
- unit cost
- ABC / XYZ class

## Method

### Baseline
Normal-demand safety stock formula:
`SS = Z * sqrt(LT * sigma_demand^2 + avg_demand^2 * sigma_LT^2)`

### Improved Approach
- Segmented safety stock by ABC/XYZ class
- Simulation-based SS for intermittent or skewed demand
- Sensitivity analysis on service level vs working capital trade-off

## Outputs
- Recommended safety stock per SKU
- Safety stock bands (lower / base / upper)
- Overstock / understock flags vs current buffer
- Working capital impact summary
- Service level vs cost trade-off chart

## Example Use Case
A buyer has 300 SKUs with a flat safety stock of 2 weeks. This tool shows that A/X items need only 0.5 weeks buffer (low variability) while C/Z items need 4 weeks. Reallocating reduces total working capital in buffers by 18% while maintaining or improving service.

## Folder Structure
```text
.
├── README.md
├── data/
├── notebooks/
│   └── 02_safety_stock.ipynb
├── src/
├── outputs/
└── figures/
```

## Evaluation

### Model Metrics
Error distribution fit, uncertainty classification quality per segment

### Business Metrics
Inventory reduction vs current, stockout risk change, working capital impact

## Assumptions
- Demand is approximately normal for continuous items
- Lead time variability is known or estimable
- Service targets are set per ABC/XYZ segment

## Gaps / Future Improvements
- Intermittent demand handling (Poisson, negative binomial)
- Dynamic safety stock (rolling recalculation)
- Shelf-life constraints

## How to Run
```bash
jupyter notebook notebooks/02_safety_stock.ipynb
```

## Expected Deliverables
- Safety stock recommendation table
- Buffer band charts per segment
- Working capital impact summary
- README summary

## Portfolio Link
```
Project 1 (Forecast Accuracy) → Project 2 → Project 3 (Reorder Point)
```
Uses forecast error as input. Feeds safety stock into reorder point calculations.
