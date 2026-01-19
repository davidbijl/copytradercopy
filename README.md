# copytrader
Python copy-trading script to copy Futures positions between Kraken acounts.

## How to use
1. Fork this repository
2. Enable GitHub Actions
3. Add the required secrets
4. (Optional) Adjust the schedule
5. Test via "Run workflow"

## Required secrets
- SOURCE_KRAKEN_FUTURES_KEY
- SOURCE_KRAKEN_FUTURES_SECRET
- YOUR_KRAKEN_FUTURES_KEY
- YOUR_KRAKEN_FUTURES_SECRET

## Scheduling
- Default: every 5 minutes
- Change in `.github/workflows/run.yml`

## Pause / resume
- Disable the workflow in Actions

## Updating from upstream
- Click "Sync fork" in GitHub
