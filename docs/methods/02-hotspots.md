# Step 2 · Hotspot identification

**Goal:** tell RFdiffusion *where* on myostatin the binder must dock — the few
knuckle residues it must contact.

**Environment:** PyMOL (no GPU).

This is the most scientifically critical step. See
[the epitope](../background/epitope.md) for the biology; this page is the method.

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

The printed residues are your **data-driven** hotspot list. Cross-check against
the provisional list (Ile33/Ala34/Pro35/Tyr38, Met84/Leu85/Tyr86/Phe87); they
should overlap heavily.

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
patch. Favor Ile33, Ala34, Pro35, Leu85, Tyr86, Phe87.

## Pitfalls

- **Numbering must match the extracted PDB.** Re-open `myostatin_target.pdb` and
  confirm the residue numbers match 5JI1's scheme after extraction (extraction can
  renumber). RFdiffusion reads literal numbers.
- **Chain ID must match.** If you renamed the chain to `A`, hotspots are `A33`…
- **Drop unresolved residues** — a hotspot in a missing loop is useless.

Save the final list to `hotspots/hotspot_residues.txt`.
→ Continue to [Step 3 · RFdiffusion](03-rfdiffusion.md).
