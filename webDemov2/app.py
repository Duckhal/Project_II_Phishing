from flask import Flask, request, render_template, redirect, url_for, flash
import joblib
import numpy as np
import requests
from Utils.features import extract_features_from_url
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key' # Cần thiết cho flash messages
model = joblib.load("D:\\Python\\webDemov2\\Model\\xgb_model.pkl")

#API_KEY = '0196d1c6-6b67-7754-bf2d-b25a9f28ab01'
LOG_FILE_PATH = "D:\\Python\\webDemov2\\UserLog\\user_report.csv"

# Hàm phân tích url rút gọn
def unshorten_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; URLExpander/1.0)',
        }
        response = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
        return response.url
    except requests.RequestException:
        return url

@app.route('/', methods=['GET', 'POST'])
def index():
    result_display = None 
    prediction_label = None 
    confidence = None
    url = ""
    real_url = ""
    features_dict = {}

    if request.method == 'POST':
        url = request.form['url'].strip()
        if url:
            try:
                real_url = unshorten_url(url)
                features_dict = extract_features_from_url(real_url)
                feature_array = np.array([list(features_dict.values())])
                prediction = model.predict(feature_array)[0]
                probability = model.predict_proba(feature_array)[0]

                if prediction == 1:
                    result_display = "🔴 Phishing"
                    prediction_label = "Phishing"
                    confidence = round(probability[1] * 100, 2)
                else:
                    result_display = "🟢 Safe"
                    prediction_label = "Safe"
                    confidence = round(probability[0] * 100, 2)
            except Exception as e:
                result_display = f"⚠️ Error: {str(e)}"
                app.logger.error(f"Error processing URL {url}: {e}") # Ghi log lỗi server
        else:
            result_display = "⚠️ Please insert correct URL's format."

    return render_template("index.html",
                           result_display=result_display,
                           prediction_label=prediction_label,
                           url=url,
                           real_url=real_url,
                           features=features_dict,
                           confidence=confidence)

@app.route('/report', methods=['POST'])
def report():
    if request.method == 'POST':
        reported_url = request.form.get('reported_url')
        model_prediction = request.form.get('model_prediction')
        user_label = request.form.get('user_label')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not all([reported_url, model_prediction, user_label]):
            flash('⚠️ Please fill in the report information completely.', 'error')
            return redirect(url_for('index')) 

        try:
            # Ghi vào file CSV
            file_exists = os.path.isfile(LOG_FILE_PATH)
            with open(LOG_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'url', 'model_prediction', 'user_actual_label']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()  # Viết header nếu file mới được tạo

                writer.writerow({
                    'timestamp': timestamp,
                    'url': reported_url,
                    'model_prediction': model_prediction,
                    'user_actual_label': user_label
                })
            flash('✔️ Thank you for sending report!', 'success')
        except Exception as e:
            flash(f'⚠️ Error!: {str(e)}', 'error')
            app.logger.error(f"Error saving report: {e}")

        return redirect(url_for('index'))

    return redirect(url_for('index')) 

if __name__ == '__main__':
    app.run(debug=True)