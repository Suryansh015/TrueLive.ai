import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from newspaper import Article
from flask import Flask, render_template_string, request

# Initialize Flask app
app = Flask(__name__)

# Load your pre-trained model and tokenizer
MODEL_PATH = r"C:\Users\surya\Desktop\_token model 1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None  # Variable to store the result
    input_url = None  # Variable to store the article URL
    error_message = None  # Error message if URL is invalid

    if request.method == 'POST':
        # Get the article URL from the form
        input_url = request.form['article_url']

        try:
            # Process the article
            article = Article(input_url)
            article.download()
            article.parse()

            # Combine title and text to form the input for the model
            article_text = f"Title: {article.title}\nContent: {article.text}"

            # Tokenize the input text
            inputs = tokenizer(article_text, return_tensors="pt", truncation=True, padding=True)

            # Perform inference
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                predicted_class = torch.argmax(logits, dim=1).item()

            # Map class index to a label (adjust the class labels as per your model)
            class_labels = ["True", "False", "Unverified"]  # Adjust as per your model's output
            result = class_labels[predicted_class] if predicted_class < len(class_labels) else "Unknown"

        except Exception as e:
            error_message = f"Error processing article: {str(e)}"

    # HTML template with input form and result display
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Article Claim Detection</title>
    </head>
    <body>
        <h1>Article Claim Detection</h1>
        <form method="POST" action="/">
            <label for="article_url">Enter Article URL:</label><br>
            <input type="text" id="article_url" name="article_url" placeholder="Enter article URL here" required style="width: 300px; padding: 8px;"><br><br>
            <button type="submit" style="padding: 8px 16px;">Submit</button>
        </form>
        
        {% if error_message %}
        <p style="color: red;">{{ error_message }}</p>
        {% endif %}

        {% if result %}
        <h2>Claim Detection Result</h2>
        <p><strong>Article URL:</strong> {{ input_url }}</p>
        <p><strong>Claim Detection Result:</strong> {{ result }}</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, result=result, input_url=input_url, error_message=error_message)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
