from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load models
model_disease = load_model('plant_disease_cnn.h5')
model_species = load_model('fruit_species_cnn.h5')
model_grading = load_model('fruit_grading_cnn.h5')
model_ripeness = load_model('fruit_ripeness_cnn.h5')

# Manually define class indices (update these based on your training dataset)
class_indices_disease = {
    0: "Cordana (कोरडाणा)",
    1: "Healthy (निरोगी)",
    2: "Pestalotiopsis (पेस्टालोटिया सॅपोटी)",
    3: "Sigatoka (सिगाटोका)",
}
class_indices_species = {
    0: "Anwar Ratool (अन्वर रातूल)",
    1: "Chaunsa-Black (काळा चौंसा)",
    2: "Chaunsa-Summer Bahisht (उन्हाळी बहिष्त चौंसा)",
    3: "Chaunsa-White (पांढरा चौंसा)",
    4: "Dusehri (दशेरी)",
    5: "Fazli (फाजली)",
    6: "Langra (लंगडा)",
    7: "Sindhri (सिंधरी)"
}

class_indices_ripeness = {
    0: "Unripe (न पिकलेले)",
    1: "Early Ripe (लवकर पिकलेले)",
    2: "Partially Ripe (अर्धवट पिकलेले)",
    3: "Ripe (पिकलेले)",
}

class_indices_grading = {
    0: "Class 1 (वर्ग १)",
    1: "Class 2 (वर्ग 2)",
    2: "Extra Class (अतिरिक्त वर्ग)",
}

# Additional data
disease_info = {
    "Cordana (कोरडाणा)": {
        "fertilizer": "Mancozeb (मॅन्कोझेब)",
        "alert_one" : "Your plant is showing signs of disease. Adjust your fertilization strategy to support recovery:",
        "description" : [
            "Excessive nitrogen encourages rapid growth, which can make the plant more vulnerable to disease. Use balanced fertilizers with lower nitrogen content.",
            "Avoid applying fertilizers directly on leaves, as it can exacerbate fungal growth. Instead, focus on soil-based feeding.",
            "Adding well-composted organic matter can improve soil health and promote the plant’s natural resistance to diseases."
            ],
        "description_marathi" : [
            "अत्याधिक नायट्रोजन जलद वाढीस प्रोत्साहन देते, ज्यामुळे झाडाला रोग होण्याची अधिक शक्यता असते. कमी नायट्रोजन सामग्रीसह संतुलित खतांचा वापर करा.",
            "खते थेट पानांवर टाकणे टाळा, कारण यामुळे बुरशीची वाढ वाढू शकते. त्याऐवजी, माती-आधारित आहारावर लक्ष केंद्रित करा.",
            "चांगले कंपोस्ट केलेले सेंद्रिय पदार्थ जोडल्याने मातीचे आरोग्य सुधारू शकते आणि रोगांवरील वनस्पतीच्या नैसर्गिक प्रतिकारशक्तीला चालना मिळते."
            ],
        "alert_two" : "To manage the disease and prevent its spread, take the following actions:",
        "preventive_measures": [
            "Carefully prune any affected leaves and dispose of them to reduce fungal spores in the environment.",
            "Use a fungicide specifically labeled for banana plants or Cordana leaf spot disease. Copper-based fungicides or systemic fungicides may be effective.",
            "Inspect the plant every few days for new signs of infection and continue to prune infected leaves."
        ],
        "preventive_measures_marathi": [
           "वातावरणातील बुरशीजन्य बीजाणू कमी करण्यासाठी कोणत्याही प्रभावित पानांची काळजीपूर्वक छाटणी करा आणि त्यांची विल्हेवाट लावा.",
            "केळीच्या झाडांसाठी किंवा कोरडानाच्या पानावरील डाग रोगासाठी विशेषत: लेबल केलेले बुरशीनाशक वापरा. ​​तांबे-आधारित बुरशीनाशके किंवा पद्धतशीर बुरशीनाशके प्रभावी असू शकतात.",
            "संक्रमणाच्या नवीन लक्षणांसाठी दर काही दिवसांनी रोपाची तपासणी करा आणि संक्रमित पानांची छाटणी सुरू ठेवा."
        ]
    },

    "Healthy (निरोगी)": {
        "fertilizer": "No Fertilizers (खते नाहीत)",
        "alert_one" : "Your plant is thriving! To maintain its health, follow these fertilization tips:",
        "description" : [
            "Apply a balanced fertilizer, such as NPK 10-10-10, every 4–6 weeks during the growing season.",
            "Incorporate organic compost around the base of the plant to improve soil nutrients and retain moisture.",
            "Avoid over-fertilizing, as it can lead to salt buildup and harm the roots."
            ],
        "description_marathi" : [
            "वाढत्या हंगामात दर 4-6 आठवड्यांनी NPK 10-10-10 सारखे संतुलित खत वापरा.",
            "जमिनीची पोषक द्रव्ये सुधारण्यासाठी आणि ओलावा टिकवून ठेवण्यासाठी वनस्पतीच्या पायाभोवती सेंद्रिय कंपोस्टचा समावेश करा.",
            "जास्त प्रमाणात खत घालणे टाळा, कारण यामुळे मीठ तयार होऊ शकते आणि मुळांना हानी पोहोचू शकते."
            ],
        "alert_two" : "Keep your plant healthy with these preventive measures:",
        "preventive_measures": [
            "Inspect leaves and stems weekly for any signs of pests, discoloration, or unusual spots.",
            "Water in the morning to prevent fungal infections from excess moisture overnight.",
            "Mulch around the base to regulate soil temperature and prevent weeds."
        ],
        "preventive_measures_marathi": [
           "कीड, विरंगुळा किंवा असामान्य डागांच्या कोणत्याही लक्षणांसाठी पाने आणि देठांची साप्ताहिक तपासणी करा.",
            "रात्रभर जास्त आर्द्रतेमुळे बुरशीजन्य संसर्ग टाळण्यासाठी सकाळी पाणी.",
            "मातीचे तापमान नियंत्रित करण्यासाठी आणि तणांना प्रतिबंध करण्यासाठी तळाभोवती पालापाचोळा घाला."
        ]
    },

    "Pestalotiopsis (पेस्टालोटिया सॅपोटी)": {
        "fertilizer": "Carbendazim (कार्बेन्डाझिम)",
        "alert_one" : "Your plant is showing signs of disease. Adjust your fertilization strategy to support recovery:",
        "description" : [
            "High nitrogen levels can stimulate excessive growth, which might weaken the plant’s defenses. Use a balanced fertilizer with moderate nitrogen content.",
            "Use a fungicide specifically labeled for banana plants or Cordana leaf spot disease. Copper-based fungicides or systemic fungicides may be effective.",
            "Avoid overhead watering, which can spread spores onto healthy leaves. Instead, water at the base of the plant."
            ],
        "description_marathi" : [
            "उच्च नायट्रोजन पातळी जास्त वाढीस उत्तेजित करू शकते, ज्यामुळे वनस्पतीचे संरक्षण कमकुवत होऊ शकते. मध्यम नायट्रोजन सामग्रीसह संतुलित खत वापरा.",
            "केळीच्या झाडांसाठी किंवा कोरडानाच्या पानावरील डाग रोगासाठी विशेषत: लेबल केलेले बुरशीनाशक वापरा. ​​तांबे-आधारित बुरशीनाशके किंवा पद्धतशीर बुरशीनाशके प्रभावी असू शकतात.",
            "ओव्हरहेड पाणी देणे टाळा, ज्यामुळे बीजाणू निरोगी पानांवर पसरू शकतात. त्याऐवजी, झाडाच्या पायथ्याशी पाणी द्या."
            ],
        "alert_two" : "To manage the disease and prevent its spread, take the following actions:",
        "preventive_measures": [
            "Remove and discard any leaves showing signs of the disease, including blackened spots or lesions, to reduce fungal spread.",
            "Use a fungicide that targets Pestalotiopsis, such as a copper-based fungicide or one containing thiophanate-methyl or propiconazole. Apply it as directed to both the leaves and soil.",
            "Ensure that your banana plants are spaced adequately to allow for proper airflow, reducing humidity around the plant and helping to prevent fungal growth."
        ],
        "preventive_measures_marathi": [
            "बुरशीचा प्रादुर्भाव कमी करण्यासाठी, काळे डाग किंवा जखमांसह रोगाची लक्षणे दर्शविणारी कोणतीही पाने काढा आणि टाकून द्या.",
            "पेस्टालोटिओप्सिसला लक्ष्य करणारे बुरशीनाशक वापरा, जसे की तांबे-आधारित बुरशीनाशक किंवा थिओफेनेट-मिथाइल किंवा प्रोपिकोनाझोल असलेले. ते पाने आणि माती दोन्हीवर निर्देशानुसार लावा.",
            "तुमच्या केळीची झाडे योग्य प्रमाणात हवेच्या प्रवाहासाठी, झाडाभोवतीची आर्द्रता कमी करण्यासाठी आणि बुरशीजन्य वाढ रोखण्यास मदत करण्यासाठी पुरेशा अंतरावर असल्याची खात्री करा."
        ]
    },
    
    "Sigatoka (सिगाटोका)": {
        "fertilizer": "Kocide/Copper Hydroxide (कोसाइड/कॉपर हायड्रॉक्साइड)",
        "alert_one" : "Your plant is showing signs of disease. Adjust your fertilization strategy to support recovery:",
        "description" : [
            "Apply a balanced fertilizer with moderate nitrogen levels (e.g., NPK 15-15-15) to help your plant recover. High nitrogen levels can encourage fungal growth, so use fertilizers with a well-rounded nutrient profile.",
            "Potassium can help strengthen the plant’s cell walls and improve its ability to resist diseases. Consider adding a fertilizer with higher potassium content.",
            "Do not apply fertilizers directly on leaves as moisture from the fertilizer can encourage fungal spores to spread."
            ],
        "description_marathi" : [
            "तुमच्या झाडाला सावरण्यासाठी मध्यम नायट्रोजन पातळीसह संतुलित खत वापरा (उदा. NPK 15-15-15)",
            "पोटॅशियम वनस्पतीच्या पेशींच्या भिंती मजबूत करण्यास आणि रोगांचा प्रतिकार करण्याची क्षमता सुधारण्यास मदत करू शकते. जास्त पोटॅशियम सामग्रीसह खत घालण्याचा विचार करा.",
            "खते थेट पानांवर लावू नका कारण खतातील ओलावा बुरशीजन्य बीजाणूंचा प्रसार करण्यास प्रोत्साहित करू शकतो."
            ],
        "alert_two" : "To manage the disease and prevent its spread, take the following actions:",
        "preventive_measures": [
            "Prune and dispose of leaves with visible black lesions to limit the spread of the fungus. Always sanitize pruning tools to prevent transmission.",
            "Use fungicides labeled for Black Sigatoka, such as copper-based fungicides or systemic fungicides containing azoxystrobin or propiconazole. Apply these to both the leaves and soil as recommended.",
            "Space plants adequately to ensure good airflow, which helps to dry out moisture on leaves and reduce fungal growth."
        ],
        "preventive_measures_marathi": [
           "बुरशीचा प्रसार मर्यादित करण्यासाठी दृश्यमान काळ्या जखम असलेल्या पानांची छाटणी करा आणि विल्हेवाट लावा. प्रसार रोखण्यासाठी नेहमी छाटणीची साधने स्वच्छ करा.",
            "ब्लॅक सिगाटोकासाठी लेबल केलेली बुरशीनाशके वापरा, जसे की तांबे-आधारित बुरशीनाशके किंवा अझॉक्सीस्ट्रोबिन किंवा प्रोपिकोनाझोल असलेली सिस्टीमिक बुरशीनाशके. शिफारस केल्यानुसार ते पाने आणि माती दोन्हीवर लावा.",
            "स्पेस रोपे पुरेशा प्रमाणात हवेचा प्रवाह सुनिश्चित करतात, ज्यामुळे पानावरील ओलावा सुकण्यास आणि बुरशीची वाढ कमी होण्यास मदत होते."
        ]
    },

}

fruit_region_info = {
    "Anwar Ratool (अन्वर रातूल)": {"region": "Himachal Pradesh ", "state": "Himachal Pradesh"},
    "Chaunsa-Black (काळा चौंसा)": {"region": "Tamil Nadu", "state": "Tamil Nadu"},
    "Chaunsa-Summer Bahisht (उन्हाळी बहिष्त चौंसा)": {"region": "Jammu & Kashmir", "state": "Jammu & Kashmir"},
    "Chaunsa-White (पांढरा चौंसा)": {"region": "Jammu & Kashmir", "state": "Jammu & Kashmir"},
    "Dusehri (दशेरी)": {"region": "Jammu & Kashmir", "state": "Jammu & Kashmir"},
    "Fazli (फाजली)": {"region": "Jammu & Kashmir", "state": "Jammu & Kashmir"},
    "Langra (लंगडा)": {"region": "Jammu & Kashmir", "state": "Jammu & Kashmir"},
    "Sindhri (सिंधरी)": {"region": "Jammu & Kashmir", "state": "Jammu & Kashmir"}

}

# Set image size
img_size = (128, 128)

# Disease prediction
def predict_disease(image_path):
    img = image.load_img(image_path, target_size=img_size)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    disease_pred = model_disease.predict(img_array)
    disease_idx = np.argmax(disease_pred)
    disease_name = class_indices_disease[disease_idx]  # Map index to class name
    disease_confidence = disease_pred[0][disease_idx] * 100
    return disease_name, disease_confidence

# Fruit prediction (species, ripeness, grading)
def predict_fruit_details(image_path):
    img = image.load_img(image_path, target_size=img_size)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    species_pred = model_species.predict(img_array)
    species_idx = np.argmax(species_pred)
    species_name = class_indices_species[species_idx]  # Map index to class name
    
    ripeness_pred = model_ripeness.predict(img_array)
    ripeness_idx = np.argmax(ripeness_pred)
    ripeness = class_indices_ripeness[ripeness_idx]
    
    grading_pred = model_grading.predict(img_array)
    grading_idx = np.argmax(grading_pred)
    grading = class_indices_grading[grading_idx]

    return species_name, ripeness, grading

@app.route('/predict_disease', methods=['POST'])
def predict_plant_disease():
    file = request.files['image']
    image_path = os.path.join('uploads', file.filename)
    file.save(image_path)

    disease_name, disease_confidence = predict_disease(image_path)

    # Retrieve additional information for the disease
    disease_details = disease_info.get(disease_name, {})
    fertilizer = disease_details.get("fertilizer", "No specific fertilizer recommended.")
    alert_one = disease_details.get("alert_one", "No specific fertilizer recommended.")
    description = disease_details.get("description", "No specific fertilizer recommended.")
    description_marathi = disease_details.get("description_marathi", "No specific fertilizer recommended.")
    fertilizer = disease_details.get("fertilizer", "No specific fertilizer recommended.")
    fertilizer = disease_details.get("fertilizer", "No specific fertilizer recommended.")
    alert_two = disease_details.get("alert_two", "No specific fertilizer recommended.")
    preventive_measures = disease_details.get("preventive_measures", ["No preventive measures available."])
    preventive_measures_marathi = disease_details.get("preventive_measures_marathi", ["No preventive measures available."])
    return jsonify({
        "disease_name": disease_name,
        "confidence": round(disease_confidence, 2),
        "fertilizer": fertilizer,
        "alert_one": alert_one,
        "description": description,
        "description_marathi": description_marathi,
        "alert_two": alert_two,
        "preventive_measures": preventive_measures,
        "preventive_measures_marathi": preventive_measures_marathi,
    })

@app.route('/predict_fruit_details', methods=['POST'])
def predict_fruit_details_route():
    file = request.files['image']
    image_path = os.path.join('uploads', file.filename)
    file.save(image_path)

    species_name, ripeness, grading = predict_fruit_details(image_path)

    # Retrieve region and state information
    fruit_region = fruit_region_info.get(species_name, {"region": "Unknown", "state": "Unknown"})

    return jsonify({
        "species_name": species_name,
        "ripeness": ripeness,
        "grading": grading,
        "region": fruit_region["region"],
        "state": fruit_region["state"]
    })

if __name__ == '__main__':
    app.run(debug=True)
