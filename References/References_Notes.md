# References Notes

Per-paper notes for every reference in `References/`. Each entry: verified
citation, key claim, methodology, relevance to thesis, and any thesis-
correction implications.

Compiled 2026-05-02 after the user's challenge that the mobility-weighted
desert section had been written without reading cited literature. The notes
below reflect actual readings of the PDFs (or PubMed citation snippets where
only those were available).

---

## Mobility / Spatial-Accessibility Methodology

### Ver Ploeg et al. 2012 (USDA ERR-143) — full text read

- **Citation**: Ver Ploeg M., Breneman V., Dutko P., Williams R., Snyder S.,
  Dicken C., Kaufman P. (2012). *Access to Affordable and Nutritious Food:
  Updated Estimates of Distance to Supermarkets Using 2010 Data*. USDA
  Economic Research Service, ERR-143.
- **Key claim**: National-level estimates of food access integrating distance
  AND vehicle availability. 9.7% of US population lives in low-income areas
  >1 mi from a supermarket; 1.8% of all households (2.1M) are >1 mi without a
  vehicle.
- **Methodology**: ½-km grid cells (NOT census tracts in this 2012 report);
  Euclidean distance to nearest supermarket; urban thresholds 0.5 / 0.5–1 / >1
  mi; rural 10 / 10–20 / >20 mi. **Vehicle availability is reported as a
  separate cross-tabulation**, NOT weighted into a single index. Reports
  "% of households without vehicle AND >1 mi from supermarket" as one of
  several indicators.
- **Relevance**: This is the closest published precedent for vehicle-aware
  food/pharmacy desert classification (the Low-Income Low-Access / "LILA"
  framework). MWDR is conceptually descended from this lineage but differs
  methodologically: USDA presents distance and vehicle access as separate
  tables; MWDR collapses them into a single per-tract continuous score.
- **Thesis implication**: Cite as foundation in §3.5 / §4.6, with explicit
  note that MWDR diverges by using continuous population-weighted aggregation.

### Ver Ploeg et al. 2009 (USDA AP-036) — citation noted, partial read

- **Citation**: Ver Ploeg M. et al. (2009). *Access to Affordable and
  Nutritious Food—Measuring and Understanding Food Deserts and Their
  Consequences: Report to Congress.* USDA ERS Administrative Publication
  AP-036.
- **Key claim**: First national-level food access measurement; estimated 8.4%
  of US population in low-income areas >1 mi from supermarket.
- **Methodology**: 1-km grids; same dual-indicator approach (distance +
  vehicle).
- **Relevance**: Original USDA framework that ERR-143 updates. Cite as
  predecessor.

### Walker, Keane & Burke 2010 — citation only (no full text)

- **Citation**: Walker R.E., Keane C.R., Burke J.G. (2010). Disparities and
  access to healthy food in the United States: A review of food desert
  literature. *Health & Place* 16(5), 876–884. doi:10.1016/j.healthplace.2010.04.013
- **Key claim**: Review of food desert literature. Documents inconsistency
  in measurement methods and emphasizes need for transport-aware metrics
  beyond pure distance measures.
- **Relevance**: General review citation for "distance-only metrics are
  inadequate for capturing real access deprivation." Use in §5.2 (centroid-
  threshold limitations) and §3.5 (rationale for mobility weighting).

### Luo & Wang 2003 — citation only (no full text)

- **Citation**: Luo W., Wang F. (2003). Measures of Spatial Accessibility to
  Healthcare in a GIS Environment: Synthesis and a Case Study in Chicago
  Region. *Environment and Planning B* 30(6), 865–884. doi:10.1068/b29120
- **Key claim**: Original derivation of Two-Step Floating Catchment Area
  (2SFCA) method. Synthesizes container, gravity, and provider-to-population
  ratio approaches.
- **Relevance**: Methodological root for any continuous spatial accessibility
  measure, including MWDR conceptually. Cite as the canonical reference for
  alternative-to-binary-threshold accessibility frameworks.

### Apparicio, Cloutier & Shearmur 2007 — citation only (no full text)

- **Citation**: Apparicio P., Cloutier M.S., Shearmur R. (2007). The case of
  Montréal's missing food deserts: evaluation of accessibility to food
  supermarkets. *International Journal of Health Geographics* 6:4.
  doi:10.1186/1476-072X-6-4
- **Key claim**: Three accessibility metrics applied to Montreal: nearest
  supermarket, three nearest, average. Conclusion that "missing deserts" in
  Montreal reflect transit/transport context not captured by binary distance.
- **Relevance**: Precedent for transport-aware food desert critique.
  Particularly relevant to §5.2 critique of binary half-mile thresholds.

### McEntee & Agyeman 2010 — full text read

- **Citation**: McEntee J., Agyeman J. (2010). Towards the development of a
  GIS method for identifying rural food deserts: Geographic access in
  Vermont, USA. *Applied Geography* 30(1), 165–176.
  doi:10.1016/j.apgeog.2009.05.004
- **Key claim**: Rural food desert identification method for Vermont using
  network distance from population units to retailers.
- **Methodology**: GIS-based; 500m, 1 mi, 10 mi thresholds tested.
  **Important footnote (p.171)**: "We have also assumed that most people will
  travel by car or other private automobile to food retailers. Vehicle
  ownership data is unavailable." → They identified the need for
  vehicle-weighted analysis but couldn't implement it.
- **Relevance**: Documents the methodological gap that MWDR fills. Cite as
  evidence that vehicle ownership data has been recognized as missing-but-
  needed for desert classification, supporting the contribution claim of
  the present analysis.

### Wang 2012 — citation only (no full text)

- **Citation**: Wang F. (2012). Measurement, Optimization, and Impact of
  Health Care Accessibility: A Methodological Review. *Annals of the
  Association of American Geographers* 102(5), 1104–1112.
  doi:10.1080/00045608.2012.657146
- **Key claim**: Methodological review of healthcare accessibility metrics:
  proximity, gravity, 2SFCA variants, optimization approaches.
- **Relevance**: Comprehensive review citation for accessibility methods.
  Use as anchor in §3.5 to position MWDR within the accessibility-measurement
  literature.

### Páez et al. 2010 — partial read (full PDF available)

- **Citation**: Páez A., Mercado R.G., Färber S., Morency C., Roorda M.
  (2010). Relative Accessibility Deprivation Indicators for Urban Settings:
  Definitions and Application to Food Deserts in Montreal. *Urban Studies*
  47(7), 1415–1438. doi:10.1177/0042098009353626
- **Key claim**: Develops "relative accessibility deprivation indicators" that
  explicitly integrate vehicle ownership into accessibility measurement.
  Demonstrates the **effect of vehicle ownership for accessibility to food
  services** highlighting social exclusion implications.
- **Methodology**: Cumulative-opportunities accessibility based on model-
  estimated distance traveled, specific to geographical location AND type of
  individual (income / vehicle ownership / disability).
- **Relevance**: Most directly precedent-setting paper for the MWDR concept.
  Páez et al. 2010 explicitly construct accessibility indicators that vary by
  vehicle ownership, which is the conceptual core of MWDR. Cite as the
  primary methodological precedent for §4.6.

### Sharkey 2009 — full text read

- **Citation**: Sharkey J.R. (2009). Measuring potential access to food
  stores and food-service places in rural areas in the U.S. *American
  Journal of Preventive Medicine* 36(4 Suppl), S151–S155.
  doi:10.1016/j.amepre.2009.01.004
- **Key claim**: Argues for ground-truthing in rural food access measurement.
  Documents that public databases miss 19% of stores; specifically 26% of
  supermarkets, 36% of convenience stores, 20% of discount stores.
- **Methodology**: Conceptual review; recommends GPS field validation.
- **Relevance**: Supports thesis argument about validation against regulatory
  ground truth; directly parallel to NPPES-vs-Board issue documented in the
  thesis. Cite in §3.3 (ground truth construction) and §5.1 (data source
  discrepancies).

---

## Pharmacy Deserts / Health Equity (existing thesis citations to verify)

### Qato et al. 2014 — citation confirmed

- **Citation**: Qato D.M., Daviglus M.L., Wilder J., Lee T., Qato D.,
  Lambert B. (2014). 'Pharmacy deserts' are prevalent in Chicago's
  predominantly minority communities, raising medication access concerns.
  *Health Affairs (Millwood)* 33(11), 1958–1965.
  doi:10.1377/hlthaff.2013.1397
- **CORRECTION TO BIB**: Current `qato2014` entry has volume 33 number 8
  pages 1359–1367, which is WRONG. Correct is 33(11):1958–1965.
- **Key claim**: Foundational pharmacy desert paper. Defines "pharmacy
  desert" using half-mile threshold for urban tracts.
- **Methodology**: Census tract level; 0.5 mi / 1 mi thresholds; Chicago.
- **Relevance**: Already heavily cited; correction needed in references.bib.

### Qato et al. 2017 — citation confirmed

- **Citation**: Qato D.M., Zenk S., Wilder J., Harrington R., Gaskin D.,
  Alexander G.C. (2017). The availability of pharmacies in the United States:
  2007–2015. *PLoS ONE* 12(8), e0183172.
  doi:10.1371/journal.pone.0183172
- **Key claim**: National-level pharmacy availability trends 2007–2015;
  pharmacies grew unequally with persistent gaps in minority neighborhoods.
- **Relevance**: Cite for nationwide trend context.

### Guadamuz et al. 2020 — citation confirmed

- **Citation**: Guadamuz J.S., Alexander G.C., Zenk S.N., Qato D.M. (2020).
  Assessment of Pharmacy Closures in the United States From 2009 Through
  2015. *JAMA Internal Medicine* 180(1), 157–160.
  doi:10.1001/jamainternmed.2019.4588
- **Key claim**: Documents 2009–2015 pharmacy closure trends; closures were
  concentrated in independents and disproportionately affected minority
  neighborhoods.
- **Relevance**: Already cited; supports independent pharmacy closure
  argument in §1.1.

### Guadamuz et al. 2021 — citation confirmed

- **Citation**: Guadamuz J.S., Wilder J.R., Mouslim M.C., Zenk S.N.,
  Alexander G.C., Qato D.M. (2021). Fewer Pharmacies In Black And
  Hispanic/Latino Neighborhoods Compared With White Or Diverse Neighborhoods,
  2007–15. *Health Affairs (Millwood)* 40(5), 802–811.
  doi:10.1377/hlthaff.2020.01699
- **Relevance**: Already cited; race × pharmacy access connection.

### Wittenauer et al. 2024 — full text read; citation verified

- **Citation**: Wittenauer R., Shah P.D., Bacci J.L., Stergachis A. (2024).
  Locations and characteristics of pharmacy deserts in the United States: a
  geospatial study. *Health Affairs Scholar* 2(4), qxae035.
  doi:10.1093/haschl/qxae035
- **Key claim**: National pharmacy desert map; 15.8M (4.7%) US population in
  pharmacy deserts. Pharmacy deserts have higher proportions of low education,
  uninsured, low English ability, ambulatory disability, racial/ethnic
  minority residents.
- **Methodology**: Census tract level definition using pharmacy address data
  + Census surveys. Defines pharmacy deserts as low-access AND low-income
  tracts. National scope, all 50 states.
- **Relevance**: Already cited; primary national reference for pharmacy
  desert prevalence.

### Catalano, Woldesenbet & Pawlik 2025 (replaces plosone2025) — full text read

- **Citation**: Catalano G., Woldesenbet S., Pawlik T.M. (2025). Distribution
  of pharmacy deserts and its association with digital divide and residential
  redlining across the United States. *PLOS ONE* 20(8), e0330027.
  doi:10.1371/journal.pone.0330027
- **CORRECTION TO BIB**: Current `plosone2025` entry is wrong on author
  ("PLOS ONE Editorial"), volume (was 20(2), should be 20(8)), pages (was
  e0316789, should be e0330027), and DOI. Replace with `catalano2025`.
- **Key claim**: Pharmacy deserts strongly associated with both Digital
  Divide Index (OR 6.94) and historical redlining (OR 2.18). Pharmacy
  deserts more likely Black, Hispanic, AI/AN segregated communities.
- **Methodology**: 3,105 census tracts (3.72%) classified as pharmacy
  deserts; multivariate logistic regression.
- **Relevance**: Already cited as `plosone2025`. The HOLC overlay analysis
  in §5.2 cites this paper; the citation now needs correct authorship.

### Anderson & Mattingly 2025 — full text read

- **Citation**: Anderson K.E., Mattingly T.J. II (2025). Measuring
  Geographic Access to Pharmacies. *JAMA Network Open* 8(3), e250725.
  doi:10.1001/jamanetworkopen.2025.0725 (Invited Commentary on Mathis et al.)
- **Key claim**: Commentary discussing Mathis et al.'s "keystone pharmacy"
  framework. Notes that Mathis et al. extend desert measurement with
  drive-time-based indices, addressing limitations of binary distance.
- **Relevance**: Could be cited in §5.2 to support the centroid-threshold
  critique. The PDF user downloaded under filename "Geographic access to
  pharmacies in the United States.pdf" is actually this commentary, NOT the
  `dill2023` reference originally in the bib.

### 🟢 Sharareh et al. 2025 — full text read; PRIMARY MOBILITY PRECEDENT

- **Citation**: Sharareh N., Tang S., Bress A., Mathis W.S.,
  Berenbrok L.A., Hernandez I. (2025). Geographic access to community
  pharmacies based on walking, driving, and public transportation in the
  10 most populated U.S. areas. *Journal of the American Pharmacists
  Association* 65, 102479. doi:10.1016/j.japh.2025.102479
- **Key claim**: Pharmacy access measured solely by driving time
  overestimates effective access. Driving-only measures overestimate
  pharmacy access for ~702{,}708 individuals when walking is the binding
  mode and ~2{,}430{,}764 when public transit is the binding mode, across
  the ten largest U.S.\ metros.
- **Methodology**: Enhanced 2-Step Floating Catchment Area (E2SFCA) with
  Gaussian distance decay; ACS block-group household vehicle availability;
  20-minute travel time threshold (calibrated from 2022 NHTS); access
  computed by mode (driving / walking / public transit) and reported per
  10{,}000 people. Block-group-level analysis across 10 MSAs.
- **Relevance**: 🟢 **This is the most directly relevant precedent for
  the MWDR analysis in §4.6**. It is pharmacy-specific, recent (2025),
  uses ACS vehicle data, and arrives at the same core conclusion that
  driving-only desert classification systematically misrepresents access
  for carless populations. MWDR is a methodological cousin: same
  conceptual core (mode-aware accessibility); different mechanic (binary
  thresholds vs continuous Gaussian decay; aggregated single score vs
  by-mode reporting). Explicitly cited in §3.5 / §4.6 / §5.2 as the
  primary anchor.
- **Thesis implication**: Replaces the previous dill2023 citation as the
  pharmacy-domain anchor; MWDR is positioned as an extension of the
  Sharareh framework adapted for direct comparability with the Qato
  binary-threshold tradition.

### dill2023 — REMOVED FROM BIB

- The `dill2023` entry in the original bib (Dill M.J. & Gelmon S., JAPhA
  2023, 63(1):148-156, doi 10.1016/j.japh.2022.09.006) could not be
  verified by the user via search and is not present in the
  References/ folder. **Removed from references.bib on 2026-05-02.**
  Citations that previously pointed to `dill2023` have been re-attributed
  to `wittenauer2024` (national pharmacy desert + sociodemographic
  characterization) where the surrounding claim is adequately supported.

---

## NETS Database / Commercial Data Critique

### Barnatchez, Crane & Decker 2017 — full text read; CITATION ERROR FOUND

- **Citation**: Barnatchez K., Crane L.D., Decker R.A. (2017). An Assessment
  of the National Establishment Time Series (NETS) Database. Federal Reserve
  Board, Finance and Economics Discussion Series 2017-110.
  doi:10.17016/FEDS.2017.110
- **Key claim**: NETS coverage compared with CBP/NES/QCEW. Largest
  discrepancies are among small establishments where imputation is prevalent.
  After sample restrictions, NETS covers ~75% of US private sector employment.
- **Methodology**: National comparison study; documents imputation rates and
  recommends sample restrictions for static analysis.
- **🔴 IMPORTANT — thesis miscitation**: The thesis (02_literature.tex, also
  01_introduction.tex) attributes a "minority-owned underrepresentation"
  finding to Barnatchez 2017. **The Barnatchez paper does NOT make this
  claim**. Searching the full text returns zero matches for "minority",
  "race", "Hispanic", "Black", or "underrepresent". The minority-
  underrepresentation observation comes from the Washington State 2021 D&B
  evaluation (washington2021), which DOES note that "D&B only has a small
  percentage of minority- and woman-owned businesses identified on their
  file" (page 38). The thesis must re-attribute this claim to washington2021.

### Walls 2007 — full text read

- **Citation**: Walls D.W. (2007). National Establishment Time-Series
  Database: Data Overview. SSRN Working Paper 1022962.
  doi:10.2139/ssrn.1022962
- **Key claim**: Vendor overview of NETS construction from D&B DUNS
  Marketing Information; 32.2M total records, 16.2M active (2006). Annual
  updates; 17 years of historical data 1989–2006.
- **Relevance**: Cite as primary source for NETS construction details.

### Neumark, Zhang & Wall 2005/2011 — full text read (PPIC working paper)

- **Citation**: Neumark D., Zhang J., Wall B. (2005). Employment Dynamics
  and Business Relocation: New Evidence from the National Establishment
  Time Series. NBER Working Paper W11647.
  Published version: Neumark D., Zhang J., Wall B. (2011). *Research in
  Labor Economics* vol 32, pp 1–32.
- **Key claim**: NETS validates against state UI data; reliable for
  static employment analysis. Identifies six dynamic processes
  (births, deaths, expansion, contraction, in-migration, out-migration).
- **Relevance**: Already cited as `neumark2011`; supports NETS validation
  claims in §2.2.

### Washington State 2021 — full text read

- **Citation**: Washington State Department of Commerce / Workforce Training
  and Education Coordinating Board (2021). *Data Driven Insight: Evaluating
  the Dun and Bradstreet Toolkit*.
- **Key claim**: One-year pilot evaluation of D&B EconoVue/Market Insight
  toolkit. Notes (p.38) that "D&B only has a small percentage of minority-
  and woman-owned businesses identified on their file."
- **Relevance**: Should be the primary cite for the minority-underrepresentation
  claim, NOT Barnatchez.

---

## Foundational Retail Geography

### Chapple & Jacobus 2009 — partial read

- **Citation**: Chapple K., Jacobus R. (2009). Retail Trade as a Route to
  Neighborhood Revitalization. In *Urban and Regional Policy and Its
  Effects*, vol 2 (eds. Pindus, Wial, Wolman), pp. 19–68. (Bib lists
  pp 191–228, which may match a different edition; verify if needed.)
  Brookings Institution Press.
- **Relevance**: Cited as foundational retail-geography reference in §2.2.

### Meltzer & Schuetz 2012 — full text read

- **Citation**: Meltzer R., Schuetz J. (2012). Bodegas or Bagel Shops?
  Neighborhood Differences in Retail and Household Services. *Economic
  Development Quarterly* 26(1), 73–94. doi:10.1177/0891242411430328
- **Key claim**: Documents persistent retail/services differences across
  income-stratified Chicago neighborhoods using NETS data.
- **Relevance**: Cited as core NETS-application paper in §2.2.

---

## AI / LLM in Urban Geography

### Xu et al. 2025 — full text read; citation verified

- **Citation**: Xu L., Zhao S., Lin Q., Chen L., Luo Q., Wu S., Ye X.,
  Feng H., Du Z. (2025). Evaluating large language models on geospatial
  tasks: a multiple geospatial task benchmarking study. *International
  Journal of Digital Earth* 18(1), 2480268.
  doi:10.1080/17538947.2025.2480268
- **Key claim**: Benchmark of LLMs on multiple geospatial tasks; finds
  GPT-4 class achieves competitive accuracy on classification with
  structured prompts.
- **Relevance**: Cited as primary LLM-geography validation reference.

### Liu, Yigitcanlar et al. 2025 (replaces sciencedirect2025urban) — full text read

- **Citation**: Liu K., Yigitcanlar T., Mehmood R., Corchado J., Fu X. (2025).
  Large Language Models in Urban Planning: A Systematic Review and
  Conceptual Framework. *Journal of Urban Technology*, published online
  10 Nov 2025. doi:10.1080/10630732.2025.2556551
- **CORRECTION TO BIB**: Current `sciencedirect2025urban` entry has author
  `{ScienceDirect}` (a placeholder, not real). Replace with actual authors;
  rename key to `liu_yigitcanlar_2025`.
- **Key claim**: PRISMA-method systematic review of LLM applications in
  urban planning across five domains.
- **Relevance**: Already cited as the LLM-urban-planning review reference.

### Huang 2025 — full text read

- **Citation**: Huang X. (2025). Geospatial Artificial Intelligence (GeoAI)
  Is Widening the Digital Divide. *Annals of the American Association of
  Geographers*. doi:10.1080/24694452.2025.2527316
- **Key claim**: Conceptual essay arguing GeoAI risks deepening data
  sovereignty / computational / literacy inequities. Beyond access gaps
  to inequities in capability.
- **Relevance**: Cited in §2.3 (AI in urban geography) and supports the
  digital invisibility argument in §5.1.

### Li et al. 2025 — full text read

- **Citation**: Li H., Zhou A., Zheng X., Xu J., Zhang J. (2025). Restaurant
  survival prediction using machine learning: Do the variance and sources
  of customers' online reviews matter? *Tourism Management* 107, 105038.
  doi:10.1016/j.tourman.2024.105038
- **Key claim**: Online review variance is leading indicator of restaurant
  survival. Boston dataset of 2,838 restaurants.
- **Relevance**: Cited as Google Maps validation precedent in §2.3.

---

## Minnesota-Specific

### Pereira et al. 2024 — abstract only (.htm)

- **Citation**: Pereira C., Tran M., Liu Y., Isetts B. (2024). The Minnesota
  Pharmacy Landscape Is Drying Up: Pharmacy Desert Emergence and
  Implications. APHA Annual Meeting Abstract 551580.
- **Relevance**: Minnesota pharmacy closure trend baseline.

### MN Department of Health 2024 — no PDF

- **Citation**: Minnesota Department of Health (2024). Pharmacy Deserts in
  Minnesota 2009–2024.
- **Relevance**: 8% of MN residents live in pharmacy deserts.

---

## Summary of Required Bib / Thesis Corrections

### Bib corrections (must do)

1. **`plosone2025` → rename to `catalano2025`**: real authors Catalano,
   Woldesenbet, Pawlik; vol 20(8), pages e0330027, DOI .../journal.pone.0330027
2. **`sciencedirect2025urban` → rename to `liu_yigitcanlar_2025`**: real
   authors Liu, Yigitcanlar, Mehmood, Corchado, Fu (2025); DOI
   10.1080/10630732.2025.2556551
3. **`qato2014`**: vol 33(11) pp 1958–1965, NOT 33(8) pp 1359–1367
4. **Delete `federalreserve2017`**: duplicate of barnatchez2017 (and wrongly
   attributed to Minneapolis Fed)
5. **Add new entries**:
   - `verploeg2012` (USDA ERR-143)
   - `verploeg2009` (USDA AP-036)
   - `walker2010` (Health & Place)
   - `luo_wang_2003` (Env Plann B)
   - `apparicio2007` (IJHG)
   - `mcentee_2010` (Applied Geography)
   - `wang2012` (AAAG)
   - `paez2010` (Urban Studies)
   - `sharkey2009` (AJPM)
   - **`sharareh2025` (JAPhA) — PRIMARY pharmacy-domain mobility precedent**
6. **Remove `dill2023`**: Not verifiable; surrounding claims re-attributed
   to `wittenauer2024`.

### Thesis text corrections

1. **02_literature.tex Barnatchez paragraph**: Remove "Dun and Bradstreet
   exhibited documented underrepresentation of minority-owned enterprises"
   as a Barnatchez finding. Re-attribute to Washington 2021.
2. **§3.5 spatial methodology**: Add proper citations for mobility-weighted
   approach (Ver Ploeg, Walker, Luo & Wang, Apparicio, Páez). Flag MWDR
   formulation as a continuous extension diverging from USDA's discrete
   dual-indicator approach.
3. **§4.6 Mobility-Adjusted Desert Analysis**: Add foundation citations.
4. **All `\citet{plosone2025}` → `\citet{catalano2025}`**.
5. **All `\citet{sciencedirect2025urban}` → `\citet{liu_yigitcanlar_2025}`**.
