# Step 2 · Hotspot identification

**Goal:** tell RFdiffusion *where* on myostatin the binder must dock — the few
knuckle residues it must contact.

**Environment:** PyMOL (no GPU).

This is the most scientifically critical step. See
[the epitope](../concepts/epitope.md) for the biology; this page is the method.

## Why homology transfer

No GDF8:ActRIIB structure exists, and our target 5JI1 is **apo**, so the ActRIIB
footprint cannot be read off it directly. We borrow it from **6MAC** — the
**GDF11:ActRIIB:ALK5** ternary complex (Goebel et al., *PNAS* 2019). GDF11 is
**~90 % identical to GDF8 in the mature domain** and engages the same type II
receptor, so its ActRIIB contacts transfer with high confidence. We superpose apo
GDF8 (5JI1) onto the GDF11 chain of 6MAC and read off the GDF8 residues that fall
under ActRIIB.

(We first considered the activin A:ActRIIB complex 1NYS; **6MAC is the stronger
proxy** because GDF11 is far closer to GDF8 than activin is.)

## Procedure (PyMOL)

```python
fetch 5ji1, async=0          # apo GDF8 (the target)
fetch 6mac, async=0          # GDF11 + ActRIIB (type II) + ALK5 (type I)

# Identify chains in 6MAC first: GDF11 = cystine-knot ligand dimer;
# ActRIIB ectodomain = the smaller ~100-aa three-finger-toxin fold; ALK5 = type I.
# We want the type II (ActRIIB) footprint only — ignore ALK5 (type I / wrist).

# 1. Read GDF11's ActRIIB contacts:
select gdf11_epitope, byres (6mac and chain <GDF11_CHAIN>) within 4.5 of (6mac and chain <ACTRIIB_CHAIN>)
iterate gdf11_epitope and name CA, print(f"{resi} {resn}")

# 2. Superpose apo GDF8 onto GDF11, then read the spatially-equivalent GDF8 residues:
align (5ji1 and polymer), (6mac and chain <GDF11_CHAIN>)
select knuckle, byres (5ji1 and polymer) within 4.5 of (6mac and chain <ACTRIIB_CHAIN>)
iterate knuckle and name CA, print(f"{resi} {resn}")
show sticks, knuckle
```

The printed residues are your **data-driven** hotspot list.

!!! note "Use `super`, not `align`"
    `align` anchors on a sequence alignment first; for homologs that lets the
    flexible loops drag the superposition. `super` is structure-based with
    outlier rejection — here it gives 0.70 Å over 81 residues.

### Rank by buried area, not by distance

A 4.5 Å cutoff is a yes/no test: it scores a glancing backbone brush the same as
a sidechain fully engulfed by the receptor. Compute **ΔSASA** instead — each
residue's solvent-accessible surface free vs. covered by ActRIIB:

```python
cmd.set('dot_solvent', 1)
buried = cmd.get_area('gdf8 and resi 85') - cmd.get_area('complex and chain A and resi 85')
```

This is what separates a real hotspot from a bystander, and it is what caught the
two errors in this project's provisional list (see below).

**Confirm conservation (the step that makes the transfer defensible):** for each
transferred position, verify it is **identical or a conservative substitution**
between GDF11 and GDF8 (they are ~90 % identical here, so most are). Flag any that
aren't before trusting them — this turns "I assumed it transfers" into "I verified
each contact residue is conserved."

**Optional corroboration:** repeat the transfer with **7MRZ** (a second
GDF11:ActRIIB structure, 2022). Residues in the ActRIIB footprint in *both* 6MAC
and 7MRZ are trustworthy; disagreements deserve a closer look before you commit.

## Choosing the final set

Pick the **5–8 strongest hydrophobic/aromatic positions** — RFdiffusion's
`ppi.hotspot_res` wants the residues the binder *must* contact, not the whole
patch. Spread them across the epitope's two lobes (the finger 1–2 loop and the
finger 3 convex face), or a binder can satisfy the constraint while covering only
half the receptor footprint.

## Result for this project

Run `python scripts/02_hotspots.py` (env `esm`) to reproduce everything below.

**Consensus footprint (21 residues, in both 6MAC and 7MRZ):** E25, I33, A34, P35,
K36, R37, Y38, K39, S80, P81, I82, N83, M84, L85, F87, E91, I93, Y95, K97, V102,
D104. 7MRZ adds only two peripheral positions (78, 105) — crystal-form noise.

**Final hotspots** → `hotspots/hotspot_residues.txt`:

```
ppi.hotspot_res=[A33,A34,A85,A87,A93,A95]
```

| Residue | Buried (Å²) | % of free surface | Lobe |
|---|---|---|---|
| Ile33 | 46 | 81 % | finger 1–2 loop |
| Ala34 | 40 | 99 % | finger 1–2 loop |
| Leu85 | 57 | 100 % | finger 3 |
| Phe87 | 47 | 59 % | finger 3 |
| Ile93 | 53 | 62 % | finger 3 |
| Tyr95 | 78 | 50 % | finger 3 |

**Two corrections to the provisional list — both worth understanding:**

- **Met84 is not a hotspot.** It buries **0.2 Å² (1 %)** against ActRIIB because
  it points into GDF8's own hydrophobic core. It is *near* the interface in
  space, which is exactly why a distance cutoff alone would have kept it.
- **Tyr86 is on the wrong receptor.** It is not in the ActRIIB footprint at all —
  in 6MAC it faces the **type I (ALK5)** site. Reading contacts against the wrong
  chain of a ternary complex is the easiest mistake to make here; check which
  receptor each contact belongs to.

Ile93 and Tyr95 were *missing* from the provisional list, and Tyr95 buries more
surface than any other residue in the footprint.

**Verification that licenses the homology transfer:** 20 of the 21 footprint
residues are the **identical amino acid** in GDF8 and GDF11 (overall mature-domain
identity 91 %). The one exception, Gln91→Glu, is conservative and buries 23 %.
Separately, **no footprint residue is occluded by the partner monomer** in the
myostatin dimer (max 5 %), so targeting the extracted monomer does not
misrepresent the epitope.

## Pitfalls

- **Numbering must match the extracted PDB.** Re-open `myostatin_target.pdb` and
  confirm the residue numbers match 5JI1's scheme after extraction (extraction can
  renumber). RFdiffusion reads literal numbers.
- **Chain ID must match.** If you renamed the chain to `A`, hotspots are `A33`…
- **Drop unresolved residues** — a hotspot in a missing loop is useless.

Save the final list to `hotspots/hotspot_residues.txt`.
→ Continue to [Step 3 · RFdiffusion](03-rfdiffusion.md).
