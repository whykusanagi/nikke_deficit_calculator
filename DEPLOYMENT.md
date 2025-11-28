# Deployment Guide

## Path Configuration

The calculator uses relative paths that need to be adjusted based on deployment location.

### Current Structure (GitHub Projects)
```
site/
├── assets/
│   ├── css/corrupted-theme/
│   └── js/
└── github_projects/
    └── nikke_deficit_calculator/
        ├── index.html
        ├── calculator.js
        └── data/
```

**Current paths in index.html:**
- `../../assets/js/env-config.js`
- `../../assets/css/corrupted-theme/theme.css`

### Deployment Options

#### Option 1: Standalone (No Site Dependencies)
If deploying as a standalone tool without the main site:

1. Copy corrupted-theme CSS to calculator directory:
   ```bash
   mkdir -p assets/css/corrupted-theme
   cp ../../assets/css/corrupted-theme/theme.css assets/css/corrupted-theme/
   ```

2. Update paths in `index.html`:
   - `../../assets/js/env-config.js` → `assets/js/env-config.js` (or remove if not needed)
   - `../../assets/css/corrupted-theme/theme.css` → `assets/css/corrupted-theme/theme.css`

3. Create minimal env-config.js if needed, or remove video background dependencies

#### Option 2: Integrated with nikkers.gg Site
If deploying to `nikkers.gg/tools/cp-deficit-calculator/`:

1. Update paths in `index.html`:
   - `../../assets/` → `../../../assets/` (or adjust based on actual depth)
   - `../../index.html` → `../../../index.html`
   - `../../tools.html` → `../../../tools.html`

2. Test paths after deployment and adjust as needed

#### Option 3: Root Level Deployment
If deploying to `nikkers.gg/cp-deficit-calculator/`:

1. Update paths in `index.html`:
   - `../../assets/` → `../assets/`
   - `../../index.html` → `../index.html`
   - `../../tools.html` → `../tools.html`

## Production Checklist

- [ ] Verify all asset paths load correctly
- [ ] Test calculator functionality with lookup table
- [ ] Verify corrupted-theme styling applies correctly
- [ ] Test responsive design on mobile/tablet
- [ ] Verify accessibility (keyboard navigation, screen readers)
- [ ] Test error handling (invalid inputs, network errors)
- [ ] Verify data/stat_penalty_lookup.json loads correctly
- [ ] Check console for errors
- [ ] Test in multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Verify video background loads (or remove if not needed)

## Standalone Deployment (Recommended for nikkers.gg)

For a standalone deployment that doesn't depend on the main site:

1. **Create standalone version:**
   ```bash
   # Copy corrupted-theme CSS
   mkdir -p assets/css/corrupted-theme
   cp ../../assets/css/corrupted-theme/theme.css assets/css/corrupted-theme/
   
   # Create minimal env-config.js (or use CDN)
   # Update index.html paths
   ```

2. **Use CDN for corrupted-theme:**
   ```html
   <link rel="stylesheet" href="https://s3.whykusanagi.xyz/corrupted-theme/theme.css">
   ```

3. **Remove site-specific dependencies:**
   - Remove video background if not needed
   - Simplify navbar or remove site links
   - Use standalone styling

## Testing

After deployment, test:
1. Calculator loads and displays correctly
2. Input validation works
3. Calculations are accurate
4. Lookup table loads (check Network tab)
5. Styling matches corrupted-theme
6. Mobile responsiveness
7. Error messages display correctly

