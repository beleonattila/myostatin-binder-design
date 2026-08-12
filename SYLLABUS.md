# Syllabus — De Novo Miniprotein Binder Design Against Myostatin

A structured curriculum for gaining demonstrable, defensible competence in RFdiffusion + ProteinMPNN through a single coherent project: designing de novo binders to the ActRIIB-binding epitope of myostatin (GDF-8).

This is not a "click the Colab and get a PDB" exercise. The goal is that you can defend every step in an interview with a computational protein design group. The syllabus is organised so that each module produces both an *artifact* (a file, a structure, a score) and a *sentence you can say out loud* about what you did and why.

**Companion docs:** [docs/index.md](docs/index.md) — every molecule and method below has a dedicated theory page. Read the linked page before running the corresponding step.

---

## How to use this document

Work top to bottom. Each module has:
- **Learn** — the theory you must hold before touching a keyboard (links to `docs/`)
- **Do** — the concrete action
- **Produce** — the artifact that proves the module is done
- **Defend** — the one-sentence claim you should be able to make and back up

Do not skip the *Learn* column. The single most common way this project fails is running RFdiffusion against the wrong surface because the biology was skipped. The tools are easy; the target definition is where the science lives.

---

## Module 0 — Orientation and Compute

**Learn:** The four-stage pipeline logic — why backbone generation, sequence design, and folding validation are three separate problems solved by three separate tools. See [de novo binder design](docs/concepts/de-novo-binder-design.md).

**Do:**
- Run `nvidia-smi` in PowerShell. Record GPU model and VRAM.
- Check `wsl --status` and `wsl --list --verbose`.
- Decide the execution path: local WSL2+CUDA if you have ≥8 GB VRAM, else Colab for the RFdiffusion step only.

**Produce:** A one-line note in `CONTEXT.md` recording your compute decision.

**Defend:** *"RFdiffusion needs a GPU because it runs 50–200 forward passes of a fine-tuned RoseTTAFold per design; ProteinMPNN and ESMFold I can offload to CPU or a REST API."*

---

## Module 1 — The Biology of the Target

**Learn:**
- [TGF-β superfamily](docs/concepts/TGF-beta-superfamily.md) — the structural fold family myostatin belongs to (cystine knot, "hand" topology, wrist and knuckle epitopes).
- [GDF8 (myostatin)](docs/molecules/GDF8.md) — the ligand itself: dimer, latency, receptor usage.
- [ActRIIB](docs/molecules/ActRIIB.md) — the type II receptor whose binding you want to block.

**Do:** Read the three pages. Draw, by hand, the myostatin dimer with the two type II (knuckle) and two type I (wrist/fingertip) receptor sites marked. You cannot design a competitive binder if you cannot point to the epitope you are competing with.

**Produce:** A labelled sketch (photo it into the vault). Crude is fine; the point is that the mental model is yours.

**Defend:** *"Myostatin signals by recruiting two ActRIIB (type II) and two ALK4/5 (type I) receptors; a binder that occludes the type II knuckle epitope is a competitive antagonist."*

---

## Module 2 — Choosing and Cleaning the Structure

**Learn:**
- [5JI1](docs/molecules/5JI1.md) — apo GDF8, your RFdiffusion target and why apo matters.
- [3HH2](docs/molecules/3HH2.md) — the GDF8:follistatin-288 complex, and why its validation scores disqualify it as a target.
- [follistatin-288](docs/molecules/follistatin-288.md) — what is sitting on the surface in 3HH2 and why that occludes the epitope.
- [validation metrics](docs/concepts/validation-metrics.md) — how to read a wwPDB slider (Rfree, clashscore, Ramachandran, sidechain, RSRZ).

**Do:**
- Download 5JI1 from RCSB → `data/raw/`.
- In PyMOL: strip HETATM/waters, keep only the GDF8 chain(s), inspect for missing loops.
- Save cleaned target → `data/prepared/myostatin_target.pdb`.

**Produce:** A clean, single-molecule target PDB and a note on any missing residues near the epitope.

**Defend:** *"I used apo-GDF8 (5JI1, 2.25 Å) as the target so the ActRIIB face is unoccupied, rather than 3HH2 whose clashscore and sidechain-outlier percentiles make its interface geometry unreliable."*

---

## Module 3 — Hotspot Identification (the scientific crux)

**Learn:**
- [PPI hotspots](docs/concepts/PPI-hotspots.md) — what a hotspot residue is (ΔΔG on alanine mutation), why interfaces are driven by a few residues.
- [GDF11](docs/molecules/GDF11.md) and [6MAC](docs/molecules/6MAC.md) — the GDF11:ActRIIB:ALK5 ternary complex you will borrow interface geometry from, and the 90% mature-domain identity that licenses the transfer.

**Do:**
- Superpose 5JI1 (GDF8) onto the GDF11 chain of 6MAC in PyMOL.
- Select GDF11 residues within 4–5 Å of ActRIIB; read them off.
- Map them onto 5JI1 numbering via sequence alignment.
- Write the final hotspot list.

**Produce:** `hotspots/hotspot_residues.txt` with residue IDs in the numbering scheme RFdiffusion will see.

**Defend:** *"Because no GDF8:ActRIIB crystal structure exists, I transferred the type II interface from the GDF11:ActRIIB complex (6MAC), justified by ~90% sequence identity in the mature domain, and verified the contact residues are conserved before using them as hotspots."*

---

## Module 4 — Backbone Generation with RFdiffusion

**Learn:**
- [diffusion models](docs/concepts/diffusion-models.md) — forward noising / reverse denoising, why this is a generative model.
- [RFdiffusion](docs/tools/RFdiffusion.md) — the fine-tuned RoseTTAFold, contig syntax, `ppi.hotspot_res`, self-conditioning, what the outputs are (and aren't).

**Do:** Run binder hallucination, 20 designs, binder length 50–70, hotspots from Module 3. Inspect every output in PyMOL against the target.

**Produce:** ~20 backbone PDBs in `rfdiffusion/outputs/`; a shortlist of 5–10 that actually contact the hotspots with clean secondary structure.

**Defend:** *"RFdiffusion gave me backbone-only designs conditioned on my hotspots; I visually triaged for helical binders making buried contact at the epitope and discarded floaters and coils."*

---

## Module 5 — Sequence Design with ProteinMPNN

**Learn:**
- [inverse folding](docs/concepts/inverse-folding.md) — the structure→sequence problem, why it is distinct from folding.
- [ProteinMPNN](docs/tools/ProteinMPNN.md) — MPNN encoder over backbone graph, order-agnostic autoregressive decoding, temperature, fixing the target chain.

**Do:** For each shortlisted backbone, design 8+ sequences at temperature 0.1 (raise to 0.2 if outputs collapse), fixing the target chain, designing only the binder chain.

**Produce:** FASTA files in `proteinmpnn/outputs/`, each with per-sequence scores.

**Defend:** *"ProteinMPNN solved the inverse-folding problem for each backbone with order-agnostic decoding; I fixed the myostatin chain and designed only the binder, sampling several sequences per backbone at low temperature."*

---

## Module 6 — In Silico Validation

**Learn:**
- [ESMFold](docs/tools/ESMFold.md) — language-model folding, why an independent refold is a self-consistency test.
- [AlphaFold2](docs/tools/AlphaFold2.md) — the stronger (AF2-multimer) alternative and its interface metrics (iPTM, pAE).
- [TMalign](docs/tools/TMalign.md) and [PyMOL](docs/tools/PyMOL.md) — measuring RMSD of refold vs. design.
- [validation metrics](docs/concepts/validation-metrics.md) — pLDDT, pTM, pAE, iPTM thresholds.

**Do:** Refold each designed sequence (ESMFold API first; AF2-multimer if you have GPU/Colab budget). Superpose onto the RFdiffusion backbone, compute RMSD, record pTM/pLDDT.

**Produce:** `esm_validation/scores.tsv` — one row per (backbone, sequence) with pTM, mean pLDDT, RMSD-to-design, MPNN score.

**Defend:** *"I validated self-consistency by refolding each design and requiring pTM > 0.7 and Cα-RMSD < 2 Å to the intended backbone — the standard filter that predicts experimental success."*

---

## Module 7 — Ranking, Interpretation, Write-up

**Learn:** Re-read [de novo binder design](docs/concepts/de-novo-binder-design.md) end-to-end now that you've done every step; the pieces should click into a single narrative.

**Do:** Apply the filter cascade (pTM → pLDDT → RMSD → MPNN score). Open the top 3–5 in PyMOL, confirm interface contacts, screenshot.

**Produce:** `results/top_designs/` with the final PDBs, a short `README.md` summarising the pipeline, parameters, and outcomes, and the figures.

**Defend:** The full sentence from `CONTEXT.md`: *"I ran RFdiffusion binder hallucination against the ActRIIB-binding epitope of myostatin, using hotspot residues derived from the GDF11:ActRIIB complex, designed sequences with ProteinMPNN, and validated by ESMFold refolding, filtering on pTM and RMSD to the design."*

---

## What "done" looks like

You can hold a 10-minute conversation with a protein-design PI in which you correctly distinguish backbone generation from sequence design from folding validation, explain why you chose your target and epitope, name the metric you filtered on and why it correlates with wet-lab success, and state honestly what this pipeline does *not* prove (no experimental binding, no affinity, no specificity data — this is an in silico design exercise, and you should say so before they ask).

---

## Honest scope boundaries — state these proactively

- This produces **candidate designs**, not validated binders. No wet-lab data.
- ESMFold/AF2 self-consistency **predicts** designability; it is not proof of binding.
- Using GDF11's interface as a proxy is a **defensible approximation**, not ground truth for GDF8.
- The point of the exercise is demonstrated **tool fluency and sound structural reasoning**, and it should be pitched exactly that way. Overselling it is the fastest way to lose credibility with the people you're contacting.

---

## Reference reading order (papers)

1. RFdiffusion — Watson et al., *Nature* 620, 1089–1100 (2023).
2. ProteinMPNN — Dauparas et al., *Science* 378, 49–56 (2022).
3. ESMFold — Lin et al., *Science* 379, 1123–1130 (2023).
4. GDF8/GDF11 structural comparison — Walker et al., *BMC Biology* 15, 19 (2017) (covers 3HH2, 5JI1, potency determinants).
5. GDF11 ternary receptor complex — Goebel et al., *PNAS* 116, 15505–15513 (2019) (6MAC).

Full theory for each is in the [documentation site](docs/index.md).
