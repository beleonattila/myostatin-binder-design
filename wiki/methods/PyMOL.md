# PyMOL

**The analysis workhorse.** Used at three points: preparing the target, identifying hotspots, and triaging/validating designs. You already use it (thesis: aligning β-lactamase models, active-site inspection, RMSD) — this page is a project-specific command reference.

| Field | Value |
|-------|-------|
| Type | Molecular visualisation + structural analysis |
| Role here | Target prep, interface selection, superposition, RMSD, figures |
| Alternatives | ChimeraX (viz), [TMalign](TMalign.md) (sequence-independent RMSD) |

---

## Where it's used in the pipeline

| Module | Task | Key commands |
|--------|------|--------------|
| 2 — target prep | strip HETATM, extract chain, inspect | `remove solvent`, `remove not polymer`, `save` |
| 3 — hotspots | select interface residues, superpose ligands | `select ... within`, `align`/`super` |
| 4 — triage | inspect RFdiffusion backbones vs target | visual, `cealign` |
| 6 — validation | superpose ESMFold refold on design, RMSD | `align`, `rms_cur` |
| 7 — figures | render top designs at the interface | `ray`, `png` |

---

## Module 2 — target preparation (5JI1)

```python
fetch 5ji1, async=0
remove solvent            # drop waters
remove not polymer        # drop ligands/ions (HETATM)
# inspect chains:
set_name 5ji1, target
hide everything
show cartoon
util.cbc                  # color by chain
# keep only GDF8 chain(s) — replace X with the real chain id:
create gdf8_target, target and chain X
save data/prepared/myostatin_target.pdb, gdf8_target
```
Check the log for gaps (missing residues) near the epitope before saving. See [5JI1](../molecules/5JI1.md).

---

## Module 3 — hotspot identification (6MAC)

```python
fetch 6mac, async=0
# identify chains first (check header): GDF11 ligand, ActRIIB, ALK5
# select ligand residues contacting ActRIIB:
select actriib_epitope, (chain <GDF11>) within 4.5 of (chain <ActRIIB>)
iterate actriib_epitope and name CA, print(resi, resn)   # list them

# superpose apo-GDF8 onto GDF11 to transfer numbering:
fetch 5ji1, async=0
align 5ji1, 6mac and chain <GDF11>
# now read the GDF8 residues spatially matching the epitope
```
Cross-check with 7MRZ. See [6MAC](../molecules/6MAC.md), [ActRIIB](../molecules/ActRIIB.md), [PPI hotspots](../concepts/PPI-hotspots.md).

**`align` vs `super` vs `cealign`:** `align` does a sequence alignment first (good when sequences are similar — GDF8/GDF11); `super` is sequence-independent (good for low identity); `cealign` uses the CE algorithm (robust for very different structures). For GDF8↔GDF11 use `align`; for comparing a de novo design to anything, prefer `super`/`cealign` or [TMalign](TMalign.md).

---

## Module 6 — RMSD of refold vs design

```python
load rfdiffusion/outputs/design_0.pdb, design
load esm_validation/predicted_structures/design_0_seq1.pdb, refold
align refold, design            # returns RMSD + atoms aligned
# or, without re-superposing:
rms_cur refold, design
```
`align` prints RMSD after superposition and the number of atoms used — report both. A low RMSD over few atoms is not the same as a low RMSD over the whole chain. For a sequence-independent, length-robust number, use [TMalign](TMalign.md) as well.

---

## Gotchas

- **Chain IDs change** between structures and after RFdiffusion/ProteinMPNN. Always re-check which chain is binder vs target before selecting.
- **`align` reports RMSD over the *aligned* subset**, and it prunes outliers by default (`cycles=5`). For a raw all-atom number use `rms_cur` on matched selections, or TMalign.
- **PyMOL renumbers/renames** on some operations; verify residue IDs before writing them into your hotspot file.

---

## Links

- Target: [5JI1](../molecules/5JI1.md)
- Hotspot source: [6MAC](../molecules/6MAC.md)
- Sequence-independent RMSD: [TMalign](TMalign.md)
- What you're measuring against: [validation metrics](../concepts/validation-metrics.md)
