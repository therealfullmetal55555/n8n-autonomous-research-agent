#!/usr/bin/env python3
"""
Offline Benchmark & Simulation Suite for Autonomous Research Agent with Tool Selection.
Verifies multi-tool routing (search, fetch, calc, internal), budget caps, and citation truthfulness.
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from research_agent import ResearchAgent

def run_research_benchmark():
    print("=" * 85)
    print(">>> N8N AUTONOMOUS RESEARCH AGENT: TOOL USE, BUDGET & CITATION HONESTY BENCHMARK")
    print("=" * 85)

    agent = ResearchAgent(max_tool_calls=8)
    queries_path = os.path.join(os.path.dirname(__file__), "demo-data", "research_queries.json")
    with open(queries_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    passed = 0
    total = len(queries)
    start_time = time.time()

    for idx, q in enumerate(queries, 1):
        brief = agent.run_research(q["question"])
        brief_md = brief.to_markdown()

        keyword_ok = q["expected_answer_keyword"].lower() in brief_md.lower()
        url_ok = any(q["expected_primary_url"] in u for u in brief.cited_urls)
        budget_ok = brief.total_tool_calls <= q["max_tool_calls"]
        citation_ok = len(brief.unverified_citations) == 0

        is_passed = keyword_ok and url_ok and budget_ok and citation_ok
        if is_passed:
            passed += 1

        status_flag = "[\033[92mPASS\033[0m]" if is_passed else "[\033[91mFAIL\033[0m]"
        print(f"{status_flag} Query #{idx} [{q['id']}]: \"{q['question'][:75]}...\"")
        print(f"       Title       : {brief.title}")
        print(f"       Tool Calls  : {brief.total_tool_calls} (Cap: {q['max_tool_calls']}) | Budget OK: {budget_ok}")
        print(f"       Primary URLs: {brief.cited_urls}")
        print(f"       TL;DR       : \"{brief.tldr[:85]}...\"")
        print("-" * 85)

    elapsed_ms = (time.time() - start_time) * 1000
    print(f"\nResearch Agent Benchmark: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print(f"Average Execution Latency: {elapsed_ms/total:.2f} ms / research run\n")

    # Safety Guardrail Verification: Catching Unverified/Hallucinated URL in Brief
    print("=" * 85)
    print(">>> CITATION TRUTHFULNESS GUARD: DETECTING UNFETCHED CITATION & AUTO-REPAIR")
    print("=" * 85)

    hallucinated_brief = agent.run_research(
        "Compare the entry-level paid plan price of n8n Cloud and Zapier",
        force_hallucinated_citation=True
    )
    caught_hallucination = len(hallucinated_brief.unverified_citations) > 0 or hallucinated_brief.is_repaired
    repaired_clean = hallucinated_brief.is_repaired and "UNVERIFIED CITATION FLAGGED" in " ".join(hallucinated_brief.risks_and_uncertainties)

    print(f"1. Hallucinated URL Intercept : Flagged='{hallucinated_brief.unverified_citations}' | Intercepted={caught_hallucination}")
    print(f"2. Auto-Repair Demotion Pass  : Repaired={repaired_clean}")
    print(f"3. Final Clean Sources        : {hallucinated_brief.cited_urls}")
    print("-" * 85)

    if (passed == total) and caught_hallucination and repaired_clean:
        print("\033[92m[SUCCESS] ALL RESEARCH AGENT & CITATION GUARD SUITES PASSED 100%\033[0m\n")
        return 0
    else:
        print("\033[91m[FAILURE] RESEARCH SUITE REGRESSION DETECTED\033[0m\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_research_benchmark())
