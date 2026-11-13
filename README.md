# Nvidia CEO Forecaster

This forecaster estimates the Yes price of markets in Polymarket's "Next CEO of NVIDIA?" event, predicting five quantiles for the next 240 minutes after each checkpoint. The model uses robust statistics (median and interquartile range) on the last 1440 minutes of price history to estimate a stationary spread and median drift, ensuring immunity to price spikes and opening chaos.

## Local Performance (Practice)
These are local practice numbers, not server scores; the final window consists of unseen prices. Measured by running this entry's main.py on the kit's six practice cases and scoring against prices reconstructed from Polymarket's public history:
- Practice pinball loss: 0.293380
- Tune split (p00-p02): 0.407942
- Holdout split (p03-p05): 0.201407
- House baseline (all six cases): 0.363589
- Per case: p00 0.498672, p01 0.303411, p02 0.421744, p03 0.291250, p04 0.190506, p05 0.126208
