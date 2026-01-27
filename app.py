import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import subprocess
import csv
import pandas as pd
import json
import os
import math
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

"""
@app.post("/api/test")
def test():
  cmd = [
    "docker", "compose",
    "-f", "/mnt/c/Users/arhod/Desktop/arhodia/docker/docker-compose.yml",
    "run", "--rm",
    "spark-client",
    "python3", "/data/backend/kmeans_ap_timer2_1.py"
    ]
  subprocess.run(cmd, check=True)
  #os.system("docker compose -f /mnt/c/Users/arhod/Desktop/arhodia/docker/docker-compose.yml   run --rm spark-client python3 /data/backend/kmeans_ap_timer2_1.py")
  return jsonify('ok')
"""


# ... (υπόλοιπα imports και αρχικοποίηση Flask)
"""
@app.post("/api/test")
def test():
    # 1. Λήψη δεδομένων JSON από το React
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # 2. Εξαγωγή και Καθαρισμός Τιμών (όπως ακριβώς το έχεις στο upload)
    def clean_param(value, target_type):
        if value is None or str(value).strip() == "":
            return None
        try:
            return target_type(value)
        except (ValueError, TypeError):
            return None

    industry = data.get('industry')
    algorithms = data.get('algorithms')
    # Αν το algorithms είναι λίστα, το κάνουμε string για να μπει σε ένα κελί του CSV
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

    try:
        neighbor = int(float(neighbor_raw))
    except (TypeError, ValueError):
        neighbor = 5
    neighbor = max(3, min(neighbor, 80))

    # 3. Δημιουργία του CSV αρχείου στο σωστό Path
    # Γράφουμε στο path του WSL που είναι mounted ως /data/ στο container
    csv_file_path = "/mnt/c/Users/arhod/Desktop/DIPLOMATIKIFINAL/parameter.csv"
    
    # Τα δεδομένα που θα γράψουμε
    header = [
        'industry', 'algorithms', 'radioOption', 'name', 'neighbor',
        'k_min', 'k_max', 'seed', 'maxIter', 'sample_frac'
    ]
    
    row = [
        industry, algorithms, radioOption, name, neighbor,
        input_k_min, input_k_max, input_seed, input_maxIter, input_sample_frac
    ]

    try:
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header) # Γράφουμε τους τίτλους
            writer.writerow(row)    # Γράφουμε τις τιμές
        print(f"DEBUG: parameter.csv written successfully to {csv_file_path}")
    except Exception as e:
        print(f"ERROR: Could not write csv file: {e}")
        return jsonify({"error": "Failed to write parameter file"}), 500

    # 4. Εκτέλεση του Docker Command
    # Το container θα βρει το αρχείο στο /data/parameter.csv
    cmd = [
        "docker", "compose",
        "-f", "/mnt/c/Users/arhod/Desktop/arhodia/docker/docker-compose.yml",
        "run", "--rm",
        "spark-client",
        "python3", "/data/backend/kmeans_ap_timer2_1.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return jsonify('ok')
    except subprocess.CalledProcessError as e:
        print(f"ERROR executing docker command: {e}")
        return jsonify({"error": "Docker execution failed"}), 500
"""
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
              'k_min', 'k_max', 'seed', 'maxIter', 'sample_frac']
    row = [industry, algorithms, radioOption, name, neighbor,
           input_k_min, input_k_max, input_seed, input_maxIter, input_sample_frac]

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
        "python3", "/data/backend/kmeans_ap_timer2_1.py"
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

    # Helper function για ασφαλές διάβασμα CSV
    def read_csv_safe(filename):
        path = os.path.join(results_dir, filename)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                # Αντικατάσταση NaN με None (null στο JSON)
                df = df.where(pd.notnull(df), None)
                return df.to_dict(orient='records')
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                return []
        return []

    # 1. Hyperparameters
    hyperparams_list = read_csv_safe("output_hyperparameters.csv")
    hyperparams_dict = hyperparams_list[0] if hyperparams_list else {}

    # 2. Matches
    top_matches_df = read_csv_safe("output_top_matches.csv")
    recommended_matches_df = read_csv_safe("output_recommended.csv")

    # 3. Execution Time
    exec_time_dict = read_json_safe("output_time.json")

    # 4. Visual Data
    clean_visual_data = read_json_safe("output_charts.json")

    # 5. LSH Results
    lsh_brp_dict = read_csv_safe("output_lsh_brp.csv")
    lsh_minihash_dict = read_csv_safe("output_lsh_minihash.csv")

    # Συγκέντρωση όλων των δεδομένων σε ένα dictionary
    response_data = {
        "hyperparameters": hyperparams_dict,
        "top_matches": top_matches_df,
        "recommended_matches": recommended_matches_df,
        "execution_time": exec_time_dict,
        "lsh_brp": lsh_brp_dict,
        "lsh_minihash": lsh_minihash_dict,
        "visual_data": clean_visual_data
    }

    # ΤΕΛΙΚΟΣ ΚΑΘΑΡΙΣΜΟΣ: Περνάμε όλο το response από τη clean_nans
    # Αυτό εξασφαλίζει ότι κανένα NaN δεν θα φύγει προς το frontend
    final_response = clean_nans(response_data)

    return jsonify(final_response)
"""
@app.post("/api/upload")
def upload():
    print("--- DEBUG start ---\n")
    # 1. Get the JSON data sent from React
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # 2. Extract values safely from the JSON dictionary
    industry = data.get('industry')
    algorithms = data.get('algorithms')
    radioOption = data.get('radioOption')
    name = data.get('name')
    neighbor=data.get('neighbor')


# --- 3. Extract & Clean Hyperparameters (NEW) ---
    # Συνάρτηση για ασφαλή μετατροπή (αν είναι κενό string ή None -> επιστρέφει None)
    def clean_param(value, target_type):
        if value is None or str(value).strip() == "":
            return None
        try:
            return target_type(value)
        except (ValueError, TypeError):
            return None

    input_k_min = clean_param(data.get('k_min'), int)
    input_k_max = clean_param(data.get('k_max'), int)
    input_seed = clean_param(data.get('seed'), int)
    input_maxIter = clean_param(data.get('maxIter'), int)
    input_sample_frac = clean_param(data.get('sample_frac'), float)


    try:
        neighbor = int(float(neighbor))
    except (TypeError, ValueError):
        neighbor = 5
    neighbor = max(3, min(neighbor, 80))


    print(f"DEBUG: Industry: {industry}, Algorithms: {algorithms}, Option: {radioOption}")

    # 3. Run the logic
    df_hyperparameters_clustering, top_matches_df, recommended_matches_df,execution_time_list, df_lsh_brp, df_lsh_minihash,all_charts = run_logic(
    industry, 
    radioOption,
    algorithms, 
    name,
    neighbor,
    input_k_min,
    input_k_max,
    input_seed,
    input_maxIter,
    input_sample_frac)

    # --- DEFINE COLUMNS TO DROP (Non-serializable Vectors) ---
    vector_cols = ['features', 'features_norm', 'features_sparse', 'features_arr', 'hashes_brp', 'hashes_mh', 'prediction']

    # --- 5. Format Results for JSON Response ---
    
    # Hyperparameters
    if df_hyperparameters_clustering is not None and not df_hyperparameters_clustering.empty:
        hyperparams_dict = df_hyperparameters_clustering.fillna(0).to_dict(orient="records")
    else:
        hyperparams_dict = []

    # Potential Matches
    if top_matches_df is not None:
        pdf_matches = top_matches_df.toPandas().fillna(0)
        drop_cols = [c for c in vector_cols if c in pdf_matches.columns]
        top_matches_df = pdf_matches.drop(columns=drop_cols).to_dict(orient="records")
    else:
        top_matches_df = []

    # Potential Matches
    if recommended_matches_df is not None:
        pdf_matches = recommended_matches_df.toPandas().fillna(0)
        drop_cols = [c for c in vector_cols if c in pdf_matches.columns]
        recommended_matches_df = pdf_matches.drop(columns=drop_cols).to_dict(orient="records")
    else:
        recommended_matches_df = []

    # LSH BRP
    if df_lsh_brp is not None:
        pdf_brp = df_lsh_brp.toPandas().fillna(0)
        drop_cols = [c for c in vector_cols if c in pdf_brp.columns]
        lsh_brp_dict = pdf_brp.drop(columns=drop_cols).to_dict(orient="records")
    else:
        lsh_brp_dict = []

    # LSH MinHash
    if df_lsh_minihash is not None:
        pdf_mh = df_lsh_minihash.toPandas().fillna(0)
        drop_cols = [c for c in vector_cols if c in pdf_mh.columns]
        lsh_minihash_dict = pdf_mh.drop(columns=drop_cols).to_dict(orient="records")
    else:
        lsh_minihash_dict = []







    # Execution Time
    exec_time_dict = [{"algorithm": item[0], "time": round(item[1], 4)} for item in execution_time_list]

   # Καθαρισμός του all_charts για να είναι συμβατό με JSON
    clean_visual_data = {}
    if all_charts and isinstance(all_charts, dict):
        for algo, series_list in all_charts.items():
            clean_series_list = []
            for series in series_list:
                clean_series = {
                    "label": str(series.get("label")),
                    "id": str(series.get("id")),
                    "data": [
                        {"x": float(d["x"]), "y": float(d["y"])} 
                        for d in series.get("data", [])
                    ]
                }
                if "color" in series:
                    clean_series["color"] = series["color"]
                clean_series_list.append(clean_series)
            clean_visual_data[algo] = clean_series_list

    # 6. Return JSON
    return jsonify({
        "hyperparameters": hyperparams_dict,#δειχνω τις τιμες των υπερπαραμετρων που χρησιμοποιηθηκαν για τους αλγοριθμους
        "top_matches": top_matches_df,
        "recommended_matches":recommended_matches_df,
        "execution_time": exec_time_dict,
        "lsh_brp": lsh_brp_dict,
        "lsh_minihash": lsh_minihash_dict,
        "visual_data": clean_visual_data#Στέλνουμε το καθαρισμένο dictionary
    })
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)