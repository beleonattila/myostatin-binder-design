# Protein–Protein Interaction Hotspots

The theory behind Module 3. "Hotspot residues" is what you hand RFdiffusion as `ppi.hotspot_res`, so you need to know precisely what they are and how to identify them.

---

## Definition

At a protein–protein interface, binding free energy is **not** spread evenly across all contacting residues. A small subset contributes the bulk of ΔG. These are **hotspots**, defined operationally by **alanine scanning**: mutate an interface residue to alanine, measure the change in binding free energy (**ΔΔG**). A residue is a hotspot if its Ala mutation costs roughly **ΔΔG ≥ 1.5–2 kcal/mol** (thresholds vary by convention).

The empirical generalisation (O'Neil–Clackson–Wells lineage): interfaces often behave as if a few central residues dominate, frequently surrounded by a ring of less energetically important contacts — the "hotspot / O-ring" picture, where the periphery occludes water to protect the hot core.

Hotspots are enriched in **Trp, Tyr, Arg** and buried hydrophobics; they are typically well-packed and solvent-occluded at the interface.

---

## Why they matter for de novo binder design

RFdiffusion's PPI mode doesn't need you to describe the *whole* interface — it needs to know **which target residues the new binder should contact**. You give it hotspots; it generates backbones that pack a binder against those residues. Choosing hotspots therefore **defines the epitope** the binder is built against. Choose residues on the ActRIIB knuckle → competitive antagonist. Choose the wrong face → a faithfully-designed binder to a useless site.

This is why Module 3 is the scientific crux: the tools downstream are mechanical, but this choice determines whether the whole exercise means anything.

---

## How you identify them in THIS project

You have no alanine-scanning data for GDF8:ActRIIB and no direct complex. So you use **structure-based inference from a proxy complex**:

1. In [6MAC](../molecules/6MAC.md) (GDF11:[ActRIIB](../molecules/ActRIIB.md):ALK5), select [GDF11](../molecules/GDF11.md) residues within ~4–5 Å of the ActRIIB ECD. These are the physical contacts = the structural epitope.
2. Optionally weight toward buried hydrophobics and aromatics/Arg (likely energetic hotspots) rather than every peripheral contact.
3. Map onto [GDF8](../molecules/GDF8.md) via superposition on [5JI1](../molecules/5JI1.md).
4. **Conservation-check** each: is the GDF8 residue identical or conservatively substituted? Keep the conserved ones; flag the rest.
5. Cross-check against 7MRZ (a second GDF11:ActRIIB complex) — residues in both are the most trustworthy.

The result is a short list (typically ~5–10 residues) for `ppi.hotspot_res`.

---

## Distance cutoff, briefly

- **~4 Å** ≈ direct van der Waals / H-bond contact — the strict definition of "in contact."
- **~5 Å** ≈ includes near-contact residues that may still matter energetically.

Start at 4.5 Å. Too tight a cutoff misses real contributors; too loose adds noise that over-constrains RFdiffusion. You can iterate.

---

## Caveats to voice

- Structural contact ≠ energetic hotspot. Proximity is a proxy for ΔΔG, not a measurement. Without alanine scanning you are approximating.
- You're reading the epitope off **GDF11**, not GDF8 (see [GDF11](../molecules/GDF11.md) caveats). The type II epitope's conservation is what makes this acceptable.
- Naming both caveats *before* being asked is the difference between "I picked some interface residues" and "I inferred the epitope from a proxy complex and validated conservation, aware that structural contact only approximates energetic contribution."

---

## Links

- Where hotspots come from: [6MAC](../molecules/6MAC.md), [GDF11](../molecules/GDF11.md)
- Where they map to: [GDF8](../molecules/GDF8.md) / [5JI1](../molecules/5JI1.md)
- The receptor defining them: [ActRIIB](../molecules/ActRIIB.md)
- Where they're used: [RFdiffusion](../tools/RFdiffusion.md)
- Tool: [PyMOL](../tools/PyMOL.md)
