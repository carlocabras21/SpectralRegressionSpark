from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import DecisionTreeRegressor
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.sql.types import FloatType, StringType, StructType, DoubleType, StructField
from pyspark import SparkContext, SparkConf, SQLContext


'''

Capire perche' non riesco ad accedere ad S3.

forse non ho fatto partire gli slave
controllare le porte in entrata ed uscita dagli slave

'''

# sparkk 2.0+
# from pyspark.sql import SparkSession

# Create a Scala Spark Context.

# spark 1.6 per EMR
conf = SparkConf().setAppName("Spectral Regression in Spark")\
    .set("spark.shuffle.service.enabled", "false")\
    .set("spark.dynamicAllocation.enabled", "false")

sc = SparkContext(conf=conf)
sc.setLogLevel("WARN")
sqlContext = SQLContext(sc)

# spark 2.0+ per locale
# sc = SparkContext()
# spark = SparkSession \
#     .builder \
#     .appName("Python Spark training model") \
#     .config("spark.some.config.option", "some-value") \
#     .getOrCreate()
# spark.sparkContext.setLogLevel("ERROR")

# build the data scheme in the csv files
schema = StructType([
    StructField("spectroFlux_u", FloatType(), True),
    StructField("spectroFlux_g", FloatType(), True),
    StructField("spectroFlux_r", FloatType(), True),
    StructField("spectroFlux_i", FloatType(), True),
    StructField("spectroFlux_z", FloatType(), True),
    StructField("source_class",  StringType(), True),
    StructField("redshift",      DoubleType(), True)])


# read only one file
# inputFile = "src/main/resources/spectral_data_class.csv"
# inputFile = "home/SparkRegressionScala/src/main/resources/test.csv"
inputFile  = "s3://spectral-regression-spark-bucket/test.csv"
outputFile = "s3://spectral-regression-spark-bucket/output.txt"
# df = spark.read.csv(inputFile, header=True, schema=schema)

# df = sqlContext.read.format("com.databricks.spark.csv").option("header", "true").load(inputFile, schema=schema)

print("\n\n\n*******\n\n\n")
print(inputFile)
print("\n\n\n*******\n\n\n")
with open(outputFile) as f:
    f.write("provaaa")

# load CSV into RDD and transform it into a Dataframe
rdd = sc.textFile(inputFile).map(lambda x: x.split(","))
rdd.mapPartitionsWithIndex( lambda idx, other : other.drop(1) if idx == 0 else other)
print(rdd.count())
df = rdd.toDF(schema)

print("df schema:")
df.printSchema()

print("\n\n\n *******\n\n\n")
print(df.count())
print("\n\n\n *******\n\n\n")

print("\n\n\n *******\n\n\n")
print(" FINE PROGRAMMA")
print("\n\n\n *******\n\n\n")

with open(outputFile) as f:
    f.write(df.count())

sc.stop()

'''
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

trainingData, testData = df3.randomSplit([0.9, 0.1])

dt = DecisionTreeRegressor(labelCol="redshift", featuresCol="features", maxDepth=4)
paramGrid = ParamGridBuilder().build()
evaluator = RegressionEvaluator(labelCol="redshift", predictionCol="prediction", metricName="rmse")

cv = CrossValidator(estimator=dt, evaluator=evaluator, estimatorParamMaps=paramGrid, numFolds=3)
cvModel = cv.fit(trainingData)
predictions = cvModel.transform(testData)

rmse = evaluator.evaluate(predictions)
print("\n\n\n*******\n\n\n")
print("Root Mean Squared Error (RMSE) on test data = " + str(rmse))
print("\n\n\n*******")

'''

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