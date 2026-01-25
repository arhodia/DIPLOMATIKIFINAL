import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from backend.kmeans_ap_timer2_1 import run_logic
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# Read the first CSV file as a DataFrame
#dataINC5000 = pd.read_csv('C:\\Users\\arhod\\Desktop\\Diploma-vscode\\INC 5000 Companies 2019.csv')

# Count the size of the DataFrames in MB
#size_inc5000_mb = dataINC5000.memory_usage(deep=True).sum() / (1024 * 1024)
#dataINC5000 = dataINC5000.replace({np.nan: None})

"""
@app.post("/api/upload")
def upload():
    # 1. Get the JSON data sent from React
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # 2. Extract values safely from the JSON dictionary
    industry = data.get('industry')      # Note: 'industry' matches your React state key
    algorithms = data.get('algorithms')
    radioOption = data.get('radioOption')

    print(f"DEBUG: Industry: {industry}, Algorithms: {algorithms}, Option: {radioOption}")

    # 3. Pass these to your logic
    all_algorithms_results = run_logic(industry, radioOption, algorithms)
# --- DEBUGGING PRINTS START ---
    print("\n--- DEBUG: Inspecting run_logic output ---")
    
    # 1. Έλεγχος τύπου (βεβαιώσου ότι είναι dict)
    print(f"Type of return: {type(all_algorithms_results)}")
    
    if isinstance(all_algorithms_results, dict):
        # 2. Έλεγχος των κλειδιών (των αλγορίθμων)
        print(f"Algorithms keys found: {list(all_algorithms_results.keys())}")
        
        # 3. Έλεγχος της δομής του πρώτου αλγορίθμου (για να δεις αν υπάρχουν τα spark_results/recos)
        for algo, content in all_algorithms_results.items():
            print(f"Checking algo '{algo}': keys -> {content.keys()}")
            
            # Προαιρετικά: Αν θες να δεις τα ίδια τα δεδομένα του Spark στο τερματικό:
            # content['spark_results'].show(2) 
            # content['spark_recos'].show(2)
            break # Σταματάμε στον πρώτο για να μην γεμίσουμε το log
    else:
        print(f"Raw content: {all_algorithms_results}")
        
    print("--- DEBUG END ---\n")
    # --- DEBUGGING PRINTS END ---

    json_response = {}
    
    for algo, data in all_algorithms_results.items():
        # Μετατροπή Results
        df_res = data['spark_results'].toPandas()
        
        # FIX: Μετατροπή σε object για να δεχτεί το None αντί για NaN
        df_res = df_res.astype(object).where(pd.notnull(df_res), None)

        # Μετατροπή Recommendations
        df_rec = data['spark_recos'].limit(20).toPandas()
        
        # FIX: Το ίδιο και εδώ
        df_rec = df_rec.astype(object).where(pd.notnull(df_rec), None)
        
        json_response[algo] = {
            "results": df_res.to_dict(orient="records"),
            "recommendations": df_rec.to_dict(orient="records")
        }
    return jsonify(json_response)
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

    try:
        neighbor = int(float(neighbor))
    except (TypeError, ValueError):
        neighbor = 5
    neighbor = max(3, min(neighbor, 80))


    print(f"DEBUG: Industry: {industry}, Algorithms: {algorithms}, Option: {radioOption}")

    # 3. Run the logic
    df_hyperparameters_clustering, potential_matches_df, execution_time_list, df_lsh_brp, df_lsh_minihash = run_logic(industry, radioOption, algorithms, name,neighbor)

    # --- DEFINE COLUMNS TO DROP (Non-serializable Vectors) ---
    # These columns cause the JSON error because they contain Vector objects
    vector_cols = ['features', 'features_norm', 'features_sparse', 'features_arr', 'hashes_brp', 'hashes_mh', 'prediction']

    # --- 1. Hyperparameters (Already Pandas) ---
    if df_hyperparameters_clustering is not None and not df_hyperparameters_clustering.empty:
        hyperparams_dict = df_hyperparameters_clustering.fillna(0).to_dict(orient="records")
    else:
        hyperparams_dict = []

    # --- 2. Potential Matches (Spark -> Pandas) ---
    if potential_matches_df is not None:
        pdf_matches = potential_matches_df.toPandas().fillna(0)
        # Drop vector columns if they exist
        drop_cols = [c for c in vector_cols if c in pdf_matches.columns]
        matches_dict = pdf_matches.drop(columns=drop_cols).to_dict(orient="records")
    else:
        matches_dict = []

    # --- 3. LSH BRP (Spark -> Pandas) ---
    if df_lsh_brp is not None:
        pdf_brp = df_lsh_brp.toPandas().fillna(0)
        # Drop vector columns so JSON serialization works
        drop_cols = [c for c in vector_cols if c in pdf_brp.columns]
        lsh_brp_dict = pdf_brp.drop(columns=drop_cols).to_dict(orient="records")
    else:
        lsh_brp_dict = []

    # --- 4. LSH MinHash (Spark -> Pandas) ---
    if df_lsh_minihash is not None:
        pdf_mh = df_lsh_minihash.toPandas().fillna(0)
        # Drop vector columns
        drop_cols = [c for c in vector_cols if c in pdf_mh.columns]
        lsh_minihash_dict = pdf_mh.drop(columns=drop_cols).to_dict(orient="records")
    else:
        lsh_minihash_dict = []
    # --- 5. Execution Time ---
    exec_time_dict = [{"algorithm": item[0], "time": round(item[1], 4)} for item in execution_time_list]
   
    # 6. Return JSON
    return jsonify({
        "hyperparameters": hyperparams_dict,
        "matches": matches_dict,
        "execution_time": exec_time_dict,
        "lsh_brp": lsh_brp_dict,
        "lsh_minihash": lsh_minihash_dict
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)