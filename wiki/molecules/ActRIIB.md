# ActRIIB (ACVR2B)

**The competitor.** The type II receptor whose binding to myostatin your designed miniprotein is meant to out-compete or occlude. You are not designing *against* ActRIIB — you are designing a binder that occupies ActRIIB's footprint on [GDF8](GDF8.md).

| Field | Value |
|-------|-------|
| Names | ActRIIB, Activin receptor type IIB |
| Gene | ACVR2B |
| Human UniProt | Q13705 |
| Type | Single-pass transmembrane serine/threonine kinase receptor |
| Relevant part | Extracellular ligand-binding domain (ECD) |
| Ligands | Activins, myostatin (GDF8), GDF11, some BMPs |
| Key structure here | [6MAC](6MAC.md) — GDF11:ActRIIB:ALK5 |

---

## Role in myostatin signalling

ActRIIB is the **primary ligand-binding receptor** transmitting myostatin signal, though myostatin also binds ActRIIA with lower affinity. Mechanistically: myostatin dimer recruits two type II receptors (ActRIIB) via the knuckle epitope; the type II receptors then recruit and trans-phosphorylate two type I receptors (ALK4/5) via the wrist epitope; the activated type I kinases phosphorylate SMAD2/3; the signal represses muscle growth.

The therapeutic logic that makes ActRIIB a landmark for muscle biology:
- A **soluble ActRIIB-Fc "trap"** (decoy receptor) sequesters myostatin and can increase muscle mass dramatically in weeks in mice.
- But ActRIIB is promiscuous — it also binds activins and GDF11 — so a trap causes on-target-but-broad effects. This is *why* an epitope-focused approach on the ligand (what you're designing) is conceptually attractive: it can, in principle, be more ligand-selective than trapping at the receptor.

You should be able to articulate this trade-off: **receptor trap = broad; ligand-epitope binder = potentially selective.** It is the strategic framing for the whole project.

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
- Interface theory: [PPI hotspots](../concepts/PPI-hotspots.md)
- What consumes the hotspots: [RFdiffusion](../methods/RFdiffusion.md)
