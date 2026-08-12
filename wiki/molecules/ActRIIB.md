# ActRIIB (ACVR2B)

**The competitor.** The type II receptor whose binding to myostatin your designed miniprotein is meant to out-compete or occlude. You are not designing *against* ActRIIB — you are designing a binder that occupies ActRIIB's footprint on [GDF8](GDF8.md).

| Field | Value |
|-------|-------|
| Names | ActRIIB, Activin receptor type IIB |
| Gene | ACVR2B |
| Human UniProt | Q13705 |
| Type | Single-pass transmembrane serine/threonine kinase receptor |
| Relevant part | Extracellular ligand-binding domain (ECD) |
| Ligands | Activins A/B, myostatin (GDF8), GDF11, nodal, BMP9/10; BMP2/4/6/7 weakly |
| Key structure here | [6MAC](6MAC.md) — GDF11:ActRIIB:ALK5 |

---

## Role in myostatin signalling

ActRIIB is the **primary ligand-binding receptor** transmitting myostatin signal, though myostatin also binds ActRIIA with lower affinity. Mechanistically: myostatin dimer recruits two type II receptors (ActRIIB) via the knuckle epitope; the type II receptors then recruit and trans-phosphorylate two type I receptors (ALK4/5) via the wrist epitope; the activated type I kinases phosphorylate SMAD2/3; the signal represses muscle growth.

The therapeutic logic that makes ActRIIB a landmark for muscle biology:
- A **soluble ActRIIB-Fc "trap"** (decoy receptor) sequesters myostatin and can increase muscle mass dramatically in weeks in mice.
- But ActRIIB is promiscuous — it also binds activins and GDF11 — so a trap causes on-target-but-broad effects. This is *why* an epitope-focused approach on the ligand (what you're designing) is conceptually attractive: it can, in principle, be more ligand-selective than trapping at the receptor.

You should be able to articulate this trade-off: **receptor trap = broad; ligand-epitope binder = potentially selective.** It is the strategic framing for the whole project.

---

## Biology and tissue distribution

ActRIIB is a **hub**: many unrelated ligands converge on this single receptor, and it is expressed in far more tissues than muscle. Those two facts together are the entire argument for intervening at the ligand instead.

### How it actually signals

Its kinase is **constitutively active** — unlike a receptor tyrosine kinase, ligand binding does not switch it on. The regulated step is *proximity*: the ligand dimer acts as a clamp holding a type I receptor next to the always-on type II kinase, which phosphorylates the type I receptor's **GS box**. The activated type I kinase then phosphorylates R-SMADs, which trimerise with SMAD4 and translocate to the nucleus. Three steps from cell surface to transcription — no second-messenger cascade.

**Design consequence:** because regulation is by proximity rather than enzyme activation, you never need to inhibit a kinase. Preventing complex assembly is sufficient to kill the signal.

### Ligands through this one receptor

| Ligand | Type I partner | SMADs | Output |
|--------|----------------|-------|--------|
| **Myostatin (GDF8)** | ALK4/ALK5 | 2/3 | Muscle atrophy — **your target** |
| **GDF11** | ALK4/ALK5 | 2/3 | Axial patterning, erythroid maturation |
| **Activin A/B/AB** | ALK4 | 2/3 | FSH release, inflammation, cachexia |
| **Nodal** | ALK4 + Cripto | 2/3 | Embryonic left–right asymmetry |
| **BMP9 (GDF2), BMP10** | ALK1 + endoglin | 1/5/8 | Vascular quiescence |
| BMP2/4/6/7 | ALK2/ALK3 | 1/5/8 | Weak — these prefer BMPR2 |

Note the BMP9/BMP10 row. Those are BMP-arm ligands running through the *same* type II receptor as myostatin into a *different* SMAD branch. That row is where receptor traps get into trouble.

### Where it is expressed

| Tissue | Cells | Role of ActRIIB signalling |
|--------|-------|----------------------------|
| **Skeletal muscle** | Myofibres, satellite cells | Myostatin → SMAD2/3 → MuRF1/atrogin-1 up, Akt/mTOR down; holds satellite cells quiescent |
| **Vascular endothelium** | Endothelial cells | BMP9/10–ALK1 maintains vessel quiescence |
| **Heart** | Cardiomyocytes | Development; `Acvr2b−/−` mice die with cardiac malformations |
| **Bone** | Osteoblasts, osteoclasts | Restrains bone formation |
| **Adipose** | White + brown | Blockade drives browning, improves insulin sensitivity |
| **Bone marrow** | Late erythroid progenitors | GDF11/activin B brake terminal maturation |
| **Pancreas** | Islet β-cells | Islet development, insulin secretion |
| **Pituitary** | Gonadotropes | Activin → FSHβ transcription (mostly ActRIIA) |
| **Gonads** | Granulosa, Sertoli, Leydig | Folliculogenesis, spermatogenesis |
| **Embryo** | Node, lateral plate | Nodal-dependent left–right asymmetry |

Liver, kidney, lung, gut and CNS also express it at lower levels. The breadth *is* the finding — there is no tissue-restricted window to exploit at the receptor.

### ActRIIA vs ActRIIB

Myostatin uses **both** type II receptors, binding ActRIIB roughly an order of magnitude more tightly.

| | ActRIIA (ACVR2A) | ActRIIB (ACVR2B) |
|---|---|---|
| Myostatin affinity | Lower | **Higher** |
| Dominant role | Pituitary FSH, reproductive | Skeletal muscle, heart |
| Knockout | Viable, mild | Perinatal lethal — laterality + cardiac defects |
| Clinical trap | Sotatercept (PAH) | Luspatercept (anaemia), ACE-031 (halted) |

**This strengthens the epitope argument.** Blocking ActRIIB alone leaves myostatin a lower-affinity route through ActRIIA. But the **knuckle epitope is the site both type II receptors use** — so occluding it on the ligand shuts down both routes at once, with one binder.

---

## The ACE-031 story

The cautionary tale that justifies this whole project. Learn to tell it in four sentences.

**ACE-031** (ramatercept) was a soluble ActRIIB-Fc trap — the ECD fused to an antibody Fc, dosed to sponge up circulating ligand. In Duchenne muscular dystrophy trials it produced real increases in lean mass. It was **halted in 2011** for **epistaxis (nosebleeds), gum bleeding, and telangiectasia**. The cause: the trap could not tell myostatin from **BMP9 and BMP10**, and stripping those away removed the ALK1–endoglin signal that keeps endothelium quiescent.

The closure is what makes it convincing: humans with loss-of-function mutations in **ALK1** (*ACVRL1*) or **endoglin** (*ENG*) have **hereditary haemorrhagic telangiectasia** — nosebleeds, telangiectasias, arteriovenous malformations. ACE-031 produced a **pharmacological phenocopy of a genetic vascular disease.** That is not a vague safety signal; it is a mechanistically explained one.

**Two corollaries worth holding onto:**

1. **A binder on GDF8 cannot do this.** It never touches BMP9, BMP10 or nodal, because it is not at the receptor. That is the selectivity ceiling you gain by moving the intervention from the hub to the ligand.
2. **"Off-target" is context-dependent.** The same promiscuity that killed ACE-031 in muscle became the *therapeutic mechanism* of **luspatercept** — a modified ActRIIB-Fc now approved for β-thalassemia and MDS, working precisely by trapping GDF11/activin B to release the brake on erythroid maturation. Same molecule class, same breadth, different indication.

Note that corollary 1 is bounded by the [selectivity caveat](#selectivity-caveat-to-state-up-front) below: it buys you separation from the BMP arm, **not** from GDF11.

---

## The part of ActRIIB you actually care about

Only the **extracellular domain (ECD)** matters for the interface. It is a small (~100-residue) three-finger toxin-fold module. In the ternary complexes ([6MAC](6MAC.md), 7MRZ) it docks onto the convex knuckle of the ligand fingertips. The residues of the ligand that the ActRIIB ECD contacts are precisely the **hotspots** you extract and hand to [RFdiffusion](../methods/RFdiffusion.md).

The kinase domain (intracellular) has its own crystal structures (e.g. with adenine, at 2.0 Å) but is irrelevant to your extracellular design problem — don't get pulled into it.

---

## How ActRIIB defines your hotspots

Workflow (detail on [6MAC](6MAC.md) and [PPI hotspots](../concepts/PPI-hotspots.md)):

1. In [6MAC](6MAC.md), select ligand ([GDF11](GDF11.md)) residues within ~4–5 Å of the ActRIIB ECD chain.
2. Those residues are the knuckle epitope.
3. Map them onto [GDF8](GDF8.md) via [5JI1](5JI1.md).
4. Feed as `ppi.hotspot_res` to RFdiffusion.

Your binder then gets designed to contact the same GDF8 atoms ActRIIB would — i.e. it competes for the receptor site.

---

## Selectivity caveat to state up front

Because ActRIIB binds activins and GDF11 as well as GDF8, and because you are deriving your epitope *from* a GDF11 complex, your design targets a surface that is **shared across several ligands**. A binder built purely to this shared epitope may not be GDF8-selective. Achieving selectivity would require exploiting the GDF8-specific residues *around* the conserved core — a genuinely hard problem you are not solving in this exercise, but should name as the natural next step.

---

## Links

- The ligand it binds (your target): [GDF8](GDF8.md)
- The proxy complex that shows the interface: [6MAC](6MAC.md) via [GDF11](GDF11.md)
- The fold and its two epitopes: [TGF-β superfamily](../concepts/TGF-beta-superfamily.md)
- Interface theory: [PPI hotspots](../concepts/PPI-hotspots.md)
- What consumes the hotspots: [RFdiffusion](../methods/RFdiffusion.md)
