# Inverse Folding

The theory behind [ProteinMPNN](../methods/ProteinMPNN.md). Understanding why this is a *separate* problem from folding is the key conceptual gain.

---

## Folding vs inverse folding

| | Folding | Inverse folding |
|--|---------|-----------------|
| Question | Given a **sequence**, what **structure**? | Given a **structure**, what **sequence**? |
| Direction | sequence → structure | structure → sequence |
| Tools | AlphaFold2, ESMFold, RoseTTAFold | ProteinMPNN, ESM-IF, Rosetta design |
| In this project | validation ([ESMFold](../methods/ESMFold.md)) | design ([ProteinMPNN](../methods/ProteinMPNN.md)) |

[RFdiffusion](../methods/RFdiffusion.md) hands you a backbone with **no sequence**. Inverse folding fills it in. Then folding (validation) checks the fill-in was correct. The pipeline literally runs the arrow both ways: inverse-fold to design, fold to validate.

---

## Why it's a hard, distinct problem

Many sequences can fold into the same backbone (the mapping is many-to-one), but most random sequences fitting the geometry will **not** actually fold, express, or stay soluble. Inverse folding is the problem of finding sequences that are not just geometrically compatible but **foldable and stable**. It is not "read off the shape"; it is a learned (or energy-optimised) prediction of `p(sequence | structure)`.

Formally, autoregressive inverse folding factorises:
```
p(s | x) = Π_i p(s_i | x, s_{<i})
```
sequence `s` given backbone `x`, one residue at a time, each conditioned on the structure and previously-decided residues.

---

## How ProteinMPNN does it (mechanism recap)

Full detail on the [ProteinMPNN page](../methods/ProteinMPNN.md); the inverse-folding-relevant essentials:

- **Structure as a graph:** residues = nodes, edges to nearest neighbours, edge features from inter-atomic distances (N, Cα, C, O, virtual Cβ). Message passing builds a representation of each residue's structural environment.
- **Order-agnostic decoding:** residues are decoded in random order so each position conditions on all others already placed — not just N-terminal ones. This is the trick that lifts it above naive left-to-right models.
- Learned end-to-end from the PDB, so it captures real sequence–structure statistics rather than a hand-built energy function.

---

## Why learned inverse folding beats Rosetta

Rosetta design searches sequence space by Monte Carlo against a physics-based energy function — slow and only as good as the force field. ProteinMPNN predicts favourable sequences directly from learned patterns: **52.4% vs 32.9% native sequence recovery** on native backbones, far faster, and experimentally its sequences express solubly and fold correctly at much higher rates. This is why the RFdiffusion→ProteinMPNN pairing became the default.

---

## Temperature and sampling (design knob)

Because it's a probabilistic model, you **sample** sequences. Sampling **temperature** controls diversity:
- low (0.1): conservative, near the model's argmax, sequences similar to each other;
- higher (0.2+): more diverse, exploring alternative solutions for the same backbone.

You sample several per backbone so the [validation step](validation-metrics.md) has multiple candidates to discriminate — some sequences will encode the backbone better than others, and only the refold test reveals which.

---

## Links

- The tool: [ProteinMPNN](../methods/ProteinMPNN.md)
- The inverse direction (validation): [ESMFold](../methods/ESMFold.md), [AlphaFold2](../methods/AlphaFold2.md)
- Where the backbone comes from: [RFdiffusion](../methods/RFdiffusion.md)
- Pipeline role: [de novo binder design](de-novo-binder-design.md)
