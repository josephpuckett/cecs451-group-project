import pandas as pd
import streamlit as st
import os
from gemini_classifier import classify_comment

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

    # Clear previous results when a different file is uploaded.
    file_contents = uploaded_file.getvalue()

    if st.session_state.get("analyzed_file") != file_contents:
        st.session_state["analyzed_file"] = file_contents
        st.session_state["analysis_results"] = None

    if st.button("Analyze comments"):
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("Gemini API key is missing. Start the app from the terminal where you set the key.")
        else:
            results = []
            progress = st.progress(0)

            allowed_topics = {
                "scheduling", "wait_times", "staff_communication",
                "billing", "other"
            }
            allowed_sentiments = {
                "positive", "negative", "neutral", "mixed"
            }

            for number, row in enumerate(df.to_dict("records"), start=1):
                result_row = row.copy()

                try:
                    prediction = classify_comment(row["comment_text"])
                    topics = prediction["topics"]
                    sentiment = prediction["sentiment"]

                    if (
                        not isinstance(topics, list)
                        or not topics
                        or any(topic not in allowed_topics for topic in topics)
                        or ("other" in topics and len(topics) > 1)
                        or sentiment not in allowed_sentiments
                    ):
                        raise ValueError("Invalid classification")

                    result_row["topics"] = ", ".join(
                        topic.replace("_", " ") for topic in topics
                    )
                    result_row["sentiment"] = sentiment
                    result_row["status"] = "success"

                except Exception:
                    result_row["topics"] = ""
                    result_row["sentiment"] = ""
                    result_row["status"] = "failed"

                results.append(result_row)
                progress.progress(number / len(df))

            st.session_state["analysis_results"] = pd.DataFrame(results)

    if st.session_state.get("analysis_results") is not None:
        df = st.session_state["analysis_results"].copy()
        failed_count = (df["status"] == "failed").sum()

        if failed_count:
            st.warning(f"{failed_count} comments could not be classified.")
        else:
            st.success("All comments classified successfully.")

    if st.session_state.get("analysis_results") is not None:
        successful_df = df[df["status"] == "success"]

        if not successful_df.empty:
            st.subheader("Feedback summary")

            st.caption(
                "Charts include successfully classified comments only. "
                "A comment can have multiple topics."
            )

            topic_counts = (
                successful_df["topics"]
                .str.split(", ")
                .explode()
                .value_counts()
            )

            sentiment_counts = (
                successful_df["sentiment"]
                .value_counts()
                .reindex(
                    ["positive", "negative", "neutral", "mixed"],
                    fill_value=0
                )
            )

            st.write("Comments by topic")
            st.bar_chart(topic_counts)

            st.write("Comments by sentiment")
            st.bar_chart(sentiment_counts)

    st.subheader("Uploaded comments")
    search_text = st.text_input("Search comments")

    filtered_df = df

    if "topics" in df.columns:
        selected_topic = st.selectbox(
            "Filter by topic",
            ["All", "scheduling", "wait times",
             "staff communication", "billing", "other"]
        )

        selected_sentiment = st.selectbox(
            "Filter by sentiment",
            ["All", "positive", "negative", "neutral", "mixed"]
        )

        if selected_topic != "All":
            filtered_df = filtered_df[
                filtered_df["topics"].str.split(", ").apply(
                    lambda topics: selected_topic in topics
                )
            ]

        if selected_sentiment != "All":
            filtered_df = filtered_df[
                filtered_df["sentiment"] == selected_sentiment
            ]

    if search_text.strip():
        filtered_df = filtered_df[
            filtered_df["comment_text"].str.contains(
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

