from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import qrcode
import os

app = Flask(__name__)

FOR_FOLDERS = ['static/qrcodes', 'static/images', 'static/audio']
for folder in FOR_FOLDERS:
    os.makedirs(folder, exist_ok=True)

def get_medicine_data(med_name):
    """Helper to find medicine regardless of case."""
    df = pd.read_csv('dataset.csv')
    # Case-insensitive search
    match = df[df['name'].str.lower() == med_name.lower()]
    return match.iloc[0].to_dict() if not match.empty else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.form.get('medicine_name', '').strip()
    
    med_data = get_medicine_data(user_input)
    
    if med_data:
        
        med_id = med_data['name'].lower().replace(" ", "_")
        target_url = f"{request.host_url}details/{med_id}"
        
        
        qr = qrcode.make(target_url)
        qr_path = f"static/qrcodes/{med_id}.png"
        qr.save(qr_path)
        
        return render_template('qr_display.html', qr_path=qr_path, med_name=med_data['name'])
    
    return "Medicine not found in dataset!", 404

@app.route('/details/<med_id>')
def details(med_id):
   
    search_name = med_id.replace("_", " ")
    med_data = get_medicine_data(search_name)
    
    if med_data:
        
        medicine_obj = {
            "name": med_data['name'],
            "when_to_use": med_data['when_to_use'],
            "how_to_use": med_data['how_to_use'],
            "age_limit": med_data['age_limit'],
            "side_effects": med_data['side_effects'],
            "image": f"images/{med_id}.jpg" 
        }
       
        audio_filename = f"audio/{med_id}.mp3"
        
        return render_template('details.html', medicine=medicine_obj, audio_file=audio_filename)
    
    return "Details not found", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
