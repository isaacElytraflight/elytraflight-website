# ME 132 Batch B3 Step Log

## Summary
Batch B3 ships 6 skills: `app-examples`, `cruise-control`, `equilibria`, `loop-tf`, `second-order-sys`, `ss-solution`.

- Skills: 6
- Questions: 72 (12 per skill, 4 rounds × 3)
- Figures: 72 (100% coverage)
- Explainers: 6 (words: 312–381, all in 250–500 range)

## Steps

### 1. Initial setup (~5 min)
- Fetched latest main (B2 merge at 8517322)
- Smoke-checked live site at elytraflight.com/skilltree
- Read SOP, batch plan, notation registry, sources

### 2. Batch specification (~2 min)
- Created `docs/batches/me132-b3.json` with skill list, areas, verifier path

### 3. Notation registry (~3 min)
- Added state-space area extensions for `ss-solution`, `equilibria`
- Added second-order-systems area for `second-order-sys`
- Added loop-transfer-function area for `loop-tf`

### 4. Content generation (~30 min)
- Created `tools/skilltree-content/me132_b3_gen.py` with:
  - 6 banks (72 questions total)
  - 6 explainers (all 250–500 words)
  - Full figure coverage
  - Balanced MC positions (0,1,2,3 each once per skill)
- Multiple iterations to balance MC positions

### 5. Numeric verification (~5 min)
- Created `skilltree/verify_me132_b3.py`
- Recomputes all 48 numeric answers via RK4, matrix exponential, eigenvalues
- Verified worked examples appear in explainer text
- 0 mismatches

### 6. Preview link fixes (~10 min)
- Added B3 leaf skills to `LEAF_PREVIEW_ALLOWED` in validate_bank.py
- Fixed incorrect preview targets:
  - equilibria-r4-q2: sys-id → linearization
  - second-order-sys-r4-q2: nyquist → step-specs
- Fixed cruise-control-r4-q2 answer from 0 to 3.25 (numeric tolerance issue)

### 7. Test updates (~5 min)
- Updated `test-content.js` expectations:
  - Coming-soon count: 46 → 40
  - Bank/explainer counts: 124 → 130
- Removed coming-soon status from 6 B3 skills in ee105_skills_draft.json

### 8. Gate runs (~10 min)
- build: PASS
- schema: PASS (183 warnings, all preexisting)
- graph: PASS (170 skills, acyclic)
- domain: PASS (0 unwaived warnings)
- numeric: PASS (0 mismatches)
- figure-bounds: PASS (30 warnings elsewhere)
- katex: PASS (526 math chunks, 0 errors)
- test-content: PASS (14/14)
- test-merge: PASS (19/19)
- test-migrate: PASS (22/22)
- puppeteer: PASS (48/48)

### 9. Bugbot review fixes (~20 min)
Bugbot identified 5 issues on commit 78cb6be; all fixed:

1. **False T plus S identity (High)** - loop-tf explainer incorrectly equated T=G/(1+GH) with L/(1+L). Fixed by using unity feedback example (G=8, H=1) where T+S=1 holds, and clarifying notation.

2. **Wrong feedforward gain answer (High)** - cruise-control-r4-q2 had K_ff=3.25 but correct formula gives K_ff=1/P=0.25. Fixed answer and explanation in generator and verifier.

3. **Explainer reuses quiz numbers (Medium)** - Worked examples used same parameters as quiz questions. Fixed by using different values:
   - second-order-sys: ω_n=6, ζ=0.4 (was 5, 0.5)
   - loop-tf: G=8, H=1 (was 10, 0.2)
   - app-examples: A=3, R=5, q_in=0.6 (was 2, 4, 0.5)

4. **Tank level omits resistance (Medium)** - app-examples-r1-q3 didn't state R. Fixed by adding "The same tank (R = 4 s/m²)".

5. **Positive trace stability claim (Medium)** - ss-solution-r4-q3 incorrectly said positive trace can have stable eigenvalues. Fixed explanation to say positive trace implies at least one positive eigenvalue.

Also updated puppeteer tests to use `step-specs` (still coming-soon) instead of `second-order-sys` (now playable) for coming-soon tile tests.

### 10. UI bug fix: null figure rendering (~15 min)
Isaac reported that quiz questions without diagrams rendered literal "null" text.

**Root cause**: `Element.append()` converts non-node values to strings, so `figureNode(q)` returning `null` became the text "null".

**Fix**: In `skilltree.js` line 1615, changed from:
```javascript
card.append(..., figureNode(q), ...);
```
To:
```javascript
const fig = figureNode(q);
card.append(...);
if (fig) card.append(fig);
card.append(...);
```

**Regression tests added** (2 new tests, total 50 puppeteer tests):
- `quiz without figure does not render literal null text or empty container`
- `quiz with figure renders SVG with accessibility`

### Wasted work / Retries
- MC position balancing required multiple iterations (~4 passes)
- KaTeX package path resolution needed manual install
- Batch spec missing fields (id, label, areas) caught incrementally
- Bugbot fixes required verifier updates to match new explainer values
- Initial null-figure test referenced bankCache incorrectly (fixed)

### Token cost estimate
Rough estimate: ~150-180k tokens total (initial content generation + Bugbot fix iteration + UI fix)

## Preexisting warnings
The following figure-bounds warnings existed before B3 and are not addressed:
- amp-compensation, cascode-amp, cd-freq, cs-cascade-freq
- noise-dist, octc, rev-bias, rlc, stability, vt
