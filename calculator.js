/**
 * NIKKE CP Deficit Calculator
 * 
 * Core calculator logic for determining Combat Power (CP) deficit and stat penalties.
 */

class CPDeficitCalculator {
  constructor() {
    // Piecewise function parameters fitted to included dataset
    // Data: 501 points from 0.00% to 49.91% CP deficit
    // Uses piecewise function: lookup table for low/high ranges, power law for main range
    this.piecewiseParams = {
      lowRangeThreshold: 0.01,   // Use lookup for < 1%
      highRangeThreshold: 0.48,   // Use lookup for > 48%
      mainRange: {
        a: 1.0399570265430915,    // Optimized for 1% - 48% range
        b: 0.478827201593444,      // R² = 0.995062
      }
    };
    
    // Lookup table will be loaded asynchronously
    this.lookupTable = null;
    this.lookupTableLoaded = false;
  }

  /**
   * Load lookup table from JSON file
   * @param {Array} lookupData - Array of {cp_deficit, stat_penalty} objects
   */
  loadLookupTable(lookupData) {
    if (!lookupData || !Array.isArray(lookupData)) {
      console.warn('Invalid lookup table data, using power law fallback');
      return;
    }
    
    // Sort by cp_deficit for binary search
    this.lookupTable = lookupData.sort((a, b) => a.cp_deficit - b.cp_deficit);
    this.lookupTableLoaded = true;
  }

  /**
   * Binary search in lookup table
   * @param {number} deficit - CP deficit to look up
   * @returns {number|null} Stat penalty or null if not found
   */
  lookupPenalty(deficit) {
    if (!this.lookupTable || this.lookupTable.length === 0) {
      return null;
    }

    // Exact match
    const exact = this.lookupTable.find(d => Math.abs(d.cp_deficit - deficit) < 1e-6);
    if (exact) {
      return exact.stat_penalty;
    }

    // Binary search for closest match
    let left = 0;
    let right = this.lookupTable.length - 1;
    let closest = null;
    let minDiff = Infinity;

    while (left <= right) {
      const mid = Math.floor((left + right) / 2);
      const midDeficit = this.lookupTable[mid].cp_deficit;
      const diff = Math.abs(midDeficit - deficit);

      if (diff < minDiff) {
        minDiff = diff;
        closest = this.lookupTable[mid];
      }

      if (midDeficit < deficit) {
        left = mid + 1;
      } else {
        right = mid - 1;
      }
    }

    // If very close, return the value; otherwise interpolate
    if (closest && minDiff < 0.001) {
      return closest.stat_penalty;
    }

    // Linear interpolation between closest points
    if (closest) {
      const idx = this.lookupTable.indexOf(closest);
      if (idx > 0 && idx < this.lookupTable.length - 1) {
        const prev = this.lookupTable[idx - 1];
        const next = this.lookupTable[idx + 1];
        
        if (deficit < closest.cp_deficit && prev) {
          // Interpolate between prev and closest
          const t = (deficit - prev.cp_deficit) / (closest.cp_deficit - prev.cp_deficit);
          return prev.stat_penalty + t * (closest.stat_penalty - prev.stat_penalty);
        } else if (next) {
          // Interpolate between closest and next
          const t = (deficit - closest.cp_deficit) / (next.cp_deficit - closest.cp_deficit);
          return closest.stat_penalty + t * (next.stat_penalty - closest.stat_penalty);
        }
      }
      return closest.stat_penalty;
    }

    return null;
  }

  /**
   * Validate CP input value
   * @param {number} cp - CP value to validate
   * @returns {boolean} True if valid
   */
  validateCP(cp) {
    return !isNaN(cp) && isFinite(cp) && cp > 0;
  }

  /**
   * Calculate CP deficit percentage
   * @param {number} stageCp - Recommended CP for the stage
   * @param {number} teamCp - Actual team CP
   * @returns {number} CP deficit as decimal (0.0 to 1.0)
   * @throws {Error} If inputs are invalid
   */
  calculateCpDeficit(stageCp, teamCp) {
    if (!this.validateCP(stageCp)) {
      throw new Error('Stage CP must be a positive number');
    }
    if (!this.validateCP(teamCp)) {
      throw new Error('Team CP must be a positive number');
    }

    const deficit = Math.max(0, stageCp - teamCp);
    return deficit / stageCp;
  }

  /**
   * Calculate stat penalty using piecewise function
   * Uses lookup table for low/high ranges, power law for main range
   * Formula derived from included dataset (501 data points)
   * @param {number} cpDeficit - CP deficit as decimal (0.0 to 1.0)
   * @returns {number} Stat penalty as decimal
   */
  calculateStatPenalty(cpDeficit) {
    const nonNegativeDeficit = Math.max(0, Math.min(1, cpDeficit));
    
    // Handle zero deficit
    if (nonNegativeDeficit === 0) {
      return 0;
    }

    const { lowRangeThreshold, highRangeThreshold, mainRange } = this.piecewiseParams;

    // Use lookup table for low range (< 1%) and high range (> 48%) for accuracy
    if (this.lookupTableLoaded && 
        (nonNegativeDeficit < lowRangeThreshold || nonNegativeDeficit > highRangeThreshold)) {
      const lookupPenalty = this.lookupPenalty(nonNegativeDeficit);
      if (lookupPenalty !== null) {
        return lookupPenalty;
      }
    }

    // Use power law for main range (1% - 48%)
    // Fallback to power law if lookup table not loaded
    const { a, b } = mainRange;
    return a * Math.pow(nonNegativeDeficit, b);
  }

  /**
   * Get color class based on CP deficit
   * @param {number} cpDeficit - CP deficit as decimal
   * @returns {string} Color class (corrupted-theme compatible)
   */
  getDeficitColorClass(cpDeficit) {
    // Use corrupted-theme compatible classes
    if (cpDeficit >= 0.35) return 'danger';      // High deficit - red
    if (cpDeficit >= 0.30) return 'warning';      // Moderate deficit - orange
    if (cpDeficit >= 0.25) return 'caution';      // Minor deficit - yellow
    return 'success';                              // Low deficit - green
  }

  /**
   * Format percentage for display
   * @param {number} value - Decimal value (0.0 to 1.0)
   * @returns {string} Formatted percentage string
   */
  formatPercentage(value) {
    return (value * 100).toFixed(2) + '%';
  }

  /**
   * Calculate and return all results
   * @param {number} stageCp - Recommended CP for the stage
   * @param {number} teamCp - Actual team CP
   * @returns {Object} Calculation results
   */
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

// Export for use in tests or modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CPDeficitCalculator;
}

