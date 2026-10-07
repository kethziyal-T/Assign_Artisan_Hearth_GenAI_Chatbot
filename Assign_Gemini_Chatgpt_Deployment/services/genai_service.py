import time
import utils  
# ✅ FIXED: Restored the missing SDK and error handling module imports
from google import genai
from google.genai import errors
from config import GENAI_API_KEY

# Initialize the modern SDK client using your imported key
client = genai.Client(api_key=GENAI_API_KEY)

def get_response(prompt):
    # 1. Check your strategic FAQ knowledge baseline first
    faq_context = ""
    try:
        faq_response = utils.resolve_handwritten_faq(prompt)
        if faq_response:
            faq_context = f"\nCRITICAL POLICY CONTEXT TO ENFORCE:\n{faq_response}\n"
    except Exception:
        pass

    # 2. Build the structural prompt blending your business requirements
    fixed_prompt = f"""
Answer the following question in valid HTML formatting only.

{faq_context}

Requirements:
- Use <h2>, <h3> headings for structure.
- Use <p> for paragraphs.
- Use <ul><li> for bullet points.
- Use <pre><code> for code blocks.
- Do not use Markdown notation like **bold** or ```html. Use raw HTML tags.
- Do not include <html>, <body>, or <head> containers.

Question:
{prompt}
"""

    max_retries = 2
    for attempt in range(max_retries):
        try:
            # 💡 CRITICAL FIX: Changed model to the universally supported "gemini-2.5-flash"
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite", 
                contents=fixed_prompt
            )
            return response.text.strip()
            
        except errors.APIError as e:
            if ("503" in str(e) or "Server" in str(e)) and attempt < max_retries - 1:
                time.sleep(2)  
                continue
            
            # 💡 EXPOSE ACTUAL ERROR: Shows you exactly why Google rejected the request
            return f"""
            <h2>Gemini API Error</h2>
            <p><strong>Details:</strong> {str(e)}</p>
            <p>Please verify your API key and model permissions.</p>
            """
        except Exception as general_error:
            # Catches network, import, or key loading issues outside of the API call
            return f"""
            <h2>System Exception</h2>
            <p><strong>Details:</strong> {str(general_error)}</p>
            """

