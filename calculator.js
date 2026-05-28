/**
 * NIKKE CP Deficit Calculator
 *
 * Core calculator logic for determining Combat Power (CP) deficit and stat penalties.
 */

const ALGORITHMS = Object.freeze({
  LOOKUP: 'lookup',       // Linear interpolation across the 501-point dataset (default)
  POWER_LAW: 'power_law'  // a · d^b — original fit, ~1pp pessimistic in the 15-35% zone
});

const DEFAULT_ALGORITHM = ALGORITHMS.LOOKUP;

class CPDeficitCalculator {
  constructor(options = {}) {
    const requested = options.algorithm || DEFAULT_ALGORITHM;
    // Unknown values silently coerce to the default — keeps the URL surface forgiving.
    this.algorithm = Object.values(ALGORITHMS).includes(requested) ? requested : DEFAULT_ALGORITHM;

    // Power-law parameters, fitted to the 1%–48% subset of the dataset.
    this.powerLawParams = {
      a: 1.0399570265430915,
      b: 0.478827201593444
    };

    this.lookupTable = null;
    this.lookupTableLoaded = false;
  }

  /**
   * Load lookup table from JSON.
   * @param {Array<{cp_deficit:number, stat_penalty:number}>} lookupData
   */
  loadLookupTable(lookupData) {
    if (!lookupData || !Array.isArray(lookupData) || lookupData.length === 0) {
      console.warn('Invalid lookup table data, calculator will use power-law fallback');
      return;
    }

    // Copy + sort so we don't mutate the caller's array.
    this.lookupTable = lookupData.slice().sort((a, b) => a.cp_deficit - b.cp_deficit);
    this.lookupTableLoaded = true;
  }

  /**
   * Linear interpolation across the sorted lookup table.
   *
   * Bisect to find the upper-bound index, then lerp between the bracketing pair.
   * Below the table's first nonzero entry, returns the first entry's penalty —
   * honors the game's "any nonzero deficit triggers the 5pp jump" mechanic.
   * Above the last entry, clamps to the last entry.
   *
   * @param {number} deficit
   * @returns {number|null} interpolated penalty, or null if no table loaded
   */
  _interpolate(deficit) {
    const table = this.lookupTable;
    if (!table || table.length === 0) return null;

    if (deficit <= table[0].cp_deficit) return table[0].stat_penalty;
    const last = table[table.length - 1];
    if (deficit >= last.cp_deficit) return last.stat_penalty;

    // Bisect for the smallest index whose cp_deficit >= deficit.
    let lo = 0;
    let hi = table.length - 1;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (table[mid].cp_deficit < deficit) lo = mid + 1;
      else hi = mid;
    }
    const upper = table[lo];
    const lower = table[lo - 1];
    const span = upper.cp_deficit - lower.cp_deficit;
    if (span === 0) return upper.stat_penalty;
    const t = (deficit - lower.cp_deficit) / span;
    return lower.stat_penalty + t * (upper.stat_penalty - lower.stat_penalty);
  }

  /**
   * Power-law evaluation: a · d^b.
   */
  _powerLaw(deficit) {
    const { a, b } = this.powerLawParams;
    return a * Math.pow(deficit, b);
  }

  /**
   * Validate CP input value.
   */
  validateCP(cp) {
    return !isNaN(cp) && isFinite(cp) && cp > 0;
  }

  /**
   * Calculate CP deficit as a fraction in [0, 1].
   * @throws {Error} on invalid inputs.
   */
  calculateCpDeficit(stageCp, teamCp) {
    if (!this.validateCP(stageCp)) throw new Error('Stage CP must be a positive number');
    if (!this.validateCP(teamCp)) throw new Error('Team CP must be a positive number');
    return Math.max(0, stageCp - teamCp) / stageCp;
  }

  /**
   * Calculate stat penalty using the active algorithm.
   *
   * Lookup mode: interpolated lookup, falls back to power law only when the table
   *   hasn't loaded yet (so the calculator works on first paint and on file://).
   * Power-law mode: always a · d^b, regardless of lookup state.
   */
  calculateStatPenalty(cpDeficit) {
    const deficit = Math.max(0, Math.min(1, cpDeficit));
    if (deficit === 0) return 0;

    if (this.algorithm === ALGORITHMS.POWER_LAW) {
      return this._powerLaw(deficit);
    }

    // Lookup mode (default).
    if (this.lookupTableLoaded) {
      const interp = this._interpolate(deficit);
      if (interp !== null) return interp;
    }
    return this._powerLaw(deficit);
  }

  /**
   * Get color class for the current deficit. Corrupted-theme compatible.
   */
  getDeficitColorClass(cpDeficit) {
    if (cpDeficit >= 0.35) return 'danger';
    if (cpDeficit >= 0.30) return 'warning';
    if (cpDeficit >= 0.25) return 'caution';
    return 'success';
  }

  formatPercentage(value) {
    return (value * 100).toFixed(2) + '%';
  }

  calculate(stageCp, teamCp) {
    const cpDeficit = this.calculateCpDeficit(stageCp, teamCp);
    const statPenalty = this.calculateStatPenalty(cpDeficit);
    const colorClass = this.getDeficitColorClass(cpDeficit);
    return {
      cpDeficit,
      statPenalty,
      cpDeficitFormatted: this.formatPercentage(cpDeficit),
      statPenaltyFormatted: this.formatPercentage(statPenalty),
      colorClass
    };
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = CPDeficitCalculator;
  module.exports.ALGORITHMS = ALGORITHMS;
  module.exports.DEFAULT_ALGORITHM = DEFAULT_ALGORITHM;
}
