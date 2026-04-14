# Data Collection API Limitations

**Project:** NETS-AI Pharmacy Access Study  
**Last updated:** 2026-04-13

This file records hard constraints and known biases in each data source.
Intended as a reference for both pipeline development and thesis discussion sections.

---

## 1. Google Places API

### 1.1 Text Search result cap: 60 per query

The Places Text Search API (`client.places(query=...)`) returns a maximum of
**60 results per query** (3 pages x 20 results). This is a hard API constraint
with no workaround within a single query.

**Implication:** In dense urban ZIPs (e.g., 55113, 55406), the true number of
pharmacies likely exceeds 60. Any single-term, single-ZIP query systematically
undercounts establishments.

**Mitigation implemented:** `agent_workflow.py` now runs multiple query
variants per ZIP (`"Pharmacy"`, `"Drug Store"`, `"Drugstore"`) and de-duplicates
by `place_id`. This recovers some missed establishments but does not guarantee
complete coverage -- a ZIP with 90 pharmacies under the term "Pharmacy" alone
will still be truncated at 60 for that term.

**Thesis note:** The AI-collected dataset represents a lower bound on pharmacy
counts, not a census. Coverage is consumer-visibility-biased (well-reviewed,
active listings rank higher in search results).

---

### 1.2 Review count: 5 reviews per place, random by default

The Place Details API returns at most **5 reviews per place**. The default sort
order is `most_relevant`, which is algorithmically determined and not
reproducible -- effectively random from a research perspective.

**Implication:** `Last_Review_Date` derived from default results reflects
the most recent date among 5 algorithmically-selected reviews, not the
actual last review date for the business.

**Mitigation implemented:** `get_place_details` now passes
`reviews_sort="newest"`, so the 5 returned reviews are the 5 chronologically
most recent. `Last_Review_Date` now represents a lower-bound estimate of the
most recent customer activity date (accurate to within the gap between
review #5 and #6 most recent, which is unknown).

**Thesis note:** `Last_Review_Date` should be cited as
*"most recent date among the 5 newest reviews returned by Google Places API."*
It is a lower-bound estimate of last customer activity, not a verified closure
or activity indicator. For pharmacies with fewer than 5 total reviews, it is
exact.

---

### 1.3 Google Maps reflects consumer-facing visibility, not licensure

Google Places indexes businesses that have claimed or been auto-generated as
Google Business Profiles. A licensed pharmacy with no online presence, no
reviews, and no claimed profile may not appear in search results.

**Implication:** The AI dataset is biased toward:
- Chain pharmacies (high search ranking, many reviews)
- Urban/walkable areas (higher consumer engagement)
- Recently active businesses

Independent, low-profile, or recently opened pharmacies are systematically
under-represented.

**Comparison:** NPPES NPI Registry indexes by licensure, not consumer
visibility. This explains a large share of NPPES False Negatives classified
as "Possible Missed Retail" -- these are licensed but low-visibility
establishments.

---

## 2. NPPES NPI Registry

### 2.1 Interim ground truth status

NPPES is used as an interim ground truth because MN Board of Pharmacy
licensure data was requested but not yet received as of 2026-04-13.

**Implication:** NPPES includes non-retail pharmacy types (mail-order,
specialty, hospital outpatient) that inflate the False Negative count.
The current FN classification (`closed_chain`, `corporate_legal_name`,
`specialty_nonretail`, `possible_missed_retail`) partially corrects for
this, but the "Possible Missed Retail" category (n=69 of 191 FNs) still
conflates true misses with NPPES-only non-retail entries.

**Thesis note:** Precision/Recall figures should be reported with the
caveat that the denominator (NPPES ground truth) is itself imperfect.
Report both raw figures and adjusted figures excluding `corporate_legal_name`
and `specialty_nonretail` FNs.

---

## 3. Wayback Machine

### 3.1 Chain pharmacies bypassed (sentinel -1)

Chain pharmacies (CVS, Walgreens, Rite Aid, Walmart, Target, Costco,
Kroger, Hy-Vee, Cub) are assigned `Wayback_Snapshot_Count = -1` as a
sentinel value. Their Wayback coverage is not queried.

**Implication:** Chains (n=176 of 399 in full-MSA run) have no longevity
signal from Wayback. The Wayback distribution analysis applies only to
independent pharmacies.

### 3.2 No web presence (value = 0)

Pharmacies with no `Business_Website` recorded have `Wayback_Snapshot_Count = 0`.
This conflates "no website ever" with "website not captured by Wayback."

**Implication:** 0 is a lower bound; the true web-presence rate may be
slightly higher than the 0-count group implies.

---

## 4. ACS / Census Data

### 4.1 Tract-level income is 5-year estimate

`med_hh_income` is from ACS 5-year 2023 (2019-2023 average). It does not
reflect point-in-time conditions and smooths over within-tract variation.

### 4.2 Pharmacy desert metric uses tract centroid

Nearest-pharmacy distance is computed from tract centroid, not residential
population-weighted centroid. For large or irregular tracts this may
overestimate or underestimate actual resident access.

---

## Summary Table

| Source | Limitation | Severity | Mitigation |
|--------|-----------|----------|-----------|
| Google Places Text Search | 60 results/query hard cap | High | Multi-variant queries per ZIP |
| Google Places Details | 5 reviews, random sort | Medium | `reviews_sort="newest"` |
| Google Places | Consumer-visibility bias | High | Note in thesis; compare to NPPES |
| NPPES | Includes non-retail types | Medium | FN classification + adjusted metrics |
| NPPES | Interim ground truth only | High | Awaiting MN Board of Pharmacy data |
| Wayback Machine | Chains bypassed (sentinel -1) | Low | Documented; independent only |
| ACS | 5-year tract-level estimate | Low | Standard in literature |
| Desert metric | Centroid-based distance | Low | Note in methods |
