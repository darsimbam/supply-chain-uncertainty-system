# Project 3 — Reorder Point Classification Engine

> Trigger replenishment correctly.

## Main Question
When should we replenish inventory?

## Link to the Big Question
This project turns expected lead-time demand and uncertainty into replenishment triggers.

**How do we improve service at the lowest total cost under demand uncertainty?**

It does this by ensuring replenishment is triggered at the right moment — not too late (stockout) and not too early (excess).

## Business Problem
What is going wrong today?
- Reorder points are set manually or with flat rules
- Late triggers cause stockouts
- Early triggers create excess inventory
- No segmentation between continuous and periodic review items

Who cares?
- Planner
- Buyer
- Inventory manager
- Supply chain manager

## 4-Lens View

### Cost
Balances ordering cost, shortage cost, and unnecessary inventory from mistimed replenishment.

### Efficiency
Improves replenishment timing, reduces emergency orders, and stabilizes order flow.

### Decision-Making
Helps buyers and planners know exactly when to trigger orders for each SKU.

### KPIs
- Reorder point (units)
- Replenishment frequency
- Stock cover (days)
- Stockout rate before replenishment arrives
- Order timing accuracy

## Objective
Build a tool that calculates reorder points per SKU-location using lead-time demand and safety stock, with segmentation by replenishment policy type (continuous vs periodic review).

## Inputs / Data Needed
- demand history and forecast
- lead time (average, std dev)
- safety stock (from Project 2)
- on-hand inventory
- on-order inventory
- MOQ / order quantity
- review period
- ABC / XYZ class

## Method

### Baseline
`ROP = avg_demand * lead_time + safety_stock`

### Improved Approach
- Segmented ROP by ABC/XYZ and replenishment type
- Dynamic ROP with rolling demand and lead-time updates
- Continuous vs periodic review comparison (s,S) vs (R,S) policies

## Outputs
- Reorder point recommendation per SKU
- Replenishment trigger table
- Inventory policy matrix (continuous / periodic)
- Stock cover analysis

## Example Use Case
A distribution center has 150 SKUs on continuous review. This tool shows that 40 SKUs have reorder points set below lead-time demand (no safety stock included), causing recurring stockouts. Correcting the ROP formula eliminates 60% of those events.

## Folder Structure
```text
.
├── README.md
├── data/
├── notebooks/
│   └── 03_reorder_point.ipynb
├── src/
├── outputs/
└── figures/
```

## Evaluation

### Model Metrics
Policy stability, sensitivity to demand and lead-time changes

### Business Metrics
Stockout reduction, inventory productivity, replenishment responsiveness

## Assumptions
- Demand during lead time is approximately normal
- Lead times are known with some measurable variability
- Safety stock from Project 2 is used as direct input

## Gaps / Future Improvements
- Multi-echelon reorder point logic
- Supplier capacity constraints
- Batch ordering and MOQ effects

## How to Run
```bash
jupyter notebook notebooks/03_reorder_point.ipynb
```

## Expected Deliverables
- ROP recommendation table
- Policy type matrix per SKU
- Stock cover and trigger timing charts
- README summary

## Portfolio Link
```
Project 2 (Safety Stock) → Project 3 → Project 4 (Fill Rate Simulator)
```
Built on safety stock output. Feeds replenishment policy into service simulation.
