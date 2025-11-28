# Production Deployment Checklist

## Pre-Deployment

### Code Quality
- [x] Piecewise function implemented with lookup table
- [x] Error handling for network failures (lookup table loading)
- [x] Input validation for edge cases
- [x] Corrupted-theme integration complete
- [x] Responsive design tested
- [x] Accessibility features (keyboard navigation, ARIA labels)

### Data & Accuracy
- [x] Lookup table generated (501 points)
- [x] Piecewise function parameters optimized
- [x] Formula verified against included dataset
- [x] R² score documented (0.995062)

### Documentation
- [x] README updated with piecewise function info
- [x] DEPLOYMENT.md created with path configuration
- [x] FORMULA_ANALYSIS.md with detailed analysis
- [x] Code comments and JSDoc complete

## Deployment Steps

### 1. Path Configuration
- [ ] Determine deployment location (e.g., `nikkers.gg/tools/cp-deficit-calculator/`)
- [ ] Update asset paths in `index.html` based on deployment depth
- [ ] Test all asset loading (CSS, JS, lookup table JSON)

### 2. Asset Verification
- [ ] Verify corrupted-theme CSS loads correctly
- [ ] Verify lookup table JSON loads (`data/stat_penalty_lookup.json`)
- [ ] Verify video background loads (or disable if not needed)
- [ ] Check console for 404 errors

### 3. Functionality Testing
- [ ] Test calculator with various CP values
- [ ] Verify piecewise function works (test < 1%, 1-48%, > 48% ranges)
- [ ] Test error handling (invalid inputs, network failures)
- [ ] Verify color coding displays correctly
- [ ] Test responsive design on mobile/tablet

### 4. Performance
- [ ] Check page load time
- [ ] Verify lookup table loads quickly
- [ ] Test calculation speed (should be instant)
- [ ] Check for memory leaks (long-running sessions)

### 5. Browser Compatibility
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### 6. Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader compatibility
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible

## Post-Deployment

### Monitoring
- [ ] Monitor error logs for lookup table loading failures
- [ ] Track user feedback on accuracy
- [ ] Monitor page load performance

### Updates
- [ ] Set up process for updating dataset and rebuilding models if needed
- [ ] Document versioning strategy
- [ ] Plan for formula refinements based on user feedback

## Rollback Plan

If issues are discovered:
1. Revert to previous version (if versioned)
2. Fallback to power law only (remove lookup table dependency)
3. Document issues for future fixes

## Success Criteria

✅ Calculator loads without errors  
✅ All calculations are accurate  
✅ UI matches corrupted-theme design  
✅ Works on all target browsers  
✅ Mobile responsive  
✅ Accessible to all users  
✅ Performance is acceptable (< 2s load time)

