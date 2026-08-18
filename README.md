# AI QA Mentor Agent

A local-first agent that reads a project's documentation and a tester's bug
sheet, finds real testing gaps, and coaches the tester on what to test next
and why — while remembering each tester's personal blind spots across
sessions, and flagging when a gap resembles a bug pattern seen in other,
unrelated projects.

Runs entirely on your machine via [Ollama](https://ollama.com) — no API keys,
no cloud calls.

## How it works

1. **Requirement extraction** — an LLM reads the docs and produces a
   structured list of every feature, user flow, state, and business rule.
2. **Coverage mapping** — that list is compared against the bug sheet; each
   requirement is tagged `tested` / `partial` / `untested`.
3. **Personal blind-spot matching** — untested/partial items are checked
   against this tester's own history of previously-missed categories.
4. **Cross-client pattern matching** (the unique step) — separately,
   untested/partial items are embedded and compared against a corpus of
   abstracted "bug motifs" (root cause + trigger condition, stripped of any
   client-specific detail) via local cosine-similarity search, surfacing
   gaps that structurally resemble bugs seen in other, unrelated projects.
5. **Test case + coaching generation** — for every real gap: exact test
   steps, plus a plain-language explanation of the reasoning behind it,
   naming any recurring personal blind spot or cross-client pattern found.
6. **Memory update** — this session's gaps are saved to the tester's profile
   (`data/profiles/<tester>.json`) so future sessions can flag recurring
   blind spots.

The `data/bug_motifs.json` corpus shipped here is a **synthetic starter
set** (~35 generic web-app QA failure patterns) — a placeholder for what
Phase 4 of the original plan describes as real bug data abstracted across
multiple client projects. Swap it for real data once you have it; the
schema (`id`, `category`, `root_cause`, `trigger_condition`, `description`)
stays the same.

Fine-tuning (Phase 5 of the original plan) is intentionally not built —
it's explicitly gated on having real usage data, which doesn't exist yet.

## Setup

```bash
brew install ollama
brew services start ollama
ollama pull qwen2.5:7b-instruct
ollama pull nomic-embed-text

python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Usage

```bash
./venv/bin/python cli.py \
  --docs samples/sample_docs.md \
  --bugsheet samples/sample_bugsheet.md \
  --tester alice \
  --project "TaskFlow Demo"
```

Output is printed to the terminal and saved to `output/<project>_<tester>.md`.

## Project layout

```
qa_mentor/
  llm.py                  local Ollama chat client (no API keys)
  embeddings.py           local Ollama embedding client
  vector_index.py         cosine-similarity search over the bug-motif corpus
  stage1_requirements.py  docs -> structured requirement list
  stage2_coverage.py      requirements + bug sheet -> tested/partial/untested
  stage3_blindspots.py    personal blind-spot lookup
  stage4_cross_client.py  cross-client bug-motif matching
  stage5_coaching.py      gap -> test steps + reasoning
  stage6_memory_update.py writes session results back to tester profile
  profile_store.py        JSON-file-backed per-tester profile store
  pipeline.py             orchestrates all stages
cli.py                    command-line entry point
samples/                  sample docs + bug sheet to try it out
data/bug_motifs.json      synthetic cross-client bug-motif corpus (seed data)
data/motif_embeddings.json  cached embeddings for the corpus (git-ignored, auto-rebuilt)
data/profiles/            per-tester memory (git-ignored)
```
