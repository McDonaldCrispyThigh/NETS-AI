# Synthetic Urban Intelligence  
## Validating Commercial Geographies via AI Agents

**Honors Thesis Project**

**Principal Investigator:**  
Congyuan (Student), Boulder, CO

**Advisors:**  
- Prof. Jessica Finlay (Supervisor)  
- Prof. Michael Esposito (University of Minnesota)  
- Prof. Stephen Becker (Applied Mathematics)

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

