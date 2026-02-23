"""
Sentiment Analysis Module
Placeholder for ML model integration
"""

RISK_KEYWORDS = [
    "suicide", "self-harm", "kill myself", "want to die",
    "end my life", "hurt myself", "no reason to live",
    "better off dead", "self harm", "cut myself", "overdose",
    "hang myself", "jump off", "slit my wrists"
]

EMOTION_KEYWORDS = {
    "Happy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "love", "grateful", "blessed"],
    "Sad": ["sad", "depressed", "down", "unhappy", "miserable", "hopeless", "lonely", "empty"],
    "Angry": ["angry", "mad", "frustrated", "annoyed", "irritated", "furious", "hate"],
    "Anxious": ["worried", "nervous", "stressed", "overwhelmed", "panic", "fear", "anxious"],
    "Calm": ["calm", "relaxed", "peaceful", "serene", "content", "at ease"],
    "Excited": ["excited", "thrilled", "eager", "enthusiastic", "pumped"],
    "Tired": ["tired", "exhausted", "drained", "fatigued", "sleepy"],
    "Confused": ["confused", "lost", "uncertain", "unsure", "puzzled"]
}

POSITIVE_WORDS = [
    "happy", "joy", "great", "wonderful", "amazing", "excited", "good", "better",
    "best", "love", "grateful", "blessed", "awesome", "fantastic",
    "perfect", "beautiful", "excellent", "outstanding", "superb"
]

NEGATIVE_WORDS = [
    "sad", "depressed", "bad", "terrible", "awful", "hate", "worst", "angry",
    "anxious", "stressed", "hopeless", "miserable", "frustrated", "disappointed",
    "devastated", "heartbroken", "worthless", "guilty", "ashamed"
]


def check_risk_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in RISK_KEYWORDS)


def detect_emotion(text: str) -> str:
    text_lower = text.lower()
    emotion_scores = {}
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            emotion_scores[emotion] = score
    
    if emotion_scores:
        return max(emotion_scores, key=emotion_scores.get)
    return "Neutral"


def analyze_sentiment(text: str) -> dict:
    text_lower = text.lower()
    
    pos_count = sum(1 for word in POSITIVE_WORDS if word in text_lower)
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    total = pos_count + neg_count
    
    if total == 0:
        score = 0.0
    else:
        score = (pos_count - neg_count) / total
        score = max(-1.0, min(1.0, score))
    
    emotion = detect_emotion(text)
    risk_flag = check_risk_keywords(text)
    
    return {
        "score": round(score, 3),
        "emotion": emotion,
        "risk_flag": risk_flag
    }


def get_sentiment_label(score: float) -> str:
    if score >= 0.5:
        return "Very Positive"
    elif score >= 0.1:
        return "Positive"
    elif score > -0.1:
        return "Neutral"
    elif score > -0.5:
        return "Negative"
    else:
        return "Very Negative"
