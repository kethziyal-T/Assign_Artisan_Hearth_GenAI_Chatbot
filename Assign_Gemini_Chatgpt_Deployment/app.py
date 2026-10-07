from flask import Flask, render_template, request
from services.genai_service import get_response 

app = Flask(__name__)


# --- Product and Category Image Mapping ---
PRODUCT_IMAGE_MAP = {
    "pet sweater": "/static/images/products/pet-sweater.jpg",
    "sweater": "/static/images/products/pet-sweater.jpg",
    "baby dress": "/static/images/products/baby-dress.jpg",
    "dress": "/static/images/products/baby-dress.jpg",
    "bag": "/static/images/products/crochet-bag.jpg",
    "tote": "/static/images/products/crochet-bag.jpg",
    "crochet": "/static/images/products/crochet-default.jpg",
    "oil painting": "/static/images/products/oil-painting.jpg",
    "canvas": "/static/images/products/canvas-painting.jpg",
    "painting": "/static/images/products/painting-default.jpg"
}
GLOBAL_PLACEHOLDER = "/static/images/products/placeholder.jpg"

def match_image_to_prompt(prompt_text):
    """Scans the prompt text to match it with a corresponding category image."""
    if not prompt_text:
        return GLOBAL_PLACEHOLDER
    
    clean_text = prompt_text.lower()
    
    # Check for specific phrase matches first (e.g., "oil painting", "pet sweater")
    for key, path in PRODUCT_IMAGE_MAP.items():
        if " " in key and key in clean_text:
            return path
            
    # Check for single keyword matches (e.g., "bag", "canvas")
    for key, path in PRODUCT_IMAGE_MAP.items():
        if key in clean_text:
            return path
            
    return GLOBAL_PLACEHOLDER

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # 1. Safeguard against empty or missing prompt submissions
    prompt = request.form.get("prompt", "").strip()
 
    
    if not prompt:
        return render_template("index.html", error="Please enter a valid prompt.")
    
    
    try:
        # 2. Fetch the clean raw HTML block directly from your service file
        response_html = get_response(prompt)
        
      # 3. Match the prompt against your product database to find the image
        matched_image_url = match_image_to_prompt(prompt)

        
    except Exception as e:
        # 3. Fallback guard so your application doesn't crash on unforeseen exceptions
        response_html = f"<p style='color:red;'>⚠️ Error generating response: {str(e)}</p>"
        matched_image_url = GLOBAL_PLACEHOLDER

    # 4. Return the rendered safe HTML variable directly into your result template layout
    return render_template(
        "result.html",
        prompt=prompt,
        response=response_html,
        image_url=matched_image_url
    )


if __name__ == "__main__":
    app.run(debug=True)
    
    
    
   