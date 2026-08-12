# Glossary

Grouped by topic: the signalling biology, then the structural vocabulary, then
the design pipeline and its metrics.

---

## Signalling biology

**Serine/threonine kinase** — an enzyme that transfers the γ-phosphate of ATP
onto the hydroxyl of a **serine** or **threonine** side chain. (Contrast
tyrosine kinases such as EGFR.) The phosphate adds roughly two negative charges,
which changes conformation or creates a docking site for another protein.
Reversible — phosphatases strip it off — which is what makes phosphorylation a
switch rather than a mark. Both **type I** and **type II** TGF-β receptors are
ser/thr kinases.

**Constitutively active** — always on, not switched by a signal. The type II
receptor kinase is constitutively active, so ligand binding does *not* turn it
on. The regulated step is **proximity**: the ligand dimer clamps a type I
receptor next to the always-running type II kinase. Design consequence —
preventing complex assembly is sufficient to kill the signal, so no kinase
inhibition is required.

**GS box** — a glycine/serine-rich juxtamembrane segment (~30 aa, core motif
`TTSGSGSG`) found **only in type I receptors**. At rest it is an autoinhibitory
clamp, locked further by FKBP12. Phosphorylation by the type II kinase releases
the clamp *and* creates the negatively charged docking site that recruits
R-SMADs — one event that both activates the enzyme and delivers its substrate.
This is the step our binder is designed to prevent.

**SMAD / R-SMAD** — the intracellular transducers. The name is a portmanteau of
*Sma* (*C. elegans*) and *Mad* (*Drosophila* **M**others **A**gainst
**D**ecapentaplegic). **R-SMAD** (receptor-regulated): SMAD2/3 for the
TGF-β/activin/myostatin arm, SMAD1/5/8 for the BMP arm, phosphorylated on a
C-terminal `SSXS` motif. **Co-SMAD**: SMAD4, shared by both arms. **I-SMAD**:
SMAD6/7, negative feedback. Two phosphorylated R-SMADs plus SMAD4 form a
heterotrimer that translocates to the nucleus and binds DNA directly — only
three steps from cell surface to transcription, with no second-messenger
cascade.

**Type I / II / III receptor** — the TGF-β superfamily's own naming scheme, not
a general receptor classification. The numbering is historical, from apparent
band sizes on 1980s affinity-labelling gels.

| Type | Kinase? | Role | Required? |
|------|---------|------|-----------|
| **III** (co-receptor) | No | Captures and presents ligand | No — modulatory |
| **II** | Yes, **always on** | Binds ligand first; phosphorylates type I | Yes |
| **I** | Yes, **off until phosphorylated** | Phosphorylates SMADs; **sets which SMAD** | Yes |

Humans have 5 type II (`TGFBR2`, ActRIIA, ActRIIB, `BMPR2`, `AMHR2`), 7 type I
(the **ALKs**), and a handful of type III co-receptors — **betaglycan**
(`TGFBR3`, needed for inhibin to antagonise activin) and **endoglin** (CD105,
`ENG`, partners ALK1 on endothelium). The **type I** receptor is the specificity
determinant.

**ALK (Activin receptor-Like Kinase)** — collective name for the seven type I
receptors.

| ALK | Gene | Notable for |
|-----|------|-------------|
| ALK1 | `ACVRL1` | BMP9/10 on endothelium; mutated in **HHT** |
| ALK2 | `ACVR1` | BMPs; mutated in FOP |
| ALK3 | `BMPR1A` | BMPs |
| ALK4 | `ACVR1B` | Activin, nodal, **myostatin** |
| ALK5 | `TGFBR1` | TGF-β, **myostatin** |
| ALK6 | `BMPR1B` | BMPs |
| ALK7 | `ACVR1C` | Activin B, GDF3 |

**ActRIIB** — Activin receptor type IIB (`ACVR2B`). A TGF-β-family **type II**
receptor; binds the ligand **knuckle**. Our binder does not mimic it — it
occupies ActRIIB's footprint on GDF8 to block the interaction.

**ActRIIA** — the paralogue (`ACVR2A`). Binds myostatin ~10× more weakly than
ActRIIB and dominates in the pituitary rather than muscle. Relevant because
myostatin can signal through *both*, but both dock the same **knuckle** — so
occluding the knuckle on the ligand closes both routes with one binder.

**GDF8 / myostatin** — the same protein, two names (gene `MSTN`). *Myostatin*
is the functional name (McPherron & Lee, 1997: *myo-* + *-statin*); *GDF8* is
the systematic family name. Structural work favours GDF8; physiology favours
myostatin. Loss of function produces double-muscled cattle, "bully" whippets,
and one documented human case — the evidence that the target is safe if hit
cleanly.

**GDF11** — myostatin's closest relative (~**90 % identical** mature domain),
sharing the same receptors. Broadly expressed; drives embryonic anterior-
posterior axial patterning and brakes erythroid maturation. Knockout is
perinatally lethal, unlike `MSTN`. The two diverge most at the **wrist** and
least at the **knuckle** — which is exactly why our hotspot transfer works and
why GDF11 cross-reactivity is hard to avoid.

**Activin** — dimers of inhibin β subunits (activin A = βA:βA, activin B =
βB:βB). Named for *activating* FSH release. Also drives inflammation and cancer
cachexia. Antagonised by **inhibin** and **follistatin**.

**Nodal** — embryonic morphogen establishing left-right asymmetry; requires the
co-receptor Cripto. Essentially absent in adults. Its loss explains the
laterality defects in `Acvr2b−/−` mice.

**BMP9 / BMP10** — BMP-arm ligands (BMP9 = `GDF2`, from liver; BMP10 from heart)
that bind ActRIIB **tightly** and signal through ALK1 + endoglin → SMAD1/5/8 to
maintain vascular **quiescence**. BMP2/4/6/7 bind ActRIIB only weakly — they
prefer `BMPR2`. The BMP9/10 pair is the reason receptor traps bleed.

**Ligand trap** — a soluble receptor ectodomain fused to an antibody Fc, dosed
to sponge up circulating ligand. **ACE-031** (ActRIIB-Fc) raised lean mass in
DMD trials but was halted in 2011 for epistaxis and telangiectasia, having also
stripped out BMP9/10 — a pharmacological phenocopy of **HHT**. **Luspatercept**
(modified ActRIIB-Fc) and **sotatercept** (ActRIIA-Fc) are the same architecture
turned into approved drugs. The core lesson: a trap blocks the *receptor*, which
is shared; our binder blocks the *ligand*, which is not.

**HHT** — hereditary haemorrhagic telangiectasia. Caused by loss-of-function
mutations in **ALK1** or **endoglin**; presents as nosebleeds, telangiectasias
and arteriovenous malformations. The genetic disease whose phenotype ACE-031
reproduced pharmacologically.

**Quiescence** — a **reversible** non-dividing state (cell-cycle G0), distinct
from senescence (permanent) and terminal differentiation (committed). *Vascular
quiescence*: healthy endothelium is stable, non-proliferating and non-leaky,
actively maintained by BMP9/10–ALK1. *Satellite-cell quiescence*: muscle stem
cells held dormant, partly by myostatin.

**Satellite cells** — skeletal muscle stem cells (marker **Pax7**), named in
1961 for sitting like satellites between the fibre's membrane and its basal
lamina. Muscle fibres are post-mitotic syncytia and cannot divide, so all growth
and repair capacity comes from satellite cells activating, proliferating and
fusing in to donate nuclei. Myostatin restrains muscle by two routes: degrading
protein in existing fibres, and keeping this pool asleep.

**Endothelial cells (ECs)** — the single cell layer lining every blood and
lymphatic vessel. The cells kept quiescent by BMP9/10–ALK1, and the cells that
fail in both HHT and the ACE-031 bleeding.

**FSH** — follicle-stimulating hormone, from anterior pituitary gonadotropes;
drives ovarian follicle growth and supports spermatogenesis. Gonadotropes make
activin B locally, which signals through ActRIIA/ALK4 → SMAD2/3 to transcribe
the `FSHB` subunit. Inhibin (via betaglycan) and follistatin oppose it. This is
the reproductive-endocrine liability of blocking ActRII systemically.

**Latent complex** — myostatin held inactive by its bound prodomain until
proteolytic release of the mature growth factor.

---

## Structure and epitopes

**Cystine-knot fold** — the TGF-β core: three disulfides forming a knotted ring
("palm"), with β-strand "fingers" and a "wrist" helix.

**Knuckle epitope** — convex outer face of one ligand monomer's β-fingers; the
**type II** receptor site. Our target. (Hydrophobic, single-monomer.)

**Wrist epitope** — concave site at the dimer interface; the **type I** receptor
site. *Not* our target.

---

## Design pipeline

**Contig (RFdiffusion)** — the string describing what to build, e.g.
`[A1-109/0 45-60]`: keep target chain A residues 1–109, a chain break (`/0`),
then design a new 45–60-residue binder.

**Hotspot residues** — the few target residues the binder *must* contact; passed
to RFdiffusion as `ppi.hotspot_res`.

**SE(3)-equivariance** — the property that a network's outputs transform
consistently under 3D rotations/translations. RFdiffusion's SE3Transformer uses
it so structure predictions don't depend on arbitrary coordinate framing.

**ProteinMPNN score** — a sequence log-likelihood under the model; more negative
= the model is more confident the sequence fits the backbone.

**Self-consistency** — the design-validation idea: a good sequence, folded
independently (ESMFold), should return to the structure it was designed for.

---

## Validation metrics

**pLDDT** — predicted Local Distance Difference Test (0–100). Per-residue
confidence; ESMFold stores it in the PDB B-factor column. Mean > 70 is good.

**pTM** — predicted TM-score (0–1). Global fold confidence; > 0.7 is good,
< 0.5 suggests disorder.

**RMSD** — root-mean-square deviation of atomic positions after superposition;
here, ESMFold prediction vs RFdiffusion backbone. < 2 Å = good self-consistency.

**TM-score / TMalign** — length-normalized structural similarity (0–1) and the
tool that computes it; more robust than raw RMSD to length and outliers.
