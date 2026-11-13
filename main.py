import json
import math
import os
import sys

# Constants as per DESIGN.md
QUANTILE_LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
NORMAL_QUANTILES = [-1.644854, -0.674490, 0.0, 0.674490, 1.644854]

def get_median(data):
    if not data:
        return 0.5
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 1:
        return float(sorted_data[n // 2])
    return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2.0

def get_percentile(data, p):
    # p is a value between 0 and 1
    if not data:
        return 0.5
    sorted_data = sorted(data)
    n = len(sorted_data)
    idx = p * (n - 1)
    lower = int(math.floor(idx))
    upper = int(math.ceil(idx))
    if lower == upper:
        return float(sorted_data[lower])
    # Linear interpolation
    weight = idx - lower
    return float(sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight)

def forecast_market(prices):
    if not prices:
        x, L, S = 0.5, 0.5, 0.01
    else:
        x = prices[-1]
        recent_1440 = prices[-1440:]
        last_360 = prices[-360:]
        L = get_median(last_360)
        
        # Deviations
        deviations = [p - L for p in recent_1440]
        q75 = get_percentile(deviations, 0.75)
        q25 = get_percentile(deviations, 0.25)
        raw_spread = (q75 - q25) / 1.349
        S = max(0.0005, min(0.05, raw_spread))
        
    forecasts = []
    for h in range(1, 241):
        # Median forecast
        mean_reversion_factor = 1 - math.exp(-h / 720.0)
        median_f = x + (L - x) * mean_reversion_factor
        
        # Variance
        variance = (S**2) * (1 - math.exp(-2 * h / 720.0)) + (0.0002**2 * h)
        spread = math.sqrt(variance)
        
        # Quantiles
        row = []
        for z in NORMAL_QUANTILES:
            val = median_f + z * spread
            # Clamp [0, 1]
            val = max(0.0, min(1.0, val))
            row.append(val)
            
        # Rounding 6 decimals (adding 0.0 to avoid negative zero)
        row = [round(v + 0.0, 6) for v in row]
        
        # Non-decreasing
        for i in range(1, 5):
            if row[i] < row[i-1]:
                row[i] = row[i-1]
        
        forecasts.append(row)
        
    return forecasts

def main():
    input_dir = os.environ.get('MAKEFUN_INPUT_DIR', '/input')
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith('.in'):
            continue
            
        with open(os.path.join(input_dir, filename), 'r') as f:
            case = json.load(f)
            
        # Verify quantiles
        if case['quantiles'] != QUANTILE_LEVELS:
            raise ValueError(f"Invalid quantiles: {case['quantiles']}")
            
        output = {"forecasts": []}
        for market in case['markets']:
            forecasts = forecast_market(market['prices'])
            output["forecasts"].append({"id": market['id'], "q": forecasts})
            
        out_filename = filename.replace('.in', '.out')
        with open(os.path.join(output_dir, out_filename), 'w') as f:
            json.dump(output, f)

if __name__ == '__main__':
    main()
