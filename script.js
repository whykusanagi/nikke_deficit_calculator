/**
 * Main script for CP Deficit Calculator
 * Handles UI interactions and calculator initialization.
 */

let calculator;

document.addEventListener('DOMContentLoaded', () => {
  const allowedAlgos = ['lookup', 'power_law'];
  const requestedAlgo = new URLSearchParams(location.search).get('algo');
  const algorithm = allowedAlgos.includes(requestedAlgo) ? requestedAlgo : 'lookup';

  calculator = new CPDeficitCalculator({ algorithm });

  const stageCpInput = document.getElementById("stage_cp");
  const teamCpInput = document.getElementById("team_cp");
  const cpDeficitDisplay = document.getElementById("cp_deficit_value");
  const statPenaltyDisplay = document.getElementById("stat_penalty_value");
  const errorDisplay = document.getElementById("error");

  stageCpInput.value = 10000;
  teamCpInput.value = 8000;

  // Render the algorithm badge when running a non-default mode, so a shared
  // ?algo=power_law link is self-identifying in screenshots.
  if (algorithm !== 'lookup' && statPenaltyDisplay && statPenaltyDisplay.parentNode) {
    const badge = document.createElement('span');
    badge.className = 'algo-badge';
    badge.textContent = `algorithm: ${algorithm}`;
    statPenaltyDisplay.parentNode.appendChild(badge);
  }

  function clearResults() {
    cpDeficitDisplay.textContent = '—';
    statPenaltyDisplay.textContent = '—';
    statPenaltyDisplay.className = 'result-value stat-penalty-display';
    statPenaltyDisplay.removeAttribute('data-color');
  }

  function updateOutputs() {
    try {
      const stageCp = parseFloat(stageCpInput.value);
      const teamCp = parseFloat(teamCpInput.value);
      const results = calculator.calculate(stageCp, teamCp);

      cpDeficitDisplay.textContent = results.cpDeficitFormatted;
      statPenaltyDisplay.textContent = results.statPenaltyFormatted;
      statPenaltyDisplay.className = `result-value stat-penalty-display ${results.colorClass}`;
      statPenaltyDisplay.setAttribute('data-color', results.colorClass);

      if (errorDisplay) {
        errorDisplay.style.display = 'none';
        errorDisplay.textContent = '';
      }
    } catch (error) {
      clearResults();
      if (errorDisplay) {
        errorDisplay.textContent = error.message;
        errorDisplay.style.display = 'block';
      }
      console.error('Calculation error:', error);
    }
  }

  stageCpInput.addEventListener("input", updateOutputs);
  teamCpInput.addEventListener("input", updateOutputs);

  updateOutputs();

  // Load lookup table in the background; recompute once it's ready so users
  // get accurate values without waiting on the fetch.
  fetch('data/stat_penalty_lookup.json')
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(lookupData => {
      calculator.loadLookupTable(lookupData);
      updateOutputs();
      console.log('Lookup table loaded successfully');
    })
    .catch(error => {
      console.warn('Could not load lookup table, using power law fallback:', error);
    });
});
