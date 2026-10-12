"""
Simulated Pension Scheme - Open-Group Projection Model
=======================================================

A simple open-group projection of membership, contributions, benefit outgo,
assets and funding indicators for a SIMULATED pension scheme.

IMPORTANT: Every assumption below is illustrative. This is a learning/portfolio
project and does NOT use real data from NAPSA or any other institution.

"Open group" means new entrants join each year, so the scheme is projected as
an ongoing concern rather than only for today's members.

How to run:
    pip install -r requirements.txt
    python model.py

Outputs (written to the ./output folder):
    projection_base.csv          year-by-year results for the base case
    scenario_summary.csv         key indicators for every scenario
    chart_*.png                  charts used in the README / presentation
"""

from copy import deepcopy
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ----------------------------------------------------------------------------
# 1. ASSUMPTIONS (illustrative - NOT real scheme data)
# ----------------------------------------------------------------------------
BASE_ASSUMPTIONS = {
    "start_year": 2026,
    "projection_years": 30,

    # Membership
    "initial_active_members": 100_000,
    "initial_pensioners": 10_000,
    "new_entrants_per_year": 6_000,
    "annual_exit_rate_active": 0.03,      # withdrawals and deaths before retirement
    "annual_retirement_rate": 0.02,       # actives moving onto pension
    "annual_pensioner_mortality": 0.04,   # pensioners dying each year

    # Money (Kwacha)
    "avg_annual_earnings": 60_000,
    "earnings_growth": 0.07,
    "contribution_rate": 0.10,            # share of earnings paid in
    "avg_annual_pension": 18_000,
    "pension_increase": 0.05,
    "admin_expense_ratio": 0.02,          # share of contribution income

    # Assets
    "initial_assets": 5_000_000_000,
    "investment_return": 0.09,
}


# ----------------------------------------------------------------------------
# 2. THE PROJECTION ENGINE
# ----------------------------------------------------------------------------
def project(a: dict) -> pd.DataFrame:
    """Run the open-group projection for one set of assumptions.

    Returns one row per year with membership, cash flows, assets and indicators.
    """
    rows = []

    actives = a["initial_active_members"]
    pensioners = a["initial_pensioners"]
    assets = a["initial_assets"]
    earnings = a["avg_annual_earnings"]
    pension = a["avg_annual_pension"]

    for t in range(a["projection_years"]):
        year = a["start_year"] + t

        # --- Step 2: membership movements -----------------------------------
        new_entrants = a["new_entrants_per_year"]
        exits = actives * a["annual_exit_rate_active"]
        retirements = actives * a["annual_retirement_rate"]
        deaths = pensioners * a["annual_pensioner_mortality"]

        actives_end = actives + new_entrants - exits - retirements
        pensioners_end = pensioners + retirements - deaths

        # Use the average headcount over the year for money flows
        avg_actives = (actives + actives_end) / 2
        avg_pensioners = (pensioners + pensioners_end) / 2

        # --- Step 3: cash flows ---------------------------------------------
        contributions = avg_actives * earnings * a["contribution_rate"]
        benefits = avg_pensioners * pension
        expenses = contributions * a["admin_expense_ratio"]
        net_cash_flow = contributions - benefits - expenses

        # Investment income: full-year return on opening assets, half-year
        # return on net cash flow (assumes cash arrives evenly through the year)
        investment_income = (
            assets * a["investment_return"]
            + net_cash_flow * a["investment_return"] / 2
        )
        assets_end = assets + net_cash_flow + investment_income

        # --- Step 4: indicators ---------------------------------------------
        support_ratio = avg_actives / avg_pensioners if avg_pensioners else float("nan")
        benefit_cost_pct = benefits / contributions if contributions else float("nan")
        reserve_ratio = assets_end / benefits if benefits else float("nan")

        rows.append({
            "year": year,
            "active_members_start": actives,
            "new_entrants": new_entrants,
            "exits": exits,
            "retirements": retirements,
            "pensioner_deaths": deaths,
            "active_members_end": actives_end,
            "pensioners_end": pensioners_end,
            "contributions": contributions,
            "benefits": benefits,
            "expenses": expenses,
            "net_cash_flow": net_cash_flow,
            "investment_income": investment_income,
            "assets_end": assets_end,
            "support_ratio": support_ratio,
            "benefit_cost_pct_of_contributions": benefit_cost_pct,
            "reserve_ratio_years": reserve_ratio,
        })

        # Roll forward to next year
        actives, pensioners, assets = actives_end, pensioners_end, assets_end
        earnings *= 1 + a["earnings_growth"]
        pension *= 1 + a["pension_increase"]

        # If assets run out, flag it and stop meaningful projection
        if assets < 0:
            assets = 0.0  # keep the model running, but the shortfall is visible
            rows[-1]["assets_end"] = 0.0
            rows[-1]["reserve_ratio_years"] = 0.0

    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# 3. SCENARIOS (Step 5)
# ----------------------------------------------------------------------------
def build_scenarios() -> dict:
    """Return named assumption sets: the base case plus stress tests."""
    base = deepcopy(BASE_ASSUMPTIONS)

    low_returns = deepcopy(base)
    low_returns["investment_return"] = 0.06

    high_pension_increase = deepcopy(base)
    high_pension_increase["pension_increase"] = 0.08

    low_entrants = deepcopy(base)
    low_entrants["new_entrants_per_year"] = 3_000

    combined_stress = deepcopy(base)
    combined_stress["investment_return"] = 0.06
    combined_stress["pension_increase"] = 0.08
    combined_stress["new_entrants_per_year"] = 3_000

    return {
        "Base case": base,
        "Low investment returns (6%)": low_returns,
        "High pension increases (8%)": high_pension_increase,
        "Low new entrants (3,000/yr)": low_entrants,
        "Combined stress": combined_stress,
    }


def summarise(name: str, df: pd.DataFrame) -> dict:
    """Pull the headline numbers from one scenario's projection."""
    depleted = df[df["assets_end"] <= 0]
    first_year_negative_cf = df[df["net_cash_flow"] < 0]
    last = df.iloc[-1]
    return {
        "scenario": name,
        "first_year_negative_cash_flow":
            int(first_year_negative_cf["year"].iloc[0]) if len(first_year_negative_cf) else None,
        "assets_exhausted_year":
            int(depleted["year"].iloc[0]) if len(depleted) else None,
        "final_year": int(last["year"]),
        "final_assets_bn": round(last["assets_end"] / 1e9, 2),
        "final_support_ratio": round(last["support_ratio"], 2),
        "final_benefit_cost_pct": round(last["benefit_cost_pct_of_contributions"] * 100, 1),
        "final_reserve_ratio_years": round(last["reserve_ratio_years"], 1),
    }


# ----------------------------------------------------------------------------
# 4. CHARTS
# ----------------------------------------------------------------------------
def make_charts(results: dict, out: Path) -> None:
    base = results["Base case"]

    # Chart 1: membership
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(base["year"], base["active_members_end"], label="Active members")
    ax.plot(base["year"], base["pensioners_end"], label="Pensioners")
    ax.set_title("Projected membership (base case)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of members")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "chart_membership.png", dpi=150)
    plt.close(fig)

    # Chart 2: contributions vs benefits
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(base["year"], base["contributions"] / 1e9, label="Contributions")
    ax.plot(base["year"], base["benefits"] / 1e9, label="Benefit outgo")
    ax.set_title("Contributions vs benefit outgo (base case)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Kwacha (billions)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "chart_cashflows.png", dpi=150)
    plt.close(fig)

    # Chart 3: assets by scenario
    fig, ax = plt.subplots(figsize=(9, 5))
    for name, df in results.items():
        ax.plot(df["year"], df["assets_end"] / 1e9, label=name)
    ax.set_title("Projected assets by scenario")
    ax.set_xlabel("Year")
    ax.set_ylabel("Kwacha (billions)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "chart_assets_scenarios.png", dpi=150)
    plt.close(fig)

    # Chart 4: support ratio and benefit cost
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(base["year"], base["support_ratio"], color="tab:blue", label="Support ratio")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Actives per pensioner", color="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(base["year"], base["benefit_cost_pct_of_contributions"] * 100,
             color="tab:red", label="Benefit cost % of contributions")
    ax2.set_ylabel("Benefits as % of contributions", color="tab:red")
    ax1.set_title("Key funding indicators (base case)")
    ax1.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "chart_indicators.png", dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------
# 5. MAIN
# ----------------------------------------------------------------------------
def main() -> None:
    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    scenarios = build_scenarios()
    results = {name: project(a) for name, a in scenarios.items()}

    results["Base case"].round(2).to_csv(out / "projection_base.csv", index=False)

    summary = pd.DataFrame([summarise(n, df) for n, df in results.items()])
    summary.to_csv(out / "scenario_summary.csv", index=False)

    make_charts(results, out)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print("\nScenario summary")
    print("-" * 60)
    print(summary.to_string(index=False))
    print(f"\nFiles written to: {out}")


if __name__ == "__main__":
    main()
