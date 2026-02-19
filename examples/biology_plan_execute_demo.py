#!/usr/bin/env python3
"""
Demo: Plan-Execute with Multi-Domain Expert Agents for Biology Research.

A complex biology question that spans genomics, protein biochemistry, cancer
biology, and clinical therapeutics is:

  1. Decomposed by a Planner Agent into domain-specific sub-questions
  2. Researched in parallel by 4 Domain Expert Agents (each with web search)
  3. Synthesized by a final Planner/Synthesizer Agent into a comprehensive report

Each agent has its own carefully crafted system prompt so they complement
each other and each contribute unique domain expertise.

Requires: Codex CLI with gpt-5.2-codex model (web search enabled)
"""

import sys
import json
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, ".")

from src.agent import Agent, AgentResult
from src.base import CoordinatorResult
from src.tracing import build_trace, save_trace

# ── The Complex Cross-Disciplinary Biology Question ─────────────────────────
#
# This question REQUIRES expertise from genomics, protein science, cancer
# biology, AND clinical oncology to answer fully.  No single domain expert
# can provide a complete answer alone.

BIOLOGY_QUESTION = """\
The interplay between tumor-intrinsic genomic features and the tumor immune
microenvironment (TIME) has become central to precision immuno-oncology.

Please provide a comprehensive, multi-disciplinary analysis addressing ALL of
the following:

1. How do key tumor-intrinsic genomic features — including tumor mutational
   burden (TMB), microsatellite instability (MSI), specific driver mutations
   (e.g., KRAS, TP53, STK11/LKB1, KEAP1), and chromosomal instability (CIN)
   — vary across major cancer types, and what are the latest large-scale
   genomic studies characterizing these features?

2. At the molecular/protein level, how do these genomic alterations affect
   antigen presentation (MHC-I/II), immune checkpoint ligand expression
   (PD-L1, CTLA-4, LAG-3, TIGIT), and downstream signaling pathways
   (MAPK/ERK, PI3K/AKT/mTOR, JAK-STAT, cGAS-STING)? What are the
   structural and biochemical mechanisms involved?

3. How do these tumor-intrinsic features shape the composition and functional
   state of the tumor immune microenvironment — including CD8+ T cells,
   regulatory T cells, tumor-associated macrophages, myeloid-derived
   suppressor cells, and NK cells? What pathological patterns distinguish
   "hot" vs "cold" tumors?

4. Based on the above biology, what are the most promising biomarker-driven
   immunotherapy combination strategies currently in clinical trials
   (2023–2025), including checkpoint inhibitor combos, bispecifics,
   cancer vaccines, and cellular therapies? What recent clinical trial
   results have been most significant?
"""


# ══════════════════════════════════════════════════════════════════════════════
#  AGENT DEFINITIONS — each agent has a unique, complementary system prompt
# ══════════════════════════════════════════════════════════════════════════════

PLANNER = Agent(
    name="planner",
    role=(
        "You are a senior biomedical research coordinator who specializes in "
        "designing multi-disciplinary research plans for complex biology questions.\n\n"
        "You have 4 domain experts available:\n"
        "  1. genomics-expert — cancer genomics, mutation landscapes, TMB, MSI, "
        "bioinformatics, large-scale sequencing studies, databases (COSMIC, TCGA, "
        "cBioPortal)\n"
        "  2. protein-biochemistry-expert — protein structure/function, immune "
        "checkpoint proteins, signaling cascades, post-translational modifications, "
        "structural biology\n"
        "  3. cancer-biology-expert — tumor microenvironment, immune cell biology, "
        "hot vs cold tumors, immune evasion, tumor-immune interactions, pathology\n"
        "  4. clinical-therapeutics-expert — immunotherapy clinical trials, "
        "combination strategies, biomarkers, FDA approvals, clinical outcomes\n\n"
        "Your job:\n"
        "• Analyze the question and create EXACTLY 4 sub-questions, one per expert.\n"
        "• Each sub-question must be specific, actionable, and scoped to that "
        "expert's domain.\n"
        "• Sub-questions should be complementary — no overlap, but together they "
        "cover the full question.\n"
        "• Include search terms and databases the expert should consult.\n\n"
        "Return ONLY a JSON array of exactly 4 objects with keys:\n"
        '  "domain" — one of the 4 agent names above\n'
        '  "question" — the focused research question for this expert\n'
        '  "key_terms" — JSON array of search terms\n'
        '  "search_suggestions" — string describing what to search for\n'
    ),
)

GENOMICS_EXPERT = Agent(
    name="genomics-expert",
    role=(
        "You are a cancer genomics and bioinformatics expert with 15+ years of "
        "experience analyzing tumor genomes.\n\n"
        "Your expertise includes:\n"
        "• Whole-genome and whole-exome sequencing analysis\n"
        "• Somatic mutation calling, variant classification (pathogenic, VUS, benign)\n"
        "• Tumor mutational burden (TMB) quantification and interpretation\n"
        "• Microsatellite instability (MSI) and mismatch repair deficiency (dMMR)\n"
        "• Driver mutation identification and co-mutation landscape analysis\n"
        "• Cancer genomics databases: TCGA, COSMIC, cBioPortal, AACR GENIE\n"
        "• Chromosomal instability (CIN) and copy number variation analysis\n\n"
        "IMPORTANT INSTRUCTIONS:\n"
        "• Use web search to find the LATEST genomic data and publications (2023-2025)\n"
        "• Cite specific studies: author, journal, year, key findings\n"
        "• Provide quantitative data: mutation frequencies, TMB values, percentages\n"
        "• Reference specific databases and datasets you consulted\n"
        "• Compare across cancer types (NSCLC, CRC, melanoma, etc.)\n"
        "• Structure your answer with clear headings and subsections\n"
        "• DO NOT cover protein mechanisms or clinical trials — stay in your lane\n"
    ),
)

PROTEIN_EXPERT = Agent(
    name="protein-biochemistry-expert",
    role=(
        "You are a protein biochemist and structural biologist specializing in "
        "immune signaling and cancer-related proteins.\n\n"
        "Your expertise includes:\n"
        "• Protein 3D structure analysis (X-ray crystallography, cryo-EM)\n"
        "• Immune checkpoint receptor/ligand interactions: PD-1/PD-L1, CTLA-4/B7, "
        "LAG-3, TIGIT/CD155, TIM-3\n"
        "• Signal transduction: MAPK/ERK, PI3K/AKT/mTOR, JAK-STAT, cGAS-STING\n"
        "• MHC class I and II antigen presentation machinery\n"
        "• Post-translational modifications (phosphorylation, ubiquitination, "
        "glycosylation) in signaling\n"
        "• Protein-protein interaction networks\n\n"
        "IMPORTANT INSTRUCTIONS:\n"
        "• Use web search to find the latest structural and mechanistic studies\n"
        "• Explain molecular mechanisms with biochemical precision\n"
        "• Reference PDB structure IDs where relevant\n"
        "• Describe how specific mutations (KRAS G12C/D/V, TP53 hotspots, "
        "STK11 loss) alter protein function and downstream signaling\n"
        "• Connect signaling changes to immune molecule expression\n"
        "• Structure your answer with clear headings and subsections\n"
        "• DO NOT cover genomic epidemiology or clinical trials — stay in your lane\n"
    ),
)

CANCER_BIOLOGY_EXPERT = Agent(
    name="cancer-biology-expert",
    role=(
        "You are a cancer biologist and tumor immunologist specializing in the "
        "tumor immune microenvironment (TIME).\n\n"
        "Your expertise includes:\n"
        "• Tumor-infiltrating lymphocyte (TIL) biology and phenotyping\n"
        "• CD8+ cytotoxic T cells, CD4+ helper T cells, regulatory T cells (Tregs)\n"
        "• Tumor-associated macrophages (TAMs): M1 vs M2 polarization\n"
        "• Myeloid-derived suppressor cells (MDSCs) and dendritic cells\n"
        "• Natural killer (NK) cell biology in tumors\n"
        "• Immune exclusion, immune desert, and inflamed tumor phenotypes\n"
        "• Single-cell RNA sequencing and spatial transcriptomics of TIME\n"
        "• Immunosuppressive mechanisms: TGF-β, IL-10, IDO, adenosine pathway\n\n"
        "IMPORTANT INSTRUCTIONS:\n"
        "• Use web search to find the latest research on tumor-immune interactions\n"
        "• Explain how specific driver mutations reshape the immune microenvironment\n"
        "  (e.g., STK11 loss → cold tumors, MSI-H → hot tumors)\n"
        "• Describe pathological patterns: immune-inflamed vs immune-excluded vs "
        "immune-desert\n"
        "• Reference recent single-cell and spatial transcriptomics studies\n"
        "• Provide a mechanistic link between genomic features and immune phenotypes\n"
        "• Structure your answer with clear headings and subsections\n"
        "• DO NOT cover raw genomic statistics or clinical trial data — stay in your lane\n"
    ),
)

CLINICAL_EXPERT = Agent(
    name="clinical-therapeutics-expert",
    role=(
        "You are a clinical oncologist and drug development expert specializing "
        "in immuno-oncology clinical trials.\n\n"
        "Your expertise includes:\n"
        "• Immune checkpoint inhibitors: anti-PD-1 (nivolumab, pembrolizumab), "
        "anti-PD-L1 (atezolizumab, durvalumab), anti-CTLA-4 (ipilimumab, "
        "tremelimumab)\n"
        "• Next-generation checkpoint targets: LAG-3 (relatlimab), TIGIT "
        "(tiragolumab), TIM-3\n"
        "• Bispecific antibodies and bispecific T-cell engagers\n"
        "• Cancer vaccines: mRNA vaccines (e.g., mRNA-4157/V940), neoantigen vaccines\n"
        "• Cellular therapies: TIL therapy (lifileucel), CAR-T in solid tumors\n"
        "• Biomarker-driven patient selection: TMB, MSI, PD-L1 IHC, gene signatures\n"
        "• Combination strategies: ICI + chemo, ICI + ICI, ICI + targeted therapy\n\n"
        "IMPORTANT INSTRUCTIONS:\n"
        "• Use web search to find the LATEST clinical trial results (2023–2025)\n"
        "• Cite specific trials: name, NCT number, phase, key endpoints\n"
        "• Report quantitative outcomes: ORR, PFS, OS, hazard ratios, p-values\n"
        "• Cover FDA approvals and breakthrough therapy designations\n"
        "• Highlight biomarker-stratified outcomes where available\n"
        "• Discuss combination strategies backed by recent trial data\n"
        "• Structure your answer with clear headings and subsections\n"
        "• DO NOT cover basic biology mechanisms — stay in your lane\n"
    ),
)

SYNTHESIZER = Agent(
    name="synthesizer",
    role=(
        "You are a distinguished professor of oncology who has published "
        "extensively in Nature, Science, Cell, and NEJM. You are writing a "
        "comprehensive review article.\n\n"
        "Your task is to synthesize research findings from 4 domain experts "
        "(genomics, protein biochemistry, cancer biology, clinical therapeutics) "
        "into a single, coherent, publication-quality report.\n\n"
        "Your synthesis must:\n"
        "1. CROSS-REFERENCE findings across domains — show how genomic features "
        "connect to molecular mechanisms, which shape the tumor microenvironment, "
        "which determine clinical outcomes\n"
        "2. BUILD A NARRATIVE — tell the story from genome → protein → tumor biology "
        "→ clinical application\n"
        "3. HIGHLIGHT TRANSLATIONAL INSIGHTS — where basic science findings have "
        "direct clinical implications\n"
        "4. IDENTIFY GAPS — where the evidence is insufficient or contradictory\n"
        "5. PROPOSE FUTURE DIRECTIONS — what experiments, trials, or studies are "
        "needed next\n\n"
        "Structure your report as:\n"
        "  I.   Executive Summary (key takeaways in 5-7 bullet points)\n"
        "  II.  Integrated Analysis (the genome-to-clinic narrative)\n"
        "  III. Translational Implications\n"
        "  IV.  Key Challenges and Knowledge Gaps\n"
        "  V.   Future Directions\n"
        "  VI.  References (consolidated from all experts)\n\n"
        "Write in a clear, authoritative scientific style. Be specific and cite "
        "the data points mentioned by the domain experts.\n"
    ),
)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN EXECUTION FLOW
# ══════════════════════════════════════════════════════════════════════════════

def _parse_plan(raw_text: str) -> list[dict]:
    """Extract JSON array from planner output, with fallback."""
    text = raw_text.strip()
    # Try to find JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    # Fallback: create a default plan with one question per expert
    print("  [warn] Could not parse planner JSON, using default domain split")
    return [
        {
            "domain": "genomics-expert",
            "question": "Analyze the genomic landscape of TMB, MSI, and key driver mutations (KRAS, TP53, STK11, KEAP1) across major cancer types.",
            "key_terms": ["TMB", "MSI", "KRAS", "TP53", "STK11", "TCGA", "COSMIC"],
            "search_suggestions": "Search TCGA, COSMIC, cBioPortal for mutation prevalence data",
        },
        {
            "domain": "protein-biochemistry-expert",
            "question": "Explain the molecular mechanisms by which driver mutations alter immune checkpoint expression, antigen presentation, and key signaling pathways (MAPK, PI3K, JAK-STAT, cGAS-STING).",
            "key_terms": ["PD-L1", "MHC-I", "cGAS-STING", "MAPK", "PI3K", "JAK-STAT"],
            "search_suggestions": "Search for structural studies and signaling pathway analyses",
        },
        {
            "domain": "cancer-biology-expert",
            "question": "How do tumor-intrinsic genomic features shape the tumor immune microenvironment composition and determine hot vs cold tumor phenotypes?",
            "key_terms": ["TILs", "TAMs", "MDSCs", "immune desert", "inflamed tumor", "single-cell RNA-seq"],
            "search_suggestions": "Search for single-cell and spatial transcriptomics studies of TIME",
        },
        {
            "domain": "clinical-therapeutics-expert",
            "question": "What are the most promising biomarker-driven immunotherapy combination strategies in clinical trials (2023-2025), and what recent results have been most impactful?",
            "key_terms": ["checkpoint inhibitors", "bispecifics", "cancer vaccines", "TIL therapy", "biomarker selection"],
            "search_suggestions": "Search ClinicalTrials.gov and ASCO/ESMO abstracts for 2023-2025 trial results",
        },
    ]


def _run_expert(agent: Agent, sub_question: dict) -> tuple[str, AgentResult]:
    """Execute a domain expert agent on its assigned sub-question."""
    domain = sub_question.get("domain", agent.name)
    question = sub_question.get("question", "")
    key_terms = sub_question.get("key_terms", [])
    search_suggestions = sub_question.get("search_suggestions", "")

    task = (
        f"Research the following question thoroughly using web search to find "
        f"the latest data and publications.\n\n"
        f"RESEARCH QUESTION:\n{question}\n\n"
        f"KEY TERMS TO INVESTIGATE:\n{', '.join(key_terms)}\n\n"
        f"SEARCH STRATEGY:\n{search_suggestions}\n\n"
        f"Provide a comprehensive, well-structured answer including:\n"
        f"• Key findings with specific data points and statistics\n"
        f"• Recent publications (cite authors, journal, year)\n"
        f"• Important databases or resources consulted\n"
        f"• Any conflicting evidence or open questions\n"
        f"• Summary of the most significant findings\n"
    )

    print(f"  [{domain}] Starting research...")
    start_time = time.time()
    result = agent.run(task)
    elapsed = time.time() - start_time
    output_len = len(result.output) if result.output else 0
    print(f"  [{domain}] Done — {output_len} chars in {elapsed:.1f}s")
    return domain, result


def _next_run_dir() -> str:
    """Return the next numbered run directory under outputs/plan-execute/."""
    base = os.path.join("outputs", "plan-execute")
    os.makedirs(base, exist_ok=True)
    existing = [int(d) for d in os.listdir(base) if d.isdigit()]
    next_num = max(existing, default=0) + 1
    run_dir = os.path.join(base, str(next_num))
    os.makedirs(run_dir)
    return run_dir


def main():
    run_start = time.time()
    run_dir = _next_run_dir()
    report_file = os.path.join(run_dir, "biology_report.md")
    trace_file = os.path.join(run_dir, "biology_trace.json")

    output_lines: list[str] = []  # collect everything for the report file
    all_steps: list[AgentResult] = []  # collect agent results for trace

    def log(text: str = ""):
        """Print and accumulate output."""
        print(text)
        output_lines.append(text)

    log("=" * 80)
    log("BIOLOGY PLAN-EXECUTE DEMO")
    log("Multi-Domain Research Coordination with Codex GPT-5.2")
    log(f"Timestamp: {datetime.now().isoformat()}")
    log("=" * 80)
    log()
    log("RESEARCH QUESTION:")
    log(BIOLOGY_QUESTION)
    log()

    # ── Step 1: Planning ────────────────────────────────────────────────────
    log("=" * 80)
    log("STEP 1: PLANNER — Decomposing into domain-specific sub-questions")
    log("=" * 80)
    log()

    planner_result = PLANNER.run(BIOLOGY_QUESTION)
    planner_result.step_label = "step-1-planning"
    all_steps.append(planner_result)

    if planner_result.error:
        log(f"PLANNER ERROR: {planner_result.error}")
        log("Falling back to default plan...")

    sub_questions = _parse_plan(planner_result.output or "")

    log(f"Planner generated {len(sub_questions)} sub-questions:\n")
    for i, sq in enumerate(sub_questions):
        log(f"  {i + 1}. Domain:  {sq.get('domain', '?')}")
        log(f"     Question: {sq.get('question', 'N/A')}")
        terms = sq.get("key_terms", [])
        if terms:
            log(f"     Terms:    {', '.join(terms)}")
        log()

    # ── Step 2: Parallel domain expert execution ────────────────────────────
    log("=" * 80)
    log("STEP 2: DOMAIN EXPERTS — Parallel research execution")
    log("=" * 80)
    log()

    experts_map = {
        "genomics-expert": GENOMICS_EXPERT,
        "protein-biochemistry-expert": PROTEIN_EXPERT,
        "cancer-biology-expert": CANCER_BIOLOGY_EXPERT,
        "clinical-therapeutics-expert": CLINICAL_EXPERT,
    }

    # Match sub-questions to experts
    assignments: list[tuple[Agent, dict]] = []
    for sq in sub_questions:
        domain = sq.get("domain", "")
        agent = experts_map.get(domain)
        if not agent:
            # Try fuzzy match
            for key, a in experts_map.items():
                if key.startswith(domain.split("-")[0]):
                    agent = a
                    break
        if not agent:
            agent = list(experts_map.values())[len(assignments) % len(experts_map)]
        assignments.append((agent, sq))

    log(f"Launching {len(assignments)} domain experts in parallel...\n")

    expert_results: dict[str, AgentResult] = {}

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(_run_expert, agent, sq): sq.get("domain", f"expert-{i}")
            for i, (agent, sq) in enumerate(assignments)
        }
        for future in as_completed(futures):
            domain, result = future.result()
            result.step_label = f"step-2-{domain}"
            expert_results[domain] = result
            all_steps.append(result)
            if result.error:
                log(f"  [{domain}] ERROR: {result.error}")

    log(f"\nAll {len(expert_results)} domain experts completed.\n")

    # ── Step 3: Synthesis ───────────────────────────────────────────────────
    log("=" * 80)
    log("STEP 3: SYNTHESIZER — Integrating all findings into final report")
    log("=" * 80)
    log()

    # Build context from all expert outputs
    context_parts = []
    for domain, result in expert_results.items():
        context_parts.append(
            f"══ FINDINGS FROM {domain.upper()} ══\n\n{result.output or '[no output]'}"
        )
    all_context = "\n\n\n".join(context_parts)

    synthesis_task = (
        "Based on the research findings from 4 domain experts provided below, "
        "create a comprehensive, integrated report that fully answers the "
        "original research question.\n\n"
        f"ORIGINAL QUESTION:\n{BIOLOGY_QUESTION}\n\n"
        "Your report must:\n"
        "1. Open with an Executive Summary (5-7 key takeaways)\n"
        "2. Provide an Integrated Analysis that traces the path from genomic "
        "features → molecular mechanisms → immune microenvironment → clinical "
        "outcomes\n"
        "3. Highlight Translational Implications — where basic science meets "
        "clinical practice\n"
        "4. Identify Key Challenges and Knowledge Gaps across all domains\n"
        "5. Propose Future Directions for research and clinical development\n"
        "6. Include a consolidated References section\n"
    )

    log("Synthesizer is integrating all expert findings...\n")
    synthesis_result = SYNTHESIZER.run(synthesis_task, context=all_context)
    synthesis_result.step_label = "step-3-synthesis"
    all_steps.append(synthesis_result)
    log(f"Synthesis completed in {synthesis_result.elapsed:.1f}s\n")

    if synthesis_result.error:
        log(f"SYNTHESIS ERROR: {synthesis_result.error}")

    # ── Final Output ────────────────────────────────────────────────────────
    log()
    log("=" * 80)
    log("DOMAIN EXPERT REPORTS")
    log("=" * 80)

    for domain, result in expert_results.items():
        log(f"\n{'─' * 70}")
        log(f"DOMAIN: {domain}")
        log(f"{'─' * 70}")
        if result.error:
            log(f"ERROR: {result.error}")
        else:
            log(result.output or "[empty output]")

    log(f"\n{'━' * 80}")
    log("INTEGRATED SYNTHESIS REPORT")
    log(f"{'━' * 80}\n")
    log(synthesis_result.output if synthesis_result.output else "[no synthesis produced]")

    # ── Execution Summary ───────────────────────────────────────────────────
    total_elapsed = time.time() - run_start
    total_expert_chars = sum(
        len(r.output) for r in expert_results.values() if r.output
    )
    synthesis_chars = len(synthesis_result.output) if synthesis_result.output else 0
    errors = [d for d, r in expert_results.items() if r.error]

    log(f"\n{'=' * 80}")
    log("EXECUTION SUMMARY")
    log(f"{'=' * 80}")
    log(f"Domain experts:         {len(expert_results)}")
    log(f"Total research output:  {total_expert_chars:,} chars")
    log(f"Synthesis output:       {synthesis_chars:,} chars")
    log(f"Total elapsed time:     {total_elapsed:.1f}s")
    if errors:
        log(f"Errors in:              {', '.join(errors)}")
    else:
        log("Status:                 All agents completed successfully!")

    # ── Save report ─────────────────────────────────────────────────────────
    with open(report_file, "w") as f:
        f.write("\n".join(output_lines))
    log(f"\nFull report saved to: {report_file}")

    # ── Save trace ──────────────────────────────────────────────────────────
    coord_result = CoordinatorResult(
        steps=all_steps,
        metadata={"pattern": "plan-execute"},
        elapsed=total_elapsed,
    )
    trace = build_trace(coord_result, task=BIOLOGY_QUESTION)
    save_trace(trace, trace_file)
    log(f"Trace saved to: {trace_file}")


if __name__ == "__main__":
    main()
