# Project 6 — ROI Comparator

> Choose the best improvement lever.

## Main Question
Which uncertainty-reduction lever gives the highest return on investment?

## Link to the Big Question
This project compares improvement levers and helps management choose where to invest first.

**How do we improve service at the lowest total cost under demand uncertainty?**

It does this by ranking the financial return of each improvement lever — so investment goes to where it matters most.

## Business Problem
What is going wrong today?
- Management assumes better forecasting is always the answer
- No tool to compare forecast improvement vs shorter lead times vs postponement
- Investment decisions are made on intuition, not ROI
- No link between improvement initiatives and their inventory and service impact

Who cares?
- Supply chain manager
- Finance / S&OP
- Leadership
- Operations / transformation team

## 4-Lens View

### Cost
Compares total cost impact (holding + shortage + ordering) across improvement levers.

### Efficiency
Shows how responsiveness, planning exposure, and inventory productivity change per lever.

### Decision-Making
Helps management prioritize transformation initiatives by financial return.

### KPIs
- ROI per lever
- Inventory reduction (units and CHF)
- Fill rate improvement (percentage points)
- Payback period (years)
- Annual cost saving (CHF)

## Objective
Build a scenario comparison tool that evaluates three main uncertainty-reduction levers — forecast improvement, lead-time reduction, and review period reduction (or postponement) — and ranks them by ROI and payback period.

## Inputs / Data Needed
- Forecast accuracy scenarios (current vs improved WAPE)
- Lead time scenarios (current vs reduced)
- Review period scenarios (current vs reduced)
- Postponement assumptions
- Shortage cost (from Project 5)
- Holding cost (from Project 5)
- Ordering cost
- Implementation cost per lever

## Method

### Baseline
Simple scenario comparison: calculate expected safety stock and service under each lever assumption.

### Improved Approach
- ROI model: annual saving / implementation cost
- Sensitivity analysis on key assumptions
- Monte Carlo scenario ranking

## Outputs
- Lever comparison dashboard
- ROI ranking table
- Payback period chart
- Management recommendation (top 1–3 levers)
- Sensitivity analysis summary

## Example Use Case
A supply chain director has budget for one initiative. Options are: invest in a new forecasting tool (cost CHF 200k, expected WAPE reduction 15%), reduce supplier lead time by 2 weeks (cost CHF 50k in renegotiation), or shift to weekly review cycles (cost CHF 20k in process change).

This tool shows: lead-time reduction has the highest ROI (8x) and shortest payback (0.6 years). Forecasting improvement has a 2x ROI. Weekly review has a 4x ROI. Recommendation: lead time first, then review cycle.

## Folder Structure
```text
.
├── README.md
├── data/
├── notebooks/
│   └── 06_roi_compare.ipynb
├── src/
├── outputs/
└── figures/
```

## Evaluation

### Model Metrics
Scenario robustness, sensitivity quality, assumption stability

### Business Metrics
CHF saved per lever, inventory released, fill rate improvement, payback period

## Assumptions
- Safety stock savings scale approximately linearly with uncertainty reduction
- Implementation costs are one-time; savings are annual and recurring
- Levers are modeled independently (interaction effects not included in baseline)

## Gaps / Future Improvements
- Combined lever modeling (forecast + lead time simultaneously)
- Risk-adjusted ROI (accounting for implementation risk)
- Integration with financial planning / S&OP process

## How to Run
```bash
jupyter notebook notebooks/06_roi_compare.ipynb
```

## Expected Deliverables
- Lever comparison table with ROI and payback
- Scenario sensitivity charts
- Management recommendation summary
- README summary

## Portfolio Link
```
Project 5 (Monetization) → Project 6 → [Strategic recommendation]
```
Final strategic layer — synthesizes all prior project outputs into a prioritized action plan.
