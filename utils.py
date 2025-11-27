# utils.py
import re
import csv
import os
from difflib import get_close_matches

PHONE_RE_SIMPLE = re.compile(r'^\+?[0-9\-\s\(\)]{6,}$')
# detect if mostly digits with optional +, spaces, dashes, parentheses

DATE_PATTERNS = [
    re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$'),
    re.compile(r'^\d{1,2}/\d{1,2}/\d{2,4}$'),
    re.compile(r'^[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}$'),  # e.g. March 2, 2020
    re.compile(r'^\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}$'),
]

def load_list_file(path):
    items = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            s = line.strip()
            if s:
                items.append(s)
    return items

def normalize_text(s):
    if s is None:
        return ''
    s = str(s).strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def looks_like_phone(s):
    if not s:
        return False
    s = s.strip()
    # must contain at least 6 digits
    digits = re.sub(r'\D', '', s)
    if len(digits) < 6:
        return False
    # basic format check
    return bool(PHONE_RE_SIMPLE.match(s))

def looks_like_date(s):
    if not s:
        return False
    s = s.strip()
    for p in DATE_PATTERNS:
        if p.match(s):
            return True
    # fallback: any string with month names
    if re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\b', s.lower()):
        return True
    return False

def fraction_matching(values, predicate):
    total = 0
    matches = 0
    for v in values:
        total += 1
        if predicate(v):
            matches += 1
    if total == 0:
        return 0.0
    return matches / total

def best_country_match(s, countries):
    # exact match or close match
    s_norm = normalize_text(s).lower()
    country_map = {c.lower(): c for c in countries}
    if s_norm in country_map:
        return country_map[s_norm]
    # fuzzy via get_close_matches
    candidates = get_close_matches(s_norm, list(country_map.keys()), n=1, cutoff=0.85)
    if candidates:
        return country_map[candidates[0]]
    return None

# Basic country code map for parsing country codes from leading + codes
COMMON_CC_MAP = {
    '1': 'US',
    '91': 'India',
    '44': 'UK',
    '61': 'Australia',
    '49': 'Germany',
    '81': 'Japan',
    '86': 'China',
    '7': 'Russia',
    '39': 'Italy',
    '33': 'France',
    '27': 'South Africa',
    '34': 'Spain',
    '55': 'Brazil',
}

def parse_phone_number(raw):
    if raw is None:
        return None, None
    s = str(raw).strip()
    digits = re.sub(r'\D', '', s)
    if not digits:
        return None, None
    # if starts with + (has country code)
    if s.startswith('+'):
        # try extracting up to 3 digits for country code
        for cc_len in (1,2,3):
            cc = digits[:cc_len]
            rest = digits[cc_len:]
            if cc in COMMON_CC_MAP:
                return COMMON_CC_MAP[cc], rest
        # fallback: unknown cc
        # assume 10-digit national number if rest length matches 10
        if len(digits) > 10:
            return None, digits[-10:]
        return None, digits
    else:
        # no leading +. If digits length > 10, maybe contains country code (first 1-3 digits)
        if len(digits) > 10:
            for cc_len in (1,2,3):
                cc = digits[:cc_len]
                rest = digits[cc_len:]
                if cc in COMMON_CC_MAP:
                    return COMMON_CC_MAP[cc], rest
            # fallback last 10
            if len(digits) >= 10:
                return None, digits[-10:]
        elif len(digits) == 10:
            return None, digits
        else:
            return None, digits

def split_company_name(company, legal_suffixes):
    """
    Return (name, legal) where legal is matched suffix (normalized), name is remainder.
    If no suffix found, legal is empty.
    """
    if company is None:
        return None, None
    s = normalize_text(company)
    s_low = s.lower()
    # try to find any suffix from legal_suffixes at end
   
