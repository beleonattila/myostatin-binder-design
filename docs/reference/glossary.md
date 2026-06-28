# Glossary

**ActRIIB** — Activin receptor type IIB. A TGF-β-family **type II** receptor;
binds the ligand **knuckle**. Our binder mimics/antagonizes it.

**Contig (RFdiffusion)** — the string describing what to build, e.g.
`[A1-109/0 45-60]`: keep target chain A residues 1–109, a chain break (`/0`),
then design a new 45–60-residue binder.

**Cystine-knot fold** — the TGF-β core: three disulfides forming a knotted ring
("palm"), with β-strand "fingers" and a "wrist" helix.

**Hotspot residues** — the few target residues the binder *must* contact; passed
to RFdiffusion as `ppi.hotspot_res`.

**Knuckle epitope** — convex outer face of one ligand monomer's β-fingers; the
**type II** receptor site. Our target. (Hydrophobic, single-monomer.)

**Wrist epitope** — concave site at the dimer interface; the **type I** receptor
site. *Not* our target.

**pLDDT** — predicted Local Distance Difference Test (0–100). Per-residue
confidence; ESMFold stores it in the PDB B-factor column. Mean > 70 is good.

**pTM** — predicted TM-score (0–1). Global fold confidence; > 0.7 is good,
< 0.5 suggests disorder.

**RMSD** — root-mean-square deviation of atomic positions after superposition;
here, ESMFold prediction vs RFdiffusion backbone. < 2 Å = good self-consistency.

**TM-score / TMalign** — length-normalized structural similarity (0–1) and the
tool that computes it; more robust than raw RMSD to length and outliers.

**SE(3)-equivariance** — the property that a network's outputs transform
consistently under 3D rotations/translations. RFdiffusion's SE3Transformer uses
it so structure predictions don't depend on arbitrary coordinate framing.

**ProteinMPNN score** — a sequence log-likelihood under the model; more negative
= the model is more confident the sequence fits the backbone.

**Self-consistency** — the design-validation idea: a good sequence, folded
independently (ESMFold), should return to the structure it was designed for.

**Latent complex** — myostatin held inactive by its bound prodomain until
proteolytic release of the mature growth factor.
