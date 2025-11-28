/**
 * Main script for CP Deficit Calculator
 * Handles UI interactions and calculator initialization
 */

let calculator;

// Initialize calculator when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  calculator = new CPDeficitCalculator();
  
  // Load lookup table for accurate low/high range calculations
  try {
    const response = await fetch('data/stat_penalty_lookup.json');
    if (response.ok) {
      const lookupData = await response.json();
      calculator.loadLookupTable(lookupData);
      console.log('Lookup table loaded successfully');
    } else {
      console.warn('Could not load lookup table, using power law fallback');
    }
  } catch (error) {
    console.warn('Error loading lookup table:', error);
    console.warn('Using power law fallback');
  }

  const stageCpInput = document.getElementById("stage_cp");
  const teamCpInput = document.getElementById("team_cp");
  const cpDeficitDisplay = document.getElementById("cp_deficit_value");
  const statPenaltyDisplay = document.getElementById("stat_penalty_value");
  const errorDisplay = document.getElementById("error");

  // Set default values
  stageCpInput.value = 10000;
  teamCpInput.value = 8000;

  /**
   * Update calculator outputs
   */
  function updateOutputs() {
    try {
      const stageCp = parseFloat(stageCpInput.value);
      const teamCp = parseFloat(teamCpInput.value);

      // Validate inputs
      if (!calculator.validateCP(stageCp) || !calculator.validateCP(teamCp)) {
        throw new Error('Please enter valid positive numbers for both CP values');
      }

      // Calculate results
      const results = calculator.calculate(stageCp, teamCp);

      // Update displays
      cpDeficitDisplay.textContent = results.cpDeficitFormatted;
      statPenaltyDisplay.textContent = results.statPenaltyFormatted;

      // Update color class (corrupted-theme compatible)
      statPenaltyDisplay.className = `result-value stat-penalty-display ${results.colorClass}`;
      statPenaltyDisplay.setAttribute('data-color', results.colorClass);

      // Hide error if calculation succeeded
      if (errorDisplay) {
        errorDisplay.style.display = 'none';
        errorDisplay.textContent = '';
      }
    } catch (error) {
      // Show error message
      if (errorDisplay) {
        errorDisplay.textContent = error.message;
        errorDisplay.style.display = 'block';
      }
      console.error('Calculation error:', error);
    }
  }

  // Add event listeners
  stageCpInput.addEventListener("input", updateOutputs);
  stageCpInput.addEventListener("change", updateOutputs);
  teamCpInput.addEventListener("input", updateOutputs);
  teamCpInput.addEventListener("change", updateOutputs);

  // Initial calculation
  updateOutputs();
});
