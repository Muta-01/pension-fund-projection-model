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
Main finding: The scheme’s long-term position depends far more on how fast pensions rise than on investment returns or membership growth. That’s a good point to raise with the panel, because it ties to funding decisions.
Base case: The scheme stays healthy. Assets reach about K148bn by 2055, benefits take 62.8% of contributions, and the support ratio falls from about 9 actives per pensioner to 2.76.
Low investment returns: Cash flow never turns negative, but assets end at K80bn instead of K148bn. Returns matter a lot for the final asset position, even when the scheme isn’t in trouble.
High pension increases (8%): This is the biggest single risk. Cash flow turns negative in 2043 and benefits reach 142% of contributions by 2055. The scheme survives only because of its large asset cushion.
Low new entrants: Fewer people joining pushes the support ratio down to 2.27 and benefit cost up to 76.6%, with cash flow still positive.
Combined stress: Cash flow turns negative in 2038, benefits reach 173% of contributions, and the reserve ratio drops to 4 years of benefits. Assets aren’t exhausted by 2055, but the model is heading that way, so it would likely run out shortly afterwards.

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
