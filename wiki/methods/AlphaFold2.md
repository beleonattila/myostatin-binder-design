# AlphaFold2 (and AF2-multimer)

**Stage 3, stronger variant — interface validation.** The higher-accuracy alternative to [ESMFold](ESMFold.md) for confirming your top designs, and the standard way to score the binder–target *interface*.

| Field | Value |
|-------|-------|
| Paper | Jumper et al., *Nature* 596, 583–589 (2021); AF-Multimer: Evans et al., bioRxiv 2021 |
| Lab | DeepMind |
| Basis | MSA + pairwise representation → Evoformer → structure module |
| Input | Sequence(s) (+ MSA); multimer mode takes multiple chains |
| Output | Structure + pLDDT + PAE; multimer adds iPTM |
| Access | ColabFold (practical), local, or various servers |
| Needs GPU | Yes (or Colab) |

You already know AF2 from your thesis (AlphaFold2 → PyMOL evaluation of β-lactamase candidates), so this page focuses on what's *different* in a binder-design context.

---

## Why it reappears in a design pipeline

In your thesis AF2 was a **predictor** — you folded candidate enzymes and checked active sites. Here it plays the same mechanical role but for a different question: **does the designed binder fold, and does it dock onto the target the way it was designed to?** The single-chain use is identical to what you did before. The new and important mode is **AF2-multimer**: fold the **binder + target together** and read out interface confidence.

---

## The metrics that matter for binders

Beyond pLDDT and pTM (see [validation metrics](../concepts/validation-metrics.md)):

- **PAE (Predicted Aligned Error)** — an N×N matrix; entry (i,j) is the expected error in residue i's position when the structure is aligned on residue j. **Low cross-chain PAE blocks** (binder rows vs target columns) mean the model is confident about the *relative placement* of binder and target — i.e. confident about the interface. This is more informative for binders than pLDDT, which only reports local confidence.
- **iPTM (interface pTM)** — AF2-multimer's single-number interface confidence. Combined scores like `0.8·iPTM + 0.2·pTM` are commonly used to rank binder designs. Higher is better; thresholds are target-dependent but iPTM > 0.5–0.7 is a typical "worth pursuing" range.

The RFdiffusion paper and standard binder workflows use **AF2 (often single-sequence / initial-guess AF2) refolding + pAE/iPTM as the in silico success filter** before synthesis.

---

## Practical route: ColabFold

For a no-HPC setup, **ColabFold** (MMseqs2 for fast MSAs + AF2) in a notebook is the pragmatic tool. For binder scoring you can run AF2-multimer on the binder+target sequences and inspect the PAE plot and iPTM. Budget: AF2-multimer is slow, so run it only on the **ESMFold survivors**, not all designs.

---

## ESMFold-first, AF2-confirm

| Step | Tool | Scope |
|------|------|-------|
| Screen all designs | [ESMFold](ESMFold.md) | fast, monomer self-consistency |
| Confirm top ~5 | AF2-multimer (ColabFold) | interface, iPTM, cross-chain PAE |

Using both, and knowing *why* each is used where, is a more sophisticated story than "I ran AlphaFold."

---

## A caveat worth stating

AF2 was trained on natural proteins with MSAs. **De novo designs have shallow or no MSAs**, which can make AF2 confidence metrics behave differently than on natural proteins. This is a live methodological caveat in the field and part of why single-sequence approaches (ESMFold, single-sequence AF2 "initial guess") are used for designs. Naming this shows you understand the tools' assumptions rather than treating them as oracles.

---

## Links

- Fast first-pass alternative: [ESMFold](ESMFold.md)
- Metric definitions (PAE, iPTM, pLDDT, pTM): [validation metrics](../concepts/validation-metrics.md)
- Downstream analysis: [PyMOL](PyMOL.md)
- What it validates: [ProteinMPNN](ProteinMPNN.md) sequences on [RFdiffusion](RFdiffusion.md) backbones
