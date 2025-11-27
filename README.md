# Tresata-Project
# IIT Madras Hack — Auto Column Tagging & Parser

## Overview
This repo implements:
- `predict.py` : Predict semantic type of a CSV column (phone, company, country, date, other)
- `parser.py`  : If phone/company columns are present, parse them into normalized fields and write `output.csv`
- `mcp_server.py` : Minimal MCP connector (Flask) to list files and run predict/parse endpoints
- `utils.py` : Shared helpers

Training/aux files are expected in `./data/` (or `/mnt/data` if present):
- `countries.txt`
- `legal.txt`
- `company.csv`
- `phone.csv`
- `dates.csv`

## Requirements
- Python 3.8+
- pip packages:
