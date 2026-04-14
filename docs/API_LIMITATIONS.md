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

NPPES indexes healthcare providers by National Provider Identifier (NPI),
not by consumer-facing retail location. This structural mismatch produces
three distinct categories of False Negatives that inflate the registry count
relative to the true population of active retail pharmacy locations.

---

### 2.2 Corporate legal names (non-retail NPI holders)

NPPES assigns NPIs to legal entities, not individual store locations.
Large retail pharmacy chains frequently hold a single NPI under the
corporate parent name rather than registering each location separately.

**Named example:** `SUPERVALU PHARMACIES INC` appears as a single NPPES
record for the entire Supervalu/Cub Foods pharmacy network, which operates
multiple in-store pharmacy counters across the Twin Cities MSA. A search
within the target ZIP codes returns this corporate NPI rather than
individual Cub Pharmacy locations.

**Implication:** AI collection retrieves each Cub Pharmacy as a distinct
place (correct for a retail dataset), while NPPES records a single
corporate entity. This generates one or more NPPES False Negatives per
affected ZIP code even when the AI dataset correctly captured the retail
presence.

**Affected ZIPs (observed):** 55411, 55413, 55421, and others where
Cub Pharmacy operates in-store pharmacies.

---

### 2.3 Closed and acquired chains

NPPES records are not systematically deactivated when a pharmacy chain
closes or is acquired by another brand. Legacy NPI records remain in the
registry with `Active` status even when the physical location no longer
exists.

**Named examples:**
- `Snyder Drug` -- regional chain (Minnesota/Wisconsin/Dakotas) that
  ceased operations; NPI records persist as active.
- `Osco Drug` -- acquired by Albertsons/Jewel; many store-level NPIs
  remain active in the registry despite closures.
- `Phar-Mor` -- deep-discount pharmacy chain that liquidated; historical
  NPIs still retrievable via NPPES.

**Implication:** AI collection (based on current Google Maps listings)
will not return closed chains. These records appear as NPPES False
Negatives classified as `closed_chain`, artificially depressing recall.

---

### 2.4 Specialty and non-retail pharmacies

NPPES uses taxonomy code `333600000X` for all pharmacy types including
retail, mail-order, compounding, infusion, oncology, and long-term care
dispensing services. The taxonomy code does not distinguish retail
consumer-facing pharmacies from back-office or closed-system dispensing
operations.

**Pattern-matched non-retail categories (implemented in `validate_nppes.py`):**
- Mail-order / specialty: `MAIL ORDER`, `SPECIALTY`, `MAIL-ORDER`
- Compounding: `COMPOUNDING`, `COMPOUND`, `COMPD`
- Infusion/clinical: `INFUSION`, `ONCOLOGY`, `NUCLEAR`, `RADIOPHARM`
- Long-term care: `LONG TERM CARE`, `LTC`, `NURSING`, `ASSISTED LIVING`
- Hospital outpatient: `HOSPITAL`, `MEDICAL CENTER`, `CLINIC`

**Implication:** These entries count as NPPES ground truth records within
the target ZIPs but are not discoverable via Google Maps consumer search.
They inflate the False Negative count under the `specialty_nonretail`
classification without representing a failure of AI collection.

---

### 2.5 Effect on precision and recall metrics

The reported validation figures (Precision 38.8%, Recall 17.8%, F1 24.4%)
are computed against the full NPPES registry and reflect NPPES structural
limitations as much as AI data quality.

**Decomposition of NPPES False Negatives (n=755):**

| Category | n | Share of FNs | AI failure? |
|----------|---|--------------|-------------|
| Possible missed retail | 252 | 33.4% | Likely yes |
| Corporate legal name | 237 | 31.4% | No -- NPPES artifact |
| Closed / acquired chain | 150 | 19.9% | No -- stale NPPES record |
| Specialty / non-retail | 116 | 15.4% | No -- not a retail location |

**Adjusted recall (excluding non-AI-attributable FNs):** Removing
`corporate_legal_name`, `closed_chain`, and `specialty_nonretail`
FNs reduces the effective denominator from 872 to approximately 252 + 117
(True Positives) = ~369 retail-comparable records, yielding an adjusted
recall of approximately 31.7%. Adjusted precision is unchanged (38.8%
is determined by AI True Positives / AI total, not by NPPES structure).

**Thesis note:** Both raw and adjusted figures should be reported. The
raw figures reflect validation against the NPPES registry as administered.
The adjusted figures reflect performance against the subset of NPPES
records that are structurally comparable to an AI consumer-visibility
dataset.

---

## 3. MN Board of Pharmacy (Planned Primary Ground Truth)

### 3.1 Data request status

A formal data request for the current licensure database of active retail
pharmacy locations in Minnesota was submitted to the Minnesota Board of
Pharmacy on 2026-04-13. Receipt is pending as of this writing.

**Scope of expected dataset:** Active retail dispensary licenses within
the 60 target ZIP codes. Expected to exclude corporate legal names,
closed establishments, and specialty/non-retail dispensers by virtue of
indexing on current retail licensure rather than NPI registration.

---

### 3.2 Planned geocoding approach

MN Board of Pharmacy records will be provided as a licensure database
with street address fields rather than geographic coordinates. Geocoding
will be performed using the U.S. Census Bureau Geocoder API
(`geocoding.geo.census.gov/geocoder/locations/onelineaddress`), which
returns TIGER/Line-matched coordinate pairs at no cost and with no
API key requirement.

**Implication:** Addresses that do not match the TIGER/Line road network
(e.g., new construction, rural routes) will require manual verification
or fallback to Google Maps geocoding.

---

### 3.3 Expected improvement over NPPES

Replacing NPPES with MN Board of Pharmacy as the primary ground truth is
expected to substantially improve precision and recall figures by:

1. Eliminating corporate legal name records (SUPERVALU-type inflation)
2. Excluding closed/acquired chain records (Snyder Drug-type staleness)
3. Restricting the ground truth to currently licensed retail dispensaries

The adjusted NPPES recall estimate (approximately 31.7%) is expected to
serve as a lower bound for the MN Board-based recall figure.

---

## 4. Wayback Machine

### 4.1 Chain pharmacies bypassed (sentinel -1)

Chain pharmacies (CVS, Walgreens, Rite Aid, Walmart, Target, Costco,
Kroger, Hy-Vee, Cub) are assigned `Wayback_Snapshot_Count = -1` as a
sentinel value. Their Wayback coverage is not queried.

**Implication:** Chains (n=176 of 399 in full-MSA run) have no longevity
signal from Wayback. The Wayback distribution analysis applies only to
independent pharmacies.

### 4.2 No web presence (value = 0)

Pharmacies with no `Business_Website` recorded have `Wayback_Snapshot_Count = 0`.
This conflates "no website ever" with "website not captured by Wayback."

**Implication:** 0 is a lower bound; the true web-presence rate may be
slightly higher than the 0-count group implies.

---

## 5. ACS / Census Data

### 5.1 Tract-level income is 5-year estimate

`med_hh_income` is from ACS 5-year 2023 (2019-2023 average). It does not
reflect point-in-time conditions and smooths over within-tract variation.

### 5.2 Pharmacy desert metric uses tract centroid

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
| NPPES | Corporate legal names inflate FN count | High | FN classification (`corporate_legal_name`) |
| NPPES | Closed/acquired chains remain active | High | FN classification (`closed_chain`) |
| NPPES | Specialty/non-retail inflate FN count | Medium | FN classification (`specialty_nonretail`) |
| NPPES | Precision/Recall reflect registry quality | High | Report adjusted figures alongside raw |
| NPPES | Interim ground truth only | High | Awaiting MN Board of Pharmacy data |
| MN Board of Pharmacy | Addresses require geocoding | Medium | Census Bureau Geocoder API (planned) |
| Wayback Machine | Chains bypassed (sentinel -1) | Low | Documented; independent only |
| ACS | 5-year tract-level estimate | Low | Standard in literature |
| Desert metric | Centroid-based distance | Low | Note in methods |
