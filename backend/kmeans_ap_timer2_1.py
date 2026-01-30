import time
import numpy as np
import itertools
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, monotonically_increasing_id, coalesce, col, lower, trim,broadcast, expr
from pyspark.ml import Pipeline
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.functions import vector_to_array
from pyspark.ml.linalg import Vectors
from pyspark.sql.types import ArrayType, DoubleType, StructType, StructField, IntegerType, FloatType
from pyspark.ml.clustering import BisectingKMeans, KMeans
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, Word2Vec, Normalizer, PCA, BucketedRandomProjectionLSH, MinHashLSH, CountVectorizer
import matplotlib.pyplot as plt
import seaborn as sns
from pyspark.ml.feature import PCA
import numpy as np
import matplotlib
import pandas as pd
import json
import os
matplotlib.use('Agg')
# --- Βοηθητικές Συναρτήσεις (Plot, Parse, Join, Preprocessing, Tune) ---
# Αυτές παραμένουν ίδιες, τις αφήνω ως έχουν για συντομία, 
# εστιάζουμε στις αλλαγές από το find_best_k και κάτω.
def get_cluster_data_for_react(predictions_df, model, algorithm_name="KMeans"):
    # 1. PCA για τα σημεία
    pca = PCA(k=2, inputCol="features_norm", outputCol="pca_features")
    pca_model = pca.fit(predictions_df)
    pca_df = pca_model.transform(predictions_df).select("prediction", "pca_features")
    
    pandas_df = pca_df.toPandas()
    pandas_df[['x', 'y']] = pd.DataFrame(
        pandas_df['pca_features'].apply(lambda x: x.toArray()).tolist(), 
        index=pandas_df.index
    )

    chart_data = []
    unique_clusters = sorted(pandas_df['prediction'].unique())
    
    # Προσθήκη των σημείων ανά Cluster
    for cluster_id in unique_clusters:
        cluster_points = pandas_df[pandas_df['prediction'] == cluster_id]
        chart_data.append({
            "label": f"Cluster {cluster_id}",
            "data": cluster_points[['x', 'y']].to_dict(orient='records'),
            "id": f"cluster_{cluster_id}"
        })

    # 2. Επεξεργασία Κέντρων (Centroids)
    centers = model.clusterCenters()
    # Μετατρέπουμε τα κέντρα σε Spark Vectors για να τα περάσουμε από το PCA μοντέλο
    centers_vec = [Vectors.dense(c) for c in centers]
    centers_df = spark.createDataFrame([(i, v) for i, v in enumerate(centers_vec)], ["id", "features_norm"])
    
    pca_centers = pca_model.transform(centers_df).select("pca_features").toPandas()
    pca_centers[['x', 'y']] = pd.DataFrame(
        pca_centers['pca_features'].apply(lambda x: x.toArray()).tolist()
    )

    # Προσθήκη των κέντρων ως ξεχωριστό series για το React
    chart_data.append({
        "label": "Centroids",
        "data": pca_centers[['x', 'y']].to_dict(orient='records'),
        "id": "centroids",
        "color": "#000000", # Μαύρο χρώμα για να ξεχωρίζουν
    })
        
    return chart_data
"""
def plot_clusters(predictions_df, centers_df, algorithm_name="KMeans"):
    
    Οπτικοποίηση των clusters σε 2 διαστάσεις χρησιμοποιώντας PCA και αποθήκευση σε αρχείο.
    
    print("Ξεκινά η δημιουργία του γραφήματος...")
    
    # 1. Μείωση διαστάσεων σε 2D
    pca = PCA(k=2, inputCol="features_norm", outputCol="pca_features")
    pca_model = pca.fit(predictions_df)
    pca_df = pca_model.transform(predictions_df).select("prediction", "pca_features")
    
    # Μετατροπή σε Pandas
    pandas_df = pca_df.toPandas()
    
    # Διαχωρισμός των PCA συντεταγμένων
    pandas_df[['pca_x', 'pca_y']] = pd.DataFrame(
        pandas_df['pca_features'].apply(lambda x: x.toArray()).tolist(), 
        index=pandas_df.index
    )
    
    # 2. Υπολογισμός κέντρων (centroids) για το γράφημα
    centroids = pandas_df.groupby('prediction')[['pca_x', 'pca_y']].mean().reset_index()

    # 3. Σχεδίαση
    plt.figure(figsize=(12, 8))
    
    # Χρήση παλέτας με πολλά χρώματα για τα 25 clusters
    sns.scatterplot(
        data=pandas_df, x='pca_x', y='pca_y', 
        hue='prediction', palette='turbo', alpha=0.5, s=60, legend=False
    )
    
    # Λίστα με γράμματα για τα κέντρα (αν k <= 26)
    import string
    alphabet = list(string.ascii_uppercase)

    for i, row in centroids.iterrows():
        cluster_id = int(row['prediction'])
        # Αν έχουμε λίγα clusters βάζουμε γράμματα, αλλιώς αριθμούς
        label = alphabet[cluster_id] if len(centroids) <= 26 else str(cluster_id)
        
        plt.scatter(row['pca_x'], row['pca_y'], marker='s', s=250, 
                    edgecolor='black', linewidth=1.5, color='white', alpha=0.9)
        plt.text(row['pca_x'], row['pca_y'], label, 
                 fontsize=10, fontweight='bold', ha='center', va='center', color='black')

    plt.title(f"Visual Cluster Distribution (k={len(centroids)}) - {algorithm_name}")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # --- ΤΟ ΣΗΜΕΙΟ ΠΟΥ ΡΩΤΗΣΕΣ ---
    plt.tight_layout()
    output_file = "cluster_plot.png"
    plt.savefig(output_file, dpi=300) # Αποθήκευση σε υψηλή ανάλυση
    plt.close() # Πολύ σημαντικό για να μην γεμίζει η RAM
    
    print(f"--- Το γράφημα οπτικοποίησης αποθηκεύτηκε επιτυχώς ως: {os.getcwd()}/{output_file} ---")
"""
"""
def plot_kmeans_metrics(metrics, best_k, algorithm="KMeans", save_path=None):
    
    metrics: list of (k, silhouette, wssse)
    
    mdf = pd.DataFrame(metrics, columns=["k", "silhouette", "wssse"]).sort_values("k")

    # 1) Silhouette vs k
    plt.figure()
    plt.plot(mdf["k"], mdf["silhouette"], marker="o")
    plt.axvline(best_k, linestyle="--")
    plt.scatter([best_k], [mdf.loc[mdf["k"] == best_k, "silhouette"].values[0]])
    plt.xlabel("k")
    plt.ylabel("Silhouette")
    plt.title(f"{algorithm}: Silhouette vs k (best_k={best_k})")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path.replace(".png", "_silhouette.png"), dpi=200)
        plt.close()
    else:
        plt.show()

    # 2) WSSSE vs k
    plt.figure()
    plt.plot(mdf["k"], mdf["wssse"], marker="o")
    plt.axvline(best_k, linestyle="--")
    plt.scatter([best_k], [mdf.loc[mdf["k"] == best_k, "wssse"].values[0]])
    plt.xlabel("k")
    plt.ylabel("WSSSE (trainingCost)")
    plt.title(f"{algorithm}: WSSSE vs k (best_k={best_k})")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path.replace(".png", "_wssse.png"), dpi=200)
        plt.close()
    else:
        plt.show()

    return mdf
"""
def parse_parameter():
    # Διαβάζουμε το CSV με το Spark
    # Το inferSchema είναι σημαντικό για να αναγνωρίσει τα int/float αυτόματα
    parameter_df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load("/data/parameter.csv")
    
    # Ελέγχουμε αν το αρχείο είναι άδειο
    if parameter_df.head(1) == 0:
        print("Warning: parameter.csv is empty")
        return None

    # Παίρνουμε την πρώτη (και μοναδική) γραμμή
    row = parameter_df.collect()[0]

    # Επεξεργασία του πεδίου algorithms (από "KMeans,LSH" σε ['KMeans', 'LSH'])
    algos_str = row['algorithms']
    if algos_str:
        algos_list = algos_str.split(',')
    else:
        algos_list = []

    # Δημιουργούμε ένα λεξικό με τα ονόματα των ορισμάτων της run_logic
    params = {
        "input_industry": row['industry'],
        "input_radioOption": row['radioOption'],
        "input_algorithms": algos_list,
        "input_name": row['name'],
        "input_neighbor": row['neighbor'],
        # Προαιρετικές παράμετροι (αν είναι null στο csv, θα γίνουν None εδώ)
        "input_k_min": row['k_min'],
        "input_k_max": row['k_max'],
        "input_seed": row['seed'],
        "input_maxIter": row['maxIter'],
        "input_sample_frac": row['sample_frac']
    }
    
    return params
                
def parse_data():
    # Προσαρμόστε τα paths ανάλογα με το περιβάλλον σας
    startups_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true")\
                .load("/data/INC 5000 Companies 2019.csv")
                #.load('/mnt/c/Users/arhod/Desktop/DIPLOMATIKIFINAL/INC 5000 Companies 2019.csv')
                
    
    researchers_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true")\
                .load('/data/synthetic_files/synthetic_researchers_20000_inc5000dist.csv')
                #.load('/mnt/c/Users/arhod/Desktop/DIPLOMATIKIFINAL/synthetic_files/synthetic_researchers_20000_inc5000dist.csv')
                
    
    companies_clean = startups_df.withColumnRenamed("name", "company_name").withColumnRenamed("id", "company_id").withColumnRenamed("industry", "company_industry").withColumn("source_type", lit("start-up")) 
    researchers_clean = researchers_df.withColumnRenamed("name", "researcher_name").withColumnRenamed("id", "researcher_id").withColumnRenamed("researchfield", "researcher_field").withColumn("source_type", lit("researcher")) 
    return companies_clean, researchers_clean

def join_dfs(companies_clean, researchers_clean):
    union_df = researchers_clean.unionByName(companies_clean, allowMissingColumns=True)
    union_df_with_id = union_df.withColumn("id", monotonically_increasing_id())
    other_columns = [c for c in union_df_with_id.columns if c != "id"]
    join_df = union_df_with_id.select("id", *other_columns)
    join_df = join_df.withColumn("industry", coalesce(col("researcher_field"), col("company_industry")))
    return join_df

def preprocessing(join_df):
    tokenizer = RegexTokenizer(inputCol="industry", outputCol="words", pattern="\\W")
    stopwords_remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
    word2vec = Word2Vec(inputCol="filtered_words", outputCol="features", vectorSize=50, minCount=0,maxIter=50, windowSize=5,seed=42)   
    count_vec = CountVectorizer(inputCol="filtered_words", outputCol="features_sparse", vocabSize=20000, minDF=2)
    feature_pipeline = Pipeline(stages=[tokenizer, stopwords_remover, word2vec, count_vec])
    feature_model = feature_pipeline.fit(join_df)
    feature_df = feature_model.transform(join_df)
    normalizer = Normalizer(inputCol="features", outputCol="features_norm", p=2.0)
    feature_df = normalizer.transform(feature_df).cache()
    feature_df.count()
    return feature_df

def tune_hyperparameters(df, algorithm, init_k):
    # ... (Κώδικας tune ως έχει) ...
    print(f"\n--- 🔍 Tuning Hyperparameters for {algorithm} ---")
    param_grid = {
        'seed': [42, 123],              
        'maxIter': [20, 50],            
        'sample_frac': [0.5, 1.0]       
    }
    keys, values = zip(*param_grid.items())
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    best_params = None
    best_score = -1.0
    evaluator = ClusteringEvaluator(featuresCol="features_norm", predictionCol="prediction", metricName="silhouette")
    AlgoClass = globals()[algorithm]
    for params in combinations:
        cur_seed = params['seed']
        cur_iter = params['maxIter']
        cur_frac = params['sample_frac']
        train_df = df.sample(withReplacement=False, fraction=cur_frac, seed=cur_seed) if cur_frac < 1.0 else df
        estimator = AlgoClass().setK(init_k).setSeed(cur_seed).setFeaturesCol("features_norm").setPredictionCol("prediction").setMaxIter(cur_iter)
        if algorithm == 'KMeans':
            estimator.setInitMode("k-means||")
        model = estimator.fit(train_df)
        predictions = model.transform(train_df) 
        score = evaluator.evaluate(predictions)
        if score > best_score:
            best_score = score
            best_params = params
            
    best_seed = best_params['seed']
    best_maxIter = best_params['maxIter']
    best_sample_frac = best_params['sample_frac']

    print(f"✅ Best Params found: Seed={best_seed}, MaxIter={best_maxIter}, SampleFrac={best_sample_frac} (Score: {best_score:.4f})")
    return best_seed, best_maxIter, best_sample_frac

def find_best_k(df, algorithm, k_min=None, k_max=None, seed=None, maxIter=None, sample_frac=None, distance="cosine"):
    
    # --- LOGIC: Αν είναι None πάρε το Default, αλλιώς κράτα την τιμή ---
    k_min = k_min if k_min is not None else 2
    k_max = k_max if k_max is not None else 25
    seed = seed if seed is not None else 42
    maxIter = maxIter if maxIter is not None else 20
    sample_frac = sample_frac if sample_frac is not None else 1.0
    # -------------------------------------------------------------------

    AlgoClass = globals()[algorithm]
    train_df = df.sample(False, sample_frac, seed=seed).cache() if sample_frac < 1.0 else df
    eval_df_sample = train_df.sample(False, 0.3, seed=seed).cache() 
    
    evaluator = ClusteringEvaluator(featuresCol="features_norm", predictionCol="prediction", 
                                    metricName="silhouette", distanceMeasure=distance)

    results = []
    best_k, best_score = None, float("-inf")
    
    print(f"Running {algorithm}: k=[{k_min}-{k_max}], seed={seed}, iter={maxIter}, frac={sample_frac}")

    for k in range(k_min, k_max + 1):
        start_time = time.time()        
        if algorithm == 'KMeans':
            estimator = AlgoClass().setK(k).setSeed(seed).setFeaturesCol("features_norm").setPredictionCol("prediction").setMaxIter(maxIter).setInitMode("k-means||").setTol(1e-4) 
        elif algorithm == 'BisectingKMeans':
            estimator = AlgoClass().setK(k).setSeed(seed).setFeaturesCol("features_norm").setPredictionCol("prediction").setMaxIter(maxIter)
        
        model = estimator.fit(train_df)
        predictions = model.transform(eval_df_sample)
        score = evaluator.evaluate(predictions)
        wssse = model.summary.trainingCost
        elapsed = time.time() - start_time
        results.append((k, score, wssse))
        if score > best_score:
            best_k, best_score = k, score
            
        print(f"k={k:2d} | silhouette={score:.4f} | WSSSE={wssse:.2f} | Time={elapsed:.2f}s")
    
    if sample_frac < 1.0: train_df.unpersist()
    eval_df_sample.unpersist()
    print(f"best_k={best_k:2d} | best_silhouette={best_score:.4f}")
    return best_k, best_score, results

def clustering_algo(feature_df, algorithm, input_industry, input_name, input_radioOption, 
                    input_k_min=None, input_k_max=None, input_seed=None, input_maxIter=None, input_sample_frac=None):
    
    # --- 1. Αρχικοποίηση & Hyperparameter Tuning ---
    df_hyper = pd.DataFrame()
    AlgoClass = globals()[algorithm]
    
    # Τρέχουμε το tuning για να βρούμε τα "ιδανικά" (σε περίπτωση που ο χρήστης δεν έδωσε δικά του)
    tuned_seed, tuned_maxIter, tuned_sample_frac = tune_hyperparameters(feature_df, algorithm, init_k=10)
    
    # --- LOGIC: Προτεραιότητα: Χρήστης > Tuned ---
    # Αν ο χρήστης έδωσε (δεν είναι None), παίρνουμε του χρήστη.
    # Αν ο χρήστης ΔΕΝ έδωσε (είναι None), παίρνουμε από το tuning.
    final_seed = input_seed if input_seed is not None else tuned_seed
    final_maxIter = input_maxIter if input_maxIter is not None else tuned_maxIter
    final_sample_frac = input_sample_frac if input_sample_frac is not None else tuned_sample_frac
    
    # Σημείωση: Τα input_k_min / input_k_max τα περνάμε ως έχουν (None ή τιμή) 
    # γιατί η find_best_k έχει δική της logic για τα defaults (2 και 20).
    
    # Καλούμε την find_best_k με τις ΤΕΛΙΚΕΣ τιμές
    best_k, best_score, metrics = find_best_k(
        feature_df, 
        algorithm, 
        k_min=input_k_min, 
        k_max=input_k_max, 
        seed=final_seed, 
        maxIter=final_maxIter, 
        sample_frac=final_sample_frac, 
        distance="cosine"
    )
    
    df_hyper = pd.DataFrame([{
        "algorithm": algorithm,
        "best_k": best_k,
        "best_seed": final_seed,
        "best_maxIter": final_maxIter,
        "best_sample_frac": final_sample_frac,
        "best_score": best_score 
    }])
    
    # --- 2. Ρύθμιση Estimator με τα FINAL params ---
    if algorithm == 'KMeans':   
        estimator = (AlgoClass().setK(best_k).setSeed(final_seed).setFeaturesCol("features_norm").setPredictionCol("prediction").setMaxIter(final_maxIter).setInitMode("k-means||"))
    elif algorithm == 'BisectingKMeans':   
        estimator = (AlgoClass().setK(best_k).setSeed(final_seed).setFeaturesCol("features_norm").setPredictionCol("prediction").setMaxIter(final_maxIter))
    
    # --- 3. Εκπαίδευση Μοντέλου ---
    start_time = time.time()
    model = estimator.fit(feature_df)
    predictions_df = model.transform(feature_df)
    count_pred = predictions_df.count()
    end_time = time.time()
    
    wssse = model.summary.trainingCost
    print(f"Within Set Sum of Squared Errors (WSSSE) = {wssse}")
    
    centers = model.clusterCenters()
    centers_data = [(int(i), [float(x) for x in center]) for i, center in enumerate(centers)]
    schema = StructType([
        StructField("center_id", IntegerType(), False),
        StructField("center_vec", ArrayType(DoubleType()), False)
    ])
    centers_df = spark.createDataFrame(centers_data, schema)
    df_with_arrays = predictions_df.withColumn("features_arr", vector_to_array(col("features_norm")))
    potential_matches_df = None 
    
    # Broadcast Join με τα κέντρα των clusters
    joined_df = df_with_arrays.join(
        broadcast(centers_df), 
        df_with_arrays.prediction == centers_df.center_id, 
        "left"
    )
    
    # Υπολογισμός Ευκλείδειας Απόστασης
    distance_expression = """
        sqrt(
            aggregate(
                zip_with(features_arr, center_vec, (x, y) -> power(x - y, 2)),
                0.0D,
                (acc, x) -> acc + x
            )
        )
    """
    final_df = joined_df.withColumn("distance_to_center", expr(distance_expression)).drop("features_arr", "center_id", "center_vec")
    
    # --- 4. Matching Logic ---
    top_matches_df = None
    recommended_matches_df = None
    
    if str(input_radioOption).lower() in ['researcher']:
        search_col = "researcher_name"
        target_check_col = "company_name" 
    else:
        search_col = "company_name"
        target_check_col = "researcher_name"

    entity_row = final_df.filter(lower(trim(col(search_col))) == lower(trim(lit(input_name)))).first()

    if entity_row:
        my_id = entity_row['id']
        my_cluster = entity_row['prediction']
        my_industry = str(entity_row['industry']).lower().strip() if entity_row['industry'] else None

        potential_matches = final_df.filter(
            (col("prediction") == my_cluster) & (col(target_check_col).isNotNull()) & (col("id") != my_id)
        )
        
        # 1. Top Results (Ίδιο cluster + Ίδια βιομηχανία)
        industry_match_cond = lower(trim(col("industry"))) == lit(my_industry)
        top_matches_df = potential_matches.filter(industry_match_cond).orderBy(col("distance_to_center").asc_nulls_last())
        
        # 2. Recommended Results (Ίδιο cluster + Διαφορετική βιομηχανία)
        recommended_matches_df = potential_matches.filter(~industry_match_cond).orderBy(col("distance_to_center").asc_nulls_last())

    chart_data = get_cluster_data_for_react(predictions_df, model, algorithm)
    return centers_df, final_df, end_time - start_time, df_hyper, top_matches_df, recommended_matches_df, chart_data

def run_lsh_brp(df, input_name, input_neighbor):
    # (Κώδικας LSH BRP ως έχει)
    print(f"\n--- ⚡ Running LSH: Bucketed Random Projection (Cosine/L2) ---")
    brp = BucketedRandomProjectionLSH(inputCol="features_norm", outputCol="hashes_brp", bucketLength=2.0, numHashTables=3, seed=42)
    start_time = time.time()
    model = brp.fit(df)
    df_transformed = model.transform(df)
    if input_name and input_name.strip():
        print(f"   🔍 BRP Query for: '{input_name}'")
        query_row = df.filter((col("company_name") == input_name) | (col("researcher_name") == input_name)).first()
        if query_row:
            query_vec = query_row['features_norm']
            neighbors = model.approxNearestNeighbors(df, query_vec, input_neighbor)
            print(f"   ✅ BRP Neighbors Found")
        else:
            print("   ❌ Target not found.")
    end_time = time.time()        
    return df_transformed, end_time - start_time

def run_lsh_minhash(df, input_name, input_neighbor):
    # (Κώδικας LSH MinHash ως έχει)
    print(f"\n--- ⚡ Running LSH: MinHash (Jaccard) ---")
    mh = MinHashLSH(inputCol="features_sparse", outputCol="hashes_mh", numHashTables=5, seed=42)
    start_time = time.time()
    model = mh.fit(df)
    df_transformed = model.transform(df)
    if input_name and input_name.strip():
        print(f"   🔍 MinHash Query for: '{input_name}'")
        query_row = df.filter((col("company_name") == input_name) | (col("researcher_name") == input_name)).first()
        if query_row:
            query_vec = query_row['features_sparse']
            neighbors = model.approxNearestNeighbors(df, query_vec, input_neighbor)
            print(f"   ✅ MinHash Neighbors Found")
        else:
            print("   ❌ Target not found.")
    end_time = time.time()
    return df_transformed , end_time - start_time


def run_logic(input_industry, input_radioOption, input_algorithms, input_name, input_neighbor,
              input_k_min=None, input_k_max=None, input_seed=None, input_maxIter=None, input_sample_frac=None):
    
    companies_clean, researchers_clean = parse_data()
    join_df = join_dfs(companies_clean, researchers_clean)
    join_df = join_df.repartition(partition)
    feature_df = preprocessing(join_df)
    feature_df = feature_df.repartition(partition).cache()
    feature_df.count()
    
    all_charts = {} # Λεξικό για να κρατάμε τα charts ανά αλγόριθμο
    execution_time = []
    df_lsh_brp = None
    df_lsh_minihash = None
    potential_matches_df = None 
    # ΑΡΧΙΚΟΠΟΙΗΣΗ ΩΣ NONE ΓΙΑ ΑΠΟΦΥΓΗ UnboundLocalError
    final_top_matches_dict = {} 
    final_rec_matches_dict = {}
    
    df_hyperparameters_clustering = pd.DataFrame(columns=["algorithm", "best_k", "best_seed", "best_maxIter", "best_sample_frac", "best_score"])

    algorithms_to_run = input_algorithms
    for algo in algorithms_to_run:
        
        if algo == 'KMeans' or algo == 'BisectingKMeans':
            # Περνάμε τα user params εδώ
            centers_df, df_with_arrays, time_clustering, df_hyper,  top_matches_df, recommended_matches_df,chart_data = clustering_algo(
                feature_df, algo, input_industry, input_name, input_radioOption,
                input_k_min, input_k_max, input_seed, input_maxIter, input_sample_frac # <-- PASSING
            )
            all_charts[algo] = chart_data
            df_hyperparameters_clustering = pd.concat([df_hyperparameters_clustering, df_hyper], ignore_index=True)
            execution_time.append([algo, time_clustering])

           # Προσθήκη στήλης με το όνομα του αλγορίθμου
            if top_matches_df:
                top_matches_df = top_matches_df.withColumn("algorithm_used", lit(algo))
                
                # ΚΑΘΑΡΙΣΜΟΣ: Αφαιρούμε τις στήλες που περιέχουν Vectors πριν το toPandas()
                cols_to_drop = ["features", "features_norm", "features_sparse", "features_arr"]
                clean_df = top_matches_df.drop(*[c for c in cols_to_drop if c in top_matches_df.columns])
                
                final_top_matches_dict[algo] = clean_df.toPandas().fillna(0).to_dict(orient='records')
            
            # ΕΔΩ Η ΔΙΟΡΘΩΣΗ: Χρήση του σωστού ονόματος 'recommended_matches_df'
            if recommended_matches_df:
                recommended_matches_df = recommended_matches_df.withColumn("algorithm_used", lit(algo))
                
                # ΚΑΘΑΡΙΣΜΟΣ: Παρομοίως για τα recommended
                clean_rec_df = recommended_matches_df.drop(*[c for c in cols_to_drop if c in recommended_matches_df.columns])
                
                final_rec_matches_dict[algo] = clean_rec_df.toPandas().fillna(0).to_dict(orient='records')
        elif algo == 'LSH_BRP':
            df_lsh_brp, time_lsh_brp = run_lsh_brp(feature_df, input_name, input_neighbor)
            execution_time.append([algo, time_lsh_brp])

        elif algo == 'LSH_MinHash':
            df_lsh_minihash, time_lsh_minihash = run_lsh_minhash(feature_df, input_name, input_neighbor)
            execution_time.append([algo, time_lsh_minihash])

    for result in execution_time:
        print(f"Algorithm: {result[0]}, Time: {result[1]:.4f} sec")

    print(df_hyperparameters_clustering)
    return df_hyperparameters_clustering, final_top_matches_dict, final_rec_matches_dict, execution_time, df_lsh_brp, df_lsh_minihash, all_charts

# --- Main Spark Init ---
CORES = 4
#spark = SparkSession.builder.appName(f"Benchmark_Cores").master(f"local[{CORES}]").getOrCreate()
partition = CORES * 2

spark = (
    SparkSession.builder
    .appName("bench")
    .master("spark://spark-master:7077")
    .config("spark.executor.instances", "2")
    .config("spark.executor.cores", "1")
    .config("spark.executor.memory", "1g")
    .config("spark.driver.memory", "1g")
    .config("spark.dynamicAllocation.enabled", "false")
    .config("spark.speculation", "false")
    .getOrCreate()
)
#spark = SparkSession.builder.appName(f"Benchmark_Cores").master(f"local[{CORES}]").getOrCreate()
# -------------------------------------------------------------------------
# 4. ΔΙΟΡΘΩΣΗ main: Προσομοίωση παραμέτρων από Front-end
# -------------------------------------------------------------------------

def main():
    # Βασικά Inputs
    input_industry = "Advertising & Marketing"
    input_radioOption = "start-up"
    input_name = "MuteSix"
    input_algorithms = ["KMeans"]
    input_neighbor = 5
    
    # Παράμετροι που έρχονται από το Front-End (Advanced Settings)
    # ΔΟΚΙΜΗ: Βάλτε τιμές ή None για να δείτε τη διαφορά
    
    # Π.χ. Ο χρήστης άφησε κενά τα k_min/k_max (θα πάρει 2, 20)
    input_k_min_input = None 
    input_k_max_input = None
    
    # Π.χ. Ο χρήστης όρισε συγκεκριμένο Seed και Iterations
    input_seed_input = None     # Αν None -> θα πάρει default 42
    input_maxIter_input = None  # Αν None -> θα πάρει default 20
    input_sample_frac_input = None # Αν None -> θα πάρει default 1.0

    print(f"Running for: Industry={input_industry}, Name={input_name}, Algos={input_algorithms}")
    
    # Κλήση της run_logic με τα ορίσματα
    run_logic(input_industry, input_radioOption, input_algorithms, input_name, input_neighbor,
              input_k_min=input_k_min_input, 
              input_k_max=input_k_max_input, 
              input_seed=input_seed_input, 
              input_maxIter=input_maxIter_input, 
              input_sample_frac=input_sample_frac_input)

if __name__ == "__main__":
    # 1. Διαβάζουμε τις παραμέτρους από το CSV
    params = parse_parameter()
    
    print("--- DEBUG: Running with parameters: ---")
    print(params)
    print("---------------------------------------")

    if params:
        # ΚΑΘΑΡΙΣΜΟΣ ΠΑΛΙΩΝ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ΠΡΙΝ ΤΗΝ ΕΚΤΕΛΕΣΗ
        results_path = "/data/results/"
        if not os.path.exists(results_path):
            os.makedirs(results_path)
        for f in os.listdir(results_path):
            file_path = os.path.join(results_path, f)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        # 2. Τρέχουμε τη λογική
        df_hyper, top_matches, rec_matches, exec_time, df_brp, df_minihash, charts = run_logic(**params)
        
        # 3. ΣΩΖΟΥΜΕ ΤΑ ΑΠΟΤΕΛΕΣΜΑΤΑ ΣΤΟ /data/
        # Έτσι ώστε το Flask να μπορεί να τα βρει μετά
        
        print("--- Saving outputs to /data/results/ ---")

        # Α. Hyperparameters (Είναι Pandas DataFrame)
        if df_hyper is not None:
            df_hyper.to_csv("/data/results/output_hyperparameters.csv", index=False)

        # Β. Matches (Είναι πλέον Λεξικά -> Σώζονται ως JSON για να διατηρηθεί ο διαχωρισμός KMeans/Bisecting)
        if top_matches: # top_matches είναι το final_top_matches_dict
            with open('/data/results/output_top_matches.json', 'w') as f:
                json.dump(top_matches, f)
            
        if rec_matches: # rec_matches είναι το final_rec_matches_dict
            with open('/data/results/output_recommended.json', 'w') as f:
                json.dump(rec_matches, f)
        # Γ. LSH Results
        if df_brp is not None:
            df_brp.toPandas().to_csv("/data/results/output_lsh_brp.csv", index=False)
            
        if df_minihash is not None:
            df_minihash.toPandas().to_csv("/data/results/output_lsh_minihash.csv", index=False)

        # Δ. Execution Time (Λίστα -> JSON)
        with open('/data/results/output_time.json', 'w') as f:
            json.dump(exec_time, f)

        # Ε. Charts (Λεξικό -> JSON)
        # Προσοχή: Το charts μπορεί να έχει μέσα αντικείμενα που δεν γίνονται json serializable απευθείας.
        # Αν είναι απλά strings/numbers είναι οκ.
        try:
            with open('/data/results/output_charts.json', 'w') as f:
                json.dump(charts, f)
        except Exception as e:
            print(f"Error saving charts: {e}")

        print("--- Success: All files saved. ---")

    else:
        print("Error: Could not load parameters.")









