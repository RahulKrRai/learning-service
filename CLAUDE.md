# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A personal repository with two purposes:
1. **DSA practice** — algorithm implementations in Python, organized by topic
2. **Work utility scripts** — Logward-related data processing and debugging tools

There is no build system, test framework, or linter configured. Scripts are run individually with `python3 <file>`.

## Running Code

```bash
# Run any algorithm file directly
python3 DP/Knapsack_0_1.py
python3 array/reverse_pair.py

# Work scripts require pandas (and pika for RMQ.py)
python3 binary_tree.py      # ocean shipment data processing (misleading filename)
python3 scrap_data.py        # duplicate order reference finder
```

## Repository Layout

- **`DP/`** — Dynamic programming problems (knapsack, coin change, LCS, rod cutting, palindromic subsequence). Each file contains a class with recursive, memoized, and tabular solutions plus `__main__` test cases.
- **`array/`** — Array problems (reverse pairs via merge sort).
- **`6sense_interview_prep/`** — Interview prep markdown files (study plans, templates, behavioral notes). See `CONTEXT.md` for full status.
- **`binary_tree.py`** — Despite the name, this is an ocean shipment data processing script that applies timezone offsets to timestamps using a locode-to-UTC-offset map, reformats columns for Logward, and exports chunked Excel files.
- **`scrap_data.py`** — Finds duplicate ORDER_REFERENCEs in shipment CSVs.
- **`RMQ.py`** — RabbitMQ consumer for Logward queues.

## Conventions in DSA Code

- Each problem is a class with methods progressing through solution approaches: `*_recursive` -> `*_memoization`/`*_memoize` -> `*_tabular`
- All files use `if __name__ == '__main__':` blocks with hardcoded test cases
- DP table initialization: `-1` for memoization, `0` for tabulation
- Uses `sys.maxsize` as infinity sentinel in minimization problems
