#!/usr/bin/env python3
# predict.py
import argparse
import csv
import os
import sys
from utils import (
    load_list_file, normalize_text, looks_like_phone, looks_like_date,
    fraction_matching, best_country_match, split_company_name
)

def read_column_values(path, column):
    # Try with pandas if available for convenience
    try:
        import pandas as pd
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in {path}. Available: {list(df.columns)}")
        return df[column].astype(str).tolist()
    except Exception:
        # fallback to csv module
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            if column not in reader.fieldnames:
                raise KeyError(f"Column '{column}' not found in {path}. Available: {reader.fieldnames}")
            vals = []
            for row in reader:
                vals.append(row.get(column, ''))
            return vals

def score_column(values, countries, legal_suffixes):
    # compute heuristics
    # 1. phone fraction
    phone_frac = fraction_matching(values, looks_like_phone)
    date_frac = fraction_matching(values, looks_like_date)
    country_frac = fraction_matching(values, lambda v: best_country_match(v, countries) is not None)
    # company heuristic: fraction with legal suffix OR contains capitalized words / multiple words
    def company_like(v):
        if not v:
            return False
        v = normalize_text(v)
        if v == '':
            return False
        # legal suffix
        name, legal = split_company_name(v, legal_suffixes)
        if legal and legal.strip() != '':
            return True
        # presence of words that look like proper nouns (start with capital letter) or words count >1
        words = v.split()
        if len(words) >= 2:
            # If many words and not digits, assume possible company
            if any(c.isalpha() for c in v):
                # exclude dates and countries
                if not looks_like_date(v) and best_country_match(v, countries) is None:
                    return True
        return False

    company_frac = fraction_matching(values, company_like)
    # Now map to scores and normalize
    raw_scores = {
        'Phone Number': phone_frac,
        'Date': date_frac,
        'Country': country_frac,
        'Company Name': company_frac,
        'Other': max(0.0, 1.0 - max(phone_frac, date_frac, country_frac, company_frac))
    }
    # normalize to sum 1
    total = sum(raw_scores.values())
    if total == 0:
        # uniform
        return {k: 1/5 for k in raw_scores}
    probs = {k: raw_scores[k]/total for k in raw_scores}
    return probs

def main():
    parser = argparse.ArgumentParser(description="Predict semantic type of a column (Phone Number, Company Name, Country, Date, Other).")
    parser.add_argument('--input', required=True, help='Path to CSV file')
    parser.add_argument('--column', required=True, help='Column name to predict')
    parser.add_argument('--countries', default='data/countries.txt', help='Path to countries.txt (optional)')
    parser.add_argument('--legal', default='data/legal.txt', help='Path to legal.txt (optional)')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    countries = load_list_file(args.countries)
    legal = load_list_file(args.legal)

    try:
        values = read_column_values(args.input, args.column)
    except KeyError as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(2)

    probs = score_column(values, countries, legal)
    # pick top
    top_label = max(probs.items(), key=lambda x: x[1])[0]
    # print only label (as required)
    # map to plain output labels like companyName or PhoneNumber if necessary
    label_map = {
        'Phone Number': 'phoneNumber',
        'Company Name': 'companyName',
        'Country': 'country',
        'Date': 'date',
        'Other': 'other'
    }
    print(label_map.get(top_label, top_label))

if __name__ == '__main__':
    main()
