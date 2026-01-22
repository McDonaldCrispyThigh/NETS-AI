# NETS-AI

## 1. Project Purpose

### Academic Goal

Reveal methodological challenges inherent in using the NETS database and explore whether AI can serve as a viable alternative data source.

### Technical Goal

Evaluate whether AI models (e.g., GPT, Gemini) can automatically and accurately generate research-ready business datasets that resemble NETS in structure.

---

## 2. Core Methodology: From Manual Testing to a Reproducible Agent

**Core Issue:** "Deep Research"-style usage within ChatGPT/Gemini interfaces is **not sufficiently reproducible for scientific research.**

Therefore, our core technical direction shifts toward:

> **Building a custom AI Agent via API (instead of using UI-based workflows).**

This Agent will attempt to replicate "Deep Research" behavior.

### — Agent Workflow

1. **Context Injection**
   Load all Markdown files from `docs/` (in progress) as background knowledge and system instructions.

2. **Tool Registration**
   Register external APIs the Agent is allowed to use (e.g., Google Search API, Yelp API, Google Maps API).

3. **Prompt Execution**
   The Agent executes optimized prompts from `docs/PROMPT_GUIDE.md`.

4. **Structured Output**
   Output structured data according to `docs/agent/PIPELINE_SPEC.md` (expected CSV).

---

## 3. Repository Structure — The Agent’s "Brain"

This repository is not only code; it also functions as the **knowledge base** that the Agent loads prior to execution.

```plaintext
/
├── README.md
└── docs/
    ├── PROMPT_GUIDE.md
    ├── QUESTION_CODING_SCHEME.md
    ├── DATA_COLLECTION_PROTOCOL.md
    └── agent/
        ├── PIPELINE_SPEC.md
        └── TOOLS_REGISTRY.md
```

### `README.md`

Project overview, objectives, and core methodology.

### `docs/PROMPT_GUIDE.md`

Stores optimized prompts (v2.0, v3.0, ...).
→ Iteratively updated based on AI clarifying-question analysis from Sprint 1.

### `docs/QUESTION_CODING_SCHEME.md`

Records and buckets all clarifying questions raised by AI during v1 prompt testing.
→ Helps identify ambiguous regions in the prompt → enables prompt refinement.

### `docs/DATA_COLLECTION_PROTOCOL.md`

SOP for manual execution in Sprint 1.

### `docs/agent/PIPELINE_SPEC.md`

### `code/` (The Cortex)

Contains the execution logic (`main.py`) that orchestrates the workflow.

### `skills/` (The Limbs):

Python modules for external tools (Google Maps API, Yelp API). Replaces the manual "Deep Research" browsing.

### `context/` (The Memory):

Contains the "World View" for the AI: NETS definitions, NAICS coding schemes, and refined prompts from Sprint 2.

🚧 **(TBD)**
Defines the technical execution pipeline of the Agent, e.g.:

1. Parse query → call tools
2. Extract information
3. Validate fields
4. Output CSV

### `docs/agent/TOOLS_REGISTRY.md`

🚧 **(TBD)**
Defines external tools available to the Agent, including:

* API documentation
* Returnable fields
* Cost
* Pros / cons
* Include? (Y/N)

---

## 4. Project Sprints

### ✅ Sprint 1 — Agent Implementation

*Currently in progress*

**Goal**
Build and test a runnable API-driven Agent.

**Tasks (Mike & Congyuan)**

* Write scripts to call OpenAI/Gemini APIs
* Implement Context Injection from `docs/`
* (Optional) Implement external tool registration (e.g., Yelp)

---

### ✅ Sprint 2 — Prompt Optimization & Context Expansion

**Goal**
Produce the first improved prompt.

**Tasks (Congyuan, Yue, Mallory)**

* Run v1.0 prompt (`PROMPT_GUIDE.md`)
* Record all AI clarifying questions
* Bucket and consolidate into `QUESTION_CODING_SCHEME.md`
* Analyze patterns → detect ambiguous prompt zones
* Draft v2.0 prompt (pre-answering mandatory questions)

---

### ✅ Sprint 3 — Data Generation & Analysis

**Goal**
Use the completed Agent to generate business datasets.

**Tasks**

* Generate data for target business categories
* Time coverage: **2005, 2015, 202#**
* Classification dimensions:

  * Dim 1: Information accessibility
  * Dim 2: Organization type (public/private/non-profit, etc.)

---

### ✅ Sprint 4 — NETS Comparison & Visualization

**Goal**
Answer: **To what extent can AI replace NETS?**

**Tasks**

* Compare AI-sourced data with NETS (Hackathon data)
* Key metrics:

  * Accuracy
  * Coverage
  * Classification Consistency
* Visualization via ArcGIS Pro

---

## 5. Paper Abstract (Draft)

**Objective**
Reveal methodological challenges in NETS-based research and evaluate whether AI can serve as a potential alternative solution.

**Methods**
Test a reproducible AI Agent and frame analysis within literature context.

**Key Findings**
AI capability is limited; its failure (especially with historical/time-series data) highlights blind spots in NETS.

**Keywords**
NETS • AI-generated Database • Prompt Engineering • Reproducibility • AI Agent
