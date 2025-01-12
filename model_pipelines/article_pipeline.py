import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from newspaper import Article

MODEL_PATH = r"path_to_ba-claim/distilbert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

def process_article(input_url):
    try:
        article = Article(input_url)
        article.download()
        article.parse()
        article_text = f"Title: {article.title}\nContent: {article.text}"

        # Tokenize the input text
        inputs = tokenizer(article_text, return_tensors="pt", truncation=True, padding=True)
         # inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, predicted_class].item()

        # Map class index to a label 
        class_labels = ["True", "False", "Unverified"]  
        result = class_labels[predicted_class] if predicted_class < len(class_labels) else "Unknown"

        return result, confidence

    except Exception as e:
        raise ValueError(f"Error processing article: {str(e)}")

if __name__ == "__main__":
    input_url = "input_example_article_link"
    try:
        result, confidence = process_article(input_url)
        print(f"Claim Detection Result: {result}")
        print(f"Confidence Score: {confidence:.2f}")
    except ValueError as e:
        print(e)
