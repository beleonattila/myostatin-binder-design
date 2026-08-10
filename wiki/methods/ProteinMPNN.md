# ProteinMPNN

**Stage 2 — sequence design.** Takes a backbone (from [RFdiffusion](RFdiffusion.md)) and assigns amino acid sequences predicted to fold into it. This is the *inverse-folding* step.

| Field | Value |
|-------|-------|
| Paper | Dauparas et al., "Robust deep learning–based protein sequence design using ProteinMPNN", *Science* 378, 49–56 (2022) |
| Lab | Baker lab, IPD |
| Repo | github.com/dauparas/ProteinMPNN |
| Type | Graph message-passing neural network (encoder–decoder) |
| Input | Backbone PDB + which chains to design/fix |
| Output | FASTA sequences with per-sequence scores |
| Needs GPU | No (fast on CPU) |

Prerequisite theory: [inverse folding](../concepts/inverse-folding.md). Upstream: [RFdiffusion](RFdiffusion.md). Downstream: [ESMFold](ESMFold.md).

---

## The problem it solves

RFdiffusion gave you a **shape** with no sequence. The question ProteinMPNN answers: *given this backbone geometry, what amino acid sequence will fold into it?* This is **inverse folding** — the inverse of what AlphaFold/ESMFold do (sequence → structure). See [inverse folding](../concepts/inverse-folding.md).

Formally it models `p(sequence | backbone)` and factorises it autoregressively: `p(s|x) = Π_i p(s_i | x, s_{<i})`.

---

## Architecture, correctly stated

ProteinMPNN is a **message-passing neural network** built on the "Structured Transformer" idea (Ingraham et al. 2019), with two design choices that make it work well:

1. **Geometric input features.** The backbone is represented as a graph: nodes are residues, edges connect each residue to its ~30–48 nearest neighbours. Edge features encode **inter-atomic distances between N, Cα, C, O, and a virtual Cβ**. Using distances (rather than only dihedral angles/orientations) gave the biggest single accuracy jump — sequence recovery rose from ~41% to ~49% in ablations. The encoder does message passing over this graph, updating both node **and edge** features.

2. **Order-agnostic autoregressive decoding.** A standard autoregressive model decodes left-to-right (N→C), so early positions can't see later sequence context. ProteinMPNN is trained with **random decoding orders**, so at inference it can decode in any order and every position conditions on all others already decoded. This is the key trick and part of why it beats Rosetta (52.4% vs 32.9% native sequence recovery on native backbones).

The randomised order is implemented by adding noise to a residue mask and sorting it — a detail, but it's the mechanism behind "order-agnostic."

---

## Why it beats physics-based design (Rosetta)

Rosetta designs sequences by Monte Carlo optimisation over an energy function — slow, and only as good as the energy terms. ProteinMPNN learned sequence–structure relationships directly from the PDB, so it is **much faster** and **more accurate** at recovering native-like, well-expressing sequences. Experimentally, ProteinMPNN sequences showed dramatically improved soluble expression and correct folding vs prior methods. For binder pipelines it is now the default sequence-design step downstream of RFdiffusion.

---

## Parameters you'll set

| Parameter | Controls | Value |
|-----------|----------|-------|
| `--pdb_path` | the RFdiffusion backbone (binder + target) | one design at a time / batch |
| `--pdb_path_chains_to_design` | which chain gets a new sequence | the **binder** chain only |
| (fixed chains) | target chain kept native | the **[GDF8](../molecules/GDF8.md)** chain |
| `--num_seq_per_target` | sequences per backbone | 8 to start, 32–64 for real |
| `--sampling_temp` | diversity | `0.1` conservative; `0.2` if outputs collapse |

**Fix the target, design the binder.** You do not redesign the myostatin surface — its sequence is real and must stay. Only the newly generated binder chain receives sequences.

---

## Reading the output

- FASTA, N sequences per backbone, each with a **score** = the model's negative log-likelihood (in ProteinMPNN's convention, **lower/more-negative is better** — the model is more confident this sequence encodes the backbone).
- At low temperature the sequences can be nearly identical; raise temperature for diversity. You want a few genuinely different candidates per backbone to give the validation step something to discriminate.
- No stop codons, no `X`. Length matches the binder.

The score is **not** proof the sequence folds correctly — that's what the next step tests.

---

## What to be able to say

*"ProteinMPNN is a graph message-passing inverse-folding network with order-agnostic decoding; I used it to assign sequences to each RFdiffusion backbone, fixing the myostatin target chain and designing only the binder, sampling several sequences per backbone for downstream validation."*

---

## Links

- Theory: [inverse folding](../concepts/inverse-folding.md)
- Upstream input: [RFdiffusion](RFdiffusion.md)
- Downstream test: [ESMFold](ESMFold.md) / [AlphaFold2](AlphaFold2.md)
- The chain you fix: [GDF8](../molecules/GDF8.md)
