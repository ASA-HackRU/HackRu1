class SentimentAnalyzer:
    BANNED_TERMS = ["palestine", "israel"]

    def __init__(self, model_name="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"):
        self.model = pipeline("text-classification", model=model_name)

    def analyze_text(self, text):
        if not text:
            return {
                "strength": "neutral",
                "impulse_score": 3,
                "confidence": 0.0,
                "explanation": "No content to analyze."
            }

        # Check for banned terms
        lower_text = text.lower()
        if any(term in lower_text for term in self.BANNED_TERMS):
            return {
                "strength": "neutral",
                "impulse_score": 3,
                "confidence": 0.0,
                "explanation": "Content contains banned terms."
            }

        result = self.model(text, truncation=True)[0]
        label = result["label"].lower()
        score = float(result["score"])

        # Determine strength and impulse score
        if label == "neutral" or score < 0.5:
            strength = "neutral"
            impulse_value = 3
        elif label == "positive":
            if score >= 0.75:
                strength = "large positive"
                impulse_value = 5
            else:
                strength = "small positive"
                impulse_value = 4
        elif label == "negative":
            if score >= 0.75:
                strength = "large negative"
                impulse_value = 1
            else:
                strength = "small negative"
                impulse_value = 2
        else:
            strength = "neutral"
            impulse_value = 3

        explanation = f"The article suggests a {strength} movement in the stock/valuation with {score*100:.1f}% confidence."

        return {
            "strength": strength,
            "impulse_score": impulse_value,
            "confidence": round(score, 3),
            "explanation": explanation
        }
