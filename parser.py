#!/usr/bin/env python3
# parser.py
import argparse
import os
import csv
import sys
from utils import (
    load_list_file, normalize_text, looks_like_phone, parse_phone_number,
    split_company_name, best_country_match, fraction_matching
)

def read_csv_rows(path):
    import pandas as pd
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        return df
    except Exception:
        # fallback to csv module -> returns list of dicts
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # build a dict-of-lists style for easier writing
        return rows

def detect_best_columns(path, countries, legal):
    """
    Returns dict:
    {
      'phone': (colname, score),
      'company': (colname, score)
    }
    """
    import pandas as pd
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        columns = list(df.columns)
        data = {c: df[c].astype(str).tolist() for c in columns}
    except Exception:
        # fallback
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            data = {c: [] for c in columns}
            for row in reader:
                for c in columns:
                    data[c].append(row.get(c, ''))
    # score each column
    phone_scores = {}
    company_scores = {}
    for c, vals in data.items():
        # simple heuristics
        phone_frac = fraction_matching(vals, looks_like_phone)
        # company: presence of legal suffix or multi-word text
        def company_like(v):
            if not v:
                return False
            v = normalize_text(v)
            name, legal_suf = split_company_name(v, legal)
            if legal_suf and legal_suf.strip() != '':
                return True
            if len(v.split()) >= 2 and any(ch.isalpha() for ch in v) and not best_country_match(v, countries):
                return True
            return False
        comp_frac = fraction_matching(vals, company_like)
        phone_scores[c] = phone_frac
        company_scores[c] = comp_frac
    # pick best (highest score) - may be zero
    best_phone_col = max(phone_scores.items(), key=lambda x: x[1]) if phone_scores else (None, 0.0)
    best_company_col = max(company_scores.items(), key=lambda x: x[1]) if company_scores else (None, 0.0)
    return {'phone': best_phone_col, 'company': best_company_col, 'all_data': data}

def write_output_csv(out_rows, out_path, headers):
    # out_rows is list of dicts (same keys as headers)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)

def main():
    parser = argparse.ArgumentParser(description="Parse phone/company columns in a CSV and produce output.csv")
    parser.add_argument('--input', required=True, help='Path to CSV file')
    parser.add_argument('--countries', default='data/countries.txt', help='Countries file')
    parser.add_argument('--legal', default='data/legal.txt', help='Legal suffixes file')
    parser.add_argument('--output', default='output.csv', help='Output CSV file')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    countries = load_list_file(args.countries)
    legal = load_list_file(args.legal)

    detection = detect_best_columns(args.input, countries, legal)
    best_phone_col, phone_score = detection['phone']
    best_company_col, company_score = detection['company']
    data = detection['all_data']

    # Decide thresholds: parse if score > 0.15 (tunable)
    PHONE_THRESHOLD = 0.15
    COMPANY_THRESHOLD = 0.15

    parse_phone = phone_score >= PHONE_THRESHOLD
    parse_company = company_score >= COMPANY_THRESHOLD

    # Build output rows
    # We'll construct output rows aligning by input rows count; if using dict-of-lists
    # data structure, assume equal lengths
    # Get number of rows as length of any column
    if not data:
        print("No data found in input.", file=sys.stderr)
        sys.exit(2)
    first_col = next(iter(data))
    nrows = len(data[first_col])

    out_rows = []
    headers = []
    if parse_phone:
        headers.extend(['PhoneNumber', 'Country', 'Number'])
    if parse_company:
        headers.extend(['CompanyName', 'Name', 'Legal'])
    # If neither, still write a file with original columns
    if not headers:
        # fallback: copy input to output
        headers = list(data.keys())
        for i in range(nrows):
            row = {h: data[h][i] if i < len(data[h]) else '' for h in headers}
            out_rows.append(row)
        write_output_csv(out_rows, args.output, headers)
        print(f"No phone/company columns detected above thresholds. Wrote original data to {args.output}")
        return

    for i in range(nrows):
        row = {}
        if parse_phone:
            raw = data.get(best_phone_col, [''])[i] if best_phone_col else ''
            country, number = parse_phone_number(raw)
            row['PhoneNumber'] = raw
            row['Country'] = country if country else ''
            row['Number'] = number if number else ''
        if parse_company:
            rawc = data.get(best_company_col, [''])[i] if best_company_col else ''
            name, legal_suf = split_company_name(rawc, legal)
            row['CompanyName'] = rawc
            row['Name'] = name if name else ''
            row['Legal'] = legal_suf if legal_suf else ''
        out_rows.append(row)
    write_output_csv(out_rows, args.output, headers)
    print(f"Wrote parsed output to {args.output}")
    if parse_phone:
        print(f"Parsed phone column: '{best_phone_col}' with score {phone_score:.3f}")
    if parse_company:
        print(f"Parsed company column: '{best_company_col}' with score {company_score:.3f}")

if __name__ == '__main__':
    main()
