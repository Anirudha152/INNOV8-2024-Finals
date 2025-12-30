# INNOV8 2.0 Finals Submission - Resume and Recommendation Letter Analysis

This repository contains the code and data used for the INNOV8-2024 finals submission. The project contains scripts for processing resumes and recommendation letters, extracting structured timeline entries, computing per-resume numeric metrics (a risk/vacancy factor and flags), analyzing a recommender graph, and a utility for computing skill-to-experience relevance using sentence embeddings.

## Repository layout (top-level)

- `Final_Resumes/` - PDF resumes named `Resume_of_ID_<n>.pdf` used by resume parsing scripts.
- `Final_Recommendation_Letters/` - recommendation letters organized by ID subfolders.
- `Final_Persons_And_Recommenders.csv` - CSV mapping person `ID` to a list of recommender IDs (used by graph analysis).
- `outputs/` - output text files produced by resume parsing scripts (e.g., `outputs/output<index>.txt`).
- `final.txt`, `final.csv` - aggregated numeric outputs produced by timeline analysis scripts.
- `anav.py` - skill-to-experience relevance using sentence-transformers.
- `gemini.py`, `gemini2.py` - scripts that parse resume PDFs via Google Generative AI (Gemini) into a strict machine-readable format and write to `outputs/`.
- `nnnewhello.py` - parses the `## Timeline:` section from `outputs/` files and computes per-resume metrics written to `final.txt`.
- `vagueness.py` - checks recommendation letters for vague/exaggerated phrases using a Groq API client.
- `poewrfweef.py` - networkx-based analysis of recommender graph in `Final_Persons_And_Recommenders.csv`.
- `jjj.py` - utility to convert `final.txt` into `final.csv`.
- `hi.py` - small example demonstrating a local GPT4All model.
- `requirements.txt` - minimal list (expand before running; see Observed dependencies).


## High-level pipeline implemented by the code

1. Parse resume PDFs into a strict structured text format using `gemini.py` / `gemini2.py`. The language-model prompt enforces headings called `## Education:`, `## Experience:`, `## Skills:`, `## Sector:`, `## Timeline:` with strict formatting constraints.
2. Each generated `outputs/output<index>.txt` file is expected to contain a `## Timeline:` block where each line follows the format:
   - `- TYPE :: START-TIME -- END-TIME :: EVENT :: POSITION` (TYPE is one of JOB/INT/EVE/MEM/EDU/AWD/UKN; dates are MM-YYYY or placeholders like `00-0000` or `CURRENT`).
3. `nnnewhello.py` reads `outputs/`, parses the timeline lines, and computes numeric metrics (a combined `factor`, a `vacancy_factor`, and two binary flags `flag` and `bigflag`) per resume; it writes `final.txt` containing lines: `<index> <factor> <vacancy_factor> <flag> <bigflag>`.
4. `jjj.py` can convert `final.txt` into `final.csv` with a header `Index,RiskFactor,VacancyFactor,Flag,BigFlag`.
5. `poewrfweef.py` reads `Final_Persons_And_Recommenders.csv`, constructs a directed graph (edges from person -> recommender), enumerates cycles (small sizes), computes per-person cycle statistics, and can draw the graph with `matplotlib`.
6. `vagueness.py` inspects recommendation letters and uses a Groq chat model to output identified vague/exaggerated short phrases in a strict output format.
7. `anav.py` is a separate pipeline that reads a plain-text formatted input (expects `## Experience:` and `## Skills:` sections), preprocesses text to remove stopwords, and computes cosine-similarity relevance matrix between skills and experiences using SentenceTransformers embeddings.


## Important per-script notes (inputs, outputs, behavior)

- `gemini.py` / `gemini2.py`:
  - Inputs: PDFs under `Final_Resumes/Resume_of_ID_<index>.pdf`.
  - Outputs: `outputs/output<index>.txt` files. The prompt strictly enforces a machine-readable format that downstream code expects.
  - Runtime notes: these scripts use `google.generativeai` (Gemini) and `fitz` (PyMuPDF) for PDF text extraction. They require a Gemini API key in the environment (see Environment Variables section below).
  - `gemini.py` reads `GEMINI_API_KEY` from the environment via `dotenv`.
  - `gemini2.py` originally contained an inline API key; it has been updated to use an environment-variable placeholder (see code comments).

- `nnnewhello.py`:
  - Inputs: All `outputs/output<index>.txt` files in `outputs/`.
  - Outputs: `final.txt` with lines: `<index> <factor> <vacancy_factor> <flag> <bigflag>`; the script also prints summaries (counts of flags, max dates, etc.).
  - Notes: This script expects the timeline lines to match the prompt-specified format exactly. It contains logic to handle `CURRENT` and `00-0000` placeholder dates, and it aggregates data by year to compute factors.

- `jjj.py`:
  - Small utility to convert `final.txt` -> `final.csv`. It writes a header and then splits whitespace entries; it assumes the `final.txt` format used by `nnnewhello.py`.

- `anav.py`:
  - Inputs: A plaintext file containing `## Experience:` and `## Skills:` sections (the script has a hardcoded `file_path` that should be edited before use).
  - Behavior: It removes English stopwords, builds embeddings via SentenceTransformers (`mixedbread-ai/mxbai-embed-large-v1`), computes cosine similarities, prints a per-skill relevance matrix, and reports skills with RMS above a threshold.

- `vagueness.py`:
  - Inputs: a folder of `.txt` files (the script contains an example absolute path in the file; update to point to your recommendation letters folder if necessary). It extracts lines from text and constructs a prompt for the Groq model.
  - Outputs: writes `_vague.txt` files describing flagged phrases in a strict format. The script previously contained an inline Groq API key; it has been updated to read a `GROQ_API_KEY` environment variable (or fallback placeholder) per the user's request.

- `poewrfweef.py`:
  - Input: `Final_Persons_And_Recommenders.csv` (CSV with columns `ID` and `Recommenders ID` where the latter is a bracketed list like "[218, 391]").
  - Behavior: constructs a directed graph, recursively finds cycles of limited length, computes basic per-person cycle stats, and draws the graph using matplotlib.


## Observed dependencies

The repository's `requirements.txt` lists only a subset of imports; additional packages used in source files include:

- python-dotenv
- sentence_transformers
- numpy
- scikit-learn
- google-generativeai (Gemini client)
- PyMuPDF (imported as `fitz`)
- groq (Groq client)
- networkx
- matplotlib
- gpt4all (optional, for `hi.py` example)

Before running any script install the packages used by the parts you want to run.


## Environment variables and API keys

The code expects the following environment variables (the repository previously had inline keys; they have been replaced with placeholders in the code and you should set them in your environment):

- `GEMINI_API_KEY` - used by `gemini.py` and `gemini2.py` to call Google Generative AI (Gemini).
- `GROQ_API_KEY` - used by `vagueness.py` to call Groq's API.

Security note: the repository previously contained embedded keys in source files. Those occurrences have been replaced with calls that read from environment variables or fallback placeholders; you should store real keys in a `.env` file (not checked into version control) or export them in your shell.


## Quick start — full run instructions

1) Create and activate a virtual environment (macOS / Linux):

```bash
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies (start with the provided file, then add the rest):

```bash
pip install -r requirements.txt
# Example additional installs you will likely need:
pip install python-dotenv sentence_transformers numpy scikit-learn google-generativeai PyMuPDF groq networkx matplotlib gpt4all
```

3) Prepare environment variables. Create a `.env` file in the repository root with the following contents (replace placeholders with real keys):

```text
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
```

Alternatively export them in your shell before running scripts:

```bash
export GEMINI_API_KEY="<YOUR_GEMINI_API_KEY>"
export GROQ_API_KEY="<YOUR_GROQ_API_KEY>"
```

4) Run the resume parsing pipeline (example):

- Generate `outputs/` by calling the Gemini-based script (this requires a valid `GEMINI_API_KEY` and network access):

```bash
python gemini.py
# or
python gemini2.py
```

- After `outputs/` is populated, parse timelines and compute metrics:

```bash
python nnnewhello.py
```

- Convert the produced `final.txt` into `final.csv` (if you need a CSV):

```bash
python jjj.py
```

5) Run additional analyses:

- Recommender graph cycles:

```bash
python poewrfweef.py
```

- Skill-experience relevance (edit `anav.py` to point `file_path` at a valid input file first):

```bash
python anav.py
```

- Vagueness detection on recommendation letters (ensure `GROQ_API_KEY` and input/output folders configured inside `vagueness.py`):

```bash
python vagueness.py
```

## Disclaimer

This code was developed as part of a hackathon submission for INNOV8 2.0 held at IIT Delhi. It is intended for educational purposes and was completed in September 2024, it is no longer being actively updated or maintained, please reach out to me over email or linkedin for any queries. Please cite appropriately if used in research or projects. Please refer to the included report for more details.