#!/usr/bin/env python3
"""
Demo: Biology multi-domain pipeline coordination.

A complex biology question is answered through a relay of domain-expert agents,
each using web search to research their sub-domain, passing accumulated knowledge
to the next agent.

Pipeline:
  Genomics Expert -> Molecular Biology Expert -> Cancer Pathologist
  -> Clinical Oncologist -> Integrative Synthesizer

Outputs:
  tests/outputs/pipeline/<N>/pipeline_report.md  — final synthesized report
  tests/outputs/pipeline/<N>/pipeline_trace.json — full trace of every agent's behavior
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")

from src.agent import Agent
from src.coordinators import PipelineCoordinator
from src.tracing import build_trace, save_trace


QUESTION = (
    "A 35-year-old woman of Ashkenazi Jewish descent, with a family history of "
    "breast cancer (mother diagnosed at 42, maternal aunt at 38), undergoes genetic "
    "testing and is found to carry a pathogenic BRCA1 c.68_69delAG (185delAG) "
    "founder mutation. She currently has no signs of cancer.\n\n"
    "We need a comprehensive analysis covering:\n"
    "1. The molecular genetics of this specific mutation\n"
    "2. How the resulting protein defect disrupts DNA repair\n"
    "3. The cancer risk profile and expected tumor pathology\n"
    "4. Evidence-based prevention, surveillance, and treatment strategies"
)


def main():
    agents = [
        Agent(
            name="genomics-specialist",
            role=(
                "You are a human genetics and genomics specialist with deep expertise "
                "in hereditary cancer syndromes. You have access to web search — USE IT "
                "to look up the latest data on mutation databases (ClinVar, LOVD), "
                "population genetics studies, and recent genomics publications. "
                "Provide precise, referenced information with concrete numbers."
            ),
            instruction=(
                "Research the BRCA1 c.68_69delAG (185delAG) mutation in depth:\n"
                "- What is the exact genomic location (chromosome, exon) and the molecular "
                "consequence of this 2-bp deletion (frameshift, premature stop codon position)?\n"
                "- What is the prevalence of this mutation in the Ashkenazi Jewish population "
                "vs. general population? What are the other Ashkenazi founder mutations in BRCA1/2?\n"
                "- What is the penetrance data — lifetime breast cancer risk and ovarian cancer "
                "risk for carriers of this specific mutation based on the latest large cohort studies?\n"
                "- Are there any known genotype-phenotype correlations specific to this mutation?\n\n"
                "Use web search to find the most current data. Output structured findings with sources."
            ),
            full_auto=True,
        ),
        Agent(
            name="molecular-biology-expert",
            role=(
                "You are a molecular biologist specializing in DNA damage response and "
                "repair pathways. You have expertise in protein structure-function relationships "
                "and the BRCA1/BRCA2 repair axis. You have access to web search — USE IT "
                "to look up recent research on BRCA1 protein domains, interaction partners, "
                "and mechanistic studies. Build upon the genomics findings provided."
            ),
            instruction=(
                "Based on the genomics research provided, explain the molecular consequences:\n"
                "- How does the truncated BRCA1 protein (from 185delAG) affect the RING domain, "
                "BRCT domains, and key functional regions?\n"
                "- How does loss of functional BRCA1 impair homologous recombination repair (HRR)? "
                "Describe the BRCA1-PALB2-BRCA2-RAD51 axis.\n"
                "- What happens to the BRCA1-BARD1 E3 ubiquitin ligase complex?\n"
                "- Explain the concept of 'BRCAness' and synthetic lethality with PARP inhibition "
                "at the molecular level.\n"
                "- What compensatory or reversion mutations have been documented?\n\n"
                "Use web search for the latest mechanistic research. Be precise about protein domains "
                "and molecular interactions."
            ),
            full_auto=True,
        ),
        Agent(
            name="cancer-pathologist",
            role=(
                "You are an anatomic pathologist and cancer biologist specializing in "
                "hereditary breast and ovarian cancers. You have access to web search — "
                "USE IT to look up NCCN guidelines, SEER data, tumor classification systems, "
                "and recent pathology literature. Integrate the molecular findings from "
                "previous experts into a pathological risk profile."
            ),
            instruction=(
                "Based on the genomics and molecular biology research provided, analyze:\n"
                "- What specific cancer types is this patient at elevated risk for? (breast, "
                "ovarian, pancreatic, others) — provide lifetime risk percentages from recent studies.\n"
                "- What are the expected histological subtypes? (triple-negative breast cancer, "
                "high-grade serous ovarian carcinoma, etc.) — explain why BRCA1 tumors show these patterns.\n"
                "- What molecular subtypes are expected (basal-like, etc.) and what are the "
                "immunohistochemical profiles (ER/PR/HER2 status)?\n"
                "- What is the typical age of onset and tumor grade?\n"
                "- How does the tumor microenvironment differ in BRCA1-mutant cancers? "
                "(TILs, PD-L1 expression, genomic instability scores)\n\n"
                "Use web search for the latest NCCN guidelines and epidemiological data."
            ),
            full_auto=True,
        ),
        Agent(
            name="clinical-oncologist",
            role=(
                "You are a clinical oncologist specializing in hereditary cancer management "
                "and precision oncology. You have access to web search — USE IT to look up "
                "the latest NCCN guidelines (2024-2025), FDA-approved therapies, ongoing "
                "clinical trials, and evidence-based risk reduction strategies. Synthesize "
                "all prior research into actionable clinical recommendations."
            ),
            instruction=(
                "Based on ALL the research from previous domain experts, provide comprehensive "
                "clinical recommendations for this 35-year-old BRCA1 185delAG carrier:\n\n"
                "RISK REDUCTION:\n"
                "- Prophylactic bilateral mastectomy: risk reduction percentage, optimal timing\n"
                "- Prophylactic bilateral salpingo-oophorectomy (BSO): recommended age, risk reduction\n"
                "- Chemoprevention options (tamoxifen, olaparib prevention trials)\n\n"
                "SURVEILLANCE:\n"
                "- Breast MRI and mammography schedule per latest NCCN guidelines\n"
                "- Ovarian cancer screening limitations and recommendations\n"
                "- Any emerging screening modalities (liquid biopsy, ctDNA)\n\n"
                "TREATMENT (if cancer develops):\n"
                "- PARP inhibitors: which ones are FDA-approved, clinical trial evidence "
                "(OlympiAD, EMBRACA, etc.)\n"
                "- Platinum-based chemotherapy rationale and response rates\n"
                "- Immunotherapy potential (checkpoint inhibitors given high TILs/PD-L1)\n"
                "- Emerging therapies: antibody-drug conjugates, combination approaches\n\n"
                "FAMILY IMPLICATIONS:\n"
                "- Cascade genetic testing recommendations for relatives\n"
                "- Reproductive considerations (PGT-M)\n\n"
                "Use web search for the most current guidelines and clinical trial data."
            ),
            full_auto=True,
        ),
        Agent(
            name="integrative-synthesizer",
            role=(
                "You are a senior medical director and translational medicine expert who "
                "bridges basic science and clinical practice. Your role is to synthesize "
                "complex multi-domain research into a coherent, comprehensive, and actionable "
                "clinical summary. You have access to web search to verify any details."
            ),
            instruction=(
                "You have received comprehensive research from four domain experts:\n"
                "1. Genomics Specialist — mutation details and population genetics\n"
                "2. Molecular Biologist — protein function and DNA repair mechanisms\n"
                "3. Cancer Pathologist — risk profile and tumor characteristics\n"
                "4. Clinical Oncologist — prevention, surveillance, and treatment strategies\n\n"
                "Your task: Synthesize ALL of this into a single, well-structured comprehensive "
                "report that:\n"
                "- Connects the molecular mechanism (WHY the mutation causes cancer) to the "
                "clinical phenotype (WHAT cancers develop) to treatment rationale (HOW we treat)\n"
                "- Provides a clear decision framework for the patient\n"
                "- Highlights the most critical action items with their evidence levels\n"
                "- Notes any areas of uncertainty or evolving evidence\n"
                "- Is written at a level suitable for an informed patient or referring physician\n\n"
                "Structure the final report with clear sections and a brief executive summary at the top."
            ),
            full_auto=True,
        ),
    ]

    print("=" * 70)
    print("BIOLOGY MULTI-DOMAIN PIPELINE")
    print("=" * 70)
    print(f"\nQuestion:\n{QUESTION}")
    print(f"\nPipeline: {' -> '.join(a.name for a in agents)}")
    print(f"Model: gpt-5.2-codex (with web search enabled)")
    print("=" * 70)
    print()

    coordinator = PipelineCoordinator(agents)
    result = coordinator.run(QUESTION)

    print(f"\n{'=' * 70}")
    print(f"Pipeline {'SUCCEEDED' if result.success else 'FAILED'}")
    print(f"Steps completed: {len(result.steps)}/{len(agents)}")
    print(f"Elapsed: {result.elapsed:.1f}s")
    print(f"{'=' * 70}")

    # --- Determine output directory ---
    base = os.path.join("tests", "outputs", "pipeline")
    os.makedirs(base, exist_ok=True)
    existing = [int(d) for d in os.listdir(base) if d.isdigit()]
    out_dir = Path(base) / str(max(existing, default=0) + 1)
    out_dir.mkdir()

    # --- Save trace JSON ---
    trace = build_trace(result, task=QUESTION)
    trace_path = out_dir / "pipeline_trace.json"
    save_trace(trace, str(trace_path))
    print(f"\nTrace saved to: {trace_path}")

    # --- Save report as Markdown ---
    from datetime import datetime, timezone
    report_lines = [
        "# BRCA1 185delAG Comprehensive Analysis",
        f"*Generated by multi-domain pipeline on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "---",
        "",
    ]
    for i, step in enumerate(result.steps):
        report_lines.append(f"## Step {i + 1}: {step.agent_name}")
        report_lines.append("")
        if step.error:
            report_lines.append(f"**ERROR**: {step.error}")
        else:
            report_lines.append(step.output)
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

    report_path = out_dir / "pipeline_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
