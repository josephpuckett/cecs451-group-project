import pandas as pd
import streamlit as st

st.title("Patient-Feedback Analyzer")
st.write("Upload fictional patient comments to review feedback.")
st.info(
    "Use fictional feedback only. Your CSV must include comment_id and "
    "comment_text columns. Each ID must be unique, and neither field "
    "can be blank."
)

sample_csv = """comment_id,comment_text
001,"The receptionist was helpful and explained everything clearly."
002,"I waited an hour after my scheduled appointment."
003,"Booking an appointment was easy but the bill was confusing."
004,"My appointment was on Tuesday."
005,"The parking lot was difficult to navigate."
"""

st.download_button(
    label="Download sample CSV",
    data=sample_csv.encode("utf-8"),
    file_name="sample_feedback.csv",
    mime="text/csv"
)

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
    search_text = st.text_input("Search comments")

    filtered_df = df

    if search_text.strip():
        filtered_df = df[
            df["comment_text"].str.contains(
                search_text.strip(), case=False, regex=False
            )
        ]

    st.write(f"Showing {len(filtered_df)} of {len(df)} comments.")
    st.dataframe(filtered_df, hide_index=True)
    st.download_button(
        label="Download displayed comments",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_feedback.csv",
        mime="text/csv"
    )

