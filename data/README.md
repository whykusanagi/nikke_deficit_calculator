# Dataset Documentation

## Overview

This directory contains the complete dataset used for CP deficit and stat penalty calculations. All data is self-contained in this repository.

## Data Files

### `stat_penalty_data.csv`
- **Format**: CSV with columns `cp_def` (decimal) and `stat_penalty` (decimal)
- **Range**: 0.00 to 0.4991 (0.00% to 49.91% CP deficit)
- **Points**: 501 data points
- **Usage**: Primary dataset for model fitting and analysis

### `cp_deficit_stat_penalty_data.csv`
- **Format**: CSV with columns `cp_deficit_percent` and `stat_penalty_percent`
- **Range**: 0.00% to 49.91% CP deficit
- **Points**: 501 data points
- **Usage**: Human-readable percentage format

### `stat_penalty_lookup.json`
- **Format**: JSON array of objects with `cp_deficit` and `stat_penalty` properties
- **Usage**: Lookup table for piecewise function (low/high ranges)
- **Loaded by**: `calculator.js` via `script.js`

### `piecewise_function_params.json`
- **Format**: JSON with piecewise function parameters
- **Contains**: Thresholds and power law coefficients for main range
- **Usage**: Reference for function parameters

### `model_fitting_results.json`
- **Format**: JSON with model comparison results
- **Contains**: R² scores, RMSE, coefficients for all tested models
- **Usage**: Reference for model selection and accuracy metrics

## Data Structure

### CSV Format
```csv
cp_def,stat_penalty
0.0,0.0
0.0001,0.05
0.0011,0.0551
...
```

### JSON Lookup Format
```json
[
  {"cp_deficit": 0.0, "stat_penalty": 0.0},
  {"cp_deficit": 0.0001, "stat_penalty": 0.05},
  ...
]
```

## Using the Data

### For Model Fitting
```python
import pandas as pd

# Load dataset
df = pd.read_csv('data/stat_penalty_data.csv')

# Use with model fitting scripts
from learn_stat_penalty_modernized import learn_stat_penalty_formula
formula_name, formula, coefficients, results = learn_stat_penalty_formula(df)
```

### For Calculator
The calculator automatically loads `stat_penalty_lookup.json` for piecewise function calculations. The lookup table is loaded asynchronously in `script.js`.

## Rebuilding Models

To rebuild or refine the model using this dataset:

1. **Load the data**:
   ```python
   import pandas as pd
   df = pd.read_csv('data/stat_penalty_data.csv')
   ```

2. **Run model fitting**:
   ```bash
   python3 learn_stat_penalty_modernized.py
   ```

3. **Review results** in `data/model_fitting_results.json`

4. **Update calculator** with new coefficients if needed

## Data Integrity

- All data files are included in the repository
- Dataset is self-contained (no external dependencies)
- Data can be used to rebuild models in the future
- Format is documented and reproducible

## Notes

- The dataset covers the full range of observed CP deficits (0.00% to 49.91%)
- Data points are evenly distributed across the range
- Lookup table provides exact values for low/high ranges
- Power law formula is optimized for the main range (1% - 48%)
