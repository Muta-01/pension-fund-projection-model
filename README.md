# Simulated Pension Scheme: Open-Group Projection Model

A Python model that projects membership, contributions, benefit outgo, assets and
funding indicators for a **simulated** pension scheme over 30 years, with stress-test
scenarios.

> **All assumptions are illustrative.** This project uses invented parameters. It does
> not use real data from NAPSA or any other institution, and its results are not
> forecasts for any real scheme.

## What it does
- **Open-group projection:** new entrants join every year; members move between active,
  pensioner and exit groups.
- **Cash flows:** contributions, benefit outgo, expenses and investment income, giving
  year-end assets.
- **Indicators:** support ratio (actives per pensioner), benefit cost as a % of
  contribution income, and reserve ratio (assets divided by annual benefit outgo).
- **Scenarios:** base case, low investment returns, high pension increases, low new
  entrants, and a combined stress test.

## How to run
```bash
pip install -r requirements.txt
python model.py
```
Results are written to the `output/` folder (CSV files and charts).

## Model structure
Each projection year:
1. Active members = opening + new entrants - exits - retirements
2. Pensioners = opening + retirements - deaths
3. Contributions = average actives x average earnings x contribution rate
4. Benefits = average pensioners x average pension
5. Closing assets = opening assets + net cash flow + investment income

## Key findings (base assumptions as supplied in `model.py`)
Fill this section in with your own words after running the model and looking at the
charts. Suggested points:
- How the support ratio changes as the scheme matures
- When (if ever) net cash flow turns negative in each scenario
- Which assumption the results are most sensitive to, and why that matters for
  funding decisions

## Limitations
- Flat exit, retirement and mortality rates; a fuller model would use age-based rates
  from a life table.
- One average earnings level and one average pension for all members.
- Reserve ratio is used instead of a true funding level, because a funding level needs
  a valuation of accrued liabilities.
- No salary scales, no benefit formulas, no inflation modelling.

## Possible extensions
- Age-structured membership with a life table
- Benefit formula based on salary and service
- Actuarial valuation of liabilities to produce a true funding level
- Interactive dashboard
