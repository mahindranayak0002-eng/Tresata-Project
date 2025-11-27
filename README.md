---

# README.md
#TRESATA PROJECT
## IntelliTag: Automated Semantic Column Classification and Parsing

### 1. Overview

IntelliTag is a modular system designed to automatically classify the semantic type of CSV columns using only their values, without relying on column headers. After classification, the system performs parsing and normalization for Phone Number and Company Name fields.
It also includes an MCP (Model Context Protocol) layer to expose prediction and parsing operations as tools for LLM-based agents such as ChatGPT and Claude.

This project is developed as part of the IIT Madras Hackathon.

---

### 2. Features

#### 2.1 Semantic Classification

The classifier assigns one of the following semantic types to a column:

* Phone Number
* Company Name
* Country
* Date
* Other

Classification is based on:

* Regular expressions
* Digit and pattern analysis
* Fuzzy matching
* Legal suffix identification
* Country name mapping
* Date format recognition

#### 2.2 Parsing and Normalization

If the classifier identifies a column as Phone Number or Company Name, IntelliTag parses it further.

Phone Number parsing:

* Extracts country (based on country code)
* Extracts the national number

Company Name parsing:

* Extracts company name
* Extracts legal suffix (using legal.txt)

If multiple such columns exist, the system selects the one with the highest classification probability.

#### 2.3 MCP Integration Layer

A minimal API server is provided to:

* List available files
* Predict semantic type for a given column
* Parse a selected CSV file
* Download processed output

This enables seamless integration with LLM agents.

---

### 3. Directory Structure

```
.
├── predict.py
├── parser.py
├── utils.py
├── mcp_server.py
├── requirements.txt
├── data/
│   ├── countries.txt
│   ├── legal.txt
│   ├── company.csv
│   ├── dates.csv
│   ├── phone.csv
├── output.csv
├── slides/
│   └── deck.pptx
└── README.md
```

---

### 4. Installation

#### 4.1 Clone the repository

```
git clone <repository-url>
cd <project-folder>
```

#### 4.2 Install dependencies

```
pip install -r requirements.txt
```

---

### 5. Usage

#### 5.1 Predict Semantic Type

Use `predict.py` to classify a specific column in a CSV file.

```
python3 predict.py --input data/test.csv --column ColumnName
```

The output will be one of:
`phoneNumber`, `companyName`, `country`, `date`, `other`.

#### 5.2 Parse a File

Use `parser.py` to automatically detect and parse Phone Number and Company Name columns.

```
python3 parser.py --input data/test.csv --output output.csv
```

The generated `output.csv` contains parsed columns:

* PhoneNumber, Country, Number
* CompanyName, Name, Legal

If no qualifying columns are detected, the script outputs the original data.

---

### 6. MCP Server

#### 6.1 Start the server

```
python3 mcp_server.py
```

#### 6.2 API Endpoints

List files:

```
GET /files
```

Predict a column:

```
GET /predict?file=test.csv&column=ColumnName
```

Parse and produce output:

```
POST /parse
{
  "file": "test.csv",
  "output": "output.csv"
}
```

Download output:

```
GET /download/output.csv
```

---

### 7. Classification Approach

The semantic type detection uses a scoring system based on:

* Regex-based phone and date identification
* Fuzzy string matching with country names
* Pattern recognition for company structures
* Legal suffix detection using a supplied list
* Digit density heuristics

The highest-scoring type is selected as the predicted semantic classification.

---

### 8. Parsing Approach

Phone numbers:

* Remove formatting characters
* Identify and map country code
* Extract remaining digits as national number

Company names:

* Identify longest matching legal suffix
* Separate the legal entity type
* Return normalized company name and legal suffix

---

### 9. Extensibility

The system is modular and can be extended by:

* Adding additional semantic classes
* Integrating a machine learning model
* Expanding country code mappings
* Enhancing legal suffix recognition
* Integrating databases or external APIs

---

### 10. Contributors

Developed for the IIT Madras Hackathon challenge.
Replace this section with contributor names as needed.

---

### 11. License

Add your desired license here (MIT, Apache 2.0, etc.).

---
