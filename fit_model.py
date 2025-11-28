"""
Model Fitting Script for CP Deficit Calculator

This script fits various models (logistic, power law, polynomial) to CP deficit data
to find the best coefficients for stat penalty calculation.

Usage:
    python fit_model.py [data_file.csv]
    
If no data file is provided, uses sample data. Data file should have columns:
    cp_deficit_percent, stat_penalty_percent
"""

import numpy as np
import pandas as pd
import sys
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Callable, Optional


# Sample data points based on typical NIKKE stat penalty behavior
# Format: (cp_deficit_percent, stat_penalty_percent)
# These are estimates - replace with actual community data if available
SAMPLE_DATA = [
    (0, 0),
    (5, 2.5),
    (10, 5.0),
    (15, 7.5),
    (20, 10.0),
    (25, 12.5),
    (30, 15.0),
    (35, 20.0),
    (40, 25.0),
    (45, 30.0),
    (50, 35.0),
]


def power_law(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Power law model: y = a * x^b"""
    return a * np.power(np.maximum(x, 1e-10), b)  # Avoid division by zero


def logistic(x: np.ndarray, L: float, k: float, x0: float) -> np.ndarray:
    """Logistic model: y = L / (1 + exp(-k * (x - x0)))"""
    return L / (1 + np.exp(-k * (x - x0)))


def polynomial_2(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Quadratic polynomial: y = a*x^2 + b*x + c"""
    return a * x**2 + b * x + c


def polynomial_3(x: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    """Cubic polynomial: y = a*x^3 + b*x^2 + c*x + d"""
    return a * x**3 + b * x**2 + c * x + d


def exponential(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Exponential model: y = a * (1 - exp(-b * x))"""
    return a * (1 - np.exp(-b * x))


def fit_model(
    x_data: np.ndarray,
    y_data: np.ndarray,
    model_func: Callable,
    initial_params: Tuple,
    model_name: str
) -> Dict:
    """
    Fit a model to the data and return results.
    
    Args:
        x_data: Input data (CP deficit as decimal)
        y_data: Output data (stat penalty as decimal)
        model_func: Model function to fit
        initial_params: Initial parameter guesses
        model_name: Name of the model
        
    Returns:
        Dictionary with fit results
    """
    try:
        # Fit the model
        try:
            popt, pcov = curve_fit(
                model_func, 
                x_data, 
                y_data, 
                p0=initial_params, 
                maxfev=10000
            )
        except RuntimeError:
            # Try with bounds for some models
            if len(initial_params) == 2:
                popt, pcov = curve_fit(
                    model_func, 
                    x_data, 
                    y_data, 
                    p0=initial_params, 
                    maxfev=10000,
                    bounds=([0, 0], [np.inf, np.inf])
                )
            else:
                raise
        
        # Calculate predictions
        y_pred = model_func(x_data, *popt)
        
        # Calculate R² score
        ss_res = np.sum((y_data - y_pred) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((y_data - y_pred) ** 2))
        
        # Calculate MAE
        mae = np.mean(np.abs(y_data - y_pred))
        
        return {
            'model_name': model_name,
            'parameters': popt,
            'covariance': pcov,
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'predictions': y_pred
        }
    except Exception as e:
        return {
            'model_name': model_name,
            'error': str(e),
            'r2': -np.inf,
            'rmse': np.inf,
            'mae': np.inf
        }


def load_data(file_path: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load data from file or use sample data.
    
    Args:
        file_path: Path to CSV file with cp_deficit_percent and stat_penalty_percent columns
        
    Returns:
        Tuple of (x_data, y_data) as decimals
    """
    if file_path:
        try:
            df = pd.read_csv(file_path)
            x_data = df['cp_deficit_percent'].values / 100.0
            y_data = df['stat_penalty_percent'].values / 100.0
            print(f"Loaded {len(x_data)} data points from {file_path}")
            return x_data, y_data
        except Exception as e:
            print(f"Error loading data file: {e}")
            print("Using sample data instead...")
    
    # Use sample data
    x_data = np.array([d[0] / 100.0 for d in SAMPLE_DATA])
    y_data = np.array([d[1] / 100.0 for d in SAMPLE_DATA])
    return x_data, y_data


def main():
    """Main fitting routine."""
    # Load data
    data_file = sys.argv[1] if len(sys.argv) > 1 else None
    x_data, y_data = load_data(data_file)
    
    print("="*60)
    print("CP Deficit Calculator - Model Fitting")
    print("="*60)
    print(f"Data points: {len(x_data)}")
    print(f"CP Deficit range: {x_data.min()*100:.1f}% - {x_data.max()*100:.1f}%")
    print(f"Stat Penalty range: {y_data.min()*100:.1f}% - {y_data.max()*100:.1f}%")
    print("\nFitting models...")
    print("-" * 60)
    
    # Current coefficients (for comparison)
    current_a = 10.960042817733095
    current_b = 0.49241207018330935
    
    # Calculate current model performance
    current_pred = power_law(x_data, current_a / 10, current_b)  # Divide by 10 as in calculator
    current_ss_res = np.sum((y_data - current_pred) ** 2)
    current_ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
    current_r2 = 1 - (current_ss_res / current_ss_tot) if current_ss_tot > 0 else 0
    current_rmse = np.sqrt(np.mean((y_data - current_pred) ** 2))
    
    print(f"\nCurrent Power Law Model:")
    print(f"  Parameters: a={current_a}, b={current_b}")
    print(f"  R² Score: {current_r2:.6f}")
    print(f"  RMSE: {current_rmse:.6f}")
    print("-" * 60)
    
    # Fit different models
    models = [
        {
            'func': power_law,
            'params': (current_a / 10, current_b),  # Adjust for formula
            'name': 'Power Law (current)'
        },
        {
            'func': power_law,
            'params': (1.0, 0.5),
            'name': 'Power Law (optimized)'
        },
        {
            'func': logistic,
            'params': (0.5, 20.0, 0.3),
            'name': 'Logistic'
        },
        {
            'func': exponential,
            'params': (0.5, 10.0),
            'name': 'Exponential'
        },
        {
            'func': polynomial_2,
            'params': (0.5, 0.0, 0.0),
            'name': 'Quadratic Polynomial'
        },
        {
            'func': polynomial_3,
            'params': (1.0, 0.0, 0.0, 0.0),
            'name': 'Cubic Polynomial'
        }
    ]
    
    results = []
    for model in models:
        result = fit_model(x_data, y_data, model['func'], model['params'], model['name'])
        results.append(result)
    
    # Sort by R² score (best first)
    results.sort(key=lambda x: x.get('r2', -np.inf), reverse=True)
    
    # Print results
    print("\nModel Comparison (sorted by R² score):")
    print("="*60)
    for i, result in enumerate(results, 1):
        if 'error' in result:
            print(f"{i}. {result['model_name']}: ERROR - {result['error']}")
        else:
            params_str = ', '.join([f"{p:.8f}" for p in result['parameters']])
            print(f"{i}. {result['model_name']}:")
            print(f"   Parameters: {params_str}")
            print(f"   R² Score: {result['r2']:.6f}")
            print(f"   RMSE: {result['rmse']:.6f}")
            print(f"   MAE: {result['mae']:.6f}")
            print()
    
    # Get best model
    best = results[0]
    if 'error' not in best:
        print("="*60)
        print(f"BEST MODEL: {best['model_name']}")
        print("="*60)
        print(f"Parameters: {best['parameters']}")
        print(f"R² Score: {best['r2']:.6f}")
        print(f"RMSE: {best['rmse']:.6f}")
        print(f"MAE: {best['mae']:.6f}")
        
        # Generate JavaScript code for the best model
        print("\n" + "="*60)
        print("JavaScript Code for Calculator:")
        print("="*60)
        
        if best['model_name'].startswith('Power Law'):
            a, b = best['parameters']
            # Adjust a for the /10 in the formula
            a_adjusted = a * 10
            print(f"// Power Law Model")
            print(f"this.coefficients = {{")
            print(f"  a: {a_adjusted},")
            print(f"  b: {b}")
            print(f"}};")
            print(f"\n// Formula: penalty = (a * deficit^b) / 10")
            print(f"// calculateStatPenalty(cpDeficit) {{")
            print(f"//   return (this.coefficients.a * Math.pow(cpDeficit, this.coefficients.b)) / 10;")
            print(f"// }}")
        elif best['model_name'] == 'Logistic':
            L, k, x0 = best['parameters']
            print(f"// Logistic Model")
            print(f"this.coefficients = {{")
            print(f"  L: {L},")
            print(f"  k: {k},")
            print(f"  x0: {x0}")
            print(f"}};")
            print(f"\n// Formula: penalty = L / (1 + exp(-k * (deficit - x0)))")
            print(f"// calculateStatPenalty(cpDeficit) {{")
            print(f"//   return this.coefficients.L / (1 + Math.exp(-this.coefficients.k * (cpDeficit - this.coefficients.x0)));")
            print(f"// }}")
        elif best['model_name'] == 'Exponential':
            a, b = best['parameters']
            print(f"// Exponential Model")
            print(f"this.coefficients = {{")
            print(f"  a: {a},")
            print(f"  b: {b}")
            print(f"}};")
            print(f"\n// Formula: penalty = a * (1 - exp(-b * deficit))")
            print(f"// calculateStatPenalty(cpDeficit) {{")
            print(f"//   return this.coefficients.a * (1 - Math.exp(-this.coefficients.b * cpDeficit));")
            print(f"// }}")
    
    # Plot comparison
    try:
        plt.figure(figsize=(14, 8))
        
        # Plot data points
        plt.scatter(x_data * 100, y_data * 100, label='Data Points', s=150, zorder=5, color='black', marker='o')
        
        # Plot current model
        x_plot = np.linspace(0, x_data.max(), 200)
        y_current = power_law(x_plot, current_a / 10, current_b) * 100
        plt.plot(x_plot * 100, y_current, '--', label=f'Current Power Law (R²={current_r2:.4f})', linewidth=2, alpha=0.7)
        
        # Plot top 3 models
        for result in results[:3]:
            if 'error' not in result:
                if result['model_name'].startswith('Power Law'):
                    y_plot = power_law(x_plot, *result['parameters']) * 100
                elif result['model_name'] == 'Logistic':
                    y_plot = logistic(x_plot, *result['parameters']) * 100
                elif result['model_name'] == 'Exponential':
                    y_plot = exponential(x_plot, *result['parameters']) * 100
                elif 'Quadratic' in result['model_name']:
                    y_plot = polynomial_2(x_plot, *result['parameters']) * 100
                elif 'Cubic' in result['model_name']:
                    y_plot = polynomial_3(x_plot, *result['parameters']) * 100
                else:
                    continue
                
                label = f"{result['model_name']} (R²={result['r2']:.4f})"
                plt.plot(x_plot * 100, y_plot, label=label, linewidth=2)
        
        plt.xlabel('CP Deficit (%)', fontsize=12)
        plt.ylabel('Stat Penalty (%)', fontsize=12)
        plt.title('CP Deficit vs Stat Penalty - Model Comparison', fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xlim(0, x_data.max() * 100)
        plt.ylim(0, max(y_data.max() * 100, 40))
        plt.tight_layout()
        plt.savefig('model_comparison.png', dpi=150, bbox_inches='tight')
        print(f"\n✓ Plot saved to: model_comparison.png")
    except Exception as e:
        print(f"\n⚠ Could not generate plot: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
