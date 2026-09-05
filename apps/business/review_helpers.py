def get_category_config(category: str) -> dict:
    """
    Returns category-specific enjoyment options, question 2 label, and question 2 placeholder
    based on the business category.
    """
    cat = (category or "").lower().strip()

    if any(k in cat for k in ["restaurant", "cafe", "coffee", "bakery", "bar", "lounge", "food"]):
        return {
            "enjoyment_options": ["Food", "Service", "Staff", "Ambience", "Portion size", "Value for money"],
            "order_label": "What did you order?",
            "order_placeholder": "e.g., Chicken biryani, iced coffee & brownie",
        }
    elif any(k in cat for k in ["salon", "spa", "beauty", "cosmetics"]):
        return {
            "enjoyment_options": ["Service", "Staff", "Quality", "Ambience", "Results", "Value for money"],
            "order_label": "What service did you take?",
            "order_placeholder": "e.g., Haircut, beard styling & facial",
        }
    elif any(k in cat for k in ["gym", "fitness"]):
        return {
            "enjoyment_options": ["Trainers", "Equipment", "Cleanliness", "Facilities", "Staff", "Overall experience"],
            "order_label": "What did you use / train for?",
            "order_placeholder": "e.g., Personal training session & cardio workout",
        }
    elif any(k in cat for k in ["healthcare", "clinic", "dental"]):
        return {
            "enjoyment_options": ["Doctor & Staff", "Care & Treatment", "Cleanliness", "Comfort", "Explanation", "Value for money"],
            "order_label": "What treatment or consultation did you take?",
            "order_placeholder": "e.g., Teeth cleaning & routine checkup",
        }
    elif any(k in cat for k in ["hotel", "resort", "travel", "tourism"]):
        return {
            "enjoyment_options": ["Room Quality", "Service", "Staff", "Location", "Cleanliness", "Value for money"],
            "order_label": "What type of room or package did you book?",
            "order_placeholder": "e.g., Deluxe suite stay & breakfast package",
        }
    elif any(k in cat for k in ["retail", "clothing", "fashion", "electronics"]):
        return {
            "enjoyment_options": ["Product Quality", "Selection", "Staff Help", "Pricing", "Checkout Speed", "Ambience"],
            "order_label": "What did you buy?",
            "order_placeholder": "e.g., Wireless headphones & jacket",
        }
    else:
        # Default fallback for Professional Services, Home Services, Other
        return {
            "enjoyment_options": ["Service", "Staff", "Quality", "Ambience", "Speed & Efficiency", "Value for money"],
            "order_label": "What service or product did you use?",
            "order_placeholder": "e.g., Consultation & home service",
        }
