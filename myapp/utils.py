import requests
from django.conf import settings
import json
import os

# Fallback data - will be used when API is unavailable
NUTRITION_FALLBACK_FILE = os.path.join(os.path.dirname(__file__), 'data/nutrition_fallback.json')

def get_nutrition_fallback_data():
    """Load fallback nutrition data from JSON file"""
    try:
        with open(NUTRITION_FALLBACK_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return basic default data if file not found or invalid
        return {
            "breeds": {
                "Holstein": {
                    "calf": {
                        "dry_matter": "2-3% of body weight",
                        "protein": "18-20%",
                        "energy": "3.0 Mcal/kg",
                        "calcium": "0.7%",
                        "phosphorus": "0.45%"
                    },
                    "heifer": {
                        "dry_matter": "2.2% of body weight",
                        "protein": "14-16%",
                        "energy": "2.6 Mcal/kg",
                        "calcium": "0.5%",
                        "phosphorus": "0.3%"
                    },
                    "dry": {
                        "dry_matter": "1.8% of body weight",
                        "protein": "12-14%",
                        "energy": "2.4 Mcal/kg",
                        "calcium": "0.45%",
                        "phosphorus": "0.3%"
                    },
                    "early_lactation": {
                        "dry_matter": "3.5-4% of body weight",
                        "protein": "17-19%",
                        "energy": "2.8 Mcal/kg",
                        "calcium": "0.8%",
                        "phosphorus": "0.45%"
                    }
                },
                "Jersey": {
                    "calf": {
                        "dry_matter": "2-3% of body weight",
                        "protein": "18-20%",
                        "energy": "3.0 Mcal/kg",
                        "calcium": "0.7%",
                        "phosphorus": "0.45%"
                    },
                    "heifer": {
                        "dry_matter": "2.2% of body weight",
                        "protein": "14-16%",
                        "energy": "2.6 Mcal/kg",
                        "calcium": "0.5%",
                        "phosphorus": "0.3%"
                    },
                    "dry": {
                        "dry_matter": "1.7% of body weight",
                        "protein": "12-14%",
                        "energy": "2.4 Mcal/kg",
                        "calcium": "0.45%",
                        "phosphorus": "0.3%"
                    },
                    "early_lactation": {
                        "dry_matter": "3.7-4.2% of body weight",
                        "protein": "17-19%",
                        "energy": "2.8 Mcal/kg",
                        "calcium": "0.8%",
                        "phosphorus": "0.45%"
                    }
                },
                "default": {
                    "calf": {
                        "dry_matter": "2-3% of body weight",
                        "protein": "18%",
                        "energy": "2.8 Mcal/kg",
                        "calcium": "0.7%",
                        "phosphorus": "0.4%"
                    },
                    "heifer": {
                        "dry_matter": "2.2% of body weight",
                        "protein": "14%",
                        "energy": "2.5 Mcal/kg",
                        "calcium": "0.5%",
                        "phosphorus": "0.3%"
                    },
                    "dry": {
                        "dry_matter": "1.8% of body weight",
                        "protein": "12%",
                        "energy": "2.3 Mcal/kg",
                        "calcium": "0.45%",
                        "phosphorus": "0.3%"
                    },
                    "early_lactation": {
                        "dry_matter": "3.5% of body weight",
                        "protein": "17%",
                        "energy": "2.7 Mcal/kg",
                        "calcium": "0.75%",
                        "phosphorus": "0.4%"
                    }
                }
            },
            "feed_recommendations": {
                "calf": [
                    {"name": "Calf starter feed", "amount_formula": "weight * 0.01", "purpose": "Growth and development"},
                    {"name": "High-quality hay", "amount_formula": "weight * 0.005", "purpose": "Rumen development"},
                    {"name": "Milk replacer", "amount_formula": "weight * 0.015", "purpose": "Main nutrition source"}
                ],
                "heifer": [
                    {"name": "Quality grass hay", "amount_formula": "weight * 0.015", "purpose": "Fiber source"},
                    {"name": "Heifer grain mix", "amount_formula": "weight * 0.01", "purpose": "Energy and protein"},
                    {"name": "Mineral supplement", "amount_formula": "0.1", "purpose": "Mineral requirements"}
                ],
                "dry": [
                    {"name": "Grass hay", "amount_formula": "weight * 0.015", "purpose": "Bulk feed"},
                    {"name": "Dry cow mineral mix", "amount_formula": "0.15", "purpose": "Minerals and vitamins"},
                    {"name": "Limited grain", "amount_formula": "weight * 0.003", "purpose": "Energy supplement"}
                ],
                "early_lactation": [
                    {"name": "High-quality silage", "amount_formula": "weight * 0.02", "purpose": "Bulk and energy"},
                    {"name": "Dairy concentrate", "amount_formula": "weight * 0.01 + milk_production * 0.4", "purpose": "Production support"},
                    {"name": "Protein supplement", "amount_formula": "milk_production * 0.1", "purpose": "Protein for milk production"},
                    {"name": "Mineral mix", "amount_formula": "0.15", "purpose": "Minerals and vitamins"}
                ]
            }
        }

def fetch_nutrition_from_api(cattle, production_stage):
    """
    Function to fetch nutritional data from the FarmSense API
    Falls back to local data if API is unavailable
    
    Params:
        cattle: Your Cattle model instance
        production_stage: CattleProductionStage instance for the cattle
    """
    try:
        api_url = settings.FARMSENSE_API_URL
        headers = {
            'Authorization': f'Bearer {settings.FARMSENSE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'breed': cattle.breed,
            'stage': production_stage.stage,
            'weight': float(cattle.weight),
            'age_months': cattle.age_months,
            'milk_production': float(production_stage.milk_production) if production_stage.milk_production else 0
        }
        
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API error: {response.status_code} - {response.text}")
            return get_fallback_nutrition_data(cattle, production_stage)
    except Exception as e:
        print(f"API error: {e}")
        return get_fallback_nutrition_data(cattle, production_stage)

def get_fallback_nutrition_data(cattle, production_stage):
    """
    Get fallback nutrition data when API is unavailable
    """
    data = get_nutrition_fallback_data()
    breed_name = cattle.breed
    stage = production_stage.stage
    
    # If breed not found in data, use default
    if breed_name not in data['breeds']:
        breed_name = 'default'
    
    # Map stages to simplified categories if needed
    stage_mapping = {
        'early_lactation': 'early_lactation',
        'mid_lactation': 'early_lactation',
        'late_lactation': 'early_lactation'
    }
    
    # Get the mapped stage or use the original stage
    mapped_stage = stage_mapping.get(stage, stage)
    
    # If specific stage not found, use a default stage
    if mapped_stage not in data['breeds'][breed_name]:
        if 'lactation' in mapped_stage:
            mapped_stage = 'early_lactation'
        else:
            mapped_stage = list(data['breeds'][breed_name].keys())[0]
    
    nutrition_req = data['breeds'][breed_name][mapped_stage]
    
    # Calculate feed recommendations
    feed_recommendations = []
    weight = float(cattle.weight)
    milk_production = float(production_stage.milk_production) if production_stage.milk_production else 0
    
    # Get stage recommendations from data
    stage_for_feed = 'early_lactation' if 'lactation' in stage else stage
    if stage_for_feed not in data['feed_recommendations']:
        stage_for_feed = list(data['feed_recommendations'].keys())[0]
    
    for feed in data['feed_recommendations'][stage_for_feed]:
        # Safely evaluate the formula with limited variables
        amount_formula = feed['amount_formula']
        amount = eval(amount_formula, {"__builtins__": {}}, {"weight": weight, "milk_production": milk_production})
        
        feed_recommendations.append({
            'name': feed['name'],
            'amount': round(amount, 2),
            'purpose': feed['purpose']
        })
    
    return {
        'requirements': nutrition_req,
        'feed_recommendations': feed_recommendations
    }

def get_feeding_tips(cattle, production_stage):
    """
    Get breed-specific feeding tips
    """
    tips = {
        'general': [
            "Ensure clean, fresh water is always available",
            "Make feed changes gradually over 1-2 weeks",
            "Monitor body condition regularly and adjust feeding as needed"
        ],
        'stage': {}
    }
    
    # Stage-specific tips
    tips['stage']['calf'] = [
        "Ensure adequate colostrum in the first 24 hours of life",
        "Provide milk or milk replacer at 10-12% of body weight daily",
        "Start offering calf starter from 3-4 days of age",
        "Introduce hay gradually from 2 weeks of age",
        "Wean when consistently consuming 1kg of starter daily"
    ]
    
    tips['stage']['heifer'] = [
        "Focus on steady growth without excess fattening",
        "Provide quality forage as the main component of the diet",
        "Supplement with minerals appropriate for growth",
        "Monitor growth rates to ensure proper development"
    ]
    
    tips['stage']['dry'] = [
        "Avoid overfeeding energy during the dry period",
        "Ensure adequate mineral intake, especially calcium and magnesium",
        "Provide sufficient fiber to maintain rumen function",
        "Prepare for transition to lactation with appropriate diet changes"
    ]
    
    tips['stage']['early_lactation'] = [
        "Feed multiple times daily to maximize intake and production",
        "Provide highly digestible fiber sources",
        "Balance energy and protein for milk production",
        "Monitor for signs of metabolic issues in early lactation"
    ]
    
    tips['stage']['mid_lactation'] = [
        "Adjust rations based on production and body condition",
        "Maintain consistent feeding schedule and ration composition",
        "Ensure adequate fiber to maintain rumen health"
    ]
    
    tips['stage']['late_lactation'] = [
        "Begin preparing body condition for dry period",
        "Adjust energy levels based on production and body condition",
        "Maintain adequate, but not excessive, protein levels"
    ]
    
    # Get stage-specific tips or use general lactation tips
    stage = production_stage.stage
    if stage not in tips['stage']:
        if 'lactation' in stage:
            stage = 'early_lactation'
        else:
            stage = 'general'
    
    return {
        'general': tips['general'],
        'specific': tips['stage'].get(stage, [])
    }


import os
from fpdf import FPDF
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Cattle  # Import the model

def generate_cattle_report(tagno):
    # Fetch the latest cattle data
    cattle = get_object_or_404(Cattle, tagno=tagno)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Report for Cattle Tag No: {cattle.tagno}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Breed: {cattle.breed}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Gender: {cattle.gender}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Date of Birth: {cattle.dob}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Weight: {cattle.weight}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Color: {cattle.color}", ln=True, align='L')

    # Ensure reports directory exists
    reports_dir = os.path.join(settings.BASE_DIR, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    filepath = os.path.join(reports_dir, f'cattle_{cattle.tagno}.pdf')
    pdf.output(filepath)
    return filepath