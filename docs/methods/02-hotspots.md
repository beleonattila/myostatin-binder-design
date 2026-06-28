# Step 2 · Hotspot identification

**Goal:** tell RFdiffusion *where* on myostatin the binder must dock — the few
knuckle residues it must contact.

**Environment:** PyMOL (no GPU).

This is the most scientifically critical step. See
[the epitope](../background/epitope.md) for the biology; this page is the method.

## Why homology transfer

3HH2 has **no receptor**, so the ActRIIB footprint cannot be read off it directly.
We superpose myostatin onto activin A in the ActRIIB complex (**1NYS**) and read
off the myostatin residues that fall under the receptor.

## Procedure (PyMOL)

```python
fetch 3hh2, async=0          # myostatin (A,B) + follistatin (C,D)
fetch 1nys, async=0          # activin A + ActRIIB ectodomain

# Identify chains in 1NYS first: ActRIIB ectodomain = the smaller ~100-aa
# three-finger-toxin fold; activin = the cystine-knot ligand.

align (3hh2 and chain A), (1nys and chain <ACTIVIN_CHAIN>)

select knuckle, byres (3hh2 and chain A) within 5 of (1nys and chain <ACTRIIB_CHAIN>)
iterate knuckle and name CA, print(f"{resi} {resn}")
show sticks, knuckle
```

The printed residues are your **data-driven** hotspot list. Cross-check against
the provisional list (Ile33/Ala34/Pro35/Tyr38, Met84/Leu85/Tyr86/Phe87); they
should overlap heavily.

**Optional corroboration:** follistatin (chains C/D) in 3HH2 buries the type II
site; `byres (chain A) within 5 of (chain C+D)` intersected with the homology
footprint highlights the receptor-specific knuckle residues.

## Choosing the final set

Pick the **5–8 strongest hydrophobic/aromatic positions** — RFdiffusion's
`ppi.hotspot_res` wants the residues the binder *must* contact, not the whole
patch. Favor Ile33, Ala34, Pro35, Leu85, Tyr86, Phe87.

## Pitfalls

- **Numbering must match the extracted PDB.** Re-open `myostatin_target.pdb` and
  confirm residues still read 1…109 (extraction can renumber). RFdiffusion reads
  literal numbers.
- **Chain ID must match.** If you renamed the chain to `A`, hotspots are `A33`…
- **Drop unresolved residues** — a hotspot in a missing loop is useless.

Save the final list to `hotspots/hotspot_residues.txt`.
→ Continue to [Step 3 · RFdiffusion](03-rfdiffusion.md).
