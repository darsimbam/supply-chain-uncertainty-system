# Project 5 — Shortage vs Excess Monetization Engine

> Price the risk of shortage and excess.

## Main Question
What is the expected financial impact of shortage versus excess inventory?

## Link to the Big Question
This project converts operational uncertainty into money-based decisions.

**How do we improve service at the lowest total cost under demand uncertainty?**

It does this by making the financial cost of both shortage and excess visible, enabling prioritization by financial impact rather than operational intuition.

## Business Problem
What is going wrong today?
- Stockouts and overstocks are discussed operationally, not financially
- No view of which SKUs carry the highest financial risk
- Teams cannot answer: "what is a stockout on SKU X actually costing us?"
- Excess inventory costs are underestimated (holding + markdown + obsolescence)

Who cares?
- Planner
- Inventory manager
- Supply chain manager
- Finance / S&OP / leadership
- Commercial / sales

## 4-Lens View

### Cost
Quantifies shortage cost (lost margin, expediting), holding cost, markdown risk, and obsolescence per SKU.

### Efficiency
Improves capital allocation and prioritization by SKU risk rank.

### Decision-Making
Helps teams decide whether to buy more, hold less, expedite, delay, or change policy — on a financial basis.

### KPIs
- Expected shortage cost (CHF)
- Expected excess cost (CHF)
- Working capital at risk
- Total expected loss per SKU
- SKU risk rank

## Objective
Build a tool that calculates expected shortage and excess cost per SKU using stockout probability, expected short / excess units, unit margin, holding cost rate, and markdown assumptions.

## Inputs / Data Needed
- fill rate / stockout probability (from Project 4)
- expected units short
- expected excess units
- unit margin
- unit cost
- holding cost rate
- markdown / obsolescence assumptions
- expedite cost per unit

## Method

### Baseline
Expected shortage cost = stockout_probability * units_short * (margin + expedite_cost)
Expected excess cost = excess_units * unit_cost * holding_rate + markdown_loss

### Improved Approach
- Scenario modeling: best case / base case / worst case
- Simulation with cost distributions
- Sensitivity to margin, cost rate, and demand assumptions

## Outputs
- Cost trade-off table (shortage vs excess per SKU)
- SKU risk ranking by total expected loss
- Recommended action by SKU (buy more / hold / reduce)
- Scenario comparison chart

## Example Use Case
A supply chain manager sees 500 SKUs but cannot prioritize. This tool ranks them by expected financial loss. The top 20 SKUs account for 75% of total risk. Of those, 12 are shortage-dominated (high margin, high stockout) and 8 are excess-dominated (low margin, slow-moving). Clear actions follow from the ranking.

## Folder Structure
```text
.
├── README.md
├── data/
├── notebooks/
│   └── 05_monetization.ipynb
├── src/
├── outputs/
└── figures/
```

## Evaluation

### Model Metrics
Risk estimate consistency across scenarios, sensitivity stability

### Business Metrics
CHF impact quantified, excess reduction potential, shortage avoidance value

## Assumptions
- Unit margin is known or estimable
- Holding cost rate is defined (typically 15–30% per year)
- Markdown and obsolescence rates are estimated
- Stockout probability comes from Project 4

## Gaps / Future Improvements
- Customer-specific shortage cost (strategic accounts)
- Substitution and lost-loyalty effects
- Shelf-life and perishability costs

## How to Run
```bash
jupyter notebook notebooks/05_monetization.ipynb
```

## Expected Deliverables
- Cost trade-off table per SKU
- Risk ranking table
- Scenario comparison charts
- Action recommendation summary
- README summary

## Portfolio Link
```
Project 4 (Fill Rate) → Project 5 → Project 6 (ROI Comparator)
```
Turns service results into financial prioritization. Feeds cost estimates into ROI comparison.
