# Validation Metrics

Every number you use to accept or reject a design, plus how to read a wwPDB validation slider (relevant to choosing [3HH2](../molecules/3HH2.md) vs [5JI1](../molecules/5JI1.md)). Two distinct metric families: **experimental structure quality** (for judging PDB entries) and **prediction/design confidence** (for judging your designs).

---

## Part A — wwPDB structure-quality metrics (judging PDB entries)

Used in Module 2 to decide which experimental structure to trust. The "slider" plot ranks a structure red (worse) → blue (better) as a percentile vs all X-ray structures (filled marker) and vs similar-resolution structures (open marker).

| Metric | What it measures | Good | Notes |
|--------|------------------|------|-------|
| **Resolution** | level of detail (Å) | lower = better | < 2.0 Å trustworthy sidechains; 2–2.5 Å usually fine |
| **Rfree** | cross-validated model-vs-data agreement | < ~0.25 | overfitting shows as Rfree ≫ Rwork |
| **Clashscore** | steric clashes per 1000 atoms | < 10 (excellent < 5) | high = poorly refined packing |
| **Ramachandran outliers** | residues in disallowed φ/ψ | < 0.5% | backbone geometry sanity |
| **Sidechain outliers** | non-rotameric sidechains | < ~5% | high = unreliable sidechain positions |
| **RSRZ outliers** | residues fitting the density poorly | < 5% | real-space fit to the electron density |

**Worked example — [3HH2](../molecules/3HH2.md):** clashscore ~44, sidechain outliers ~14%, elevated Rfree, Ramachandran above modern norms → every metric in the red. A 2009 structure predating current refinement standards. **Interface sidechain positions are unreliable** → don't use as a design target or read contacts off it. Contrast [5JI1](../molecules/5JI1.md) (2017, 2.25 Å, modern validation).

Combined quality metrics (PDBe) take the harmonic mean of these percentiles — a single structure can be fine on resolution yet poor on geometry, so read the whole slider, not just resolution.

---

## Part B — prediction & design confidence metrics (judging your designs)

Used in Module 6 on [ESMFold](../methods/ESMFold.md)/[AlphaFold2](../methods/AlphaFold2.md) outputs.

### pLDDT (per-residue, 0–100)
Local confidence in each residue's predicted position.
- **> 90** very high · **70–90** confident · **50–70** low · **< 50** likely disordered.
- Mean pLDDT > 70 is a reasonable per-design bar; a well-designed miniprotein should be high and uniform.
- **ESMFold stores pLDDT in the PDB B-factor column** — read it from there.

### pTM (predicted TM-score, 0–1)
Model's confidence in the **global fold**.
- **> 0.7** confident compact fold. Below ~0.5 the model doesn't believe in a single defined structure.

### PAE (Predicted Aligned Error) — AF2
N×N matrix; entry (i,j) = expected error in residue i when aligned on j. **Low cross-chain PAE blocks** = confidence in the *relative placement* of binder and target = interface confidence. More informative for binders than pLDDT.

### iPTM (interface pTM) — AF2-multimer
Single-number interface confidence. Binder rankings often use a weighted blend like `0.8·iPTM + 0.2·pTM`. Higher better; iPTM > 0.5–0.7 typically "worth pursuing" (target-dependent).

### RMSD / TM-score (design vs refold) — you compute
- **RMSD** (Å): average atomic deviation after superposition. **< 2 Å Cα** = refold matches design. Report the number of atoms aligned too — low RMSD over few atoms is misleading.
- **TM-score** (0–1, length-normalised, from [TMalign](../methods/TMalign.md)): **> 0.5** same fold, **> 0.9** near-identical. More robust to length than raw RMSD.
- **pTM vs TM-score:** pTM is the model's *self-estimate*; TM-score is a *measurement between two structures*. Use both.

---

## The filter cascade (Module 6/7)

Apply in order; drop anything that fails:

```
1. pTM        > 0.7
2. mean pLDDT > 70
3. RMSD(refold, design) < 2.0 Å   AND/OR   TM-score > 0.5 (ideally > 0.7)
4. (top designs) AF2-multimer iPTM high, cross-chain PAE low
5. Rank survivors by ProteinMPNN score (more negative = better)
```

Then eyeball the top 3–5 in [PyMOL](../methods/PyMOL.md) — metrics never fully replace looking at the interface.

---

## The honest limit of all Part-B metrics

These are **confidence and self-consistency** measures, not measurements of binding. High iPTM/pTM/low PAE mean "the models agree this should fold and dock as designed" — a validated *predictor* of experimental success, not a substitute for it. State this whenever you present results. See [de novo binder design](de-novo-binder-design.md#what-this-pipeline-does-and-does-not-establish).

---

## Links

- Structures judged with Part A: [3HH2](../molecules/3HH2.md), [5JI1](../molecules/5JI1.md)
- Tools producing Part B: [ESMFold](../methods/ESMFold.md), [AlphaFold2](../methods/AlphaFold2.md), [TMalign](../methods/TMalign.md), [PyMOL](../methods/PyMOL.md)
- Pipeline context: [de novo binder design](de-novo-binder-design.md)
