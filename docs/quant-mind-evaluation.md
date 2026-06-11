# QuantMind Evaluation

Hands-on evaluation of [LLMQuant/quant-mind](https://github.com/LLMQuant/quant-mind)
(v0.2.0, master @ June 2026): cloned, installed, test suite run, and the
extraction pipeline exercised against real inputs.

## What it is

QuantMind is a Python framework that turns unstructured financial content
(papers, news, blogs) into typed, structured knowledge objects using LLMs.
The pipeline is:

```
fetch (arXiv / DOI / HTTP / local file)
  → format (PDF→text via PyMuPDF, HTML→markdown via trafilatura)
    → flow (OpenAI Agents SDK agent with output_type=Paper)
      → typed Pydantic knowledge object (Paper, News, Earnings, Factor, Thesis)
```

Plus a `magic.resolve_magic_input()` helper that turns a free-form natural
language request into typed flow inputs, and `batch_run()` for concurrent
fan-out with error skipping and progress callbacks.

- ~935 stars, MIT license, paper accepted at the NeurIPS 2025 GenAI in
  Finance workshop.
- Python ≥3.10, managed with `uv`. Key deps: `openai-agents`, `litellm`,
  `pymupdf`, `trafilatura`, `arxiv`, `pydantic`.

## What I verified hands-on

| Step | Result |
|---|---|
| `uv pip install -e .` | Clean install (note: pyproject pins a Tsinghua PyPI mirror as default index; needed `--default-index https://pypi.org/simple` override) |
| Test suite | **233/233 passed**, 89% coverage, enforced 75% floor, runs in ~7s (LLM calls mocked via respx) |
| `fetch_url()` + `html_to_markdown()` | Works on a live page: 381 KB HTML → 8.7 KB clean markdown |
| `read_local_file()` + `pdf_to_markdown()` | Works: PDF bytes → extracted text |
| `fetch_arxiv()` | Code is sound but could not be exercised here — this sandbox's network policy blocks arxiv.org (HTTP 403 from both the API and PDF endpoints, confirmed with curl) |
| `paper_flow()` (LLM extraction) | Not run — requires an `OPENAI_API_KEY`, which is not available in this environment |

## Code quality assessment

Genuinely good for a sub-1.0 open-source project:

- Clean layering with import-linter contracts enforcing it
  (`preprocess` does fetch/format only, no LLM calls; `flows` orchestrates;
  `knowledge` holds Pydantic schemas).
- Modern toolchain: ruff, basedpyright, pytest with coverage floor,
  pre-commit, conventional commits.
- Thoughtful API: frozen dataclasses at the fetch boundary, discriminated
  unions for flow inputs, three documented customization layers
  (config → kwargs → fork the flow file).
- Async throughout, with CPU-bound work (PDF parsing) pushed to threads.

## Gaps and caveats

1. **No storage layer exists yet.** The `docs/design/en/storage.md` design
   doc describes a `quantmind.storage` module (LocalStorage, indexes,
   embeddings) that is **not in the codebase** — it was removed/deferred
   during the ongoing OpenAI Agents SDK migration. The `mind/` memory +
   store layer is scheduled for their PR6/PR7. Today the framework hands
   you a Pydantic object and persistence is your problem.
2. **Retrieval is aspirational.** The README's Stage 2 (embeddings, RAG,
   DeepResearch, knowledge graph) does not exist in code. What ships today
   is Stage 1 extraction only.
3. **OpenAI-coupled.** Flows are built on the OpenAI Agents SDK; `litellm`
   is a dependency so other providers may be routable, but the documented
   path is `gpt-4o-mini` with an OpenAI key.
4. **Mid-migration.** v0.2.0, API surface still moving (their issue #71
   tracks the migration). Expect breaking changes.
5. PDF extraction is plain-text quality (PyMuPDF); higher-fidelity engines
   (marker-pdf, llama-parse) are planned but not wired in.

## Verdict and recommended next steps

The extraction layer is real, well-built, and tested — but the "knowledge
base" half (storage, embeddings, retrieval) is design-doc-only today. If
our goal is a populated, queryable database, QuantMind currently gives us
a high-quality front half of the pipeline and nothing for the back half.

Options, in rough order of preference:

1. **Use it as the ingestion library, own the storage.** Depend on
   `quantmind` for fetch/parse/LLM-extraction, and build our own
   persistence (e.g. SQLite/Postgres + a vector index) around the Pydantic
   `Paper`/`News` objects it emits. Their storage design doc is a usable
   blueprint. Risk: API churn until their migration lands; pin a commit.
2. **Wait for PR6/PR7** (their `mind/` store layer) before committing, and
   prototype against the extraction layer in the meantime.
3. **Borrow the architecture, not the code** — if our domain isn't
   finance, the prompts/schemas are finance-specific and we'd be rewriting
   the valuable part anyway; the fetch/format layer is generic and small
   enough to reimplement.

To run the full flow end-to-end ourselves we need: an OpenAI API key and
network access to arxiv.org (or use `HttpUrl`/`LocalFilePath` inputs
instead of arXiv IDs).
