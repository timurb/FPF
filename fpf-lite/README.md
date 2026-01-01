# FPF Specification Compressor

A utility for the semantic compression of the **First Principles Framework (FPF)** specification.

It is designed to prepare large Markdown files (~1M tokens) for loading into the context window of LLMs (Google Gemini, GPT-4, Claude) while maintaining the document's normative integrity.

## 🎯 The Problem
The FPF specification contains not only rules but also extensive introductory essays, historical context (SoTA), rationales, and problem frames.
*   **Size:** The full file occupies ~1,000,000 tokens.
*   **Consequences:** This causes `resource_exhausted` errors, increases query costs, and paradoxically **reduces answer quality** due to the "Lost in the Middle" effect (attention dilution).

## 💡 The Solution
The script performs **semantic compression**: it removes informational (`Informative`) sections while retaining normative (`Normative`) ones.

**What is removed:**
1.  **Preface / Introduction:** Introductory essays, table of contents.
2.  **SoTA-Echoing:** References to scientific papers and industry comparisons (State-of-the-Art).
3.  **(Optional) Rationale / Forces / Problem:** Philosophical justification of decisions.

**What is preserved (The Core):**
1.  **Definitions:** Definitions of types and terms.
2.  **Solution:** The architectural solution itself.
3.  **Conformance Checklist:** Validation criteria.
4.  **Archetypal Grounding:** Examples (critical for Few-Shot Learning).

---

## 🧠 Impact on Model Reasoning Power

Compressing the file using this method not only saves tokens but also **changes the model's behavior**.

### ✅ Positive Impact (Instruction Density)
Removing "fluff" increases **instruction density**.
*   In the full file, rules are diluted with historical details. The model's attention mechanism gets diluted.
*   In the compressed file, the percentage of tokens containing imperatives (`MUST`, `SHALL`) is significantly higher. The model follows strict rules better and hallucinates philosophical justifications less often.

### ⚠️ Risks and Nuances
1.  **Loss of the "Spirit of the Law":** Sections like `Rationale` and `Forces` explain *why* a rule exists. Without them, the model becomes a "bureaucrat"—it follows the letter of the law brilliantly but may struggle to resolve complex edge cases.
2.  **Risk of Losing Examples:** The script is configured to **preserve** `Archetypal Grounding` sections. Removing examples would catastrophically reduce performance (LLMs understand abstract rules poorly without examples). This script protects these sections.

**Verdict:** For code generation, validation, and strict formatting tasks, the compressed version works **better and more accurately** than the full version.

---

## 🚀 Usage

### Requirements
*   Python 3.x
*   No external libraries required (uses standard `re`, `os`).

### Execution
1.  Clone the repository
2.  Run the command:

```bash
python fpf-lite/fpf_compressor.py
```

3.  The script will create 2 files: `FPF-Spec-Lite.md` (Removes only Preface and SoTA) and `FPF-Spec-Aggressive.md` (Also removes Problem, Forces, Rationale. Leaves only dry rules).


## 🛠 Script Features

1.  **Unicode Normalization:** The script handles specific characters used in FPF, such as the non-breaking hyphen (`\u2011`, used in "SoTA‑Echoing") and various dashes. Standard string searches miss these.
2.  **Structural Parsing:** The script understands Markdown header levels (`#`, `##`, `###`). If it starts cutting a `SoTA` section, it stops exactly where the next section of the same level begins, ensuring nothing extra is deleted.
3.  **Case-Insensitive:** Catches headers like `SoTA`, `SOTA`, `state-of-the-art` regardless of case.
```