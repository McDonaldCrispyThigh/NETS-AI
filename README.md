# Synthetic Urban Intelligence  
## Validating Commercial Geographies via AI Agents

**Honors Thesis Project**

**Principal Investigator:**  
Congyuan (Student), Boulder, CO

**Advisors:**  
- Prof. Jessica Finlay (Supervisor)  
- Prof. Michael Esposito (University of Minnesota)
- Yue Sun (Postdoc in CU Boulder)

---

## 1. Project Goal

### Academic Goal

This project investigates the structural and methodological problems of the  
**National Establishment Time-Series (NETS)** database and evaluates whether  
AI-generated business data can serve as a viable alternative or supplement.

### Technical Goal

To examine whether AI tools (e.g., GPT, Gemini) can automatically generate  
business establishment data that **structurally resembles NETS**, while being  
more transparent and reproducible.

### Tech Stack

- **Language:** Python  
- **AI Tools:** LangChain, OpenAI API  
- **Mapping & Spatial Tools:** Spatial SQL, PostGIS, GeoPandas  

---

## 2. Methodology: From "Chatting" to "Coding"

### The Problem

Using web-based tools such as ChatGPT or Gemini directly is **not suitable for  
scientific research**, primarily due to:

- Lack of reproducibility  
- Non-deterministic outputs  
- Opaque reasoning processes  

### Our Solution

Instead of using AI via web interfaces, we design and implement a  
**reproducible AI Agent through code**.

This agent conducts data generation tasks automatically and consistently.

---

### How the Agent Works

#### 1. Read Files (Context)

The agent reads all files in the `docs/` or `context/` directory to understand  
project goals, constraints, and data schemas.

#### 2. Use Tools

The agent can invoke external tools, including:

- Google Search  
- Google Maps API  
- Yelp API  

to retrieve real-world business information.

#### 3. Ask Questions (Prompt)

The agent follows structured instructions defined in:

- `context/prompt_guide.md`

to ensure consistent reasoning behavior.

#### 4. Save Data

Generated outputs are saved as:

- CSV files (Excel-compatible)  
- Structured according to NETS-like schemas  

---

## 3. Repository Structure — The "Brain" of the Agent

/
├── README.md
├── code/ # Main Python logic
│ ├── main.py # Entry point
│ └── agent_workflow.py # Agent reasoning workflow
├── skills/ # External tools (APIs)
│ ├── google_maps.py # Google Maps integration
│ └── yelp_api.py # Yelp API integration
├── context/ # Agent memory & rules
│ ├── prompt_guide.md # Prompt engineering guide
│ └── nets_schema.json # NETS-style data schema
└── docs/ # Project documents


### Folder Descriptions

#### `README.md`

High-level introduction and documentation of the project.

#### `code/` (The Brain)

Core Python scripts controlling the AI agent using LangChain.

#### `skills/` (The Tools)

Wrappers for external APIs such as Google Maps and Yelp.

#### `context/` (The Memory)

Background knowledge and constraints for the agent, including:

- NETS database structure  
- NAICS classifications  
- Prompt rules  

---

## 4. Project Plan (Sprints)

### ✅ Sprint 1 — Build the Agent

**Status:** In progress  
**Goal:**  
- Establish a basic agent capable of communicating with the OpenAI API.

### ✅ Sprint 2 — Fix Prompts

**Goal:**  
- Improve prompt clarity  
- Reduce unnecessary follow-up questions  
- Stabilize agent behavior  

### ✅ Sprint 3 — Generate Data (Pilot Study)

**Goal:**  
- Generate business establishment data for one city  
  (e.g., Minneapolis or Boulder)

**Focus Questions:**  
- Can historical data (2005 / 2015) be recovered?  
- Are business types and classifications accurate?  

### ✅ Sprint 4 — Compare with NETS

**Goal:**  
- Evaluate whether AI-generated data can replace or complement NETS.

**Tasks:**  
- Compare AI-generated datasets with NETS  
- Visualize spatial differences using ArcGIS Pro  

---

## 5. Abstract Draft

### Objective

To expose methodological weaknesses in NETS-based urban research and evaluate  
AI agents as a reproducible alternative for commercial geography analysis.

### Methods

A reproducible AI agent is developed and tested against NETS-based studies,  
with a focus on data structure, spatial accuracy, and historical consistency.

### Key Findings

AI-generated data is imperfect—particularly for historical reconstruction.  
However, these errors reveal similar limitations embedded within NETS itself,  
highlighting broader issues of data opacity and uncertainty.

### Keywords

NETS • AI Agents • Synthetic Data • Reproducibility • Urban Geography
