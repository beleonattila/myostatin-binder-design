# GDF11

**The hotspot proxy.** Not part of your design directly, but the molecule whose receptor complex supplies the interface geometry you cannot get from GDF8 itself.

| Field | Value |
|-------|-------|
| Names | GDF-11, BMP-11 |
| Human UniProt | O95390 |
| Family | TGF-β superfamily, activin class |
| Relationship to GDF8 | ~90% sequence identity in the mature C-terminal domain |
| Key structure here | [6MAC](6MAC.md) — GDF11:ActRIIB:ALK5 ternary complex |

---

## Why it's in this project

GDF11 and GDF8 are the two most closely related members of their subfamily. In the mature growth-factor domain — the part that engages receptors — they are about 90% identical, and they share the same receptor set: type II ActRIIA/ActRIIB and type I ALK4/5. Critically, a **crystal structure of GDF11 bound to both receptors exists** ([6MAC](6MAC.md)), whereas no GDF8:ActRIIB structure does.

That lets you do the following transfer:

1. Take the GDF11:ActRIIB interface from 6MAC.
2. Identify GDF11 residues contacting ActRIIB.
3. Map to the equivalent GDF8 positions (near-identical, so mostly a 1:1 mapping).
4. Use those GDF8 positions as hotspots for [RFdiffusion](../tools/RFdiffusion.md).

---

## The honest caveats

The 90% identity is in the mature domain overall; it is **not** uniform. The literature is explicit that the residues that *do* differ between GDF8 and GDF11 concentrate at the **type I (wrist/fingertip)** interface, and these differences drive GDF11's higher potency and stronger ALK5 engagement. For your purposes:

- **Good news:** the **type II (ActRIIB/knuckle) epitope** — the one you are targeting — is the *more* conserved of the two. Transferring type II contacts from GDF11 to GDF8 is well justified.
- **Caveat to state:** you are still using a proxy. Verify each transferred residue is actually conserved (identical or conservative substitution) between GDF8 and GDF11 before trusting it. Flag any that aren't.

This is exactly the kind of nuance a protein-design interviewer will probe. Being the one who raises it first is the strong position.

---

## Distinguishing the two epitopes (do not confuse them)

| Epitope | Receptor | Character | Conservation GDF8↔GDF11 | Your interest |
|---------|----------|-----------|-------------------------|---------------|
| Knuckle (type II) | [ActRIIB](ActRIIB.md) | convex, outer fingertips | high | **target** |
| Wrist (type I) | ALK4/5 | concave, pre-helix/dimer interface | lower (potency determinants live here) | avoid |

If your hotspots drift toward the wrist, you are (a) targeting the wrong site and (b) landing exactly where GDF8 and GDF11 differ most — a double error.

---

## Links

- The target it stands in for: [GDF8](GDF8.md)
- The structure that makes it useful: [6MAC](6MAC.md)
- The receptor at the shared epitope: [ActRIIB](ActRIIB.md)
- Interface theory: [PPI hotspots](../concepts/PPI-hotspots.md)
- Fold context: [TGF-β superfamily](../concepts/TGF-beta-superfamily.md)
