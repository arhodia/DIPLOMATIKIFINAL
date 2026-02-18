import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import subprocess
import csv
import json
import os
import math
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


@app.post("/api/test")
def test():
    # --- ΒΗΜΑ 1: Λήψη και Αποθήκευση Παραμέτρων (Όπως το είχαμε) ---
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # Helper function για καθαρισμό input
    def clean_param(value, target_type):
        if value is None or str(value).strip() == "":
            return None
        try:
            return target_type(value)
        except (ValueError, TypeError):
            return None

    # Ανάγνωση παραμέτρων
    industry = data.get('industry')
    algorithms = data.get('algorithms')
    if isinstance(algorithms, list):
        algorithms = ",".join(algorithms)
        
    radioOption = data.get('radioOption')
    name = data.get('name')
    neighbor_raw = data.get('neighbor')

    input_k_min = clean_param(data.get('k_min'), int)
    input_k_max = clean_param(data.get('k_max'), int)
    input_seed = clean_param(data.get('seed'), int)
    input_maxIter = clean_param(data.get('maxIter'), int)
    input_sample_frac = clean_param(data.get('sample_frac'), float)
    input_file_size= clean_param(data.get('file_size'), float)

    try:
        neighbor = int(float(neighbor_raw))
    except (TypeError, ValueError):
        neighbor = 5
    neighbor = max(3, min(neighbor, 80))

    # Path που βλέπει το Flask (WSL)
    base_path = "/mnt/c/Users/arhod/Desktop/DIPLOMATIKIFINAL"
    csv_file_path = os.path.join(base_path, "parameter.csv")
    
    # Εγγραφή parameter.csv
    header = ['industry', 'algorithms', 'radioOption', 'name', 'neighbor',
              'k_min', 'k_max', 'seed', 'maxIter', 'sample_frac','file_size']
    row = [industry, algorithms, radioOption, name, neighbor,
           input_k_min, input_k_max, input_seed, input_maxIter, input_sample_frac,input_file_size]

    try:
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(row)
    except Exception as e:
        print(f"ERROR: Could not write csv file: {e}")
        return jsonify({"error": "Failed to write parameter file"}), 500

    # --- ΒΗΜΑ 2: Εκτέλεση Docker ---
    cmd = [
        "docker", "compose",
        "-f", "/mnt/c/Users/arhod/Desktop/arhodia/docker/docker-compose.yml",
        "run", "--rm",
        "spark-client",
        "python3", "/data/backend/algorithms.py"
    ]
    
    try:
        # Περιμένουμε να τελειώσει το script
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR executing docker command: {e}")
        return jsonify({"error": "Docker execution failed"}), 500

    # --- ΒΗΜΑ 3: Ανάγνωση Αποτελεσμάτων (ΔΙΟΡΘΩΜΕΝΟ) ---
    results_dir = os.path.join(base_path, "results")

    # Helper function: Αναδρομικός καθαρισμός NaN -> None
    def clean_nans(obj):
        if isinstance(obj, float) and math.isnan(obj):
            return None
        elif isinstance(obj, dict):
            return {k: clean_nans(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nans(i) for i in obj]
        return obj

    # Helper function για ασφαλές διάβασμα JSON
    def read_json_safe(filename):
        path = os.path.join(results_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return clean_nans(data) # Καθαρίζουμε και εδώ για σιγουριά
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                return {}
        return {}


    def read_csv_safe(filename):
        path = os.path.join(results_dir, filename)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df = df.where(pd.notnull(df), None) # Μετατροπή NaNs σε null για το JSON
                return df.to_dict(orient='records')
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                return []
        return []

    # Διαβάζουμε τα αποτελέσματα
    # Αν ο χρήστης δεν επέλεξε LSH, το read_csv_safe θα επιστρέψει [] γιατί το αρχείο διαγράφηκε στην αρχή
    response_data = {
        "hyperparameters": read_csv_safe("output_hyperparameters.csv"),
        # ΑΛΛΑΓΗ ΕΔΩ: Χρήση read_json_safe και κατάληξης .json
        "top_matches": read_json_safe("output_top_matches.json"), 
        "recommended_matches": read_json_safe("output_recommended.json"),
        "execution_time": read_json_safe("output_time.json"),
        "lsh_brp": read_csv_safe("output_lsh_brp.csv"),
        "lsh_minihash": read_csv_safe("output_lsh_minihash.csv"),
        "visual_data": read_json_safe("output_charts.json")
    }

    return jsonify(clean_nans(response_data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)