import argparse
import json
import re
from pathlib import Path

import pandas as pd


KEEP_COLUMNS = [
    "Year",
    "DWS Name",
    "Owner Legal Name",
    "DWS Category",
    "PHU Legal Name",
    "Sample Date",
    "Sample Type Name",
    "Result",
    "Exceed2",
    "Exceed Fed?",
]

EXPORT_COLUMNS = [
    "Year",
    "Owner Legal Name",
    "DWS Category",
    "PHU Legal Name",
    "DWS Name cleared",
    "Sample Date",
    "Sample Type Name",
    "Result",
    "Exceed2",
]


def clean_dws_name(value):
    if pd.isna(value):
        return None
    return re.sub(r"^\s*R243\s+", "", str(value)).strip()


def load_master(path):
    header = pd.read_excel(path, sheet_name="Master", nrows=0)
    usecols = [column for column in KEEP_COLUMNS if column in header.columns]
    master = pd.read_excel(path, sheet_name="Master", usecols=usecols)

    if "Exceed2" not in master.columns:
        if "Exceed Fed?" not in master.columns:
            raise ValueError("Expected either 'Exceed2' or 'Exceed Fed?' in Master sheet")
        master["Exceed2"] = master["Exceed Fed?"]

    master["Result"] = pd.to_numeric(master["Result"], errors="coerce")
    master["Year"] = pd.to_numeric(master["Year"], errors="coerce").astype("Int64")
    master["Sample Date"] = pd.to_datetime(master["Sample Date"], errors="coerce")
    master["DWS Name cleared"] = master["DWS Name"].apply(clean_dws_name)
    master["Exceed2"] = master["Exceed2"].fillna("N").astype(str).str.strip().str.upper()

    # The published federal guideline is exceeded above 5 ug/L, not at exactly 5.
    master.loc[master["Result"].eq(5), "Exceed2"] = "N"
    master.loc[~master["Exceed2"].isin(["Y", "N"]), "Exceed2"] = "N"

    return master[EXPORT_COLUMNS].copy()


def rate(yes, no):
    total = yes + no
    return 0 if total == 0 else round((yes / total) * 100, 2)


def summarize_frame(frame, years):
    counts = frame["Exceed2"].value_counts()
    no_count = int(counts.get("N", 0))
    yes_count = int(counts.get("Y", 0))

    by_year = frame.groupby(["Year", "Exceed2"], observed=True).size().unstack(fill_value=0)
    section2 = {}
    for year in years:
        year_no = int(by_year.loc[year, "N"]) if year in by_year.index and "N" in by_year.columns else 0
        year_yes = int(by_year.loc[year, "Y"]) if year in by_year.index and "Y" in by_year.columns else 0
        section2[str(year)] = {
            "total tests": year_yes + year_no,
            "exceedance": year_yes,
            "failure rate": rate(year_yes, year_no),
        }

    return {
        "N": no_count,
        "Y": yes_count,
        "total tests": yes_count + no_count,
        "exceedance": yes_count,
        "failure rate": rate(yes_count, no_count),
    }, section2


def date_to_millis(value):
    if pd.isna(value):
        return None
    return int(pd.Timestamp(value).timestamp() * 1000)


def result_value(value):
    if pd.isna(value):
        return None
    number = float(value)
    return int(number) if number.is_integer() else number


def sample_records(frame, sample_limit):
    records = frame.sort_values(by=["Year", "Sample Date"], ascending=True)
    if sample_limit is not None:
        records = records.head(sample_limit)

    return [
        {
            "Sample Date": date_to_millis(row["Sample Date"]),
            "Result": result_value(row["Result"]),
            "Sample Type Name": "" if pd.isna(row["Sample Type Name"]) else str(row["Sample Type Name"]),
        }
        for _, row in records.iterrows()
    ]


def build_payload(master, sample_limit):
    years = sorted(int(year) for year in master["Year"].dropna().unique())
    payload = {}

    for school_name, frame in master.dropna(subset=["DWS Name cleared"]).groupby("DWS Name cleared", sort=True):
        section1, section2 = summarize_frame(frame, years)
        first = frame.iloc[0]
        payload[school_name] = {
            "section0": {
                "School Name": school_name,
                "Owner Legal Name": "" if pd.isna(first["Owner Legal Name"]) else str(first["Owner Legal Name"]),
                "School Category": "" if pd.isna(first["DWS Category"]) else str(first["DWS Category"]),
            },
            "section1": section1,
            "section2": section2,
            "section3": sample_records(frame, sample_limit),
        }

    section1, section2 = summarize_frame(master, years)
    payload["ALL"] = {
        "section0": {
            "School Name": "ALL",
            "Owner Legal Name": "ALL",
            "School Category": "ALL",
        },
        "section1": section1,
        "section2": section2,
        "section3": [],
    }
    return payload


def write_json(payload, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description="Export Ontario lead testing data for the website.")
    parser.add_argument("--input", default="2026-05-14- Ontario_Lead_Data.xlsx")
    parser.add_argument("--refined-output", default="new_year_refined_master.xlsx")
    parser.add_argument("--limited-json-output", default="website/js/final_limited.json")
    parser.add_argument("--full-json-output", default="website/js/final_last.json")
    parser.add_argument("--react-json-output", default="data_water2.json")
    parser.add_argument("--sample-limit", type=int, default=5)
    args = parser.parse_args()

    input_path = Path(args.input)
    master = load_master(input_path)

    if args.refined_output:
        master.to_excel(args.refined_output, sheet_name="master", index=False)

    limited_payload = build_payload(master, args.sample_limit)
    write_json(limited_payload, Path(args.limited_json_output))
    if args.react_json_output:
        write_json(limited_payload, Path(args.react_json_output))

    if args.full_json_output:
        full_payload = build_payload(master, None)
        write_json(full_payload, Path(args.full_json_output))

    all_summary = limited_payload["ALL"]["section1"]
    years = limited_payload["ALL"]["section2"]
    print(f"Rows exported: {all_summary['total tests']:,}")
    print(f"Federal exceedances >5 ug/L: {all_summary['exceedance']:,} ({all_summary['failure rate']}%)")
    print("Years:", ", ".join(years.keys()))
    print(f"Wrote {args.limited_json_output}")
    if args.react_json_output:
        print(f"Wrote {args.react_json_output}")
    if args.full_json_output:
        print(f"Wrote {args.full_json_output}")
    if args.refined_output:
        print(f"Wrote {args.refined_output}")


if __name__ == "__main__":
    main()
