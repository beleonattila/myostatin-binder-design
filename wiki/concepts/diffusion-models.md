# Diffusion Models (for proteins)

The generative-modelling theory behind [RFdiffusion](../methods/RFdiffusion.md). You don't need to re-derive DDPMs, but you should be able to explain, correctly, why "denoising" produces new proteins.

---

## The core idea in one line

A diffusion model learns to **reverse a gradual noising process**: train a network to remove a little noise, then at generation time start from pure noise and remove it step by step until a realistic sample emerges.

---

## Forward process (training-time corruption)

Take a real data point — for proteins, a real backbone structure from the PDB. Over **T steps** (~200 in RFdiffusion), progressively corrupt it:

- **Translations** (Cα positions): add Gaussian noise, step by step, until coordinates are random.
- **Orientations** (residue frames): perturb rotations via Brownian motion **on the manifold of rotation matrices** (you can't just add Gaussian noise to a rotation — it has to stay a valid rotation, hence the manifold treatment).

After T steps the structure is indistinguishable from noise. This forward process is **fixed** (no learning) — it just defines the corruption schedule.

## Reverse process (the learned part)

Train a network to predict, at each noise level, the **clean structure** (or equivalently the noise to remove). Because the forward process is known, each denoising step is well-defined. The network learns the reverse of corruption: noise → slightly-less-noise → … → structure.

## Generation (inference)

Start from **random residue frames** and run the learned reverse process for 50–200 steps. Out comes a novel, physically plausible backbone that was never in the training set — a *sample* from the distribution of protein-like structures, not a retrieval.

---

## Why RFdiffusion fine-tunes RoseTTAFold instead of training fresh

Early from-scratch protein diffusion models underperformed — protein backbone geometry and sequence–structure coupling are hard to learn from noise alone. The RFdiffusion move: **start from RoseTTAFold**, a network that already encodes rich structural priors from having learned to predict structure, and fine-tune it (minimal architectural change) to denoise. It inherits "what proteins look like" for free.

Framing difference:
- RoseTTAFold input = **sequence** → predict structure.
- RFdiffusion input = **noised frames** (coords + orientations) → predict clean structure.

## Self-conditioning

RFdiffusion feeds the model's **previous-step prediction back in as a template** at the next step. This keeps the denoising trajectory coherent (the model commits to a developing fold rather than wandering), and measurably improves results. Worth knowing by name.

---

## Conditioning = how you steer generation

Unconditional generation makes random plausible proteins. You want **conditional** generation — proteins that satisfy constraints:

- **Target + hotspots** (your case): generate a binder backbone contacting a specified surface.
- **Motif scaffolding:** hold a functional motif fixed, build a protein around it.
- **Symmetry:** enforce Cn/Dn symmetry for oligomers.

Conditioning is what turns a generative curiosity into a design tool. In the binder case, the fixed target and the [hotspot residues](PPI-hotspots.md) bias every denoising step toward backbones that dock at the epitope.

---

## Analogy (accurate, not just cute)

Image diffusion models (Stable Diffusion, etc.) start from noise and denoise into an image, optionally conditioned on a text prompt. RFdiffusion is the structural analogue: denoise into a **backbone**, conditioned on a **target + hotspots** instead of a text prompt. Same generative principle, different data manifold (SE(3) frames instead of pixels). The RFdiffusion authors make this analogy explicitly.

---

## What to be able to say

*"RFdiffusion is a denoising diffusion model over residue frames — Gaussian noise on translations, Brownian motion on the rotation manifold for orientations — built by fine-tuning RoseTTAFold so it inherits PDB structural priors, with self-conditioning for trajectory coherence; conditioning on a target and hotspots steers generation toward binder backbones."*

---

## Links

- The tool: [RFdiffusion](../methods/RFdiffusion.md)
- What steers it: [PPI hotspots](PPI-hotspots.md)
- Pipeline role: [de novo binder design](de-novo-binder-design.md)
