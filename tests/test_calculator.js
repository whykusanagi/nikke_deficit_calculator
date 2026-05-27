/**
 * Unit tests for CPDeficitCalculator
 * 
 * Run with: node tests/test_calculator.js
 * Or use a test runner like Jest or Mocha
 */

// Load calculator (adjust path as needed)
const CPDeficitCalculator = require('../calculator.js');

// Test suite
function runTests() {
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    try {
      fn();
      console.log(`✅ ${name}`);
      passed++;
    } catch (error) {
      console.error(`❌ ${name}: ${error.message}`);
      failed++;
    }
  }

  // Test 1: Validate CP
  test('validateCP accepts positive numbers', () => {
    const calc = new CPDeficitCalculator();
    if (!calc.validateCP(1000)) throw new Error('1000 should be valid');
    if (!calc.validateCP(1)) throw new Error('1 should be valid');
    if (!calc.validateCP(999999)) throw new Error('999999 should be valid');
  });

  test('validateCP rejects invalid values', () => {
    const calc = new CPDeficitCalculator();
    if (calc.validateCP(0)) throw new Error('0 should be invalid');
    if (calc.validateCP(-1)) throw new Error('-1 should be invalid');
    if (calc.validateCP(NaN)) throw new Error('NaN should be invalid');
    if (calc.validateCP(Infinity)) throw new Error('Infinity should be invalid');
    if (calc.validateCP('abc')) throw new Error('String should be invalid');
  });

  // Test 2: Calculate CP Deficit
  test('calculateCpDeficit returns correct deficit', () => {
    const calc = new CPDeficitCalculator();
    const deficit = calc.calculateCpDeficit(10000, 8000);
    if (Math.abs(deficit - 0.2) > 0.001) throw new Error(`Expected 0.2, got ${deficit}`);
  });

  test('calculateCpDeficit returns 0 when team CP >= stage CP', () => {
    const calc = new CPDeficitCalculator();
    const deficit1 = calc.calculateCpDeficit(10000, 10000);
    const deficit2 = calc.calculateCpDeficit(10000, 12000);
    if (deficit1 !== 0) throw new Error('Should be 0 when equal');
    if (deficit2 !== 0) throw new Error('Should be 0 when team CP higher');
  });

  test('calculateCpDeficit throws error for invalid inputs', () => {
    const calc = new CPDeficitCalculator();
    try {
      calc.calculateCpDeficit(0, 1000);
      throw new Error('Should have thrown error for invalid stage CP');
    } catch (error) {
      if (!error.message.includes('Stage CP')) {
        throw new Error('Should throw error with "Stage CP" message');
      }
    }
  });

  // Test 3: Calculate Stat Penalty
  test('calculateStatPenalty returns 0 for 0 deficit', () => {
    const calc = new CPDeficitCalculator();
    const penalty = calc.calculateStatPenalty(0);
    if (penalty !== 0) throw new Error(`Expected 0, got ${penalty}`);
  });

  test('calculateStatPenalty increases with deficit', () => {
    const calc = new CPDeficitCalculator();
    const penalty1 = calc.calculateStatPenalty(0.1);
    const penalty2 = calc.calculateStatPenalty(0.5);
    if (penalty2 <= penalty1) throw new Error('Penalty should increase with deficit');
  });

  // Test 4: Get Deficit Color Class
  test('getDeficitColorClass returns correct colors', () => {
    const calc = new CPDeficitCalculator();
    if (calc.getDeficitColorClass(0.1) !== 'success') throw new Error('Low deficit should be success');
    if (calc.getDeficitColorClass(0.27) !== 'caution') throw new Error('Minor deficit should be caution');
    if (calc.getDeficitColorClass(0.32) !== 'warning') throw new Error('Moderate deficit should be warning');
    if (calc.getDeficitColorClass(0.4) !== 'danger') throw new Error('High deficit should be danger');
  });

  // Test 5: Format Percentage
  test('formatPercentage formats correctly', () => {
    const calc = new CPDeficitCalculator();
    if (calc.formatPercentage(0.25) !== '25.00%') throw new Error('Should format as 25.00%');
    if (calc.formatPercentage(0.5) !== '50.00%') throw new Error('Should format as 50.00%');
  });

  // Test 6: Complete Calculate Function
  test('calculate returns all required fields', () => {
    const calc = new CPDeficitCalculator();
    const results = calc.calculate(10000, 8000);
    if (!results.hasOwnProperty('cpDeficit')) throw new Error('Missing cpDeficit');
    if (!results.hasOwnProperty('statPenalty')) throw new Error('Missing statPenalty');
    if (!results.hasOwnProperty('cpDeficitFormatted')) throw new Error('Missing cpDeficitFormatted');
    if (!results.hasOwnProperty('statPenaltyFormatted')) throw new Error('Missing statPenaltyFormatted');
    if (!results.hasOwnProperty('colorClass')) throw new Error('Missing colorClass');
  });

  // Summary
  console.log(`\nTests: ${passed} passed, ${failed} failed`);
  process.exit(failed > 0 ? 1 : 0);
}

// Run tests if executed directly
if (require.main === module) {
  runTests();
}

module.exports = { runTests };

