import os
import json
from collections import defaultdict
from google import genai
from config import GENAI_API_KEY

# ✅ File system storage paths
products_file = 'craft_products.json'
categories_file = 'craft_categories.json'
delimiter = "####"



# ✅ CRITICAL FIX: Client initialization placed at the absolute top so all functions can see it
client = genai.Client(api_key=GENAI_API_KEY)
MODEL_NAME = "gemini-3.5-flash-lite"
# Inside utils.py


# Replace this exact function inside utils.py

def get_completion_from_messages(messages, model=MODEL_NAME, temperature=0.7, max_tokens=500):
    formatted_messages = []
    extracted_system_text = ""

    # 1. Isolate system instructions and format user payload turns
    for message in messages:
        if message.get("role") == "system":
            extracted_system_text = message.get("content", "")
        elif "content" in message:  
            role_map = "user" if message["role"] == "user" else "model"
            formatted_messages.append({
                "role": role_map,  
                "parts": [{"text": message["content"]}]  
            })

    # 2. Inject business system instructions safely into the first user message turn block
    if formatted_messages and extracted_system_text:
        current_user_text = formatted_messages[0]["parts"][0]["text"]
        formatted_messages[0]["parts"][0]["text"] = f"{extracted_system_text}\n\n{current_user_text}"

    try:
        # ✅ FIXED: Extract the complete target string parameter derived from the updated list element reference
        prompt_content = formatted_messages[0]["parts"][0]["text"] if formatted_messages else ""
        
        # 3. Execute the single content generation call safely using explicit config keyword wrapping
        response = client.models.generate_content(
            model=model,
            contents=prompt_content,
            config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )
        return response.text.strip()
    except Exception as e:
        return f"<h2>System Processing Error</h2><p><strong>Details:</strong> {str(e)}</p>"


def create_categories():
    """
    Initializes your boutique business operational tracking taxonomy list.
    """
    categories_dict = {
        'Fine Art Commissions': [
            'Canvas Board Painting',
            'Custom Landscape Commissions',
            'Textured Impasto Art'
        ],
        'Crochet Training Academy': [
            'Saturday Morning Workshops',
            'Beginner Basics Course',
            'Pattern Reading Mastery'
        ],
        'Bespoke Retail Orders': [
            'Custom Anime Characters',
            'Handmade Tote Bags',
            'Newborn Clothing Sets'
        ]
    }
    with open(categories_file, 'w') as file:
        json.dump(categories_dict, file, indent=4)
    return categories_dict


def get_categories():
    try:
        with open(categories_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return create_categories()


def create_products():
    """
    Generates and saves the customized structural art & craft catalog file.
    """
    products = {
        "Sunsets Landscape Canvas": {
            "name": "Sunsets Landscape Canvas",
            "category": "Fine Art",
            "brand":"AI Art & Craft Shop",
            "type": "Commission Painting",
            "features": ["Premium canvas board", "Acrylic/Oil blend", "Protective UV varnish sealer"],
            "description": "Bespoke custom real physical scenery painting executed on structural board frames.",
            "price": 2500.00
        },
        "Textured Impasto Canvas": {
            "name": "Textured Impasto Canvas",
            "category": "Fine Art",
            "brand": "AI Art & Craft Shop",
            "type": "Finished Sale Only",
            "features": ["Heavy body acrylics", "High structural 3D texture", "Signed by artist"],
            "description": "Stunning dimensional tactile floral artwork. Note: No classes provided for painting items.",
            "price": 3200.00
        },
        "Custom Anime Character": {
            "name": "Custom Anime Character",
            "category": "Crochet Toys",
            "brand": "AI Art & Craft Shop",
            "type": "Bespoke Amigurumi",
            "features": ["Premium cotton yarn", "Embroidered safety eyes", "Washable poly-fill stuffing"],
            "description": "Handmade crochet plush figures modeled closely to any requested animation character reference.",
            "price": 850.00
        },
        "Bespoke Tote Bag": {
            "name": "Bespoke Tote Bag","AI Art & Craft Shop"
            "category": "Crochet Accessories",
            "brand": "AI Art & Craft Shop",
            "type": "Bespoke Accessories",
            "features": ["Reinforced double-stitch strap", "Internal fabric lining layer", "Magnetic snap closure"],
            "description": "High-durability everyday aesthetic woven handbag purse.",
            "price": 1200.00
        },
        "Newborn Romper": {
            "name": "Newborn Romper",
            "category": "Baby Apparel",
            "brand": "AI Art & Craft Shop",
            "type": "Infant Garments",
            "features": ["Hypoallergenic milk cotton yarn", "Zero plastic attachments", "Super soft seamless stitch layout"],
            "description": "Safe, premium organic clothing specialized for newborns and sensitive infant skin.",
            "price": 950.00
        },
        "Crochet Sandals": {
            "name": "Crochet Sandals",
            "category": "Baby Apparel",
            "brand": "AI Art & Craft Shop",
            "type": "Infant Footwear",
            "features": ["Soft woven base sole", "Adjustable secure strap buttons", "Flexible movement fit"],
            "description": "Adorable lightweight custom booties perfect for infants aged 0-12 months.",
            "price": 450.00
            
        }
    }
    with open(products_file, 'w') as file:
        json.dump(products, file, indent=4)
    return products


def get_products():
    try:
        with open(products_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return create_products()


def get_product_list():
    return list(get_products().keys())


def get_products_and_category():
    products = get_products()
    products_by_category = defaultdict(list)
    for product_name, product_info in products.items():
        category = product_info.get('category')
        if category:
            products_by_category[category].append(product_name)
    return dict(products_by_category)


def find_category_and_product_only(user_input, products_and_category):
    """
    Uses Gemini LLM to extract categories and products based on a strict system rule template.
    Returns a clean JSON list string with no surrounding text or markdown blocks.
    """
    delimiter = "####"
    
    system_message_content = f"""
You will be provided with customer service queries.  
The query will be enclosed within {delimiter} characters.  

Extract both matching category configurations and specific products found in the Allowed Schema list below.  

### **Output Format:**
Output a **Python list of objects**, where each object follows this format exactly:  
[
    {{"category": "<Category Name>", "products": ["Product 1", "Product 2"]}}
]

### **Rules for Extraction:**  
1. **Categories & Products must be found or inferred from the user query.**  
2. **Products must be matched to the correct category.**  
3. **If a category is mentioned but no specific products, include ALL products from that category.**
4. **If no relevant products or categories are found, return an empty list `[]`.**  
5. **Ignore any irrelevant words or phrases not related to the predefined allowed listings.**  

### **Allowed Products & Categories:**
**Fine Art (Sales & Commissions):**  
- Sunsets Landscape Canvas  
- Textured Impasto Canvas  

**Custom Crochet Orders:**  
- Custom Anime Character  
- Bespoke Tote Bag  
- Pet Sweaters  

**Baby Apparel:**  
- Newborn Romper  
- Crochet Sandals  

**Crochet Academy (Classes):**  
- Saturday Morning Workshops  

Only output the list of objects **without any extra text, code blocks, spaces, or conversational text.**
"""

    # ✅ Structurally format messages list to alternate turns perfectly for Gemini wrapper compliance
    messages = [  
        {"role": "system", "content": system_message_content},    
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"}
    ] 

    # Execute low temperature inference to guarantee strict array compliance
    return get_completion_from_messages(messages, temperature=0.0)


def get_product_by_name(name):
    return get_products().get(name, None)


def get_products_by_category(category):
    return [prod for prod in get_products().values() if prod.get("category") == category]


def get_mentioned_product_info(data_list):
    product_info_l = []
    if not data_list:
        return product_info_l

    for data in data_list:
        if isinstance(data, dict):
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product: product_info_l.append(product)
            elif "category" in data:
                product_info_l.extend(get_products_by_category(data["category"]))
    return product_info_l


def read_string_to_list(input_data):
    if isinstance(input_data, list):  
        return input_data
    if not input_data:
        return []
    try:
        cleaned_input = str(input_data).strip().strip("```").replace("json", "").strip()
        return json.loads(cleaned_input)
    except json.JSONDecodeError:
        return []


def generate_output_string(data_list):
    output_string = ""
    # ✅ FIX: If data_list is empty, load all products automatically as a fallback
    if not data_list:
        all_products = get_products() # Get the entire product dictionary
        for product_name, product_info in all_products.items():
            output_string += json.dumps(product_info, indent=2) + "\n"
        return output_string

    for data in data_list:
        if isinstance(data, dict):
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product: output_string += json.dumps(product, indent=2) + "\n"
            elif "category" in data:
                for product in get_products_by_category(data["category"]):
                    output_string += json.dumps(product, indent=2) + "\n"
    return output_string


def answer_user_msg(user_msg, product_info):
    """
    Answers the user query cleanly by embedding the contextual catalog info 
    INSIDE the user block to safely fulfill Gemini turn parameters and strictly follow json format.
    """
    system_message = (
        "You are an elegant AI Fashion Stylist and Craft Tutor for 'AI Art & Craft Shop' boutique. "
        "Help clients register for classes, recommend custom styles, or explain commission details. "
        "Logistics: Crochet classes happen Saturdays 10-11am at Crossroad Library, Balbinova, Prague-2 for 250 CZK. "
        "Note: Painting courses do not exist. We only sell physical canvases and take art commission requests."
    )

    # ✅ CRITICAL CORRECTION: Context and input combined within the user turn block
    messages = [ 
        {'role': 'system', 'content': system_message},
        {'role': 'user','content': f"Bespoke Available Catalog/Workshop Details:\n{product_info}\n\nCustomer  Inquiry:\n{delimiter}{user_msg}{delimiter}"}]
    return get_completion_from_messages(messages, temperature=0.3)

def classify_user_query(user_msg):
    """
    Classifies an incoming customer inquiry into specific Primary and Secondary 
    categories tailored for the Art, Craft, and Crochet business model.
    Outputs strictly a Python list of objects with no conversational fluff.
    """
    delimiter = "####"
    
    system_message_content = f"""
You will be provided with a customer service conversation.  
The most recent user query will be delimited with {delimiter} characters.  

### **Output Format:**
Output a **Python list containing a single object**, following this format exactly:  
[
    {{"primary": "<Primary Category>", "secondary": "<Secondary Category>"}}
]

### **Allowed Classifications:**

**Fine Art (Sales & Commissions):**
- Finished painting purchase
- Custom canvas commission
- Art portfolio inquiry

**Custom Crochet Orders:**
- Custom toys & anime Amigurumi
- Bags, purses, & accessories
- Baby clothing & newborn apparel
- Pet sweaters & custom items

**Crochet Academy (Classes):**
- Class schedule & location
- Pricing & session costs
- Material requirements & registration
- Skill level or age groups

**General Inquiry & Support:**
- Contact details (Email/WhatsApp)
- Feedback or complaints
- Speak to a human

Only output the list of objects **without any extra text, spaces, explanations, or markdown blocks.**
"""

    # Pack into structural list complying with Gemini turn rules
    messages = [  
        {'role': 'system', 'content': system_message_content},   
        {
            'role': 'user',  
            'content': f"Customer Message:\n{delimiter}{user_msg}{delimiter}" 
        }  
    ] 
    
    # Run with temperature 0 for strict classification consistency
    response = get_completion_from_messages(messages, temperature=0.0)
    return response



def resolve_handwritten_faq(user_query):
    """
    Uses an isolated zero-temperature LLM classification pass to map 
    the customer's query to the precise database entry.
    """
    faq_matrix = get_handwritten_faq_data()
    
    # Formulate a safe mapping schema text string
    schema_map = ""
    for key, data in faq_matrix.items():
        schema_map += f"- Key: '{key}' | Intent focus: {data['intent_description']}\n"

    system_prompt = f"""
You are an internal business routing engine. Analyze the customer inquiry and match it to the most relevant Key from our knowledge base schema below.

### **Knowledge Base Schema:**
{schema_map}

### **Output Format:**
Return ONLY the exact single-quoted string name of the matched key (e.g., 'offline_vs_online'). If the query does 



not match any specific FAQ topic listed above, return 'NONE'.^
Do not output any markdown formatting, punctuation, or extra sentences.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Customer Inquiry: {user_query}"}
    ]
    
    try:
        # Run standard wrapper pass with zero temperature for absolute routing accuracy
        matched_key = get_completion_from_messages(messages, temperature=0.0).strip().replace("'", "").replace('"', "")
        if matched_key in faq_matrix:
            return faq_matrix[matched_key]["answer"]
        
    except:
        pass
    return None

def get_handwritten_faq_data():
    """
    Returns the complete 20-item QA dataset from the handwritten records,
    fully optimized with a warm, polite, and welcoming boutique tone.
    """
    return {
        "offline_vs_online": {
            "intent_description": "Inquiries about physical/offline vs virtual/online classes.",
            "answer": "Yes, we absolutely provide offline, in-person classes! We meet every Saturday morning from 10:00 AM to 11:00 AM at the Crossroad Library (Balbinova, Prague-2). Please note that we do not offer online classes at this time, as we believe learning crochet is best experienced with hands-on, face-to-face guidance. We would love to have you join us at our physical workshop table!"
        },
        "who_can_join": {
            "intent_description": "Who can join the classes and age groups.",
            "answer": "Thank you so much for asking! Our crochet classes are completely open to everyone—from absolute beginners to intermediate crafters looking to refine their skills. Any and all age groups are warmly welcome, including both children and adults!"
        },
        "experience_requirements": {
            "intent_description": "Whether previous crochet experience or knowledge is required.",
            "answer": "Please don't worry at all! Previous crochet experience is not necessary. Our sessions are specifically designed to be perfectly suitable for complete beginners, and we will guide you step-by-step from the very start."
        },
        "class_curriculum": {
            "intent_description": "What tools, stitches, or projects are taught in the lessons.",
            "answer": "In these classes, you will enjoy a full, supportive progression starting from basic foundational stitches all the way to executing advanced, custom projects of your choosing!"
        },
        "logistics_schedule": {
            "intent_description": "When and what time the classes start, finish, or are held.",
            "answer": "We would love to have you join us! Our crochet classes are held every single Saturday morning from 10:00 AM to 11:00 AM."
        },
        "location_details": {
            "intent_description": "Where the classes are physically located.",
            "answer": "Our wonderful sessions are held in a cozy setting at the Crossroad Library, located at Balbinova, Prague-2. It is a fantastic environment for crafting together!"
        },
        "pricing_fees": {
            "intent_description": "Cost per class session or currency prices.",
            "answer": "The investment for each structural class session is exactly 250 CZK, which includes personalized, hands-on guidance throughout the hour."
        },
        "material_requirements": {
            "intent_description": "Whether materials are provided or if students bring their own.",
            "answer": "To make your creation uniquely yours, we kindly ask that you bring along your own personal crochet materials—including your favorite choice of yarn and matching hooks—to work with during the session!"
        },
        "registration_policy": {
            "intent_description": "Whether pre-booking or pre-registration is needed before showing up.",
            "answer": "Yes, please! Pre-registration is required before attending a class session. This helps us ensure that we save a dedicated, comfortable workspace just for you."
        },
        "attendance_flexibility": {
            "intent_description": "Joining just a single class versus regular sequential attendance.",
            "answer": "We offer total flexibility to match your schedule! You can absolutely join us for just a single standalone class to master a specific technique, or choose to attend regularly to build your skills."
        },
 

        "custom_orders_and_commissions": {
            # ✅ FIXED: Expanded intent description to explicitly catch contact, email, and whatsapp questions
            "intent_description": "General custom orders, ordering process queries, contact information, how to reach out, email address, or phone number inquiries.",
            "answer": "I would be absolutely delighted to bring your ideas to life! I accept customized crochet orders tailored exactly to your personal style and preferences. You can easily place an order or join a class by writing to me at christi.gladis@gmail.com or via WhatsApp at +420 776756594."
        },

        "specific_product_items": {
            "intent_description": "Queries about pet sweaters, customized bags, purses, or custom anime amigurumi characters.",
            "answer": "Yes, I handcraft a wide variety of custom pieces with love and care! I make cozy, tailored sweaters for pets, durable customized bags and purses with protective internal linings, and highly detailed custom anime characters. Feel free to share your design ideas or reference photos with me!"
        },
        "painting_classes_restriction": {
    "intent_description": "Inquiries asking about taking painting classes, canvas workshops, or drawing lessons.",
    "answer": "Thank you so much for reaching out to us! Please note that we specialize exclusively in fiber arts and only offer training classes for crochet making. We do not host any painting classes or drawing workshops at our academy. However, if you are looking to learn a beautiful new craft, we would be absolutely delighted to welcome you to our hands-on crochet workshops held every single Saturday morning from 10:00 AM to 11:00 AM at the Crossroad Library (Balbinova, Prague-2) for 250 CZK. They are completely beginner-friendly! Alternatively, if you are looking for paintings, I work strictly on a retail purchase or custom commission basis. As a professional figurative and fine artist, I create custom portraits, illustrative art, perspective art, landscapes, animal portraits, and abstract paintings. I work with high-quality mediums including oil paints, watercolors, graphite pencils, and colored pencils to bring your vision to life. Would you like me to help you reserve a workspace for our next crochet class, or would you like to discuss commissioning a custom fine art piece?"
       },

        "online_classes_policy": {
            "intent_description": "Inquiries about virtual lessons, digital courses, Zoom calls, internet sessions, or online classes. ",
            "answer": "Thank you so much for your interest! Currently, we do not offer any online classes, as we prioritize a hands-on, face-to-face workshop environment to help you perfect your stitches in real time. We would absolutely love to have you join us at our in-person sessions held every Saturday morning at the Crossroad Library instead!"
        }
    }

