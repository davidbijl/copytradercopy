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

Add these in: Settings > Secrets and variables > Actions > New repository secret

## Scheduling
- Default: every 10 minutes
- Change in `.github/workflows/run.yml`

## Enable Actions
Enable Actions at repository level:
1. Click the Settings tab
2. In the left sidebar, click Actions > General
3. Under Actions permissions, select: Allow all actions and reusable workflows. Click Save
4. Under Workflow permissions, select: Read repository contents. Click Save
  
Enable Actions for a fork:
- Click the Actions tab
- Click “I understand my workflows, go ahead and enable them”

## To pause / resume
- Disable the workflow in Actions

## To update the script
- Click "Sync fork" in GitHub
