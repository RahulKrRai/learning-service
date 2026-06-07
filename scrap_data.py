import pandas as pd

OUTPUT_FILE = "duplicate_order_references.xlsx"
def find_and_export_duplicates(df: pd.DataFrame):
    df.columns = [c.upper() for c in df.columns]   # normalise to UPPER_CASE

    counts     = df.groupby("ORDER_REFERENCE")["ORDER_REFERENCE"].transform("count")
    duplicates = (
        df[counts > 1][
            ["ORDER_REFERENCE", "CONTAINER_REFERENCE",
             "BILL_OF_LADING_LIST", "ACTIVE_BILL_OF_LADING",
             "BOOKING_REFERENCE_LIST", "ACTIVE_BOOKING_REFERENCE",
             "CURRENT_STATUS",
             "OCEAN_CARRIER",
             "PORT_OF_LOAD", "PORT_OF_DISCHARGE",
             "PLANNED_ARRIVAL_DATE", "LATEST_CARRIER_DISCHARGE_ETA",
             "CUSTOMER_ORGANIZATION"]
        ]
        .sort_values("ORDER_REFERENCE")
        .reset_index(drop=True)
    )

    if duplicates.empty:
        print("No duplicate ORDER_REFERENCEs found.")
        return

    duplicates.to_excel(OUTPUT_FILE, index=False)
    print(
        f"\nDone → {OUTPUT_FILE}"
        f"\n  {len(duplicates)} rows"
        f"\n  {duplicates['ORDER_REFERENCE'].nunique()} unique orders with multiple containers"
    )

def run_from_excel(*excel_paths: str):
    frames = []
    for path in excel_paths:
        frames.append(
            pd.read_csv(path, low_memory=False) if path.endswith(".csv") else pd.read_excel(path)
        )

    df = pd.concat(frames, ignore_index=True)
    print(f"Loaded {len(df)} records from {len(frames)} file(s)")

    find_and_export_duplicates(df)

if __name__ == "__main__":
    run_from_excel(
        "~/Downloads/ocean-2025-07-14-2026-04-30.csv",
    )
