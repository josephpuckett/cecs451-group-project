from google import genai
from google.genai._gaos.types.decisions.choiceanswer import ChoiceAnswer
from google.genai._gaos.types.decisions.noulanswer import NoulAnswer
from functools import cache

@cache
def get_client():
    # Changing api_version is necessary to make decisions API work as of 11/14/26
    # Returns an Exception if there is an error
    # Requires environment variable GEMINI_API_KEY to be set to work
    # Get a free API key from https://aistudio.google.com 
    return genai.Client(http_options={"api_version": "v1beta"}) 

def classify_comment(comment_text: str) -> dict:
    threshold = 0.5
    topic_names = ["scheduling", "wait_times", "staff_communication", "billing"]
    feedback = f"The following is feedback from a patient at a clinic: {comment_text}"
    client = get_client()

    # Uses retry with exponential backoff by default and returns an Exception if there is an error
    result = client.decisions.create(
        model="gemini-decision-1",
        input=[
            {
                "type": "text",
                "text": feedback,
            },
        ],
        questions={
            "scheduling": {
                "type": "noul",
                "instructions": "Is this feedback related to booking, rescheduling, canceling, or finding an available appointment?",
            },
            "wait_times": {
                "type": "noul",
                "instructions": "Is this feedback related to wait times?",
            },
            "staff_communication": {
                "type": "noul",
                "instructions": "Is this feedback related to staff communication?",
            },
            "billing": {
                "type": "noul",
                "instructions": "Is this feedback related to billing?"
            },
            "sentiment": {
                "type": "choice",
                "instructions": "Choose the option that best describes the overall sentiment of the feedback.",
                "criteria": {
                    "positive": "The feedback is mostly positive.",
                    "negative": "The feedback is mostly negative.",
                    "neutral": "The feedback is neither positive nor negative.",
                    "mixed": "The feedback is partially positive and partially negative.",
                },
            },
        },
    )

    if result.answers is None:
        raise ValueError("No answers were returned")
    
    topics = []
    for topic in topic_names:
        answer = result.answers[topic]
        if not isinstance(answer, NoulAnswer):
            raise TypeError(f"An answer for {topic} was {type(answer)} instead of NoulAnswer")
        if answer.noul >= threshold:
            topics.append(topic)
    if not topics:
        topics.append("other")
    
    sentiment_answer = result.answers["sentiment"]
    if not isinstance(sentiment_answer, ChoiceAnswer):
        raise TypeError(f"An answer for sentiment was {type(sentiment_answer)} instead of ChoiceAnswer")
    sentiment = sentiment_answer.choice

    return {
        "topics": topics,
        "sentiment": sentiment
    }
