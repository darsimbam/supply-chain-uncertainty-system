# Project 4 — Fill Rate / Service-Level Simulator

> Estimate service outcomes.

## Main Question
What service outcome will our current inventory policy actually deliver?

## Link to the Big Question
This project links inventory policy to customer-facing service performance.

**How do we improve service at the lowest total cost under demand uncertainty?**

It does this by converting inventory policy settings into expected fill rate and CSL — making the service consequence of every policy choice visible.

## Business Problem
What is going wrong today?
- Teams set service targets without knowing whether current inventory can achieve them
- Fill rate and CSL are tracked after the fact, not predicted
- Policy changes are made without estimating service impact
- No tool to test "what if" service scenarios

Who cares?
- Planner
- Inventory manager
- Supply chain manager
- Finance / S&OP
- Commercial / customer service

## 4-Lens View

### Cost
Shows the cost of buying higher service — every extra percent of fill rate has an inventory cost.

### Efficiency
Shows service consequences of current policy settings without waiting for real stockouts.

### Decision-Making
Helps teams choose service targets and inventory levels more rationally and transparently.

### KPIs
- Fill rate (Type 2 service level)
- CSL (Cycle Service Level / Type 1)
- OTIF proxy
- Backorder risk
- Service gap vs target

## Objective
Build a simulator that takes inventory policy inputs (ROP, safety stock, order quantity, lead time) and returns expected fill rate and CSL — both analytically and via Monte Carlo simulation.

## Inputs / Data Needed
- demand distribution or history
- reorder point
- safety stock
- order quantity
- lead time (average and variability)
- service target per SKU / segment
- ABC / XYZ class

## Method

### Baseline
Analytical fill rate (Type 2) and CSL (Type 1) formulas using normal distribution loss functions.

### Improved Approach
Monte Carlo simulation for realistic service estimation across demand and lead-time distributions.

## Outputs
- Fill rate estimate per SKU
- CSL estimate per SKU
- Service gap analysis vs target
- Policy comparison charts (what-if scenarios)
- Sensitivity: fill rate vs safety stock trade-off

## Example Use Case
A planner has a 95% fill rate target across 200 SKUs. This simulator shows that current policy only achieves 91% average — and that 30 specific SKUs are pulling the average down. Increasing safety stock on those 30 SKUs by 1 week would close the gap at a cost of CHF 80k working capital.

## Folder Structure
```text
.
├── README.md
├── data/
├── notebooks/
│   └── 04_fill_rate.ipynb
├── src/
├── outputs/
└── figures/
```

## Evaluation

### Model Metrics
Simulation accuracy, calibration against historical service performance

### Business Metrics
Service attainment, stockout risk, service-cost trade-off curve

## Assumptions
- Demand is approximately normal for continuous items
- Lead time variability is measurable
- Service targets are defined per ABC/XYZ segment

## Gaps / Future Improvements
- Multi-period simulation (rolling horizon)
- Lumpy / intermittent demand simulation
- OTIF with delivery timing modeled

## How to Run
```bash
jupyter notebook notebooks/04_fill_rate.ipynb
```

## Expected Deliverables
- Fill rate and CSL estimate table
- Service gap analysis
- Trade-off charts (service vs inventory)
- Simulation results
- README summary

## Portfolio Link
```
Project 3 (Reorder Point) → Project 4 → Project 5 (Monetization)
```
Uses ROP and safety stock as inputs. Service results feed into financial risk monetization.
