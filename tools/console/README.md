# Cold Entropy Console (Tools)

This directory contains the engineering tools for `data-records.net`.

## Structure

- **backend/**: Python 3.10 logic for hashing, schema validation, and R2 uploading.
- **frontend/**: React UI (planned) for drag-and-drop management.

## Setup

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. Run Engine Check:
   ```bash
   python backend/engine_v1.py
   ```

## Core Philosophy

- **DB is Editor**: The database holds the working state.
- **FS is Mirror**: The file system holds consumer-facing truth.
- **Strict Logic**: No data enters `data-records` without passing `RecordSchema` validation.
