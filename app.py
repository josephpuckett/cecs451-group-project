import pandas as pd
import streamlit as st

st.title("Patient-Feedback Analyzer")
st.write("Upload fictional patient comments to review feedback.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError):
        st.error("Unable to read this file. Please upload a valid UTF-8 CSV.")
        st.stop()

    required_columns = ["comment_id", "comment_text"]

    if not all(column in df.columns for column in required_columns):
        st.error("Your CSV must contain comment_id and comment_text columns.")
        st.stop()

    df = df[required_columns].copy()

    for column in required_columns:
        df[column] = df[column].str.strip()

    if df.empty:
        st.error("Your CSV contains no comments.")
        st.stop()

    if (df["comment_id"] == "").any() or (df["comment_text"] == "").any():
        st.error("Every row must have a comment ID and comment text.")
        st.stop()

    if df["comment_id"].duplicated().any():
        st.error("Each comment_id must be unique.")
        st.stop()

    st.success(f"Successfully loaded {len(df)} comments.")
    st.subheader("Uploaded comments")
    st.dataframe(df, hide_index=True)