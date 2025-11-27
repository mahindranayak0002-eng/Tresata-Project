# Slide 1 — System Architecture (Auto Column Tagging)

- **Inputs**
  - Raw CSV files (unknown/missing headers)
  - Training lists: `countries.txt`, `legal.txt`, `phone.csv`, `dates.csv`, `company.csv`
- **Components**
  - **Predictor (predict.py)**: per-column scoring using regex, fuzzy country matching, legal-suffix detection → outputs one of {Phone, Company, Country, Date, Other}
  - **Parser (parser.py)**: For chosen Phone/Company column -> extract structured fields (Country, Number) or (Name, Legal)
  - **MCP Server (mcp_server.py)**: Exposes tools to a chat agent — list files, predict, parse, download
- **Dataflow**
  - User selects file -> Predictor (per-column) -> choose highest-scoring Phone/Company -> Parser -> output.csv
- **Design choices**
  - Lightweight heuristics for high precision on small training sets
  - Fuzzy matching to handle variations
  - Modular: components can be replaced by ML models later

# Slide 2 — Workflow & Model Design

- **Prediction heuristics**
  - Phone: regex + minimum digits
  - Date: common date patterns + month names
  - Country: exact or fuzzy match against countries list
  - Company: presence of legal suffix (from `legal.txt`) OR multi-word proper-noun-like patterns
  - Other: captured as fallback
- **Parsing**
  - Phone: strip non-digits, extract country code using map -> fallback heuristics
  - Company: longest-legal-suffix-first matching -> split name vs legal part
- **MCP Integration**
  - Simple REST endpoints to list files, run predictor, run parser
  - Enables connection to ChatGPT/Claude as a tool layer
- **Extensibility**
  - Replace heuristics with small classifier (e.g., XGBoost/BERT) trained on column-level features if more labeled data available
  - Extend country-code map and legal suffix list for better coverage
