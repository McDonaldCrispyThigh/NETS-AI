# Methodology — Draft v0.1

## 1) Goal
The goal is to design a reproducible workflow for programmatic deep research
that collects business-level data online and outputs structured results
(e.g., JSON / CSV) suitable for analysis.

We aim to replace expensive datasets (e.g., NETS) by automatically generating
high-quality business records via API + web-search tools.

---

## 2) High-Level Workflow

1) Receive query
2) Break query into concrete subtasks
3) Select appropriate tools (API / web search)
4) Retrieve candidate data
5) Validate + cross-reference multiple sources
6) Resolve ambiguity
7) Output structured JSON

---

## 3) Input → Output

### Input
- User/business query
  Example:  
  "Get all coffee shops in Boulder, Colorado."

### Output (JSON)
List of business entries with fields such as
- name
- address
- lat/lon
- website
- employees
- notes
- sources

---

## 4) Core Logic

### Pseudocode

