# AI QA Mentor Agent

A local-first agent that reads a project's documentation and a tester's bug
sheet, finds real testing gaps, and coaches the tester on what to test next
and why — while remembering each tester's personal blind spots across
sessions.

Runs entirely on your machine via [Ollama](https://ollama.com) — no API keys,
no cloud calls.

## How it works

1. **Requirement extraction** — an LLM reads the docs and produces a
   structured list of every feature, user flow, state, and business rule.
2. **Coverage mapping** — that list is compared against the bug sheet; each
   requirement is tagged `tested` / `partial` / `untested`.
3. **Personal blind-spot matching** — untested/partial items are checked
   against this tester's own history of previously-missed categories.
4. **Test case + coaching generation** — for every real gap: exact test
   steps, plus a plain-language explanation of the reasoning behind it.
5. **Memory update** — this session's gaps are saved to the tester's profile
   (`data/profiles/<tester>.json`) so future sessions can flag recurring
   blind spots.

Cross-client pattern matching and fine-tuning are later phases from the
original plan and are not implemented in this MVP.

## Setup

```bash
brew install ollama
brew services start ollama
ollama pull qwen2.5:7b-instruct

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
  llm.py                  local Ollama client (no API keys)
  stage1_requirements.py  docs -> structured requirement list
  stage2_coverage.py      requirements + bug sheet -> tested/partial/untested
  stage3_blindspots.py    personal blind-spot lookup
  stage5_coaching.py      gap -> test steps + reasoning
  stage6_memory_update.py writes session results back to tester profile
  profile_store.py        JSON-file-backed per-tester profile store
  pipeline.py             orchestrates all stages
cli.py                    command-line entry point
samples/                  sample docs + bug sheet to try it out
data/profiles/            per-tester memory (git-ignored)
```
