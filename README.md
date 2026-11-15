# Patient-Feedback Analyzer

A CECS 451 group project for exploring fictional patient feedback.

## Current features

- Upload a CSV containing comment_id and comment_text.
- Reject missing required columns, blank fields, and duplicate IDs.
- Preview uploaded comments.
- Search comments without matching letter case.
- Download displayed comments as a CSV.
- Download a fictional sample CSV.

## Run the dashboard on Windows

Use Python 3.13. From the project folder, create a virtual environment:

```powershell
py -3.13 -m venv .venv
```

Install the dashboard dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install streamlit pandas
```

Start the app:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Keep the terminal running while using the app. If the browser does not
open automatically, visit http://localhost:8501.

If .venv already exists, skip the environment creation step.

## CSV format

Required columns:

- comment_id: a unique, nonblank identifier.
- comment_text: a nonblank fictional comment.

Use UTF-8 CSV files. Additional columns are excluded from the preview
and export.

## Try the app

Download the sample CSV from the dashboard and upload it.
Five comments should appear. Search for "bill" to display one comment,
then download the displayed results.

## Manual validation checks

Upload each file separately:

| File | Expected result |
|---|---|
| sample_feedback.csv | Loads five comments |
| test_missing_column.csv | Shows a missing-column error |
| test_blank_comment.csv | Shows a blank-field error |
| test_duplicate_id.csv | Shows a duplicate-ID error |

## Current limitations and remaining work

The current dashboard supports CSV review, search, and export.
Gemini classification is not connected yet. Topic and sentiment
charts, classification filters, and model evaluation remain planned.

Use fictional feedback only. This prototype is not intended for
clinical decisions or medical advice.

## Current architecture

CSV upload → pandas reads and validates the data → Streamlit displays
the comments → keyword search filters the table → CSV download exports
the displayed rows.

## Code overview

app.py contains the dashboard interface and CSV processing:

1. Displays upload instructions and a downloadable fictional sample.
2. Reads uploaded CSV values as text to preserve IDs such as 001.
3. Checks required columns, blank fields, and duplicate IDs.
4. Displays valid comments in a table.
5. Filters comments using a case-insensitive literal text search.
6. Exports the displayed rows without the pandas row index.

sample_feedback.csv contains five fictional demonstration comments.
The three test CSV files contain intentionally invalid inputs for
checking validation.

## Planned Gemini integration

The dashboard will call classify_comment(comment_text) from
gemini_classifier.py.

The agreed return format is a dictionary containing:

- topics: a list using scheduling, wait times, staff communication,
  billing, or other.
- sentiment: positive, negative, neutral, or mixed.

Failed requests will be flagged rather than assigned invented labels.
API credentials must be kept outside tracked source files.

The "other" topic is used only when none of the four specific topics
apply. It must not appear alongside a specific topic. A comment may
receive multiple specific topics.