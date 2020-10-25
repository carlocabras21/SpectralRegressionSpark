'''
InDepth: Parameter tuning for Decision Tree
https://medium.com/@mohtedibf/indepth-parameter-tuning-for-decision-tree-6753118a03c3

In Depth: Parameter tuning for Random Forest
https://medium.com/all-things-ai/in-depth-parameter-tuning-for-random-forest-d67bb7e920d

Regression Trees
https://uc-r.github.io/regression_trees

Testare i diversi tipi di regression presenti qua?
https://spark.apache.org/docs/latest/ml-classification-regression.html





'''

import os
import pwd
import time
from datetime import datetime

from pyspark               import SparkContext, SparkConf, SQLContext
from pyspark.sql           import functions as F
from pyspark.sql.types     import StructType, StructField, DoubleType, StringType
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature    import VectorAssembler
from pyspark.ml.regression import LinearRegression, DecisionTreeRegressor, RandomForestRegressor
from pyspark.ml.tuning     import CrossValidator, ParamGridBuilder

print("\n\n\n *******\n\n\n")
print(" BEGIN")
print("\n\n\n *******\n\n\n")

# -----------------------------------------------------------------------------------------------------------
# SETUP

# set test = True if you want to use data from test.csv, a small portion of the dataset
test = True

# uncomment what type of regression you want to do
regression_type = "linear"
# regression_type = "decision_tree"
# regression_type = "random_forest"

# check if the user is "yarn", in this case we are in EMR cluster and not locally
in_emr = pwd.getpwuid(os.getuid()).pw_name == "yarn"




# -----------------------------------------------------------------------------------------------------------
# STARTUP

# timer starts here, I want to check whole performance of the script,
# including Spark startup and data loading
start = time.time()

# spark 1.6.1 configuration for EMR
conf = SparkConf().setAppName("Spectral Regression in Spark")\
                  .set("spark.shuffle.service.enabled",   "false")\
                  .set("spark.dynamicAllocation.enabled", "false")

sc = SparkContext(conf=conf)
sc.setLogLevel("WARN")
sqlContext = SQLContext(sc)


# -----------------------------------------------------------------------------------------------------------
# DATA LOADING

path     = "s3a://spectral-regression-spark-bucket" if in_emr else "resources"
fileName = "test.csv" if test else "spectral_data_class.csv"

inputFile = path + "/" + fileName
print(inputFile)

# load CSV into RDD
print("Loading RDD...")
rdd = sc.textFile(inputFile)

# remove header, split lines and map data into types required
header = rdd.first()
data   = rdd.filter(lambda line:  line != header) \
            .map(lambda l: l.split(',')) \
            .map(lambda e: (float(e[0]), float(e[1]), float(e[2]), float(e[3]), float(e[4]), e[5], float(e[6]) ))

# build the data scheme for DataFrame
schema = StructType([
    StructField("spectroFlux_u", DoubleType(), True),
    StructField("spectroFlux_g", DoubleType(), True),
    StructField("spectroFlux_r", DoubleType(), True),
    StructField("spectroFlux_i", DoubleType(), True),
    StructField("spectroFlux_z", DoubleType(), True),
    StructField("source_class",  StringType(), True),
    StructField("redshift",      DoubleType(), True)])

# create DataFrame from RDD and schema
print("Creating DataFrame from RDD...")
df = sqlContext.createDataFrame(data, schema)

print("\nSchema of original DataFrame:")
df.printSchema()

# show min and max values of redshift
# df.agg(F.min(df["redshift"]),F.max(df["redshift"])).show()
# -> min: -0.01144691,  max: 7.055639

#  add columns with differences between spectra and remove unnecessary columns
df_diff = df.withColumn("u_g", df["spectroFlux_u"] - df["spectroFlux_g"]) \
            .withColumn("g_r", df["spectroFlux_g"] - df["spectroFlux_r"]) \
            .withColumn("r_i", df["spectroFlux_r"] - df["spectroFlux_i"]) \
            .withColumn("i_z", df["spectroFlux_i"] - df["spectroFlux_z"]) \
            .drop("spectroFlux_u") \
            .drop("spectroFlux_g") \
            .drop("spectroFlux_r") \
            .drop("spectroFlux_i") \
            .drop("spectroFlux_z") \
            .drop("source_class")
#         .limit(10000) # for testing

print("\nSchema of DataFrame with differences between spectral classes:")
df_diff.printSchema()

# regression methods need training features in a single vector
assembler = VectorAssembler() \
    .setInputCols(["u_g", "g_r", "r_i", "i_z"]) \
    .setOutputCol("features")

# remove old columns, keeping only "features" vector and "redshift" class-label
df_ready = assembler.transform(df_diff) \
                    .drop("u_g") \
                    .drop("g_r") \
                    .drop("r_i") \
                    .drop("i_z")

print("\nSchema of DataFrame ready for regression models:")
df_ready.printSchema()


# -----------------------------------------------------------------------------------------------------------
# TRAINING

# split the data
training_data, test_data = df_ready.randomSplit([0.9, 0.1])

if regression_type == "linear":
    # Linear Regressor setup
    lr        = LinearRegression(featuresCol="features", labelCol="redshift", maxIter=10, regParam=0.3, elasticNetParam=0.8)
    evaluator = RegressionEvaluator(labelCol="redshift", predictionCol="prediction", metricName="rmse")

    # fit
    print("\nTraining Linear Regressor on training data...")
    model = lr.fit(training_data)
    print("...done.\n")

if regression_type == "decision_tree":
    # Decision Tree Regressor setup
    dt        = DecisionTreeRegressor(labelCol="redshift", featuresCol  ="features",   maxDepth=4)
    paramGrid = ParamGridBuilder().build()
    evaluator = RegressionEvaluator(labelCol="redshift", predictionCol="prediction", metricName="rmse")
    cv        = CrossValidator(estimator=dt, evaluator=evaluator, estimatorParamMaps=paramGrid, numFolds=3)

    # fit
    print("\nTraining Decision Tree Regressor on training data...")
    model = cv.fit(training_data)
    print("...done.\n")

if regression_type == "random_forest":
    rf        = RandomForestRegressor(labelCol="redshift", featuresCol  ="features", numTrees=8,  maxDepth=8)

    paramGrid = ParamGridBuilder().build()
    evaluator = RegressionEvaluator(labelCol="redshift", predictionCol="prediction", metricName="rmse")
    cv        = CrossValidator(estimator=rf, evaluator=evaluator, estimatorParamMaps=paramGrid, numFolds=3)

    # fit
    print("\nTraining Random Forest Regressor on training data...")
    model = cv.fit(training_data)
    print("...done.\n")

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

# save results in S3 in a folder called "results_<regression_type>_<date-time>".
# data will be in file PART-00000
if in_emr:
    now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    results_rdd = sc.parallelize([r, t])
    results_rdd.coalesce(1).saveAsTextFile("s3a://spectral-regression-spark-bucket/results_" + regression_type + "_" + now)

print("\n\n\n *******\n\n\n")
print(" END")
print("\n\n\n *******\n\n\n")

sc.stop()


# /* parte con training set e test set
# # dopo la creazione di df_ready

# # Train a DecisionTree model.
# val dt = new DecisionTreeRegressor()
#     .setLabelCol("redshift")
#     .setFeaturesCol("features")
#     .setMaxDepth(4)


# # Split the data into training and test sets
# val Array(training_data, test_data) = df_ready.randomSplit(Array(0.9, 0.1))

# # Pipeline consists only in the tree
# val pipeline = new Pipeline()
#     .setStages(Array(dt))

# val model = pipeline.fit(training_data)

# # Make predictions.
# val predictions = model.transform(test_data)

# # Select (prediction, true label) and compute test error.
# val evaluator = new RegressionEvaluator()
#     .setLabelCol("redshift")
#     .setPredictionCol("prediction")
#     .setMetricName("rmse")
# val rmse = evaluator.evaluate(predictions)
# println(s"Root Mean Squared Error (RMSE) on test data = $rmse")

# val treeModel = model.stages(1).asInstanceOf[DecisionTreeRegressionModel]
# println(s"Learned regression tree model:\n ${treeModel.toDebugString}")

# https:#stackoverflow.com/questions/29716949/can-spark-use-multicore-properly

'''
How do I submit Spark jobs to an Amazon EMR cluster from a remote machine or edge node?
https:#aws.amazon.com/it/premiumsupport/knowledge-center/emr-submit-spark-job-remote-cluster/

How to run Python Spark code on Amazon Aws?
https:#stackoverflow.com/questions/40443659/how-to-run-python-spark-code-on-amazon-aws

spark-submit from outside AWS EMR cluster
https:#stackoverflow.com/questions/50750470/spark-submit-from-outside-aws-emr-cluster
'''