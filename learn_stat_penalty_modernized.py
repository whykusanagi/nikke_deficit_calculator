#!/usr/bin/env python3
"""
Modernized version of the stat penalty learning script.

This script fits various models to CP deficit and stat penalty data
to find the best formula for calculating stat penalties.

Original Colab: https://colab.research.google.com/drive/1qvhNv0H_qlpi7B8wGi6t0C6OyijGn95f
"""

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from pathlib import Path
from typing import Tuple, Optional, Callable, Dict
import json


def linear_func(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Linear model: y = a * x + b"""
    return a * x + b


def exponential_func(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Exponential model: y = a * b^x"""
    return a * np.power(b, x)


def power_law_func(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Power law model: y = a * x^b"""
    return a * np.power(np.maximum(x, 1e-10), b)  # Avoid division by zero


def logistic_func(x: np.ndarray, L: float, k: float, x0: float) -> np.ndarray:
    """Logistic model: y = L / (1 + exp(-k * (x - x0)))"""
    return L / (1 + np.exp(-k * (x - x0)))


def polynomial_2_func(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Quadratic polynomial: y = a*x^2 + b*x + c"""
    return a * x**2 + b * x + c


def learn_stat_penalty_formula(
    data_frame: pd.DataFrame,
    models: Optional[Dict[str, Callable]] = None
) -> Tuple[Optional[str], Optional[Callable], Optional[np.ndarray], Dict]:
    """
    Learn the formula for calculating stat_penalty based on cp_def.

    Args:
        data_frame: DataFrame with columns 'cp_def' and 'stat_penalty'
        models: Optional dict of model names to functions. If None, uses default models.

    Returns:
        Tuple of (best_model_name, best_model_func, best_coeffs, results_dict)
    """
    if models is None:
        models = {
            "Linear": (linear_func, (1.0, 0.0)),
            "Exponential": (exponential_func, (1.0, 2.0)),
            "Power Law": (power_law_func, (1.0, 1.0)),
            "Logistic": (logistic_func, (1.0, 10.0, 0.5)),
            "Polynomial (2nd)": (polynomial_2_func, (1.0, 1.0, 0.0)),
        }

    # Separate data for fitting
    x = data_frame["cp_def"].to_numpy()
    y = data_frame["stat_penalty"].to_numpy()

    # Validate data
    if len(x) == 0 or len(y) == 0:
        print("Error: Empty data")
        return None, None, None, {}

    if len(x) != len(y):
        print("Error: Mismatched data lengths")
        return None, None, None, {}

    # Try fitting different formulas
    results = {}
    best_model_name = None
    best_residuals = float("inf")
    best_coeffs = None
    best_model_func = None

    for model_name, (model_func, initial_params) in models.items():
        try:
            # Fit the model
            popt, pcov = curve_fit(
                model_func,
                x,
                y,
                p0=initial_params,
                maxfev=10000,
                bounds=(-np.inf, np.inf)
            )

            # Calculate residuals and R²
            y_pred = model_func(x, *popt)
            residuals = np.sum((y - y_pred) ** 2)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            # Calculate RMSE
            rmse = np.sqrt(np.mean((y - y_pred) ** 2))

            results[model_name] = {
                "coefficients": popt.tolist(),
                "residuals": float(residuals),
                "r_squared": float(r_squared),
                "rmse": float(rmse),
            }

            # Update best model if current has lower residuals
            if residuals < best_residuals:
                best_model_name = model_name
                best_residuals = residuals
                best_coeffs = popt
                best_model_func = model_func

        except (RuntimeError, ValueError) as e:
            print(f"Error fitting {model_name} model: {e}")
            results[model_name] = {"error": str(e)}

    # Return the best fitted formula and coefficients
    if best_model_name:
        return best_model_name, best_model_func, best_coeffs, results
    else:
        print("Failed to find a suitable fit for the data.")
        return None, None, None, results


def main():
    """Main function to run the fitting."""
    print("=" * 70)
    print("NIKKE Stat Penalty Formula Learning (Modernized)")
    print("=" * 70)
    print()

    # Find data file
    data_dir = Path(__file__).parent / "data"
    data_file = data_dir / "stat_penalty_data.csv"

    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        print("Data file should be included in the repository")
        return

    # Load data
    print(f"Loading data from: {data_file}")
    data_frame = pd.read_csv(data_file)
    print(f"Loaded {len(data_frame)} data points")
    print()

    # Validate columns
    if "cp_def" not in data_frame.columns or "stat_penalty" not in data_frame.columns:
        print("Error: Data must have 'cp_def' and 'stat_penalty' columns")
        return

    # Show data summary
    print("Data Summary:")
    print(f"  CP Deficit range: {data_frame['cp_def'].min():.4f} - {data_frame['cp_def'].max():.4f}")
    print(f"  Stat Penalty range: {data_frame['stat_penalty'].min():.4f} - {data_frame['stat_penalty'].max():.4f}")
    print()

    # Learn formula
    print("Fitting models...")
    print()
    formula_name, formula, coefficients, results = learn_stat_penalty_formula(data_frame)

    if formula_name:
        print("=" * 70)
        print(f"Best Fit Model: {formula_name}")
        print("=" * 70)
        print()
        print(f"Coefficients: {coefficients}")
        print()
        print(f"Model Performance:")
        best_result = results[formula_name]
        print(f"  R² Score: {best_result['r_squared']:.6f}")
        print(f"  RMSE: {best_result['rmse']:.6f}")
        print(f"  Residuals: {best_result['residuals']:.6f}")
        print()

        # Print JavaScript code
        if formula_name == "Power Law":
            a, b = coefficients
            print("JavaScript Implementation:")
            print("=" * 70)
            print(f"// Formula: penalty = a * deficit^b")
            print(f"const a = {a:.15f};")
            print(f"const b = {b:.15f};")
            print()
            print("function calculateStatPenalty(cpDeficit) {")
            print("  const nonNegativeDeficit = Math.max(0, Math.min(1, cpDeficit));")
            print(f"  return {a:.15f} * Math.pow(nonNegativeDeficit, {b:.15f});")
            print("}")
            print()
        elif formula_name == "Logistic":
            L, k, x0 = coefficients
            print("JavaScript Implementation:")
            print("=" * 70)
            print(f"// Formula: penalty = L / (1 + exp(-k * (deficit - x0)))")
            print(f"const L = {L:.15f};")
            print(f"const k = {k:.15f};")
            print(f"const x0 = {x0:.15f};")
            print()
            print("function calculateStatPenalty(cpDeficit) {")
            print("  const nonNegativeDeficit = Math.max(0, Math.min(1, cpDeficit));")
            print(f"  return {L:.15f} / (1 + Math.exp(-{k:.15f} * (nonNegativeDeficit - {x0:.15f})));")
            print("}")
            print()

        # Print all model results
        print("=" * 70)
        print("All Model Results:")
        print("=" * 70)
        for model_name, result in sorted(results.items(), key=lambda x: x[1].get('residuals', float('inf'))):
            if 'error' in result:
                print(f"{model_name}: Error - {result['error']}")
            else:
                print(f"{model_name}:")
                print(f"  R²: {result['r_squared']:.6f}")
                print(f"  RMSE: {result['rmse']:.6f}")
                print(f"  Coefficients: {result['coefficients']}")
                print()

        # Save results
        results_file = data_dir / "model_fitting_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "best_model": formula_name,
                "coefficients": coefficients.tolist() if coefficients is not None else None,
                "all_results": results,
            }, f, indent=2)
        print(f"✓ Results saved to: {results_file}")
    else:
        print("Failed to fit any model to the data.")


if __name__ == "__main__":
    main()

