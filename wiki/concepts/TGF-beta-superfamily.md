# TGF-β Superfamily (the fold and its epitopes)

The structural context for the whole target side of the project. If you understand this fold and its two receptor epitopes, everything about [GDF8](../molecules/GDF8.md), [GDF11](../molecules/GDF11.md), [ActRIIB](../molecules/ActRIIB.md), and the hotspots follows.

---

## The family

The TGF-β superfamily is a large group (30+ human ligands) of secreted signalling proteins: TGF-βs, activins/inhibins, BMPs, GDFs (including GDF8/myostatin and GDF11), and others. They regulate development, tissue homeostasis, immune modulation, and — for the GDF8/activin branch — skeletal muscle mass. They all signal through the same **two-receptor logic**: type II + type I serine/threonine kinase receptors, converging on SMADs.

---

## The cystine-knot growth-factor fold

Every mature ligand shares a fold built around a **cystine knot**: three disulfide bonds, two forming a ring through which a third passes, clamping the core. Around this knot the chain splays into elongated **β-strand "fingers"** with an α-helix (the "wrist") on the opposite side. The common metaphor:

- **Fingers** — two β-hairpin extensions (finger 1, finger 2).
- **Palm / knuckle** — the cystine-knot core and the convex outer surface of the fingers.
- **Wrist** — the central α-helix region and the pre-helix loop.
- **Heel** — the dimer interface region.

Mature ligands are almost always **disulfide-linked homodimers**, giving a two-fold symmetric, butterfly-shaped molecule.

---

## The two receptor epitopes (the crux for design)

The heterotetrameric signalling complex places receptors at two distinct ligand surfaces:

| Epitope | Location | Receptor type | Character | For myostatin |
|---------|----------|---------------|-----------|---------------|
| **Knuckle** | convex outer fingertips | **Type II** | shallow, hydrophobic-leaning | [ActRIIB](../molecules/ActRIIB.md) — **your target** |
| **Wrist** | concave, pre-helix + dimer interface | **Type I** | groove, fingertip-adjacent | ALK4/5 — avoid |

**Type II binds first** (higher intrinsic affinity), then recruits **type I** into the concave wrist site; the type II kinase trans-phosphorylates the type I kinase to fire the signal.

For your project:
- You target the **knuckle / type II** site to block ActRIIB.
- The knuckle is the **more conserved** epitope between GDF8 and GDF11, which is what makes the [6MAC](../molecules/6MAC.md) hotspot transfer defensible.
- The **wrist** is where GDF8 and GDF11 differ most (potency determinants) — stay away from it, both because it's the wrong receptor and because that's where your GDF11 proxy is least representative.

---

## Antagonism strategies in this family (context for your design)

Nature blocks these ligands several ways, and your binder is a minimal version of one of them:

- **Antagonist proteins** ([follistatin](../molecules/follistatin-288.md), FSTL3, WFIKKN, GASP1) wrap the ligand and occlude receptor sites.
- **Prodomain latency** — the cleaved prodomain can cage the mature ligand (pro-/latent myostatin).
- **Receptor traps** — soluble receptor-Fc decoys ([ActRIIB](../molecules/ActRIIB.md)-Fc) sequester ligand.
- **Your approach** — a de novo miniprotein that occupies one epitope. Conceptually the "occlude the knuckle" strategy compressed into ~60 residues.

---

## Links

- The target ligand: [GDF8](../molecules/GDF8.md)
- The proxy: [GDF11](../molecules/GDF11.md)
- The receptor: [ActRIIB](../molecules/ActRIIB.md)
- Natural antagonist: [follistatin-288](../molecules/follistatin-288.md)
- Where the epitope becomes hotspots: [PPI hotspots](PPI-hotspots.md)
