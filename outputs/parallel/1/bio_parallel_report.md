# Parallel Biology Research Report

**Generated:** 2026-02-19 01:26:48  
**Model:** gpt-5.2-codex  
**Mode:** parallel (5 agents)  
**Status:** All succeeded

---

## Q1: crispr-cas13d

**Question:** What are the latest advances (2024-2025) in CRISPR-Cas13d RNA editing for treating neurodegenerative diseases? Summarize key papers, clinical trials, and remaining delivery challenges.

Below is a focused 2024–2025 update on **CRISPR‑Cas13d (RfxCas13d/CasRx) RNA targeting** for neurodegenerative disease therapy, plus clinical-trial status and delivery challenges. I use concrete dates and prioritize primary literature and registries.

**Summary**  
In 2024–2025, the most substantive neurodegeneration‑focused advances for Cas13d are **preclinical C9ORF72 ALS/FTD studies** that demonstrate improved targeting of structured repeat RNA, dual targeting of sense/antisense repeat transcripts, and engineered **high‑fidelity Cas13d variants** to reduce collateral effects. These studies use Cas13d primarily for **RNA knockdown of toxic repeat RNAs** rather than base editing, and all are still at the cell and animal‑model stage. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/39288267/))

**Key 2024–2025 Papers (Neurodegeneration + Therapeutic Enablers)**

| Date (Published) | Paper | Disease/Model | Key Advance |
|---|---|---|---|
| **Sep 17, 2024** | Liu et al., *J Clin Invest* | C9ORF72 ALS/FTD; patient iPSC‑derived motor neurons; C9 repeat transgenic mice | Optimized Cas13d targeting of **G4C2 repeat RNA** (structured target), **reducing RAN translation/DPRs** in cells and mice. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/39288267/)) |
| **Jan 8, 2025** | McCallister et al., *Nat Commun* | C9‑ALS/FTD; C9‑BACexp mice; patient‑derived motor neuron‑like cells | **High‑fidelity Cas13d** reduces repeat RNA **without affecting normal C9ORF72**, lowers RNA foci and DPRs, and reverses transcriptional deficits after **AAV delivery**; improved specificity vs native enzyme. ([nature.com](https://www.nature.com/articles/s41467-024-55548-5)) |
| **2025** | Kempthorne et al., *Nat Commun* | C9‑ALS/FTD; patient iPSC‑neurons; zebrafish; mouse models | **Dual‑targeting CasRx (Cas13d)** reduces **sense and antisense** repeat RNAs and DPRs; protects against glutamate‑induced excitotoxicity; in vivo reductions in repeat RNAs. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/39779704/?utm_source=openai)) |
| **Feb 11, 2025** | Hart et al., *Nat Biotech* | Platform/safety | Demonstrates that **collateral cleavage depends on high Cas13d expression**; low‑copy expression yields strong on‑target knockdown with less collateral activity; **high‑fidelity variants can reduce collateral but at a potency cost**. ([nature.com](https://www.nature.com/articles/s41587-025-02558-3)) |

**Clinical Trials (Cas13 and Neurodegeneration)**  
Clinical translation of **Cas13 RNA editing** has begun outside neurodegeneration. ClinicalTrials.gov lists **HG202**, a Cas13 RNA‑editing therapy for neovascular AMD (SIGHT‑I, early phase 1). This underscores that Cas13 is entering the clinic, but **neurodegenerative Cas13d trials remain preclinical in the 2024–2025 literature** summarized above. ([clinicaltrials.gov](https://clinicaltrials.gov/study/NCT06031727?utm_source=openai))

**Remaining Delivery Challenges for Neurodegenerative Indications**

- **CNS distribution in large brains**: In a 2025 non‑human primate study, AAV‑PHP.eB improved cortical and spinal transduction vs AAV9 after intracerebroventricular delivery, but **subcortical penetration remained limited and peripheral leakage occurred**, highlighting persistent delivery constraints for broad CNS coverage. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/41438872/))  
- **Balancing efficacy vs collateral/off‑target activity**: High‑fidelity Cas13d variants improve specificity in C9‑ALS/FTD models, but more stringent variants can trade off on‑target potency; expression level strongly influences collateral activity. This complicates dosing and promoter design for CNS therapy. ([nature.com](https://www.nature.com/articles/s41467-024-55548-5))  
- **Guide design for structured repeat RNAs and allele selectivity**: C9ORF72 repeats are highly structured and embedded in specific transcript variants. 2024–2025 studies show that careful guide selection can target repeat‑containing variants while sparing normal transcripts, but this remains disease‑specific and may be harder for other neurodegenerative targets. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/39288267/))  
- **Multi‑RNA targeting without expanding payload**: Dual‑targeting of sense/antisense repeat RNAs is increasingly important for C9‑ALS/FTD. Cas13d can process guide arrays, but **packing multiple guides plus regulatory elements into AAV while preserving expression control** remains a vector‑design challenge. ([nature.com](https://www.nature.com/articles/s41467-024-55550-x?utm_source=openai))

**Sources**  
- ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/39288267/))  
- ([nature.com](https://www.nature.com/articles/s41467-024-55548-5))  
- ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/39779704/?utm_source=openai))  
- ([nature.com](https://www.nature.com/articles/s41587-025-02558-3))  
- ([clinicaltrials.gov](https://clinicaltrials.gov/study/NCT06031727?utm_source=openai))  
- ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/41438872/))

If you want, I can also add a short **“what would move these approaches toward first‑in‑human neurodegenerative trials”** roadmap (capsid selection, dosing, cell‑type targeting, biomarkers, and safety assays).

---

## Q2: alphafold3-ppi

**Question:** How does AlphaFold 3 improve prediction of protein-protein interactions compared to AlphaFold 2? Describe the architectural changes, new training data, and benchmark results on recent CASP/CAPRI targets.

Using **web-search** skill to provide up-to-date, citable sources.

**Summary**  
AlphaFold 3 (AF3) improves protein–protein interaction (PPI) prediction over AlphaFold 2 (AF2) primarily by switching to a diffusion-based, all‑atom generator and simplifying the MSA-centric trunk into a pair‑focused architecture, while training on broader complex data (including non‑protein components) and applying cross‑distillation from AF‑Multimer. These changes yield higher protein–protein interface success in developer benchmarks and modest but consistent gains on recent community tests like CASP16/CAPRI, with model ranking still a major bottleneck. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))

**Architectural Changes That Matter for PPI**  
- **Pairformer replaces Evoformer and de‑emphasizes MSA**: AF3 reduces MSA processing to a small block (four blocks vs the full AF2 evoformer), then discards the MSA representation and propagates information through a pair + single representation, improving data efficiency for complex interfaces. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))  
- **Diffusion module predicts raw atom coordinates**: AF3 replaces AF2’s residue‑frame/side‑chain torsion structure module with a diffusion model that denoises atom coordinates directly, enabling a unified treatment of protein–protein interfaces and other chemistries without heavy stereochemical constraints. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))  
- **Unified complex modeling across biomolecular types**: AF3 is explicitly designed to model complexes containing proteins plus nucleic acids, small molecules, ions, and modified residues—important because many PPI interfaces in vivo are modulated by such components. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))  

**Training Data Updates Relevant to PPIs**  
- **Expanded and newer structural data**: AF3 training used PDB assemblies (downloaded 12 Jan 2023) and templates (28 Sep 2022), plus the Chemical Components Dictionary (19 Oct 2023), reflecting newer complexes and chemical diversity than AF2-era releases. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))  
- **Broader sequence and nucleic-acid resources**: Training/evaluation pipelines draw on UniRef90, Uniclust30, MGnify, BFD, RFam, RNAcentral, nt, JASPAR, and SELEX datasets, supporting MSAs and nucleic‑acid contexts for interface modeling. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))  
- **Cross‑distillation from AF‑Multimer**: AF3 augments training with structures predicted by AlphaFold‑Multimer v2.3 to reduce diffusion “hallucinations,” improving behavior in disordered/interface regions. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))  

**Benchmarks on Recent CASP/CAPRI Targets**  
**Developer-reported interface benchmarks**  
- On low‑homology recent PDB complexes, AF3 shows **higher protein–protein interface success** (DockQ > 0.23) than AlphaFold‑Multimer v2.3, with especially strong improvements on antibody–protein interfaces. AF3’s dependence on MSA depth remains similar to AF‑Multimer, indicating that better architecture/training helps but doesn’t remove MSA limitations. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))  

**CASP16 (community blind test)**
- **Independent CASP16 analysis (Proteins 2026)** reports AF3 performs *slightly better* than AF2-based methods for protein complexes, but the advantage can vanish with massive AF2 sampling. AF3 tends to do better on easier targets, worse on harder ones, and model selection remains a key bottleneck. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/40851426/))  
- **CASP16 multimer results in one peer‑reviewed analysis** show AF3‑server achieved **average top‑5 DockQ ≈ 0.571** across 33 multimer targets, slightly higher than an AF2 server baseline (0.542) and an AF2‑Multimer v3 baseline (0.511). This illustrates a **modest but measurable gain** for AF3 in recent PPI targets. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC12321240/))  

**CAPRI (CASP16‑CAPRI Rounds 57/58)**  
- CAPRI’s CASP16 rounds included **34 targets (47 assessment units)**, and the official ranking explicitly used **AlphaFold3 (manual submission)** as a baseline alongside ColabFold. This indicates that AF3 served as a reference point, while top CAPRI groups generally improved beyond AF3 baselines through additional docking, sampling, and ranking. ([capri-docking.org](https://www.capri-docking.org/assessment/))  

**Interpretation (inference)**  
The combination of pair‑centric trunk, diffusion‑based all‑atom generation, and training on broader complex data likely drives AF3’s higher interface success rates compared to AF2/AF‑Multimer, but CASP16/CAPRI results show that improvements are **incremental rather than transformative**, and **ranking/scoring** remains a major limiter for PPIs. (Inference supported by developer benchmarks and CASP16/CAPRI analyses.) ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/))  

**Sources**  
- `https://pmc.ncbi.nlm.nih.gov/articles/PMC11168924/`  
- `https://pubmed.ncbi.nlm.nih.gov/40851426/`  
- `https://pmc.ncbi.nlm.nih.gov/articles/PMC12321240/`  
- `https://www.capri-docking.org/assessment/`  

If you want, I can also summarize the CASP16 CAPRI Round 57 scoring file (DockQ Z‑scores by target/interface) or break down AF3 vs AF‑Multimer gains by interface class (heteromer vs antibody–antigen).

---

## Q3: single-cell-spatial

**Question:** What are the current state-of-the-art spatial transcriptomics methods (e.g., MERFISH, Visium HD, Stereo-seq) and how are they being combined with single-cell RNA-seq to build whole-organ cell atlases?

Using skill: web-search (to provide up‑to‑date, cited sources).

**Summary**  
As of early 2026, state‑of‑the‑art spatial transcriptomics splits into two main technology classes: high‑plex imaging (single‑molecule FISH–based) and sequencing‑based capture arrays, with in‑situ sequencing/expansion methods bridging the gap. These platforms are increasingly combined with scRNA‑seq/snRNA‑seq references to assign cell identities, extend transcriptomes beyond spatially measured genes, and assemble whole‑organ atlases in 2D and 3D. ([genomebiology.biomedcentral.com](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-022-02824-6?utm_source=openai))

**State‑Of‑The‑Art Methods (Early 2026)**  
**Imaging‑based, single‑molecule RNA imaging (high spatial resolution; targeted gene panels)**  
- `MERFISH` (multiplexed error‑robust FISH) enables thousands of RNAs per cell at single‑molecule resolution and is widely used for atlas‑scale imaging; the original method paper established the error‑robust barcoding approach, and recent atlas efforts demonstrate whole‑organ scale. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/25858977/?utm_source=openai))  
- `seqFISH+` achieves transcriptome‑scale imaging in situ (up to ~10,000 genes in single cells), enabling unbiased cell‑type discovery directly in tissue. ([nature.com](https://www.nature.com/articles/s41586-019-1049-y?utm_source=openai))  
- `CosMx SMI` provides high‑plex RNA imaging with protein co‑detection and subcellular localization in FFPE tissue, enabling single‑cell spatial biology at clinical sample scale. ([nature.com](https://www.nature.com/articles/s41587-022-01483-z?utm_source=openai))  
- `ExSeq` (expansion sequencing) couples expansion microscopy with in‑situ sequencing to reach nanoscale localization and high multiplexing, extending spatial resolution beyond standard imaging. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/33509999/?utm_source=openai))  

**Sequencing‑based capture arrays (whole‑transcriptome; scalable tissue area)**  
- `Visium HD` (10x Genomics) is a high‑definition capture array for whole‑transcriptome spatial profiling at single‑cell scale; it was released in December 2025 and already used in high‑resolution cancer microenvironment studies. ([10xgenomics.com](https://www.10xgenomics.com/library/8012d2?utm_source=openai))  
- `Stereo‑seq` uses DNA‑nanoball patterned arrays with submicron spot spacing for ultra‑high‑resolution, large‑area capture; it supports tissue‑scale atlasing and has advanced to FFPE‑compatible total‑RNA profiling in Stereo‑seq V2. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/37288247/?utm_source=openai))  
- `Slide‑seqV2` delivers near‑cellular resolution (~10 μm) with markedly improved capture efficiency, enabling spatial profiling across diverse tissues. ([nature.com](https://www.nature.com/articles/s41587-020-0739-1?utm_source=openai))  
- `Seq‑Scope` achieves submicron spatial barcoding using Illumina‑derived clusters, enabling cellular and subcellular transcriptome mapping. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/34115981/?utm_source=openai))  
- `DBiT‑seq / DBiTplus` uses microfluidic barcoding to generate spatial grids and, in DBiTplus, integrates sequencing‑based spatial transcriptomics with multiplexed protein imaging on the same section. ([nature.com](https://www.nature.com/articles/s41592-025-02948-0?utm_source=openai))  

**How scRNA‑seq Is Combined With Spatial Methods to Build Whole‑Organ Atlases**  
- `Reference cell types and markers`: scRNA‑seq or snRNA‑seq atlases define cell types and markers that are then used to design targeted spatial panels (e.g., MERFISH gene panels built from scRNA‑seq clustering). ([nature.com](https://www.nature.com/articles/s41586-023-06808-9?utm_source=openai))  
- `Cell‑type mapping and deconvolution`: spatial data (spots or cells) are mapped to scRNA‑seq references to assign cell identities or proportions, especially for spot‑based methods like Visium HD or Slide‑seqV2. ([nature.com](https://www.nature.com/articles/s41592-025-02948-0?utm_source=openai))  
- `Transcriptome imputation`: imaging‑based spatial methods with limited panels can impute transcriptome‑wide expression using scRNA‑seq references, yielding spatially resolved, near‑whole‑transcriptome profiles. ([nature.com](https://www.nature.com/articles/s41586-023-06808-9?utm_source=openai))  
- `3D organ reconstruction`: serial spatial sections are registered to anatomical reference frameworks (e.g., brain coordinate frameworks), enabling 3D atlases with scRNA‑seq‑defined cell types. ([nature.com](https://www.nature.com/articles/s41586-023-06808-9?utm_source=openai))  

**Representative Whole‑Organ Atlas Builds (Spatial + scRNA‑seq Integration)**  
- `Adult mouse brain (MERFISH + scRNA‑seq)`: a whole‑brain MERFISH atlas imaged ~10 million cells with >1,100 genes and integrated scRNA‑seq to map >5,000 clusters and impute transcriptome‑wide profiles; the atlas is registered to a standard brain coordinate framework. ([nature.com](https://www.nature.com/articles/s41586-023-06808-9?utm_source=openai))  
- `Adult mouse brain (Stereo‑seq + snRNA‑seq)`: a Stereo‑seq atlas combined with snRNA‑seq produced single‑cell spatial mapping of ~4 million cells across 29,655 genes and 308 clusters. ([sciencedirect.com](https://www.sciencedirect.com/science/article/abs/pii/S0896627325001333?utm_source=openai))  
- `Regenerating zebrafish heart (Stereo‑seq + scRNA‑seq)`: an organ‑wide spatiotemporal atlas used Stereo‑seq with scRNA‑seq to build a 4D reconstruction across stages, totaling >500k cells/spots. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/40253397/?utm_source=openai))  
- `Human liver (MERFISH + snRNA‑seq)`: MERFISH profiling (>300 genes, ~310k cells) was integrated with snRNA‑seq to extend transcriptome coverage and resolve spatial cell states in healthy and fibrotic liver. ([nature.com](https://www.nature.com/articles/s41467-024-55325-4?utm_source=openai))  

**What This Means for Current “State‑of‑the‑Art” Atlas Building**  
- `Resolution vs. coverage tradeoff is being actively reduced`: high‑plex imaging achieves true single‑cell localization but is panel‑limited, while array‑based methods provide whole‑transcriptome coverage at spot or near‑cellular resolution; hybrid strategies and scRNA‑seq integration mitigate these tradeoffs. ([genomebiology.biomedcentral.com](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-022-02824-6?utm_source=openai))  
- `FFPE compatibility is expanding`: Visium HD and Stereo‑seq V2 explicitly target FFPE samples, and CosMx SMI provides high‑plex imaging in FFPE, enabling clinical‑grade whole‑organ atlases. ([nature.com](https://www.nature.com/articles/s41588-025-02193-3?utm_source=openai))  

If you want, I can focus on a specific organ system (brain, kidney, heart, tumor) or compare platforms for a particular experimental design (fresh‑frozen vs FFPE, whole‑transcriptome vs targeted panels, required spatial resolution).

**Possible next steps**  
1. Pick an organ or disease area and I will map the most relevant atlas papers and datasets.  
2. Share your sample type and desired resolution, and I will recommend the best platform plus integration workflow.  
3. Ask for a comparison table of platforms (resolution, plexity, throughput, cost, FFPE compatibility).

---

## Q4: tp53-gof-mutations

**Question:** Explain the gain-of-function mechanisms of TP53 missense mutations (R175H, R248W, R273H) in cancer. What are the newest therapeutic strategies targeting mutant p53, including molecular glues and PROTACs reported in 2024-2025?

**Overview**  
R175H, R248W, and R273H are classic TP53 hotspot missense mutations in the DNA‑binding domain. R175H is a conformational (structural) mutant, while R248W and R273H are DNA‑contact mutants; all three typically lose canonical sequence‑specific DNA binding and often exert dominant‑negative effects over remaining wild‑type p53, while also acquiring oncogenic gain‑of‑function (GOF) activities. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC5596564/?utm_source=openai))

**GOF Mechanisms (Shared and Mutation‑Biased)**  
- **Genomic instability via DDR disruption:** Knock‑in models show R175H, R248W, and R273H share a GOF that inactivates Mre11/ATM‑dependent DNA damage signaling, producing chromosomal translocations and defective G2/M checkpoint control. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/19881536/))  
- **Transcriptional rewiring through partner TFs:** Mutant p53 proteins commonly act as transcriptional cofactors by binding other TFs (e.g., NF‑Y, ETS1/2, Sp1, SREBP) and redirecting gene programs for proliferation, survival, invasion, and metabolism. This “TF hijacking” is a dominant GOF mechanism across multiple missense mutants. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC5729539/))  
- **Suppression of p63/p73 tumor‑suppressor programs:** Conformational mutants such as R175H bind p63/p73 strongly, while contact mutants like R273H show weaker binding; MDM2 can modulate these interactions. This suppresses p63/p73‑mediated tumor suppression and promotes invasive behavior. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/25417702/))  
- **Chromatin remodeling and epigenetic co‑option:** Mutant p53 can recruit chromatin remodelers such as SWI/SNF to open promoters (e.g., VEGFR2), and a large fraction of mutp53‑regulated genes depend on SWI/SNF. In addition, hotspot mutants including R175H, R248W, and R273H can upregulate chromatin regulators (MLL1/MLL2/MOZ) by binding their promoters together with ETS2. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/26080815/))  
- **Metastasis and EMT programs (notably strong for R273H):** R273H drives metastasis by repressing DLX2 and inducing NRP2, and also promotes migration and EMT via EGFR–AKT–FOXO1‑KLF6 repression; R175H and R248W can suppress KLF6 and promote migration as well. Recent tumor‑profiling data also link R273H to YAP/TAZ‑driven EMT/partial‑EMT transcriptional states. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC5596564/?utm_source=openai))  

**Mutation‑Specific Emphases**  
- **R175H (conformational):** Strong p63/p73 binding and chromatin‑driven transcriptional rewiring; shares the Mre11/ATM‑inactivation GOF and pro‑migratory programs with other hotspots. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/25417702/))  
- **R248W (contact):** Potent GOF with DNA‑damage signaling disruption and transcriptional co‑option; can suppress KLF6 and promote migration. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/19881536/))  
- **R273H (contact):** Particularly linked to invasion/EMT and metastasis via NRP2 and KLF6/EGFR–AKT–FOXO1 signaling, with additional epigenetic/YAP‑TAZ programs in colorectal cancer. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC5596564/?utm_source=openai))  

---

**Newest Therapeutic Strategies Targeting Mutant p53 (2024–2025)**  

**1. Mutant‑Specific Reactivation (Conformational Rescue)**  
- **Rezatapopt (PC14586, Y220C‑specific):** 2025 Cancer Discovery reports restoration of Y220C p53 conformation and transcriptional function, with preclinical efficacy and ongoing clinical evaluation; 2024 ACS Medicinal Chemistry Letters details the discovery and early clinical activity. This is the leading example of mutation‑specific reactivation, though it targets Y220C rather than R175H/R248W/R273H. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/39945593/))  
- **PYNNACLE Phase II protocol (2025):** Published trial protocol for rezatapopt monotherapy in TP53 Y220C solid tumors. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/40932470/))  
- **APR‑246 (eprenetapopt) and HO‑3867 combinations (2025):** In TP53‑mutant gynecologic cancer models, HO‑3867 and APR‑246 show strong growth inhibition; HO‑3867 is synergistic with olaparib in vitro and in vivo. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/40915175/))  

**2. Targeted Degradation (PROTACs reported in 2024)**  
- **DNA aptamer‑based PROTAC (dp53m) for R175H (Science Bulletin 2024):** A mutation‑selective degrader that promotes proteasome‑dependent R175H degradation, spares WT p53, and improves cisplatin sensitivity in vitro/in vivo. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/38811338/))  
- **Peptide‑based PROTACs for R175H (ACS Omega 2024):** P8 PROTAC selectively degrades p53‑R175H in a proteasome‑dependent manner with low toxicity in cell models, including endogenous R175H contexts. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11561642/))  
*Note:* These 2024 PROTACs are R175H‑focused and preclinical; comparable 2024–2025 PROTACs for R248W or R273H were not identified in the literature above.

**3. Molecular Glues (reported in 2024)**  
- **USP7‑engaging molecular glues (Science Bulletin 2024):** Small‑molecule glues, including bromocriptine, tether p53 to the deubiquitinase USP7, stabilizing p53 and suppressing tumor growth in xenografts. These are **not mutant‑selective**, so in GOF mutp53 tumors they may require careful context‑specific evaluation. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/38734583))  

**4. Destabilization Strategies (2024)**  
- **Proteasome inhibition as a degrader for R273H (Frontiers in Oncology 2024):** In R273H NSCLC lines, proteasome inhibitors (e.g., bortezomib) paradoxically trigger R273H degradation via Hsp70 and increase apoptosis, suggesting a potential repurposing strategy for select R273H contexts. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/38660140/))  

---

**Key Takeaways**  
- R175H, R248W, and R273H share core GOF mechanisms (TF hijacking, chromatin remodeling, DDR disruption), but R273H is especially linked to EMT/metastasis programs. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC5729539/))  
- The most **mutation‑specific** advanced therapeutic in 2024–2025 is Y220C‑targeted rezatapopt; comparable clinical‑stage reactivators for R175H/R248W/R273H remain limited. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/39945593/))  
- The most **mutation‑specific degraders** reported in 2024 are R175H‑selective PROTACs; molecular glue approaches are emerging but not yet mutant‑selective. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/38811338/))  

**Sources**  
- Key GOF mechanism papers and reviews: Oncogene 2010 (Mre11/ATM); Cell Death & Disease 2017/2020 (NRP2, KLF6); Genes & Development 2015 (SWI/SNF); Epigenetics & Chromatin 2025 (ETS2/MLL/MOZ); Oncogene 2015 (p63/p73). ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/19881536/))  
- 2024–2025 therapeutics: Science Bulletin 2024 (dp53m PROTAC; USP7 glues), ACS Omega 2024 (P8 PROTAC), Cancer Discovery 2025 + ACS Med Chem Lett 2024 (rezatapopt), Translational Oncology 2025 (HO‑3867/APR‑246), Frontiers in Oncology 2024 (R273H degradation by proteasome inhibitors). ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/38811338/))

---

## Q5: long-read-pangenome

**Question:** How are long-read sequencing technologies (PacBio HiFi, ONT) being used to build the human pangenome reference? Summarize the HPRC achievements, structural variant discovery, and clinical implications.

Using the `web-search` skill to gather the most recent, authoritative sources and cite them.

**Overview**  
The Human Pangenome Reference Consortium (HPRC) is replacing a single linear human reference with a graph‑based, telomere‑to‑telomere pangenome that better represents global genetic diversity and reduces reference bias in analyses. ([nature.com](https://www.nature.com/articles/s41586-022-04601-8)) As of February 19, 2026, the latest HPRC release is **Data Release 2 (May 12, 2025)**, a pre‑publication expansion to >200 individuals (232 total), providing substantially more long‑read data and assemblies than Release 1. ([humanpangenome.org](https://humanpangenome.org/hprc-data-release-2/))

**How PacBio HiFi and ONT are used to build the pangenome**  
- **PacBio HiFi** provides highly accurate long reads that form the backbone of haplotype‑resolved assemblies; Release 2 delivers ~60× HiFi coverage per sample and includes basecalling standardization (DeepConsensus) and methylation calls. ([humanpangenome.org](https://humanpangenome.org/hprc-data-release-2/))  
- **ONT ultralong** reads (often >100 kb) complement HiFi by spanning repeats and complex loci; Release 2 targets ~30× ultralong coverage and integrates ONT with HiFi plus trio/Hi‑C phasing, yielding markedly more contiguous and structurally accurate assemblies and enabling many telomere‑to‑telomere chromosomes. ([humanpangenome.org](https://humanpangenome.org/hprc-data-release-2/))  
- **Graph construction** from long‑read assemblies is done with multiple methods (Minigraph, Minigraph‑Cactus, PGGB), providing alternative views of homology and variation while validating SV discovery. ([nature.com](https://www.nature.com/articles/s41586-023-05896-x))  

**HPRC achievements (Release 1 → Release 2)**  
- **Release 1 (May 2023)**: 47 phased, diploid assemblies (94 haplotypes) from diverse 1000 Genomes samples, each >99% complete and >99% accurate at structural and base‑pair levels. ([nature.com](https://www.nature.com/articles/s41586-023-05896-x))  
- **Draft pangenome gains**: +119 Mb of euchromatic polymorphic sequence and 1,115 gene duplications relative to GRCh38; ~90 Mb of the added sequence is structural variation. ([nature.com](https://www.nature.com/articles/s41586-023-05896-x))  
- **Release 2 (May 12, 2025)**: >200 individuals, 232 total genomes, multiple data types (HiFi, ONT ultralong, Hi‑C, Kinnex RNA, WGS), ~3× fewer misassemblies, more telomere‑to‑telomere chromosomes, and improved base‑level accuracy (<1 error per ~0.5 Mb). ([humanpangenome.org](https://humanpangenome.org/hprc-data-release-2/))  

**Structural variant (SV) discovery enabled by long reads and pangenome graphs**  
- Using the HPRC draft pangenome as a reference reduced small‑variant error rates by **34%** and increased SV detection **104% per haplotype** compared with GRCh38‑based workflows. ([nature.com](https://www.nature.com/articles/s41586-023-05896-x))  
- In rare‑disease genomes, a pangenome graph built from HiFi assemblies revealed **>200,000 SV alleles**, ~**1,000 rare coding‑impact SVs**, and enabled diagnosis‑relevant findings (e.g., a novel **KMT2E** SV). ([nature.com](https://www.nature.com/articles/s41467-024-44980-2))  

**Clinical implications**  
- The pangenome framework directly addresses reference bias and improves gene–disease association studies across populations while expanding interpretability in repetitive and structurally complex loci. ([nature.com](https://www.nature.com/articles/s41586-022-04601-8))  
- For rare‑disease cohorts, pangenome graphs plus long‑read assemblies enable more reproducible SV calls and prioritize rare, potentially causal SVs that are often missed by linear‑reference workflows. ([nature.com](https://www.nature.com/articles/s41467-024-44980-2))  
- For somatic variants, early evidence from a 2026 bioRxiv preprint indicates pangenome‑guided alignment improves somatic variant calling accuracy and reduces germline contamination relative to GRCh38; this remains **pre‑peer‑review**. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/41509279/))  

**Sources**  
```text
https://www.nature.com/articles/s41586-022-04601-8
https://www.nature.com/articles/s41586-023-05896-x
https://humanpangenome.org/hprc-data-release-2/
https://www.humanpangenome.org/data/
https://www.humanpangenome.org/release-timeline/
https://www.nature.com/articles/s41467-024-44980-2
https://pubmed.ncbi.nlm.nih.gov/41509279/
```

---
