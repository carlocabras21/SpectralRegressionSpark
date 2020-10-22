from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import DecisionTreeRegressor
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.sql.types import FloatType, StringType, StructType, DoubleType, StructField
from pyspark import SparkContext, SparkConf, SQLContext

print("\n\n\n *******\n\n\n")
print(" BEGIN")
print("\n\n\n *******\n\n\n")

# spark 1.6 configuration for EMR

conf = SparkConf().setAppName("Spectral Regression in Spark")\
    .set("spark.shuffle.service.enabled", "false")\
    .set("spark.dynamicAllocation.enabled", "false")

sc = SparkContext(conf=conf)
sc.setLogLevel("WARN")
sqlContext = SQLContext(sc)

# build the data scheme used in the csv files
schema = StructType([
    StructField("spectroFlux_u", DoubleType(), True),
    StructField("spectroFlux_g", DoubleType(), True),
    StructField("spectroFlux_r", DoubleType(), True),
    StructField("spectroFlux_i", DoubleType(), True),
    StructField("spectroFlux_z", DoubleType(), True),
    StructField("source_class",  StringType(), True),
    StructField("redshift",      DoubleType(), True)])

# load CSV into RDD, remove header, split the lines and create DataFrame

# inputFile = "resources/spectral_data_class.csv"
inputFile = "resources/test.csv"
# inputFile  = "s3://spectral-regression-spark-bucket/test.csv"
outputFile = "s3://spectral-regression-spark-bucket/output.txt"
print(inputFile)

rdd = sc.textFile(inputFile)

header = rdd.first()
data = rdd.filter(lambda line:  line != header) \
          .map(lambda l: l.split(',')) \
          .map(lambda e: (float(e[0]), float(e[1]), float(e[2]), float(e[3]), float(e[4]), e[5], float(e[6]) ))
print("rdd data count:")
print(data.count())

df = sqlContext.createDataFrame(data, schema)

print("df schema:")
df.printSchema()

print("df count:")
print(df.count())


# show min and max values of redshift
# df.agg(min("redshift"), max("redshift")).show()

# remove source class and compute differences between spectra
df2 = df.withColumn("u_g", df["spectroFlux_u"] - df["spectroFlux_g"]) \
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

print("df2 schema:")
df2.printSchema()

# keep the features in a single vector named "features"
assembler = VectorAssembler() \
    .setInputCols(["u_g", "g_r", "r_i", "i_z"]) \
    .setOutputCol("features")

# remove old features, now df3 consists in "features" vector and "redshift" class-label
df3 = assembler.transform(df2) \
    .drop("u_g")\
    .drop("g_r")\
    .drop("r_i")\
    .drop("i_z")\

print("df3 schema:")
df3.printSchema()

# split the data, train a regressor and make predictions

trainingData, testData = df3.randomSplit([0.9, 0.1])
print("trainingData count")
print(trainingData.count())

print("training...")
dt = DecisionTreeRegressor(labelCol="redshift", featuresCol="features", maxDepth=4)
paramGrid = ParamGridBuilder().build()
evaluator = RegressionEvaluator(labelCol="redshift", predictionCol="prediction", metricName="rmse")

cv = CrossValidator(estimator=dt, evaluator=evaluator, estimatorParamMaps=paramGrid, numFolds=3)
cvModel = cv.fit(trainingData)
predictions = cvModel.transform(testData)

rmse = evaluator.evaluate(predictions)
print("...done.")
s = "Root Mean Squared Error (RMSE) on test data = " + str(rmse)
print(s)

# with open(outputFile) as f:
#     f.write(s)


print("\n\n\n *******\n\n\n")
print(" END")
print("\n\n\n *******\n\n\n")

sc.stop()


# /* parte con training set e test set
# # dopo la creazione di df3

# # Train a DecisionTree model.
# val dt = new DecisionTreeRegressor()
#     .setLabelCol("redshift")
#     .setFeaturesCol("features")
#     .setMaxDepth(4)


# # Split the data into training and test sets
# val Array(trainingData, testData) = df3.randomSplit(Array(0.9, 0.1))

# # Pipeline consists only in the tree
# val pipeline = new Pipeline()
#     .setStages(Array(dt))

# val model = pipeline.fit(trainingData)

# # Make predictions.
# val predictions = model.transform(testData)

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