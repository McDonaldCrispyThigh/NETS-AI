# Prompt Engineering Guide — NETS-AI

## Overview

This guide defines how the AI classification prompt is structured in
`code/agent_workflow.py`. Following these rules ensures reproducible,
consistent NAICS classification across all data-collection runs.

---

## 1. Prompt Architecture

Each business record is classified by a two-message exchange sent to `gpt-4o-mini`.

### System Message (Role: Researcher)

```
You are a data researcher. Today is {date}.
TASK: Assign the correct NAICS code for '{business_name}'.
Target category: {search_term} (NAICS {target_naics}).
Definition: {definition}

LOGIC:
1. Hours: Opens 6-8 AM → Coffee/Bakery. Opens 4 PM → Bar.
2. Attributes: Breakfast → Coffee. Dinner+Beer+No Breakfast → Bar.
3. Reviews confirm the vibe.
```

**Why a system message?**  
Separating the role definition from the data keeps the reasoning framework
stable regardless of the business being evaluated.

### User Message (Data payload)

```
Name: {name}
FACTS: Hours: {operating_hours} | Attrs: {attributes} | Price: {price_level}
REVIEWS:
{review_snippets}

Return JSON only:
{"Calculated_NAICS":"6-digit","Employees":null,"Year_Established":null,
 "Status":"Active/Inactive","Confidence":"High/Low","Reasoning":"brief"}
```

---

## 2. NAICS Classification Rules (per category)

| Category  | NAICS  | Key Decision Signal |
|-----------|--------|---------------------|
| Library   | 519120 | "Checkout", "Librarian", non-commercial |
| Park      | 712190 | "Trail", "Playground", outdoor |
| Coffee    | 722515 | Opens 6-8 AM, serves breakfast |
| Gym       | 713940 | "Weights", "Membership", "Classes" |
| Grocery   | 445110 | Fresh produce + meats, not gas station |
| Civic Org | 813410 | Non-profit, "Community Events" |
| Religion  | 813110 | "Worship", "Prayer", "Service" |

**Disambiguation rules:**
- Coffee vs Bar: if a place opens before 10 AM, classify as Coffee even if it serves beer.
- Park vs Residential: "Mobile Home Park" → not 712190.
- Grocery vs Convenience: if attached to a gas station → not 445110.

---

## 3. Model Settings

| Parameter   | Value      | Reason |
|-------------|------------|--------|
| model       | gpt-4o-mini | Cost-efficient for structured classification |
| temperature | 0.0         | Deterministic output for reproducibility |
| response    | JSON        | Parsed directly into CSV row |

**Reproducibility note:**  
`temperature=0.0` ensures the same input always produces the same output,
satisfying the scientific reproducibility requirement of the thesis.

---

## 4. Output Schema

The model must return a JSON object with these exact keys:

| Key               | Type    | Example       |
|-------------------|---------|---------------|
| Calculated_NAICS  | string  | "722515"      |
| Employees         | int/null| 12            |
| Year_Established  | int/null| 2018          |
| Status            | string  | "Active"      |
| Confidence        | string  | "High"        |
| Reasoning         | string  | "Opens 7 AM…" |

---

## 5. Handling Missing Data

- **No reviews:** Include `"NO REVIEWS. Judge based on Name, Hours, and Attributes only."` in the user message.
- **No hours:** Pass `"Unknown"` — model will rely on attributes and name.
- **No attributes:** Pass `"None"` — model will rely on hours and reviews.

---

## 6. Known Limitations

1. **Year_Established** is estimated by the model and should be treated as approximate.  
   Cross-reference with official business registry when precision is required.
2. **Employees** is an estimate based on business type and price level; not sourced from payroll data.
3. Reviews fetched via Google Places API are limited to 5 per place; sample may not be representative.
