# Follistatin-288 (Fst288)

**The natural antagonist.** Context molecule: it is what sits on the myostatin surface in [3HH2](3HH2.md), and understanding it tells you why 3HH2 is not a usable RFdiffusion target and what "blocking myostatin" looks like when nature does it.

| Field | Value |
|-------|-------|
| Parent protein | Follistatin (FST), human UniProt P19883 |
| Isoform | FS288 — the 288-residue splice variant (vs FS315) |
| Domains | N-terminal domain (ND) + three follistatin domains (FSD1–3) |
| Function | High-affinity antagonist of activins, myostatin, GDF11, some BMPs |
| Key structure here | [3HH2](3HH2.md) — GDF8:Fst288 |

---

## What follistatin does to myostatin

Follistatin is an endogenous, secreted antagonist. It neutralises TGF-β–class ligands not by competing for a single site but by **wrapping around the ligand**: two follistatin molecules encircle one ligand dimer, and between them they **bury both the type I and type II receptor-binding epitopes simultaneously**. The N-terminal domain is the specificity element — it undergoes conformational rearrangement to fit a given ligand and inserts into the type I (wrist) site, while the FSD domains cover the type II (knuckle) site.

The consequence that matters for you: in any GDF8:follistatin structure, **the ActRIIB epitope you want to design against is physically occupied by follistatin.** You cannot read the ActRIIB contacts off it, and you cannot use it as a clean design target.

---

## Two therapeutic lessons embedded here

1. **Occlusion is a valid antagonism mechanism.** Follistatin doesn't need to bind the receptor site with receptor-like chemistry; it just needs to cover it. Your de novo binder is, conceptually, a minimal synthetic mimic of this idea — occupy the knuckle, deny ActRIIB access. You are compressing what follistatin does with a multidomain 288-residue protein into a 50–70 residue miniprotein aimed at one epitope.
2. **FS288 vs FS315.** The two splice isoforms differ mainly in heparin binding and cell-surface retention (FS288 binds heparin more avidly, is more cell-associated). Not central to your design, but it explains why "follistatin-288" specifically appears in the structure name.

---

## Why it disqualifies 3HH2 as a target (but keeps it useful)

Because follistatin buries the epitope, [3HH2](3HH2.md) is:

- **Not a target** — the surface RFdiffusion needs is covered, and separately the structure's [validation scores](../concepts/validation-metrics.md) are poor.
- **Still a cross-check** — the GDF8 residues follistatin's FSD domains contact overlap partially with the ActRIIB knuckle epitope. If your [6MAC](6MAC.md)-derived hotspots land in a totally different region than the follistatin footprint, that's a warning sign worth investigating.

---

## Links

- The complex it forms: [3HH2](3HH2.md)
- The ligand it blocks: [GDF8](GDF8.md)
- The receptor it mimics the exclusion of: [ActRIIB](ActRIIB.md)
- The design analogy: [de novo binder design](../concepts/de-novo-binder-design.md)
