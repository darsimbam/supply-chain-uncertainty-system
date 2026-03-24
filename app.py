"""
app.py — Supply Chain Uncertainty Decision Platform
Run: streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure repo root is on sys.path so 'src' is importable on Streamlit Cloud
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Paths ───────────────────────────────────────────────────────────────────────
TABLES = ROOT / "outputs" / "tables"
FIGS   = ROOT / "outputs" / "figures"

st.set_page_config(
    page_title="SC Uncertainty Decision Platform",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ────────────────────────────────────────────────────────────────────
C = {
    "green":  "#2ecc71",
    "red":    "#e74c3c",
    "orange": "#f39c12",
    "blue":   "#2980b9",
    "purple": "#8e44ad",
    "dark":   "#2c3e50",
    "light":  "#ecf0f1",
    "teal":   "#16a085",
}

ABC_COLORS  = {"A": C["red"], "B": C["orange"], "C": C["blue"]}
RISK_COLORS = {"Shortage-dominated": C["red"], "Excess-dominated": C["blue"]}


# ── Data loaders (cached) ──────────────────────────────────────────────────────
@st.cache_data
def load_master():
    processed = ROOT / "data" / "processed" / "master_data.csv"
    sample    = ROOT / "data" / "sample"    / "master_data.csv"
    path = processed if processed.exists() else sample
    df = pd.read_csv(path, parse_dates=["date"])
    return df, path.parent.name


@st.cache_data
def load_table(name: str) -> pd.DataFrame | None:
    p = TABLES / name
    return pd.read_csv(p) if p.exists() else None


def pct(val: float, decimals: int = 1) -> str:
    return f"{val * 100:.{decimals}f}%"


def kchf(val: float) -> str:
    return f"GBP {val:,.0f}"


def delta_color(val: float) -> str:
    return "normal" if val >= 0 else "inverse"


# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 SC Decision Platform")
    st.caption("Supply Chain Uncertainty System")
    st.divider()

    page = st.radio(
        "Navigate",
        [
            "🏠  Portfolio Overview",
            "1️⃣  Forecast Accuracy",
            "2️⃣  Safety Stock",
            "3️⃣  Reorder Point",
            "4️⃣  Fill Rate & Service",
            "5️⃣  Shortage & Excess Cost",
            "6️⃣  ROI Comparator",
            "🔍  Data Explorer",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # Data source info
    _, source = load_master()
    badge = "🟢 Real data" if source == "processed" else "🟡 Synthetic data"
    st.caption(badge)

    # Filters (shared)
    st.markdown("**Filters**")
    master_df, _ = load_master()
    all_abc = sorted(master_df["abc_class"].dropna().unique())
    all_locs = sorted(master_df["location"].dropna().unique())
    sel_abc  = st.multiselect("ABC Class", all_abc, default=all_abc, key="f_abc")
    sel_locs = st.multiselect("Location",  all_locs, default=all_locs, key="f_loc")


# ── Helper: filter a results table by sidebar selections ──────────────────────
def apply_filter(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    if "abc_class" in df.columns:
        df = df[df["abc_class"].isin(sel_abc)]
    if "location" in df.columns:
        df = df[df["location"].isin(sel_locs)]
    return df


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PORTFOLIO OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Portfolio Overview":

    st.title("Supply Chain Uncertainty Decision System")
    st.markdown(
        "> **Core question:** How do we improve service at the lowest total cost under demand uncertainty?"
    )

    # Data info banner
    df, source = load_master()
    weeks  = df["date"].nunique()
    skus   = df["sku"].nunique()
    locs   = df["location"].nunique()
    d_min  = df["date"].min().strftime("%b %Y") if hasattr(df["date"].min(), "strftime") else str(df["date"].min())
    d_max  = df["date"].max().strftime("%b %Y") if hasattr(df["date"].max(), "strftime") else str(df["date"].max())

    col_src, col_skus, col_locs, col_wks, col_range = st.columns(5)
    col_src.metric("Data Source",  source.replace("processed", "Real").replace("sample", "Synthetic"))
    col_skus.metric("SKUs",        skus)
    col_locs.metric("Locations",   locs)
    col_wks.metric("Weeks",        weeks)
    col_range.metric("Period",     f"{d_min} – {d_max}")

    st.divider()

    # System flow
    st.subheader("System Flow")
    flow_cols = st.columns(6)
    flow_items = [
        ("1", "Forecast\nAccuracy",  "Demand signal quality"),
        ("2", "Safety\nStock",       "Uncertainty buffer"),
        ("3", "Reorder\nPoint",      "Replenishment trigger"),
        ("4", "Fill Rate\nSimulator","Service outcome"),
        ("5", "Shortage &\nExcess",  "Financial risk"),
        ("6", "ROI\nComparator",     "Best lever"),
    ]
    for col, (num, title, sub) in zip(flow_cols, flow_items):
        col.markdown(
            f"""<div style='background:{C["dark"]};border-radius:8px;padding:12px;text-align:center;'>
            <span style='font-size:22px;color:{C["teal"]};font-weight:bold;'>{num}</span><br>
            <span style='color:white;font-weight:600;font-size:13px;'>{title}</span><br>
            <span style='color:#aaa;font-size:11px;'>{sub}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── KPI summary strip ──────────────────────────────────────────────────────
    st.subheader("Portfolio KPIs")

    p1 = load_table("01_forecast_accuracy_results.csv")
    p2 = load_table("02_safety_stock_results.csv")
    p4 = load_table("04_fill_rate_results.csv")
    p5 = load_table("05_monetization_results.csv")
    p6 = load_table("06_roi_results.csv")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    if p1 is not None:
        wape = p1["wape"].mean()
        c1.metric("Avg WAPE", pct(wape), help="Weighted Absolute Percentage Error — lower is better")

    if p2 is not None:
        delta_wc = (p2["rec_ss_chf"] - p2["current_ss_chf"]).sum()
        c2.metric("SS WC Change", kchf(delta_wc), delta=f"{delta_wc:+,.0f}",
                  delta_color="inverse" if delta_wc < 0 else "normal",
                  help="Recommended vs current safety stock working capital")

    if p4 is not None:
        avg_fr = p4["fill_rate_sim"].mean()
        avg_tgt = p4["service_target"].mean()
        c4.metric("Avg Fill Rate", pct(avg_fr), delta=f"{(avg_fr - avg_tgt)*100:+.1f}pp vs target",
                  help="Monte Carlo simulated fill rate vs service target")

    if p5 is not None:
        total_loss = p5["total_expected_loss"].sum()
        shortage   = p5["exp_shortage_cost"].sum()
        excess     = p5["exp_excess_cost"].sum()
        c5.metric("Total Expected Loss", kchf(total_loss),
                  help="Combined expected cost of shortage and excess")

    if p6 is not None:
        top_roi = p6.iloc[0]
        c6.metric(f"#{1} Lever ROI", f"{top_roi['ROI']:.1f}x",
                  help=f"Best lever: {top_roi['Lever']}")

    st.divider()

    # ── Cost breakdown ─────────────────────────────────────────────────────────
    if p5 is not None:
        st.subheader("Financial Risk Breakdown")
        c_left, c_right = st.columns(2)

        with c_left:
            fig = go.Figure(go.Pie(
                labels=["Shortage Cost", "Excess Cost"],
                values=[p5["exp_shortage_cost"].sum(), p5["exp_excess_cost"].sum()],
                marker_colors=[C["red"], C["blue"]],
                hole=0.5,
                textinfo="label+percent",
            ))
            fig.update_layout(
                title="Expected Loss Split", height=320,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        with c_right:
            loss_abc = p5.groupby("abc_class")[["exp_shortage_cost", "exp_excess_cost"]].sum().reset_index()
            fig2 = px.bar(
                loss_abc, x="abc_class", y=["exp_shortage_cost", "exp_excess_cost"],
                barmode="stack",
                color_discrete_map={"exp_shortage_cost": C["red"], "exp_excess_cost": C["blue"]},
                labels={"value": "Expected Cost (GBP)", "abc_class": "ABC Class", "variable": ""},
                title="Expected Loss by ABC Class",
            )
            fig2.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Management recommendation ──────────────────────────────────────────────
    if p6 is not None:
        st.subheader("Management Recommendation")
        for _, row in p6.iterrows():
            verdict_color = C["green"] if "now" in str(row.get("Verdict","")) else C["orange"] if "budget" in str(row.get("Verdict","")) else C["red"]
            st.markdown(
                f"""<div style='border-left:4px solid {verdict_color};padding:10px 16px;
                margin-bottom:8px;background:#f8f9fa;border-radius:0 6px 6px 0;'>
                <b>#{int(row['Rank'])} {row['Lever']}</b> &nbsp;|&nbsp;
                ROI <b>{row['ROI']:.1f}x</b> &nbsp;|&nbsp;
                Payback <b>{row['Payback (years)']:.2f} years</b> &nbsp;|&nbsp;
                Annual saving <b>GBP {row['Annual Saving (KCHF)']*1000:,.0f}</b> &nbsp;|&nbsp;
                <span style='color:{verdict_color};font-weight:600;'>{row.get('Verdict','')}</span>
                </div>""",
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: FORECAST ACCURACY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "1️⃣  Forecast Accuracy":
    st.title("Project 1 — Forecast Accuracy Improvement Engine")
    st.caption("How good is our demand signal, and how can we improve it?")

    p1 = apply_filter(load_table("01_forecast_accuracy_results.csv"))
    if p1 is None:
        st.warning("Run notebook 01 first."); st.stop()

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("SKU-Locations",   len(p1))
    k2.metric("Avg WAPE",        pct(p1["wape"].mean()))
    k3.metric("Avg Bias",        pct(p1["bias_pct"].mean()))
    k4.metric("FVA > 0",         f"{(p1['fva']>0).sum()} / {len(p1)}")
    k5.metric("Low Forecastability", f"{(p1['forecastability']=='Low').sum()} SKUs")

    st.divider()
    tab_charts, tab_table = st.tabs(["Charts", "Results Table"])

    with tab_charts:
        c1, c2 = st.columns(2)

        with c1:
            # WAPE by segment
            fig = px.box(
                p1, x="abc_class", y="wape", color="abc_class",
                color_discrete_map=ABC_COLORS,
                labels={"wape": "WAPE", "abc_class": "ABC Class"},
                title="WAPE Distribution by ABC Class",
            )
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(showlegend=False, height=380)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Bias distribution
            p1["bias_pct_disp"] = p1["bias_pct"] * 100
            fig2 = px.histogram(
                p1, x="bias_pct_disp", color="abc_class",
                color_discrete_map=ABC_COLORS,
                labels={"bias_pct_disp": "Bias (% of avg demand)", "abc_class": "Class"},
                title="Forecast Bias Distribution",
                barmode="overlay", nbins=25,
            )
            fig2.add_vline(x=0, line_dash="dash", line_color="black")
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, use_container_width=True)

        # FVA bar
        p1_sorted = p1.sort_values("fva", ascending=False)
        fig3 = px.bar(
            p1_sorted, y="fva",
            color=p1_sorted["fva"].apply(lambda x: "Beats Naive" if x > 0 else "Worse than Naive"),
            color_discrete_map={"Beats Naive": C["green"], "Worse than Naive": C["red"]},
            labels={"fva": "Forecast Value Added", "index": "SKU-Location"},
            title="Forecast Value Added vs Naive Lag-1 Benchmark",
        )
        fig3.add_hline(y=0, line_color="black", line_width=1)
        fig3.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig3, use_container_width=True)

        # Forecastability map
        fig4 = px.scatter(
            p1, x="wape", y="bias_pct",
            color="forecastability",
            color_discrete_map={"High": C["green"], "Medium": C["orange"], "Low": C["red"]},
            symbol="abc_class",
            hover_data=["sku", "location", "recommendation"],
            labels={"wape": "WAPE", "bias_pct": "Bias %", "forecastability": "Forecastability"},
            title="Forecastability Map: WAPE vs Bias",
        )
        fig4.update_xaxes(tickformat=".0%")
        fig4.update_yaxes(tickformat=".0%")
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)

    with tab_table:
        st.dataframe(
            p1.style.background_gradient(subset=["wape"], cmap="RdYlGn_r")
                    .background_gradient(subset=["fva"],  cmap="RdYlGn"),
            use_container_width=True, height=500,
        )
        st.download_button("Download CSV", p1.to_csv(index=False),
                           "01_forecast_accuracy.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: SAFETY STOCK
# ══════════════════════════════════════════════════════════════════════════════
elif page == "2️⃣  Safety Stock":
    st.title("Project 2 — Safety Stock Classification Engine")
    st.caption("How much uncertainty buffer does each SKU-location need?")

    p2 = apply_filter(load_table("02_safety_stock_results.csv"))
    if p2 is None:
        st.warning("Run notebook 02 first."); st.stop()

    curr_wc = p2["current_ss_chf"].sum()
    rec_wc  = p2["rec_ss_chf"].sum()
    delta   = rec_wc - curr_wc

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("SKU-Locations",      len(p2))
    k2.metric("Current SS WC",      kchf(curr_wc))
    k3.metric("Recommended SS WC",  kchf(rec_wc), delta=f"{delta:+,.0f}",
              delta_color="inverse" if delta < 0 else "normal")
    k4.metric("Under-buffered",     (p2["ss_status"] == "Under-buffered").sum())
    k5.metric("Over-buffered",      (p2["ss_status"] == "Over-buffered").sum())

    st.divider()
    tab_charts, tab_tradeoff, tab_table = st.tabs(["Charts", "Service vs WC Trade-off", "Results Table"])

    with tab_charts:
        c1, c2 = st.columns(2)

        with c1:
            # Scatter: current vs recommended SS
            status_colors = {
                "Under-buffered": C["red"],
                "Over-buffered":  C["blue"],
                "On target":      C["green"],
            }
            fig = px.scatter(
                p2, x="current_ss", y="rec_ss", color="ss_status",
                color_discrete_map=status_colors,
                hover_data=["sku", "location", "abc_class"],
                labels={"current_ss": "Current SS (units)", "rec_ss": "Recommended SS (units)"},
                title="Current vs Recommended Safety Stock",
            )
            lim = max(p2[["current_ss", "rec_ss"]].max())
            fig.add_shape(type="line", x0=0, y0=0, x1=lim, y1=lim,
                          line=dict(color="black", dash="dash", width=1))
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Days on hand comparison
            doh = (
                p2.groupby("segment")[["doh_current", "doh_rec"]].mean()
                .reset_index()
                .melt(id_vars="segment", var_name="type", value_name="days")
            )
            doh["type"] = doh["type"].map({"doh_current": "Current", "doh_rec": "Recommended"})
            fig2 = px.bar(
                doh, x="segment", y="days", color="type",
                barmode="group",
                color_discrete_map={"Current": "#95a5a6", "Recommended": C["blue"]},
                labels={"days": "Days on Hand (SS buffer)", "segment": "Segment"},
                title="Safety Stock Days on Hand: Current vs Recommended",
            )
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, use_container_width=True)

        # WC by ABC class
        wc_abc = p2.groupby("abc_class")[["current_ss_chf", "rec_ss_chf"]].sum().reset_index()
        wc_abc = wc_abc.melt(id_vars="abc_class", var_name="type", value_name="chf")
        wc_abc["type"] = wc_abc["type"].map({"current_ss_chf": "Current", "rec_ss_chf": "Recommended"})
        fig3 = px.bar(
            wc_abc, x="abc_class", y="chf", color="type", barmode="group",
            color_discrete_map={"Current": "#95a5a6", "Recommended": C["blue"]},
            labels={"chf": "Working Capital (GBP)", "abc_class": "ABC Class"},
            title="Safety Stock Working Capital by ABC Class",
        )
        fig3.update_layout(height=360)
        st.plotly_chart(fig3, use_container_width=True)

    with tab_tradeoff:
        st.markdown("### Service Level vs Working Capital Trade-off")
        st.caption("How much additional working capital is required to achieve each service level target?")

        master_df, _ = load_master()
        from scipy.stats import norm
        from src.inventory import safety_stock_normal

        df_clean = master_df[
            (master_df["abc_class"].isin(sel_abc)) &
            (master_df["location"].isin(sel_locs)) &
            (master_df["promo_flag"] == 0)
        ]

        stats = (
            df_clean.groupby(["sku", "location"])
            .agg(avg_demand=("actual_demand","mean"),
                 std_demand=("actual_demand","std"),
                 lt_mean=("lead_time_mean","first"),
                 lt_std=("lead_time_std","first"),
                 unit_cost=("unit_cost","first"),
                 abc_class=("abc_class","first"))
            .reset_index()
        )

        service_levels = [0.80, 0.85, 0.90, 0.95, 0.97, 0.99]
        rows = []
        for sl in service_levels:
            for abc in ["A", "B", "C"]:
                sub = stats[stats["abc_class"] == abc]
                total = 0
                for _, r in sub.iterrows():
                    lt = r["lt_mean"] / 7
                    lt_std = r["lt_std"] / 7
                    ss = safety_stock_normal(r["std_demand"], lt, lt_std, r["avg_demand"], sl)
                    total += ss * r["unit_cost"]
                rows.append({"Service Level": sl * 100, "ABC Class": abc, "SS WC (GBP)": total})

        tradeoff = pd.DataFrame(rows)
        fig_t = px.line(
            tradeoff, x="Service Level", y="SS WC (GBP)", color="ABC Class",
            color_discrete_map=ABC_COLORS,
            markers=True,
            labels={"Service Level": "Target CSL (%)", "SS WC (GBP)": "Total SS Working Capital (GBP)"},
            title="Service Level vs Safety Stock Working Capital",
        )
        fig_t.update_layout(height=420)
        st.plotly_chart(fig_t, use_container_width=True)

    with tab_table:
        st.dataframe(
            p2.style.background_gradient(subset=["ss_delta_chf"], cmap="RdYlGn"),
            use_container_width=True, height=500,
        )
        st.download_button("Download CSV", p2.to_csv(index=False),
                           "02_safety_stock.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: REORDER POINT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "3️⃣  Reorder Point":
    st.title("Project 3 — Reorder Point Classification Engine")
    st.caption("When should we replenish inventory?")

    p3 = apply_filter(load_table("03_reorder_point_results.csv"))
    if p3 is None:
        st.warning("Run notebook 03 first."); st.stop()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("SKU-Locations",         len(p3))
    k2.metric("ROP Too Low",           (p3["rop_status"].str.contains("Too low")).sum())
    k3.metric("ROP Too High",          (p3["rop_status"].str.contains("Too high")).sum())
    k4.metric("Avg Stock Cover",       f"{p3['stock_cover_weeks'].mean():.1f} wks")
    k5.metric("Avg Stockout Rate",     pct(p3["stockout_rate"].mean()))

    st.divider()
    tab_charts, tab_policy, tab_table = st.tabs(["Charts", "Policy Matrix", "Results Table"])

    with tab_charts:
        c1, c2 = st.columns(2)

        with c1:
            rop_status_colors = {
                "Too low \u2014 replenish earlier": C["red"],
                "Too high \u2014 replenish later":  C["blue"],
                "On target":                        C["green"],
            }
            # Normalise status strings (strip special chars for matching)
            p3["rop_color"] = p3["rop_status"].apply(
                lambda x: C["red"] if "low" in x.lower() else (C["blue"] if "high" in x.lower() else C["green"])
            )
            fig = px.scatter(
                p3, x="current_rop", y="rec_rop",
                color="rop_status",
                hover_data=["sku", "location", "abc_class"],
                labels={"current_rop": "Current ROP (units)", "rec_rop": "Recommended ROP (units)"},
                title="Current vs Recommended Reorder Point",
            )
            lim = max(p3[["current_rop", "rec_rop"]].max()) * 1.05
            fig.add_shape(type="line", x0=0, y0=0, x1=lim, y1=lim,
                          line=dict(color="black", dash="dash", width=1))
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Stockout rate by segment
            so = p3.groupby("segment")["stockout_rate"].mean().reset_index()
            so["pct"] = so["stockout_rate"] * 100
            so["color"] = so["pct"].apply(
                lambda x: C["red"] if x > 15 else (C["orange"] if x > 8 else C["green"])
            )
            fig2 = px.bar(
                so, x="pct", y="segment", orientation="h",
                color="pct",
                color_continuous_scale=[[0, C["green"]], [0.5, C["orange"]], [1, C["red"]]],
                labels={"pct": "Stockout Rate (%)", "segment": "Segment"},
                title="Historical Stockout Rate by Segment",
            )
            fig2.update_layout(height=380, coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Stock cover vs lead time
        fig3 = px.scatter(
            p3, x="lt_weeks", y="stock_cover_weeks",
            color="abc_class", size="avg_weekly_demand",
            color_discrete_map=ABC_COLORS,
            hover_data=["sku", "location"],
            labels={"lt_weeks": "Lead Time (weeks)", "stock_cover_weeks": "Stock Cover (weeks)"},
            title="Stock Cover vs Lead Time (bubble = weekly demand)",
        )
        lim = p3["lt_weeks"].max() * 1.2
        fig3.add_shape(type="line", x0=0, y0=0, x1=lim, y1=lim,
                       line=dict(color="black", dash="dash", width=1))
        fig3.update_layout(height=420)
        st.plotly_chart(fig3, use_container_width=True)

    with tab_policy:
        st.markdown("### Inventory Policy Matrix")
        policy_summary = (
            p3.groupby("segment")
            .agg(n=("sku","count"),
                 review_policy=("review_policy","first"),
                 avg_rop=("rec_rop","mean"),
                 avg_eoq=("eoq","mean"),
                 avg_max_level=("max_level","mean"),
                 avg_orders_yr=("orders_per_year","mean"),
                 avg_so_rate=("stockout_rate", lambda x: x.mean()*100))
            .round(1)
            .reset_index()
        )
        st.dataframe(policy_summary, use_container_width=True)

        fig_pol = go.Figure()
        segs = policy_summary["segment"].tolist()
        x = list(range(len(segs)))
        fig_pol.add_bar(name="ROP",       x=segs, y=policy_summary["avg_rop"],       marker_color=C["blue"])
        fig_pol.add_bar(name="EOQ",       x=segs, y=policy_summary["avg_eoq"],       marker_color=C["green"])
        fig_pol.add_bar(name="Max Level", x=segs, y=policy_summary["avg_max_level"], marker_color=C["purple"])
        fig_pol.update_layout(
            barmode="group", title="Policy Parameters by Segment (ROP | EOQ | Max Level)",
            xaxis_title="Segment", yaxis_title="Units", height=420,
        )
        st.plotly_chart(fig_pol, use_container_width=True)

    with tab_table:
        st.dataframe(p3, use_container_width=True, height=500)
        st.download_button("Download CSV", p3.to_csv(index=False),
                           "03_reorder_point.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: FILL RATE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "4️⃣  Fill Rate & Service":
    st.title("Project 4 — Fill Rate / Service-Level Simulator")
    st.caption("What service outcome will our current inventory policy actually deliver?")

    p4 = apply_filter(load_table("04_fill_rate_results.csv"))
    if p4 is None:
        st.warning("Run notebook 04 first."); st.stop()

    above = (p4["fr_status"] == "Above target").sum()
    below = (p4["fr_status"] == "Below target").sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("SKU-Locations",   len(p4))
    k2.metric("Avg Fill Rate",   pct(p4["fill_rate_sim"].mean()))
    k3.metric("Avg CSL",         pct(p4["csl_sim"].mean()))
    k4.metric("Above Target",    above, delta=f"+{above}", delta_color="normal")
    k5.metric("Below Target",    below, delta=f"-{below}", delta_color="inverse")

    st.divider()
    tab_charts, tab_gap, tab_table = st.tabs(["Charts", "Service Gap Analysis", "Results Table"])

    with tab_charts:
        c1, c2 = st.columns(2)

        with c1:
            # Analytical vs simulation scatter
            fig = px.scatter(
                p4, x="fill_rate_analytical", y="fill_rate_sim",
                color="abc_class",
                color_discrete_map=ABC_COLORS,
                hover_data=["sku", "location"],
                labels={"fill_rate_analytical": "Analytical Fill Rate",
                        "fill_rate_sim": "Simulated Fill Rate"},
                title="Fill Rate: Analytical vs Monte Carlo",
            )
            fig.add_shape(type="line", x0=0.7, y0=0.7, x1=1, y1=1,
                          line=dict(dash="dash", color="black", width=1))
            fig.update_xaxes(tickformat=".0%")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # CSL by segment
            fig2 = px.box(
                p4, x="segment", y="csl_sim", color="abc_class",
                color_discrete_map=ABC_COLORS,
                labels={"csl_sim": "Simulated CSL", "segment": "Segment"},
                title="CSL Distribution by Segment",
            )
            fig2.add_hline(y=0.95, line_dash="dash", line_color=C["red"],
                           annotation_text="95%")
            fig2.add_hline(y=0.90, line_dash="dash", line_color=C["orange"],
                           annotation_text="90%")
            fig2.update_yaxes(tickformat=".0%")
            fig2.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Fill rate vs target per ABC
        abc_service = p4.groupby("abc_class").agg(
            fill_rate=("fill_rate_sim","mean"),
            target=("service_target","mean"),
            csl=("csl_sim","mean"),
        ).reset_index()

        fig3 = go.Figure()
        for _, row in abc_service.iterrows():
            col = ABC_COLORS.get(row["abc_class"], C["dark"])
            fig3.add_trace(go.Bar(
                name=f"Class {row['abc_class']} — Fill Rate",
                x=[row["abc_class"]], y=[row["fill_rate"]],
                marker_color=col, opacity=0.85,
            ))
        for _, row in abc_service.iterrows():
            fig3.add_shape(
                type="line",
                x0=row["abc_class"], x1=row["abc_class"],
                y0=0, y1=row["target"],
                line=dict(color="black", width=3, dash="dot"),
            )
        fig3.update_yaxes(tickformat=".0%", title="Fill Rate")
        fig3.update_layout(
            title="Simulated Fill Rate by ABC Class (dotted line = target)",
            height=340, showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with tab_gap:
        st.markdown("### Service Gap by SKU-Location")
        p4["gap_pct"] = p4["fr_gap"] * 100
        p4_sorted = p4.sort_values("gap_pct")

        fig_gap = px.bar(
            p4_sorted, x="gap_pct", y=p4_sorted.index,
            color="fr_status",
            color_discrete_map={"Above target": C["green"], "Below target": C["red"]},
            orientation="h",
            labels={"gap_pct": "Fill Rate Gap (pp)", "y": "SKU-Location"},
            title="Fill Rate Gap vs Target per SKU-Location",
            hover_data=["sku", "location", "abc_class", "fill_rate_sim", "service_target"],
        )
        fig_gap.add_vline(x=0, line_color="black", line_width=1)
        fig_gap.update_layout(height=max(400, len(p4) * 12), showlegend=True)
        st.plotly_chart(fig_gap, use_container_width=True)

        st.markdown("**SKUs below target — action required:**")
        below_df = p4[p4["fr_status"] == "Below target"][
            ["sku","location","abc_class","service_target","fill_rate_sim","fr_gap","recommendation"]
        ].sort_values("fr_gap")
        if len(below_df) > 0:
            st.dataframe(below_df.style.background_gradient(subset=["fr_gap"], cmap="RdYlGn"),
                         use_container_width=True)
        else:
            st.success("All SKU-locations are at or above their service target.")

    with tab_table:
        st.dataframe(p4, use_container_width=True, height=500)
        st.download_button("Download CSV", p4.to_csv(index=False),
                           "04_fill_rate.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5: MONETIZATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "5️⃣  Shortage & Excess Cost":
    st.title("Project 5 — Shortage vs Excess Monetization Engine")
    st.caption("What is the expected financial impact of shortage versus excess inventory?")

    p5 = apply_filter(load_table("05_monetization_results.csv"))
    if p5 is None:
        st.warning("Run notebook 05 first."); st.stop()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Expected Loss",    kchf(p5["total_expected_loss"].sum()))
    k2.metric("Shortage Cost",          kchf(p5["exp_shortage_cost"].sum()))
    k3.metric("Excess Cost",            kchf(p5["exp_excess_cost"].sum()))
    k4.metric("Shortage-Dominated SKUs",(p5["risk_type"] == "Shortage-dominated").sum())
    k5.metric("Excess-Dominated SKUs",  (p5["risk_type"] == "Excess-dominated").sum())

    st.divider()
    tab_risk, tab_pareto, tab_table = st.tabs(["Risk Map", "Pareto Ranking", "Results Table"])

    with tab_risk:
        c1, c2 = st.columns(2)

        with c1:
            fig = px.scatter(
                p5,
                x="exp_shortage_cost", y="exp_excess_cost",
                color="risk_type",
                color_discrete_map=RISK_COLORS,
                size=np.clip(p5["annual_demand"] / p5["annual_demand"].max() * 60, 5, 60),
                hover_data=["sku", "location", "abc_class", "total_expected_loss"],
                labels={
                    "exp_shortage_cost": "Expected Shortage Cost (GBP)",
                    "exp_excess_cost":   "Expected Excess Cost (GBP)",
                },
                title="Shortage vs Excess Cost per SKU-Location",
            )
            max_val = max(p5["exp_shortage_cost"].max(), p5["exp_excess_cost"].max())
            fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                          line=dict(dash="dash", color="black", width=1))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Stacked by ABC
            loss_abc = p5.groupby("abc_class")[["exp_shortage_cost","exp_excess_cost"]].sum().reset_index()
            loss_abc = loss_abc.melt(id_vars="abc_class", var_name="type", value_name="cost")
            loss_abc["type"] = loss_abc["type"].map({
                "exp_shortage_cost": "Shortage",
                "exp_excess_cost":   "Excess",
            })
            fig2 = px.bar(
                loss_abc, x="abc_class", y="cost", color="type", barmode="stack",
                color_discrete_map={"Shortage": C["red"], "Excess": C["blue"]},
                labels={"cost": "Expected Cost (GBP)", "abc_class": "ABC Class"},
                title="Expected Loss by ABC Class",
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

        # Recommendations table
        st.markdown("**Action priorities:**")
        action_counts = p5["recommendation"].value_counts().reset_index()
        action_counts.columns = ["Recommendation", "Count"]
        for _, row in action_counts.iterrows():
            flag = "🔴" if "urgently" in row["Recommendation"] or "shortage" in row["Recommendation"].lower() else "🔵"
            st.markdown(f"{flag} **{row['Count']} SKUs** — {row['Recommendation']}")

    with tab_pareto:
        ranked = p5.sort_values("total_expected_loss", ascending=False).reset_index(drop=True)
        ranked["cum_pct"] = ranked["total_expected_loss"].cumsum() / ranked["total_expected_loss"].sum() * 100
        n80 = (ranked["cum_pct"] <= 80).sum()

        fig_p = make_subplots(specs=[[{"secondary_y": True}]])
        fig_p.add_trace(go.Bar(
            x=list(range(len(ranked))),
            y=ranked["total_expected_loss"],
            marker_color=ranked["risk_type"].map(RISK_COLORS),
            name="Expected Loss",
        ), secondary_y=False)
        fig_p.add_trace(go.Scatter(
            x=list(range(len(ranked))),
            y=ranked["cum_pct"],
            mode="lines", name="Cumulative %",
            line=dict(color="black", width=2),
        ), secondary_y=True)
        fig_p.add_hline(y=80, secondary_y=True, line_dash="dot", line_color="gray")
        fig_p.update_layout(
            title=f"Pareto: {n80} SKU-locations = 80% of total expected loss",
            height=420, xaxis_title="SKU-Location (ranked)",
        )
        fig_p.update_yaxes(title_text="Expected Loss (GBP)", secondary_y=False)
        fig_p.update_yaxes(title_text="Cumulative (%)", secondary_y=True)
        st.plotly_chart(fig_p, use_container_width=True)

        st.info(f"**Focus on {n80} SKU-locations** to address 80% of total expected financial loss.")

        st.dataframe(
            ranked[["sku","location","abc_class","risk_type",
                    "exp_shortage_cost","exp_excess_cost","total_expected_loss","recommendation"]]
            .head(20),
            use_container_width=True,
        )

    with tab_table:
        st.dataframe(
            p5.style.background_gradient(subset=["total_expected_loss"], cmap="YlOrRd"),
            use_container_width=True, height=500,
        )
        st.download_button("Download CSV", p5.to_csv(index=False),
                           "05_monetization.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6: ROI COMPARATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "6️⃣  ROI Comparator":
    st.title("Project 6 — ROI Comparator")
    st.caption("Which uncertainty-reduction lever gives the highest return on investment?")

    p6 = load_table("06_roi_results.csv")
    if p6 is None:
        st.warning("Run notebook 06 first."); st.stop()

    # Top lever callout
    top = p6.iloc[0]
    verdict_color = C["green"] if "now" in str(top.get("Verdict","")) else C["orange"]
    st.markdown(
        f"""<div style='background:{verdict_color}22;border:1.5px solid {verdict_color};
        border-radius:8px;padding:16px 20px;margin-bottom:16px;'>
        <span style='font-size:18px;font-weight:700;'>#{int(top['Rank'])} Best lever: {top['Lever']}</span><br>
        ROI <b>{top['ROI']:.1f}x</b> &nbsp;·&nbsp;
        Payback <b>{top['Payback (years)']:.2f} years</b> &nbsp;·&nbsp;
        Annual saving <b>GBP {top['Annual Saving (KCHF)']*1000:,.0f}</b> &nbsp;·&nbsp;
        Implementation cost <b>GBP {top['Impl Cost (KCHF)']*1000:,.0f}</b>
        </div>""",
        unsafe_allow_html=True,
    )

    tab_charts, tab_sensitivity, tab_table = st.tabs(["Dashboard", "Sensitivity", "Full Results"])

    with tab_charts:
        lever_colors = [C["green"], C["blue"], C["orange"], C["purple"]]

        c1, c2 = st.columns(2)

        with c1:
            fig_roi = px.bar(
                p6, x="Lever", y="ROI",
                color="Lever",
                color_discrete_sequence=lever_colors,
                labels={"ROI": "ROI (x)", "Lever": ""},
                title="Return on Investment by Lever",
                text="ROI",
            )
            fig_roi.update_traces(texttemplate="%{text:.1f}x", textposition="outside")
            fig_roi.add_hline(y=1, line_dash="dot", line_color="gray",
                              annotation_text="Break even")
            fig_roi.update_layout(height=380, showlegend=False,
                                  xaxis=dict(tickangle=-15))
            st.plotly_chart(fig_roi, use_container_width=True)

        with c2:
            fig_pb = px.bar(
                p6, x="Lever", y="Payback (years)",
                color="Lever",
                color_discrete_sequence=lever_colors,
                labels={"Payback (years)": "Payback (years)", "Lever": ""},
                title="Payback Period by Lever",
                text="Payback (years)",
            )
            fig_pb.update_traces(texttemplate="%{text:.2f}y", textposition="outside")
            fig_pb.update_layout(height=380, showlegend=False,
                                 xaxis=dict(tickangle=-15))
            st.plotly_chart(fig_pb, use_container_width=True)

        # Annual saving vs impl cost
        fig_cost = go.Figure()
        for i, (_, row) in enumerate(p6.iterrows()):
            col = lever_colors[i % len(lever_colors)]
            fig_cost.add_trace(go.Bar(
                name=row["Lever"], x=["Annual Saving", "Impl Cost"],
                y=[row["Annual Saving (KCHF)"] * 1000, row["Impl Cost (KCHF)"] * 1000],
                marker_color=col,
            ))
        fig_cost.update_layout(
            barmode="group", title="Annual Saving vs Implementation Cost (GBP)",
            height=380, yaxis_title="GBP",
        )
        st.plotly_chart(fig_cost, use_container_width=True)

        # Fill rate improvement
        p4 = load_table("04_fill_rate_results.csv")
        baseline_fr = p4["fill_rate_sim"].mean() * 100 if p4 is not None else None

        fig_fr = px.bar(
            p6, x="Lever", y="New Fill Rate (avg %)",
            color="Lever",
            color_discrete_sequence=lever_colors,
            labels={"New Fill Rate (avg %)": "Projected Fill Rate (%)", "Lever": ""},
            title="Projected Avg Fill Rate by Lever",
            text="New Fill Rate (avg %)",
        )
        fig_fr.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        if baseline_fr:
            fig_fr.add_hline(y=baseline_fr, line_dash="dash", line_color="gray",
                             annotation_text=f"Baseline {baseline_fr:.1f}%")
        fig_fr.update_layout(height=380, showlegend=False,
                             xaxis=dict(tickangle=-15))
        st.plotly_chart(fig_fr, use_container_width=True)

    with tab_sensitivity:
        st.markdown("### ROI Sensitivity to Improvement Assumption")

        master_df, _ = load_master()
        from src.inventory import safety_stock_normal
        from src.service import fill_rate_type2

        df_clean = master_df[
            (master_df["promo_flag"] == 0) &
            (master_df["abc_class"].isin(sel_abc)) &
            (master_df["location"].isin(sel_locs))
        ]
        base_stats = (
            df_clean.groupby(["sku","location"])
            .agg(avg_d=("actual_demand","mean"), std_d=("actual_demand","std"),
                 lt_mean=("lead_time_mean","first"), lt_std=("lead_time_std","first"),
                 unit_cost=("unit_cost","first"), service_target=("service_target","first"))
            .reset_index()
        )

        p3t = load_table("03_reorder_point_results.csv")
        if p3t is not None:
            base_stats = base_stats.merge(p3t[["sku","location","eoq"]], on=["sku","location"], how="left")
            base_stats["eoq"] = base_stats["eoq"].fillna(100)
        else:
            base_stats["eoq"] = 100

        p5t = load_table("05_monetization_results.csv")
        baseline_loss = p5t["total_expected_loss"].sum() if p5t is not None else 0

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fc_impl = st.slider("Forecast tool cost (GBP)", 50_000, 500_000, 200_000, 10_000)
        with col_s2:
            lt_impl = st.slider("Lead-time renegotiation cost (GBP)", 10_000, 200_000, 50_000, 5_000)

        fc_reductions = np.linspace(0.05, 0.40, 15)
        lt_reductions = np.linspace(0.10, 0.55, 15)

        rows_fc, rows_lt = [], []
        for red in fc_reductions:
            new_ss_total, new_loss = 0, 0
            for _, r in base_stats.iterrows():
                std_new = r["std_d"] * (1 - red)
                lt = r["lt_mean"] / 7; lt_s = r["lt_std"] / 7
                ss  = safety_stock_normal(std_new, lt, lt_s, r["avg_d"], r["service_target"])
                sig = np.sqrt(lt * std_new**2 + r["avg_d"]**2 * lt_s**2)
                fr  = fill_rate_type2(ss, sig, r["eoq"])
                new_ss_total += ss * r["unit_cost"]
                new_loss     += (1 - fr) * r["avg_d"] * 52 * r["unit_cost"] * 0.1
            sav = (baseline_loss - new_loss)
            rows_fc.append({"Reduction (%)": red * 100, "ROI": sav / fc_impl if fc_impl > 0 else 0})

        for red in lt_reductions:
            new_ss_total, new_loss = 0, 0
            for _, r in base_stats.iterrows():
                lt = r["lt_mean"] / 7 * (1 - red); lt_s = r["lt_std"] / 7 * (1 - red)
                ss  = safety_stock_normal(r["std_d"], lt, lt_s, r["avg_d"], r["service_target"])
                sig = np.sqrt(lt * r["std_d"]**2 + r["avg_d"]**2 * lt_s**2)
                fr  = fill_rate_type2(ss, sig, r["eoq"])
                new_ss_total += ss * r["unit_cost"]
                new_loss     += (1 - fr) * r["avg_d"] * 52 * r["unit_cost"] * 0.1
            sav = (baseline_loss - new_loss)
            rows_lt.append({"Reduction (%)": red * 100, "ROI": sav / lt_impl if lt_impl > 0 else 0})

        sens_fig = go.Figure()
        sens_fig.add_trace(go.Scatter(
            x=[r["Reduction (%)"] for r in rows_fc],
            y=[r["ROI"] for r in rows_fc],
            name="Forecast improvement", mode="lines+markers",
            line=dict(color=C["purple"]),
        ))
        sens_fig.add_trace(go.Scatter(
            x=[r["Reduction (%)"] for r in rows_lt],
            y=[r["ROI"] for r in rows_lt],
            name="Lead-time reduction", mode="lines+markers",
            line=dict(color=C["orange"]),
        ))
        sens_fig.add_hline(y=1, line_dash="dot", line_color="gray",
                           annotation_text="Break even (ROI = 1x)")
        sens_fig.update_layout(
            title="ROI Sensitivity: How much improvement is needed to justify the cost?",
            xaxis_title="Improvement (%)", yaxis_title="ROI (x)", height=420,
        )
        st.plotly_chart(sens_fig, use_container_width=True)

    with tab_table:
        st.dataframe(p6, use_container_width=True)
        st.download_button("Download CSV", p6.to_csv(index=False),
                           "06_roi.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DATA EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Data Explorer":
    st.title("Data Explorer")
    st.caption("Explore the underlying master dataset.")

    master_df, source = load_master()
    df_filt = master_df[
        (master_df["abc_class"].isin(sel_abc)) &
        (master_df["location"].isin(sel_locs))
    ]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Rows",      f"{len(df_filt):,}")
    k2.metric("SKUs",      df_filt["sku"].nunique())
    k3.metric("Locations", df_filt["location"].nunique())
    k4.metric("Weeks",     df_filt["date"].nunique())

    st.divider()

    sel_sku = st.selectbox("Select SKU for demand chart", sorted(df_filt["sku"].unique()))
    sku_df  = df_filt[df_filt["sku"] == sel_sku].sort_values("date")

    fig_ts = go.Figure()
    for loc in sku_df["location"].unique():
        sub = sku_df[sku_df["location"] == loc]
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["actual_demand"],
            name=f"{loc} — Actual", mode="lines",
        ))
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["forecast"],
            name=f"{loc} — Forecast", mode="lines",
            line=dict(dash="dash"),
        ))
    fig_ts.update_layout(
        title=f"Demand vs Forecast: {sel_sku}",
        xaxis_title="Week", yaxis_title="Units",
        height=400,
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    # ABC/XYZ heatmap
    st.subheader("ABC / XYZ Segment Map")
    seg_count = (
        df_filt.drop_duplicates(["sku","location"])
        .groupby(["abc_class","xyz_class"])
        .size()
        .reset_index(name="count")
    )
    if len(seg_count) > 0:
        pivot = seg_count.pivot(index="abc_class", columns="xyz_class", values="count").fillna(0)
        fig_hm = px.imshow(
            pivot, text_auto=True,
            color_continuous_scale="Blues",
            labels={"color": "SKU count"},
            title="SKU Count by ABC / XYZ Segment",
        )
        fig_hm.update_layout(height=300)
        st.plotly_chart(fig_hm, use_container_width=True)

    # Raw table
    st.subheader("Raw Data")
    st.dataframe(df_filt.head(500), use_container_width=True, height=400)
    st.download_button(
        "Download Filtered Data",
        df_filt.to_csv(index=False),
        "master_data_filtered.csv", "text/csv",
    )
