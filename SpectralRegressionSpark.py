import os
import pwd
import sys
import time
from datetime import datetime

from pyspark               import SparkContext, SparkConf, SQLContext
from pyspark.sql           import SparkSession
from pyspark.sql.types     import StructType, StructField, DoubleType, StringType
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature    import VectorAssembler
from pyspark.ml.regression import LinearRegression, DecisionTreeRegressor, RandomForestRegressor
from pyspark.ml.tuning     import CrossValidator, ParamGridBuilder


# -----------------------------------------------------------------------------------------------------------
# SCRIPT SETUP

# flags
test                = False  # to use data from test.csv, a small portion of the dataset
write_results_in_S3 = True  # to write results in an external file in S3

filtered_data_testing = False # use only 2 of 3 source classes
# if the above is True, uncomment what type of filter you want to do (only one):
filter_type = "star-galaxy"
# filter_type = "star-qso"
# filter_type = "galaxy-qso"

# uncomment what type of regression you want to do (only one)
regression_type = "linear"
# regression_type = "decision-tree"
# regression_type = "random-forest"






# -----------------------------------------------------------------------------------------------------------
# SPARK STARTUP

# check if the user is "hadoop" or "yarn", in this case we are in EMR cluster and not locally;
# unless your username is one of those...
pw_name = pwd.getpwuid(os.getuid()).pw_name
in_emr  = pw_name == "hadoop" or pw_name == "yarn" # user "hadoop" in deploy-mode client, "yarn" in deploy-mode cluster 

# big message because I want to find my prints within spark/yarn logs
print("\n\n\n *******\n\n\n")
print(" BEGIN")
print("\n\n\n *******\n\n\n")

# spark 2.x configuration for EMR
sc = SparkContext()
spark = SparkSession \
    .builder \
    .appName("Spectral Regression Spark") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")


# -----------------------------------------------------------------------------------------------------------
# DATA LOADING

# set the right path 
path     = "s3://spectral-regression-spark-bucket" if in_emr else "resources"
fileName = "test.csv" if test else "spectral_data_class.csv"

inputFile = path + "/" + fileName
print(inputFile)

# data scheme for DataFrame
schema = StructType([
    StructField("spectroFlux_u", DoubleType(), True),
    StructField("spectroFlux_g", DoubleType(), True),
    StructField("spectroFlux_r", DoubleType(), True),
    StructField("spectroFlux_i", DoubleType(), True),
    StructField("spectroFlux_z", DoubleType(), True),
    StructField("source_class",  StringType(), True),
    StructField("redshift",      DoubleType(), True)])

print("Loading DataFrame from file...")
df = spark.read.csv(inputFile, header=True, schema=schema)

print("\nSchema of original DataFrame:")
df.printSchema()

#  add columns with differences between spectra and remove unnecessary columns
df_diff = df.withColumn("u_g", df["spectroFlux_u"] - df["spectroFlux_g"]) \
            .withColumn("g_r", df["spectroFlux_g"] - df["spectroFlux_r"]) \
            .withColumn("r_i", df["spectroFlux_r"] - df["spectroFlux_i"]) \
            .withColumn("i_z", df["spectroFlux_i"] - df["spectroFlux_z"]) \
            .drop("spectroFlux_u") \
            .drop("spectroFlux_g") \
            .drop("spectroFlux_r") \
            .drop("spectroFlux_i") \
            .drop("spectroFlux_z") 

print("\nSchema of DataFrame with differences between spectral classes:")
df_diff.printSchema()

# regression methods need training features in a single vector
assembler = VectorAssembler() \
    .setInputCols(["u_g", "g_r", "r_i", "i_z"]) \
    .setOutputCol("features")

# remove old columns, keeping "features" vector, "source-class" and "redshift" class-label
df_features = assembler.transform(df_diff) \
                    .drop("u_g") \
                    .drop("g_r") \
                    .drop("r_i") \
                    .drop("i_z")

print("\nSchema of DataFrame without old columns:")
df_features.printSchema()

if filtered_data_testing:
    if   filter_type == "star-galaxy":
        df_ready = df_features.filter(df.source_class != "QSO").drop("source_class")

    elif filter_type == "star-qso":
        df_ready = df_features.filter(df.source_class != "GALAXY").drop("source_class")

    elif filter_type == "galaxy-qso":
        df_ready = df_features.filter(df.source_class != "STAR").drop("source_class")

    else:
        print("ERROR\nWrong filter_type string.")
        print("Choose between: star-galaxy, star-qso, galaxy-qso.")
        print("Exiting.")
        sc.stop()
        sys.exit()
else:
    df_ready = df_features#.drop("source_class")

print("\nSchema of DataFrame ready for regression models:")
df_ready.printSchema()

# -----------------------------------------------------------------------------------------------------------
# TRAINING


# split the data
training_data, test_data = df_ready.randomSplit([0.9, 0.1])


start = time.time()
if regression_type == "linear":
    # Linear Regressor setup
    lr        = LinearRegression(featuresCol="features", labelCol="redshift", maxIter=10, regParam=0.3, elasticNetParam=0.8)
    evaluator = RegressionEvaluator(labelCol="redshift", predictionCol="prediction", metricName="rmse")

    # fit
    print("\nTraining Linear Regressor on training data...")
    model = lr.fit(training_data)
    print("...done.\n")

elif regression_type == "decision-tree":
    # Decision Tree Regressor setup
    dt        = DecisionTreeRegressor(labelCol="redshift", featuresCol  ="features",   maxDepth=10)
    paramGrid = ParamGridBuilder().build()
    evaluator = RegressionEvaluator(labelCol="redshift", predictionCol="prediction", metricName="rmse")
    cv        = CrossValidator(estimator=dt, evaluator=evaluator, estimatorParamMaps=paramGrid, numFolds=10)

    # fit
    print("\nTraining Decision Tree Regressor on training data...")
    model = cv.fit(training_data)
    print("...done.\n")

elif regression_type == "random-forest":
    # Random Forest Regressor setup
    rf        = RandomForestRegressor(labelCol="redshift", featuresCol  ="features", numTrees=8,  maxDepth=10)
    paramGrid = ParamGridBuilder().build()
    evaluator = RegressionEvaluator(labelCol="redshift", predictionCol="prediction", metricName="rmse")
    cv        = CrossValidator(estimator=rf, evaluator=evaluator, estimatorParamMaps=paramGrid, numFolds=5)

    # fit
    print("\nTraining Random Forest Regressor on training data...")
    model = cv.fit(training_data)
    print("...done.\n")

else:
    print("ERROR\nWrong regression-type string.")
    print("Choose between: linear, decision-tree, random-forest.")
    print("Exiting.")
    sc.stop()
    sys.exit()

print("\nEvaluating model on test data...\n")
predictions = model.transform(test_data)

# compute error
rmse = evaluator.evaluate(predictions)

end = time.time()

# -----------------------------------------------------------------------------------------------------------
# PRINT RESULTS

r = "Root Mean Squared Error (RMSE) on test data = " + str(rmse)
t = "Time elapsed: " + str(end-start)
print("\n" + r + "\n\n" + t)

# save results in S3 in a folder called "results_<regression-type>_<date-time>".
# data will be in file PART-00000
if write_results_in_S3 and in_emr:
    now = datetime.now().strftime("%d%m%y-%H%M%S") # e.g. 26/10/2020 17:01:52 -> 151020-180152
    results_rdd = sc.parallelize([r, t])

    # make the S3 folder name
    s3_f_name = "s3a://spectral-regression-spark-bucket/results_4xm4large_" + regression_type + "_" + now
    if filtered_data_testing:
        s3_f_name = s3_f_name + "_" + filter_type
    results_rdd.coalesce(1).saveAsTextFile(s3_f_name)

print("\n\n\n *******\n\n\n")
print(" END")
print("\n\n\n *******\n\n\n")

sc.stop()
