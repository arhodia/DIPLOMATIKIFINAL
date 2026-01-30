import time
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, monotonically_increasing_id, coalesce, col
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.functions import vector_to_array
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import col, lit, monotonically_increasing_id, coalesce, udf
from pyspark.sql.functions import col, broadcast, expr, lit
from pyspark.sql.types import ArrayType, DoubleType, StructType, StructField, IntegerType,FloatType
from pyspark.ml.clustering import BisectingKMeans, KMeans
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, Word2Vec, Normalizer, PCA, BucketedRandomProjectionLSH, MinHashLSH, CountVectorizer
from time import perf_counter
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.ml.functions import vector_to_array
from pyspark.sql.functions import col, lit, monotonically_increasing_id, coalesce, udf
from pyspark.sql.functions import col, lit, lower, trim
#def run_kmeans(selected_option,source_type,start_name,researcher_name):



def plot_kmeans_metrics(metrics, best_k, algorithm="KMeans", save_path=None):
    """
    metrics: list of (k, silhouette, wssse)
    """
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


def parse_data():
    startups_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true")\
                .load('/mnt/c/Users/arhod/Desktop/DIPLOMATIKIFINAL/INC 5000 Companies 2019.csv')
                #.load('/mnt/c/Users/tony3/Desktop/arhodia/data/INC 5000 Companies 2019.csv')
                
                #.load('/mnt/c/Users/arhod/Desktop/Diploma-vscode/INC 5000 Companies 2019.csv')
                #.load("/data/diploma/INC 5000 Companies 2019.csv")
    researchers_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true")\
                .load('/mnt/c/Users/arhod/Desktop/DIPLOMATIKIFINAL/synthetic_files/synthetic_researchers_20000_inc5000dist.csv')
                #.load('/mnt/c/Users/tony3/Desktop/arhodia/data/synthetic_researchers_20000_inc5000dist.csv')
                #.load('/mnt/c/Users/arhod/Desktop/Diploma-vscode/synthetic_files/synthetic_researchers_20000_inc5000dist.csv')
                #.load("/data/diploma/synthetic_files/synthetic_researchers_20000_inc5000dist.csv")
    companies_clean = startups_df.withColumnRenamed("name", "company_name").withColumnRenamed("id", "company_id").withColumnRenamed("industry", "company_industry").withColumn("source_type", lit("start-up")) 
    researchers_clean = researchers_df.withColumnRenamed("name", "researcher_name").withColumnRenamed("id", "researcher_id").withColumnRenamed("researchfield", "researcher_field").withColumn("source_type", lit("researcher")) 
    return companies_clean, researchers_clean


def join_dfs(companies_clean, researchers_clean):
    union_df = researchers_clean.unionByName(companies_clean, allowMissingColumns=True)
    union_df_with_id = union_df.withColumn("id", monotonically_increasing_id())
    other_columns = [c for c in union_df_with_id.columns if c != "id"]
    join_df = union_df_with_id.select("id", *other_columns)
    #ml_df = ml_df.repartition(SHUFFLE_PARTS)
    #Δημιουργία κοινής στήλης χαρακτηριστικών researcher_field + company_industry
    join_df = join_df.withColumn("industry", coalesce(col("researcher_field"), col("company_industry")))
    return join_df

# Αποθήκευση 
"""join_df.coalesce(1) \
    .write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(output_path)
"""

def preprocessing(join_df):
    tokenizer = RegexTokenizer(inputCol="industry", outputCol="words", pattern="\\W")
    stopwords_remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
    word2vec = Word2Vec(inputCol="filtered_words", outputCol="features", vectorSize=50, minCount=0,maxIter=50, windowSize=5,seed=42)   
    # Φτιάχνουμε Pipeline ΜΟΝΟ για τα features
    # 3. CountVectorizer (Για LSH MinHash) - ΑΥΤΟ ΕΛΕΙΠΕ ή δεν έτρεξε
    #count_vec = CountVectorizer(inputCol="filtered_words", outputCol="features_sparse", vocabSize=1000, minDF=1.0)
    count_vec = CountVectorizer(inputCol="filtered_words", outputCol="features_sparse", vocabSize=20000, minDF=2)
    feature_pipeline = Pipeline(stages=[tokenizer, stopwords_remover, word2vec, count_vec])
    feature_model = feature_pipeline.fit(join_df)
    feature_df = feature_model.transform(join_df)

    # Normalize vectors (unit length)
    normalizer = Normalizer(inputCol="features", outputCol="features_norm", p=2.0)
    feature_df = normalizer.transform(feature_df).cache()
    feature_df.count()  # materialize cache
    return feature_df

def tune_hyperparameters(df, algorithm, init_k):
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
        #predictions = model.transform(df) 
        score = evaluator.evaluate(predictions)
        if score > best_score:
            best_score = score
            best_params = params
            
    # Ξεπακετάρισμα των τιμών από το dictionary
    best_seed = best_params['seed']
    best_maxIter = best_params['maxIter']
    best_sample_frac = best_params['sample_frac']

    print(f"✅ Best Params found: Seed={best_seed}, MaxIter={best_maxIter}, SampleFrac={best_sample_frac} (Score: {best_score:.4f})")
    
    # Επιστροφή των 3 τιμών ξεχωριστά
    return best_seed, best_maxIter, best_sample_frac



def find_best_k(df, algorithm, k_min=2, k_max=20, seed=42, maxIter=20, sample_frac=1.0, distance="cosine"):
    AlgoClass = globals()[algorithm]
    train_df = df.sample(False, sample_frac, seed=seed).cache() if sample_frac < 1.0 else df
    eval_df_sample = train_df.sample(False, 0.3, seed=seed).cache() 
    
    evaluator = ClusteringEvaluator(featuresCol="features_norm", predictionCol="prediction", 
                                    metricName="silhouette", distanceMeasure=distance)

    results = []
    best_k, best_score = None, float("-inf")
    for k in range(k_min, k_max + 1):
        start_time = time.time()        
        if algorithm == 'KMeans':
            # tol=1e-4: Προσθήκη tolerance για να σταματάει νωρίτερα αν συγκλίνει
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
    # Καθαρισμός μνήμης
    if sample_frac < 1.0: train_df.unpersist()
    eval_df_sample.unpersist()
    print(f"best_k={best_k:2d} | best_silhouette={best_score:.4f}")
    return best_k, best_score, results

def clustering_algo(feature_df, algorithm, input_industry, input_name, input_radioOption):
    # --- 1. Αρχικοποίηση & Hyperparameter Tuning ---
    df_hyper = pd.DataFrame()
    AlgoClass = globals()[algorithm]
    # Υποθέτω ότι οι συναρτήσεις tune_hyperparameters και find_best_k υπάρχουν στον κώδικά σου
    best_seed, best_maxIter, best_sample_frac = tune_hyperparameters(feature_df, algorithm, init_k=10)
    best_k, best_score, metrics = find_best_k(feature_df, algorithm, k_min=2, k_max=25, seed=best_seed, maxIter=best_maxIter, sample_frac=best_sample_frac, distance="cosine")
    # Αποθήκευση γραφήματος (προαιρετικά αν υπάρχει η συνάρτηση)
    # metrics_df = plot_kmeans_metrics(metrics, best_k, algorithm="KMeans", save_path="kmeans_k_plots.png")
    df_hyper = pd.DataFrame([{
        "algorithm": algorithm,
        "best_k": best_k,
        "best_seed": best_seed,
        "best_maxIter": best_maxIter,
        "best_sample_frac": best_sample_frac,
        "best_score": best_score 
    }])
    # --- 2. Ρύθμιση Estimator ---
    if algorithm == 'KMeans':   
        estimator = (AlgoClass().setK(best_k).setSeed(best_seed).setFeaturesCol("features_norm").setPredictionCol("prediction").setMaxIter(best_maxIter).setInitMode("k-means||"))
    elif algorithm == 'BisectingKMeans':   
        estimator = (AlgoClass().setK(best_k).setSeed(best_seed).setFeaturesCol("features_norm").setPredictionCol("prediction").setMaxIter(best_maxIter))
    # --- 3. Εκπαίδευση Μοντέλου ---
    start_time = time.time()
    model = estimator.fit(feature_df)
    predictions_df = model.transform(feature_df)
    count_pred = predictions_df.count()
    end_time = time.time()
    #clustered_df = model.transform(feature_df)
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
    potential_matches_df = None # Αρχικοποίηση
    
    # 1. Καθορισμός Ροής (Input vs Target)
    # Ελέγχουμε το input_radioOption ή το input_name για να δούμε τι ψάχνουμε
    # Υποθέτω ότι το 'input_radioOption' περιέχει τιμές όπως 'Researcher' ή 'Company'
    
    target_is_company = False
    
    # Προσαρμογή ανάλογα με το πώς έρχεται η τιμή από το UI (π.χ. "Ερευνητής", "Researcher", "1")
    if str(input_radioOption).lower() in ['researcher']:
        # Είσοδος: Ερευνητής -> Στόχος: Εταιρείες
        search_col = "researcher_name"
        target_check_col = "company_name" 
        target_is_company = True
    else:
        # Είσοδος: Εταιρεία -> Στόχος: Ερευνητές
        search_col = "company_name"
        target_check_col = "researcher_name"
        target_is_company = False

    print(f"Searching for matches based on input: {input_name} ({search_col})")

    # 2. Εντοπισμός του Χρήστη (Input Entity) στο df_with_arrays
    # Χρησιμοποιούμε lower() και trim() για ασφάλεια στη σύγκριση strings
    entity_row = df_with_arrays.filter(
        lower(trim(col(search_col))) == lower(trim(lit(input_name)))
    ).first()

    if entity_row is None:
        print(f"Προσοχή: Η οντότητα '{input_name}' δεν βρέθηκε στα δεδομένα.")
        # Μπορείς να επιστρέψεις κενό DF ή να κάνεις raise Error
        # raise ValueError(f"Entity {input_name} not found")
    else:
        # Αν βρεθεί, κρατάμε τα 3 βασικά στοιχεία
        my_id = entity_row['id']
        my_cluster = entity_row['prediction']
        
        # Λήψη και καθαρισμός Industry (αν υπάρχει η στήλη 'industry' ή 'company_industry')
        # Βάσει Screenshot μεταβλητών: 22='industry', 15='company_industry'.
        # Χρησιμοποιώ την 'industry' γενικά, ή την 'company_industry' αν είναι εταιρεία.
        col_industry_name = 'industry' if 'industry' in df_with_arrays.columns else 'company_industry'
        my_industry = str(entity_row[col_industry_name]).lower().strip() if entity_row[col_industry_name] else None

        print(f"Entity Found: ID={my_id}, Cluster={my_cluster}, Industry={my_industry}")

        # 3. Φιλτράρισμα για Potential Matches
        # Συνθήκες:
        # α) Ίδιο Cluster (prediction == my_cluster)
        # β) Επιθυμητός τύπος (target_check_col is NOT NULL)
        # γ) Όχι ο εαυτός του (id != my_id)
        
        potential_matches_df = df_with_arrays.filter(
            (col("prediction") == my_cluster) &             # α) Ίδιο Cluster
            (col(target_check_col).isNotNull()) &           # β) Υπάρχει το target name (Εταιρεία ή Ερευνητής)
            (col("id") != my_id)                            # γ) Όχι ο εαυτός μου
        )
        
        # Προαιρετικά: Αν θέλεις να φιλτράρεις ΚΑΙ με βάση το industry (αν το ζητάει η λογική σου αυστηρά):
        # potential_matches_df = potential_matches_df.filter(lower(col(col_industry_name)) == my_industry)
        # List of columns that are not JSON serializable (Vectors)
        cols_to_drop = ['features', 'features_sparse', 'features_norm', 'features_arr']

        # Drop these columns from the Spark DataFrame
        potential_matches_df = potential_matches_df.drop(*cols_to_drop)
    # Επιστροφή και του potential_matches_df
    return centers_df, df_with_arrays, end_time - start_time, df_hyper, potential_matches_df
  



# --- 4. FIRST LSH FUNCTION: Bucketed Random Projection (Cosine/Euclidean) ---
def run_lsh_brp(df, target_name=None, num_neighbors=5):
    print(f"\n--- ⚡ Running LSH: Bucketed Random Projection (Cosine/L2) ---")
    brp = BucketedRandomProjectionLSH(inputCol="features_norm", outputCol="hashes_brp", bucketLength=2.0, numHashTables=3, seed=42)
    start_time = time.time()
    model = brp.fit(df)
    df_transformed = model.transform(df)
    if target_name and target_name.strip():
        print(f"   🔍 BRP Query for: '{target_name}'")
        query_row = df.filter((col("company_name") == target_name) | (col("researcher_name") == target_name)).first()
        
        if query_row:
            query_vec = query_row['features_norm']
            neighbors = model.approxNearestNeighbors(df, query_vec, num_neighbors)
            print(f"   ✅ BRP Neighbors (Low DistCol = More Similar):")
            #neighbors.select("source_type", "company_name", "researcher_name", "distCol").show(truncate=False)
            lsh_brp_count = neighbors.count()
        else:
            print("   ❌ Target not found.")
    end_time = time.time()        
    return df_transformed, end_time - start_time

# --- 5. SECOND LSH FUNCTION: MinHash (Jaccard) ---
def run_lsh_minhash(df, target_name=None, num_neighbors=5):
    print(f"\n--- ⚡ Running LSH: MinHash (Jaccard) ---")
    mh = MinHashLSH(inputCol="features_sparse", outputCol="hashes_mh", numHashTables=5, seed=42)
    start_time = time.time()
    model = mh.fit(df)
    df_transformed = model.transform(df)
    if target_name and target_name.strip():
        print(f"   🔍 MinHash Query for: '{target_name}'")
        query_row = df.filter((col("company_name") == target_name) | (col("researcher_name") == target_name)).first()
        
        if query_row:
            query_vec = query_row['features_sparse']
            neighbors = model.approxNearestNeighbors(df, query_vec, num_neighbors)
            print(f"   ✅ MinHash Neighbors (Low DistCol = High Jaccard Similarity):")
            #neighbors.select("source_type", "company_name", "researcher_name", "distCol").show(truncate=False)
            lsh_minihash_count = neighbors.count()
        else:
            print("   ❌ Target not found.")
    end_time = time.time()
    return df_transformed , end_time - start_time


####  MAIN ### 
#1ο παραδειγμα για researcher
"""
selected_option = "manufacturing"
start_name = " "
researcher_name = "Ryan M. H."
"""
#2o paradeigma gia startup
selected_option = "Advertising & Marketing"
start_name = "MuteSix"
researcher_name = ""
target_search = start_name if start_name.strip() else researcher_name

#####################
#check data for nulls
#type partitioning
#print in front best hyperparameters for all algorithms , plotting wsse
#lsh number neightboors = 5

CORES = 12

spark = SparkSession.builder.appName(f"Benchmark_Cores").master(f"local[{CORES}]").getOrCreate()
spark.sparkContext.setLogLevel("WARN")
partition = CORES * 2
spark.conf.set("spark.sql.shuffle.partitions", str(partition))
spark.sparkContext.setCheckpointDir("/tmp/spark_checkpoints")

"""
spark = (
    SparkSession.builder
    .appName("bench")
    .master("spark://spark-master:7077")
    .config("spark.executor.instances", "4")
    .config("spark.executor.cores", "4")
    .config("spark.executor.memory", "3g")
    .config("spark.driver.memory", "4g")
    .config("spark.sql.shuffle.partitions", "80")
    .config("spark.dynamicAllocation.enabled", "false")
    .config("spark.speculation", "false")
    .getOrCreate()
)
"""



# --- Ο ΕΛΕΓΚΤΗΣ (CONTROLLER) ---
def run_logic(input_industry, input_radioOption, input_algorithms,input_name):
    companies_clean, researchers_clean = parse_data()
    join_df = join_dfs(companies_clean, researchers_clean)
    join_df = join_df.repartition(partition)
    feature_df = preprocessing(join_df)
    feature_df = feature_df.repartition(partition).cache()
    feature_df.count()
    execution_time = []
    hyperparameters_clustering = []

    df_hyperparameters_clustering = pd.DataFrame(columns=["algorithm", "best_k", "best_seed", "best_maxIter", "best_sample_frac", "best_score"])

    algorithms_to_run = input_algorithms
    for algo in algorithms_to_run:
        
        if algo == 'KMeans' or algo == 'BisectingKMeans':
            #,predictive_data
            centers_df,df_with_arrays,time_clustering, df_hyper,potential_matches_df= clustering_algo(feature_df, algo,input_industry,input_name,input_radioOption)
            #hyperparameters_clustering.extend(hyperparam_clustering)
            df_hyperparameters_clustering = pd.concat([df_hyperparameters_clustering,df_hyper ], ignore_index=True)
            execution_time.append([algo, time_clustering])
  
        elif algo == 'LSH_BRP':
            # Τρέχει Cosine LSH
            df_lsh_brp,time_lsh_brp = run_lsh_brp(feature_df, target_name=input_industry, num_neighbors=5)
            execution_time.append([algo, time_lsh_brp])

        elif algo == 'LSH_MinHash':
            # Τρέχει Jaccard LSH
            df_lsh_minihash, time_lsh_minihash = run_lsh_minhash(feature_df, target_name=input_industry, num_neighbors=5)
            execution_time.append([algo, time_lsh_minihash])

    for result in execution_time:
        print(f"Algorithm: {result[0]}, Time: {result[1]:.4f} sec")

    print(df_hyperparameters_clustering)
    return df_hyperparameters_clustering,potential_matches_df


#for result in hyperparameters_clustering:
#    print(result)
    #print("Algorithm:" +str(result[0])+",best_k:"+int(result[1])+", best_seed:"+int(result[2])+", best_maxIter:"+int(result[3])+", best_sample_frac:"+float(result[3])+", best_score:"+float(result[4]))
# --- MAIN FUNCTION ---
def main():
    # Ορισμός παραδειγμάτων εισόδου (όπως τα είχες πιο πάνω στον κώδικα)
    input_industry = "Advertising & Marketing"  # selected_option
    input_radioOption = "start-up"            # Υποθέτουμε start-up βάσει του ονόματος
    input_name = "MuteSix"                    # start_name 
    input_algorithms = ["KMeans"]             # Λίστα αλγορίθμων προς εκτέλεση

    print(f"Running for: Industry={input_industry}, Name={input_name}, Algos={input_algorithms}")

    # Κλήση της λογικής ελέγχου
    run_logic(input_industry, input_radioOption, input_algorithms, input_name)

if __name__ == "__main__":
    main()















#---------------------------------------------------------------------------------------------------------------------------------------------------
# Broadcast Join Κάνουμε Join τα δεδομένα με τα κέντρα βάσει του prediction.Χρησιμοποιούμε broadcast γιατί ο πίνακας των κέντρων είναι πολύ μικρός.

#joined_df = df_with_arrays.join(
#    broadcast(centers_df), 
#    df_with_arrays.prediction == centers_df.center_id, 
#    "left"
#)

# --- 4. Υπολογισμός Ευκλείδειας Απόστασης με Spark SQL ---Χρησιμοποιούμε native Spark functions (zip_with, aggregate, transform)Τύπος: sqrt( sum( (x - y)^2 ) )
#distance_expression = """ sqrt(aggregate(zip_with(features_arr, center_vec, (x, y) -> power(x - y, 2)), 0.0D, (acc, x) -> acc + x ) )"""

#final_df = joined_df.withColumn("distance_to_center", expr(distance_expression)).drop("features_arr", "center_id", "center_vec") # Καθαρισμός ενδιάμεσων στηλών

# --- 5. Έλεγχος Αποτελεσμάτων ---
#final_df.select("company_name", "prediction", "distance_to_center").show(5)


#start_name = (start_name or "").strip()
#researcher_name = (researcher_name or "").strip()

#ορίζω μεταβλητές
#input_col_name = None
#input_value = None
#target_condition = None


#if start_name == "" and researcher_name != "":
#    input_col_name = "researcher_name"
#    input_value = researcher_name
    # Στόχος: Ονόματα εταιριών 
#    target_condition = F.col("company_name").isNotNull()
#elif researcher_name == ""and start_name != "":
#    input_col_name = "company_name"
#    input_value = start_name
    # Στόχος: Ερευνητές 
#    target_condition = F.col("researcher_name").isNotNull()

#input_row_list = final_df.filter(F.col(input_col_name) == input_value).collect()

#if not input_row_list:
#    raise ValueError(f"Δεν βρέθηκε input_value = {input_value}")

   
#input_row = input_row_list[0]
#input_id = input_row["id"] 
#cluster_id = input_row["prediction"]
#input_industry = input_row["industry"]
#input_industry_norm = (input_industry or "").strip().lower()


#potential_matches = final_df.filter((F.col("prediction") == cluster_id) & target_condition &(F.col("id") != input_id))

#industry_match_condition = F.lower(F.trim(F.col("industry"))) == F.lit(input_industry_norm)

# 1o DF: Top Results
#top_results = (potential_matches.filter(industry_match_condition).orderBy(F.col("distance_to_center").asc_nulls_last()))
# --- ΜΕΤΡΗΣΗ ΠΛΗΘΟΥΣ ---
#count_top = top_results.count()
#print(f"--- TOP RESULTS (Total Rows: {count_top}) ---")
# Εμφάνιση των πρώτων 5
#top_results.show(5, truncate=False)



# 2o DF: Recommended Results
#recomended_results = (potential_matches.filter(~industry_match_condition).orderBy(F.col("distance_to_center").asc_nulls_last()))
# --- ΜΕΤΡΗΣΗ ΠΛΗΘΟΥΣ ---
#count_rec = recomended_results.count()
#print(f"--- RECOMMENDED RESULTS (Total Rows: {count_rec}) ---")
#recomended_results.show(5, truncate=False)


#---------------------------------------------------------------------------------------------------------------------------------------------------
# Broadcast Join Κάνουμε Join τα δεδομένα με τα κέντρα βάσει του prediction.Χρησιμοποιούμε broadcast γιατί ο πίνακας των κέντρων είναι πολύ μικρός.

#joined_df = df_with_arrays.join(
#    broadcast(centers_df), 
#    df_with_arrays.prediction == centers_df.center_id, 
#    "left"
#)

# --- 4. Υπολογισμός Ευκλείδειας Απόστασης με Spark SQL ---Χρησιμοποιούμε native Spark functions (zip_with, aggregate, transform)Τύπος: sqrt( sum( (x - y)^2 ) )
#distance_expression = """ sqrt(aggregate(zip_with(features_arr, center_vec, (x, y) -> power(x - y, 2)), 0.0D, (acc, x) -> acc + x ) )"""

#final_df = joined_df.withColumn("distance_to_center", expr(distance_expression)).drop("features_arr", "center_id", "center_vec") # Καθαρισμός ενδιάμεσων στηλών

# --- 5. Έλεγχος Αποτελεσμάτων ---
#final_df.select("company_name", "prediction", "distance_to_center").show(5)


#start_name = (start_name or "").strip()
#researcher_name = (researcher_name or "").strip()

#ορίζω μεταβλητές
#input_col_name = None
#input_value = None
#target_condition = None


#if start_name == "" and researcher_name != "":
#    input_col_name = "researcher_name"
#    input_value = researcher_name
    # Στόχος: Ονόματα εταιριών 
#    target_condition = F.col("company_name").isNotNull()
#elif researcher_name == ""and start_name != "":
#    input_col_name = "company_name"
#    input_value = start_name
    # Στόχος: Ερευνητές 
#    target_condition = F.col("researcher_name").isNotNull()

#input_row_list = final_df.filter(F.col(input_col_name) == input_value).collect()

#if not input_row_list:
#    raise ValueError(f"Δεν βρέθηκε input_value = {input_value}")

   
#input_row = input_row_list[0]
#input_id = input_row["id"] 
#cluster_id = input_row["prediction"]
#input_industry = input_row["industry"]
#input_industry_norm = (input_industry or "").strip().lower()


#potential_matches = final_df.filter((F.col("prediction") == cluster_id) & target_condition &(F.col("id") != input_id))

#industry_match_condition = F.lower(F.trim(F.col("industry"))) == F.lit(input_industry_norm)

# 1o DF: Top Results
#top_results = (potential_matches.filter(industry_match_condition).orderBy(F.col("distance_to_center").asc_nulls_last()))
# --- ΜΕΤΡΗΣΗ ΠΛΗΘΟΥΣ ---
#count_top = top_results.count()
#print(f"--- TOP RESULTS (Total Rows: {count_top}) ---")
# Εμφάνιση των πρώτων 5
#top_results.show(5, truncate=False)



# 2o DF: Recommended Results
#recomended_results = (potential_matches.filter(~industry_match_condition).orderBy(F.col("distance_to_center").asc_nulls_last()))
# --- ΜΕΤΡΗΣΗ ΠΛΗΘΟΥΣ ---
#count_rec = recomended_results.count()
#print(f"--- RECOMMENDED RESULTS (Total Rows: {count_rec}) ---")
#recomended_results.show(5, truncate=False)


