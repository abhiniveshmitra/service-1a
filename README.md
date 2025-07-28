# Adobe India Hackathon 2025 – Service 1A: PDF Outline Extraction

## 🚀 OVERVIEW

Official submission for Service 1A of Adobe India Hackathon 2025. This system extracts hierarchical outlines from PDF documents, identifying titles and H1–H6 headings, and outputs a schema-compliant JSON.

---

## 📄 WHAT IT DOES

* Extracts structured outlines from static PDFs
* Detects heading levels (H1-H6) and their page numbers
* Transforms results into JSON format for downstream use
* Processes files under 10s with CPU-only execution
* Fully offline and self-contained

---

## 🔹 KEY FEATURES

* **Multi-Factor Heading Detection**: Font size ratios, formatting flags, layout, regex
* **Hierarchy Recognition**: Auto H1-H6 assignment via font and numbering
* **Fast Execution**: 2–5s typical per PDF (50-page max)
* **Schema Compliance**: 100% JSON validation
* **Error Resilience**: Skips failing files, continues batch
* **Dockerized**: linux/amd64 container-ready

---

## 📁 DIRECTORY STRUCTURE

```
service-1a/
├── app/
│   ├── config/            # Service config
│   ├── input/             # Input PDFs
│   ├── output/            # Output JSONs
│   ├── services/round1a/  # Core logic
│   └── utils/             # Validation/log helpers
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔧 INPUT REQUIREMENTS

* Place `.pdf` files in `/app/input/`
* ≤ 50 pages per PDF
* Valid text-based PDFs
* Naming: Any `.pdf` extension

---

## 🔄 OUTPUT FORMAT (filename.json)

```json
{
  "title": "Document Title Extracted from PDF",
  "outline": [
    {"level": "H1", "text": "Chapter 1: Introduction", "page": 1},
    {"level": "H2", "text": "1.1 Background and Context", "page": 2},
    {"level": "H3", "text": "1.1.1 Problem Statement", "page": 3}
  ]
}
```

* `title`: First-page extracted title
* `outline`: Hierarchical heading structure
* `page`: 1-based indexing

---

## 📃 QUICK START

### Prerequisites

* Docker Desktop
* Git
* 512MB+ free disk

### Setup & Build

```bash
git clone https://github.com/abhiniveshmitra/service-1a.git
cd service-1a
docker build --platform=linux/amd64 -t adobe-service-1a .
```

### Run Service

```bash
docker run --rm \
  -v "$(pwd)/app/input:/app/input:ro" \
  -v "$(pwd)/app/output:/app/output" \
  --network none \
  adobe-service-1a
```

### Docker Compose

```bash
docker-compose up
```

---

## 📊 PROCESSING PIPELINE

1. **PDF Discovery**: Reads `/app/input/`
2. **Text Extraction**: Pulls font + layout metadata
3. **Title Detection**: Identifies top heading on first page
4. **Heading Scoring**:

   * Font size, bold, numbered sections, etc.
5. **Hierarchy Assignment**: Labels as H1-H6
6. **JSON Serialization**: Outputs to `/app/output/`
7. **Schema Validation**: Confirms format compliance

---

## 🧠 ALGORITHM DETAILS

**Heading Scoring Breakdown:**

* Font Size Ratio: 35%
* Formatting Flags: 25%
* Pattern Matching: 25%
* Vocabulary Detection: 10%
* Positional Hints: 5%

**Level Assignment Heuristics:**

* H1: ≥ 1.6x base size
* H2: ≥ 1.4x
* H3: ≥ 1.2x
* Numbering: `1.` → H1, `1.1` → H2, etc.

---

## 🌟 COMPLIANCE WITH HACKATHON RULES

| Constraint                 | Met? |
| -------------------------- | ---- |
| ≤ 10s per 50-page PDF      | ✅    |
| Max 50 pages per file      | ✅    |
| ≤ 512MB memory use         | ✅    |
| CPU-only, no GPU           | ✅    |
| --network none compliant   | ✅    |
| Output schema validation   | ✅    |
| Multi-PDF batch processing | ✅    |

---

## 📊 PERFORMANCE METRICS

* Speed: 2–5s/PDF
* RAM: <512MB
* Compliance: 100% validation
* Robustness: Fault-tolerant

---

## ✅ SUBMISSION CHECKLIST

* [x] Docker build & run on AMD64
* [x] ≤10s/50pg PDF
* [x] No network/GPU
* [x] Schema-compliant JSON
* [x] Batch & error handling
* [x] Health check included

---

## 🔧 TECH SPECS

* Language: Python 3.10
* Parser: PyMuPDF
* Output: JSON (strict schema)
* Container: Docker
* RAM: ≤512MB
* Size: <200MB footprint

---

## 🔗 RESOURCES

* Repo: [https://github.com/abhiniveshmitra/service-1a](https://github.com/abhiniveshmitra/service-1a)
* Support: GitHub Issues tab
* Docs: Inline code comments + test samples

---

## 🚀 FINAL REMARK

This project delivers a fast, accurate, and schema-compliant Service 1A implementation, tailored for Adobe’s hackathon challenge and extensible for downstream analysis.
