# Implementation Status

Tracks the gap between the tech stack described in Research_Proposal.docx and what is
actually running in code. Updated as the project evolves.

---

## Implemented (running in production code)

| Component | File | Notes |
|-----------|------|-------|
| Google Maps Places API | skills/google_maps.py | ZIP-code looping, place_id dedup, auto-pagination |
| OpenAI GPT-4o-mini | code/agent_workflow.py | temperature=0.0, per-category classification_logic |
| NPPES NPI Registry validation | code/validate_nppes.py | Fuzzy name match, P/R/F1 report, retry on 429 |
| Wayback Machine CDX enrichment | skills/wayback_agent.py | Optional; captures chain vs independent signal |
| NAICS 446110 pharmacy task | code/main.py | Full config with retail-specific classification logic |

---

## Planned (not yet started)

| Component | Trigger | Rationale |
|-----------|---------|-----------|
| PostGIS | After pilot dataset exceeds ~5,000 records | Replace pandas spatial joins with ST_DWithin and ST_KernelDensity; needed for MSA-scale kernel density maps |
| PyMC spatial regression | After ground truth data arrives (MN Board of Pharmacy) | Bayesian hierarchical model with CAR prior for spatial autocorrelation; posterior CI for coverage gap estimates |
| MN Board of Pharmacy validator | When data request is fulfilled (ETA 2-3 weeks) | Replace validate_nppes.py ground truth with validate_mnbop.py; NPPES remains as secondary check |

---

## Deferred (consciously not building yet)

| Component | Decision | Reason |
|-----------|----------|--------|
| LangChain / MAS orchestration | Deferred until pharmacy data collection is validated | Single-agent workflow (agent_workflow.py) is sufficient for one city, one category; MAS adds latency and complexity without benefit at current scale |
| NCPDP DataQ | No access, shelved | Requires institutional subscription; NPPES + MN Board of Pharmacy covers the validation need |

---

## Not applicable at current scale

| Component | Reason |
|-----------|--------|
| HPC / SLURM parallelization | Minneapolis MSA pharmacy dataset is approximately 200-400 records; serial pipeline completes in under 30 minutes; HPC adds no value |

---

## Ground Truth Priority Order

1. MN Board of Pharmacy licensure database (applied, pending receipt)
2. NPPES NPI Registry (active, used in validate_nppes.py)
3. NCPDP DataQ (no access, shelved)

When MN Board data arrives: write validate_mnbop.py with same interface as
validate_nppes.py (--ai-csv, --output, --threshold flags). NPPES validation
continues as a secondary cross-check.

---

## Known Limitations to Flag in Thesis

- NPPES excludes pharmacies that do not participate in Medicare or Medicaid. This
  may systematically undercount independent pharmacies serving cash-pay populations,
  which is directionally consistent with the thesis argument that small independent
  establishments are undercounted in administrative datasets including NETS.
- Wayback Machine coverage is asymmetric: chain pharmacies with corporate websites
  have 10-15 years of snapshots; independent pharmacies with no dedicated domain
  return Snapshot_Count=0. This is a feature, not a bug: use it as a proxy for
  chain vs independent status in analysis.
