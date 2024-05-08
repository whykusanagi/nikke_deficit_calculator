const stageCpInput = document.getElementById("stage_cp");
const teamCpInput = document.getElementById("team_cp");
const cpDeficitDisplay = document.getElementById("cp_deficit_value");
const statPenaltyDisplay = document.getElementById("stat_penalty_value");

const coefficients = { a: 10.960042817733095, b: 0.49241207018330935 };  // Object for coefficients

function calculateCpDeficit() {
  const stageCp = parseFloat(stageCpInput.value) || 0;
  const teamCp = parseFloat(teamCpInput.value) || 0;
  return Math.max(0, stageCp - teamCp) / stageCp;
}

function calculateStatPenalty(cpDeficit) {
  const nonNegativeCpDeficit = Math.max(0, cpDeficit);
  return coefficients.a * Math.pow(nonNegativeCpDeficit, coefficients.b) / 10;
}

function updateOutputs() {
  const cpDeficit = calculateCpDeficit();
  const statPenalty = calculateStatPenalty(cpDeficit);

  const formattedCpDeficit = (cpDeficit * 100).toFixed(2) + "%";
  const formattedStatPenalty = (statPenalty * 100).toFixed(2) + "%";

  cpDeficitDisplay.textContent = formattedCpDeficit;
  statPenaltyDisplay.textContent = formattedStatPenalty;

  const bgColor = cpDeficit >= 35 ? 'bg-danger' :
                   cpDeficit >= 30 ? 'bg-warning' :
                   cpDeficit >= 25 ? 'bg-warning text-dark' : 'bg-success';
  statPenaltyDisplay.classList.remove(...statPenaltyDisplay.classList);
  statPenaltyDisplay.classList.add(bgColor);
}

// Set default values and update outputs on load
stageCpInput.value = 10000;
teamCpInput.value = 8000;
updateOutputs();

// Add event listeners to input fields
stageCpInput.addEventListener("change", updateOutputs);
teamCpInput.addEventListener("change", updateOutputs);