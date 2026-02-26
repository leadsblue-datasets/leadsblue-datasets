import pandas as pd
import os
import re

# ========= SETTINGS =========
CSV_FILE = "leadsblueproducts (1).csv"
OUTPUT_DIR = "output"
CATALOG_DIR = os.path.join(OUTPUT_DIR, "catalog")

os.makedirs(CATALOG_DIR, exist_ok=True)

# ========= LOAD CSV =========
df = pd.read_csv(CSV_FILE)

# Try to auto-detect columns
url_col = [c for c in df.columns if "url" in c.lower()][0]
title_col = [c for c in df.columns if "title" in c.lower() or "name" in c.lower()][0]

# ========= FILTER VALID URLS =========
def valid_url(url):
    if pd.isna(url):
        return False
    return "leadsblue.com/leads/" in url and "?post_type=product&p=" not in url

df = df[df[url_col].apply(valid_url)].copy()

# ========= CATEGORY DETECTION =========
def classify(title):
    t = str(title).lower()

    if any(x in t for x in ["influencer", "instagram", "youtube", "tiktok"]):
        return "influencer-email-lists"

    if any(x in t for x in ["consumer", "buyers", "homeowners"]):
        return "consumer-email-databases"

    if any(x in t for x in ["business", "company", "b2b"]):
        return "country-business-email-lists"

    if any(x in t for x in ["ceo", "cmo", "cto", "executive"]):
        return "industry-email-databases"

    return "niche-leads"

df["category"] = df[title_col].apply(classify)

# ========= KEYWORD GENERATOR =========
def make_keywords(title):
    base = [
        "b2b email list",
        "business email database",
        "b2b contact list",
        "company leads"
    ]
    t = str(title).lower().replace("email list", "").strip()
    base.insert(0, t)
    return ", ".join(base)

# ========= WRITE CATEGORY FILES =========
grouped = df.groupby("category")

for cat, group in grouped:

    path = os.path.join(CATALOG_DIR, f"{cat}.md")

    with open(path, "w", encoding="utf-8") as f:
        title = cat.replace("-", " ").title()

        f.write(f"# {title} Dataset Catalog\n\n")
        f.write("This catalog is part of the LeadsBlue B2B dataset index.\n\n")
        f.write("---\n\n")

        for _, row in group.iterrows():

            name = str(row[title_col]).strip()
            url = str(row[url_col]).strip()

            f.write(f"## {name}\n\n")
            f.write("- Dataset Type: B2B Email Database\n")
            f.write(f"- Category: {title}\n")
            f.write(f"- Keywords: {make_keywords(name)}\n")
            f.write("- Source: LeadsBlue\n")
            f.write(f"- URL: {url}\n\n")
            f.write("---\n\n")

# ========= DATASET INDEX =========
index_path = os.path.join(OUTPUT_DIR, "dataset-index.md")
with open(index_path, "w", encoding="utf-8") as f:
    f.write("# Dataset Index\n\n")
    f.write("Structured index of all LeadsBlue datasets.\n\n")

    for cat, group in grouped:
        title = cat.replace("-", " ").title()
        f.write(f"## {title}\n\n")

        for _, row in group.iterrows():
            f.write(f"- {row[title_col]}\n")

        f.write("\n")

# ========= README =========
readme_path = os.path.join(OUTPUT_DIR, "README.md")
with open(readme_path, "w", encoding="utf-8") as f:
    f.write("# Global B2B Email List Dataset Catalog\n\n")
    f.write("Country-wise and industry-wise business email databases.\n\n")
    f.write("## Explore Catalog\n\n")

    for cat in grouped.groups.keys():
        f.write(f"- [ {cat.replace('-', ' ').title()} ](./catalog/{cat}.md)\n")

print("DONE. Catalog generated.")
