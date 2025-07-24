# Adobe India Hackathon 2025 – PDF Document Intelligence System

## 🚀 Overview

This repository contains a competition-ready solution for the Adobe India Hackathon 2025 – "Connecting the Dots". The project transforms static PDF documents into intelligent, persona-driven interactive experiences as required in Challenge 1A (PDF Outline Extraction) and Challenge 1B (Persona-driven Document Analysis). The solution is dockerized, schema-compliant, and optimized for sub-3 second processing, supporting multi-collection analysis and five Adobe-defined personas. It leverages advanced heading detection and a semantic ranking engine for intelligent section extraction and ranking.

* **Challenge 1A:** Extracts detailed outlines (50+ headings) from PDF files using advanced heading detection.
* **Challenge 1B:** Performs persona-driven analysis, ranking and extracting the most relevant document sections as per the job-to-be-done and persona role.
* **Performance:** 87.6MB model size (well under 1GB), <3s processing per collection (well under 5-minute limit).
* **Compliance:** 100% JSON schema validation, Docker linux/amd64, multi-collection folder structure, and health checks.

## 📋 Quick Start

**Prerequisites:** Docker, Git

```bash
git clone https://github.com/abhiniveshmitra/adobe-hackathon-pipeline.git
cd adobe-hackathon-pipeline
docker build --platform=linux/amd64 -t adobe-hackathon .
```

### Run Round 1A (Outline Extraction)

```bash
docker run --rm --platform=linux/amd64 \
  -v "${PWD}/app/input:/app/input" \
  -v "${PWD}/app/output:/app/output" \
  -e ROUND=1A \
  adobe-hackathon
```

### Setup for Round 1B (Persona-driven Collections)

```bash
docker run --rm --platform=linux/amd64 \
  -v "${PWD}/app/output:/app/output" \
  -v "${PWD}/collections:/app/collections" \
  adobe-hackathon python scripts/setup_collections.py
```

### Run Round 1B (Persona-driven Analysis)

```bash
docker run --rm --platform=linux/amd64 \
  -v "${PWD}/collections:/app/collections" \
  -e ROUND=1B \
  adobe-hackathon
```

## ✅ Submission Compliance

* **Challenge 1A & 1B:** All requirements met
* **Model size:** 87.6 MB (< 1 GB limit)
* **Processing time:** 2–3 s per collection (< 5 min)
* **JSON schema:** 100% compliant outputs
* **Platform:** linux/amd64 Docker
* **Multi-collection:** Supported as per Adobe folder specification

## 📁 Folder Structure

```
adobe-hackathon-pipeline/
├── app/
├── collections/
├── scripts/
├── Dockerfile
├── health_check.py
├── README.md
```

## ⚡ Demo Example

```bash
docker run --rm -v "${PWD}/collections:/app/collections" -e ROUND=1B adobe-hackathon
cat collections/Collection\ 1/challenge1b_output.json | head -20
```

## 🧪 Validation

```bash
docker run --rm adobe-hackathon python health_check.py
```
