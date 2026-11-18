# Patient-Feedback Analyzer

A CECS 451 group project for exploring fictional patient feedback.

## Current features

- Upload a CSV containing comment_id and comment_text.
- Reject missing required columns, blank fields, and duplicate IDs.
- Preview uploaded comments.
- Search comments without matching letter case.
- Download displayed comments as a CSV.
- Download a fictional sample CSV.
- Classify comments with Gemini into topics and overall sentiment.
- Display topic and sentiment charts.
- Filter results by topic and sentiment.
- Preserve analysis results during searches and filtering.
- Flag failed classifications and exclude them from charts.

## Run the dashboard on Windows

Use Python 3.13. From the project folder, create a virtual environment:

```powershell
py -3.13 -m venv .venv
```

Install the dashboard dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install uv
.\.venv\Scripts\uv.exe sync --locked
```
Set your Gemini API key in the same PowerShell terminal:

```powershell
$env:GEMINI_API_KEY = [System.Net.NetworkCredential]::new("", (Read-Host "Paste your Gemini API key" -AsSecureString)).Password
```
Enter your key at the hidden prompt. This setting lasts for the current
terminal session. Launch Streamlit from that same terminal.
Never commit an API key.

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

Click Download sample CSV, then upload that file. Confirm that five comments load. 
Click Analyze comments and wait for the topic and sentiment charts to appear. 
Under Uploaded comments, search for bill. Only comment 003 should appear. 
Click Download displayed comments to export that row with its topics, sentiment, and status.

## Manual validation checks

Upload each file separately:

| File | Expected result |
|---|---|
| sample_feedback.csv | Loads five comments |
| test_missing_column.csv | Shows a missing-column error |
| test_blank_comment.csv | Shows a blank-field error |
| test_duplicate_id.csv | Shows a duplicate-ID error |

## Current limitations and remaining work

Gemini classification, charts, search, filters, and CSV export are
connected. Five fictional demonstration comments were successfully
classified during a functional check; this is not a formal accuracy
evaluation.

Larger-dataset evaluation and comparison with a keyword baseline remain.
Requests run sequentially, so larger uploads take longer. API access,
quotas, and network failures can affect analysis.

Results are stored in the current Streamlit session, not permanently.
Clicking Analyze comments again submits the entire uploaded dataset again.
Charts summarize successful classifications across the whole dataset;
filters affect the table and export.

Use fictional feedback only. This prototype is not intended for
clinical decisions or medical advice.

## Current architecture

CSV upload → pandas validation → Gemini classification on button click
→ results stored in Streamlit session state → summary charts and
searchable/filterable table → CSV export.

## Code overview

app.py contains the dashboard interface and CSV processing:

1. Displays upload instructions and a downloadable fictional sample.
2. Reads uploaded CSV values as text to preserve IDs such as 001.
3. Checks required columns, blank fields, and duplicate IDs.
4. Previews valid comments and calls the Gemini classifier for each comment when the user clicks Analyze comments.
5. Stores results in the current session and charts successfully classified comments.
6. Applies text, topic, and sentiment filters to the table and exports only the displayed rows.

sample_feedback.csv contains five fictional demonstration comments.
The three test CSV files contain intentionally invalid inputs for
checking validation.

## Gemini integration

The dashboard calls classify_comment(comment_text) from
gemini_classifier.py using gemini-decision-1 through the Decisions API.
Specific topics are included when their returned score is at least 0.5.

The agreed return format is a dictionary containing:

- topics: a list using scheduling, wait times, staff communication,
  billing, or other.
- sentiment: positive, negative, neutral, or mixed.

Failed requests will be flagged rather than assigned invented labels.
API credentials must be kept outside tracked source files.

The "other" topic is used only when none of the four specific topics
apply. It must not appear alongside a specific topic. A comment may
receive multiple specific topics.