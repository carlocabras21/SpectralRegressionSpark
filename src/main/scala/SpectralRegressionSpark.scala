import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.evaluation.RegressionEvaluator
import org.apache.spark.ml.feature.VectorAssembler
import org.apache.spark.ml.regression.DecisionTreeRegressor
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types.{FloatType, StringType, StructType}
import org.apache.spark.{SparkConf, SparkContext}

object SpectralRegressionSpark {

    def main(args: Array[String]) {

        // Create a Scala Spark Context.
        val conf = new SparkConf().setAppName("test").setMaster("local") // .setMaster("local") fa funzionare le cose
        //noinspection ScalaUnusedSymbol
        val sc = new SparkContext(conf) // anche se non viene mai usato, serve per poter funzionare.


        val spark = SparkSession.builder().getOrCreate() // bisogna creare questo coso "spark" che in spark-shell è già presente
        spark.sparkContext.setLogLevel("ERROR")

        // build the data scheme in the csv files
        val schema = new StructType()
            .add("spectroFlux_u", FloatType)
            .add("spectroFlux_g", FloatType)
            .add("spectroFlux_r", FloatType)
            .add("spectroFlux_i", FloatType)
            .add("spectroFlux_z", FloatType)
            .add("source_class",  StringType)
            .add("redshift",      FloatType)

        // read only one file
        val inputFile = "src/main/resources/spectral_data_class.csv"
        val df = spark.read.option("header",value = true).schema(schema).csv(inputFile)
        println("df schema:")
        df.printSchema()

        // show min and max values of redshift
//        df.agg(min("redshift"), max("redshift")).show()


        // remove source class and compute differences between spectra
        val df2 = df.withColumn("u_g", df("spectroFlux_u") - df("spectroFlux_g"))
                    .withColumn("g_r", df("spectroFlux_g") - df("spectroFlux_r"))
                    .withColumn("r_i", df("spectroFlux_r") - df("spectroFlux_i"))
                    .withColumn("i_z", df("spectroFlux_i") - df("spectroFlux_z"))
                    .drop("spectroFlux_u")
                    .drop("spectroFlux_g")
                    .drop("spectroFlux_r")
                    .drop("spectroFlux_i")
                    .drop("spectroFlux_z")
                    .drop("source_class")
                    .limit(10000) // for testing

        println("df2 schema:")
        df2.printSchema()

        // keep the features in a single vector
        val assembler = new VectorAssembler()
                          .setInputCols(Array("u_g", "g_r", "r_i", "i_z"))
                          .setOutputCol("features")

        val df3 = assembler.transform(df2).drop("u_g", "g_r", "r_i", "i_z")
        println("df3 schema:")
        df3.printSchema()

        // Train a DecisionTree model.
        val dt = new DecisionTreeRegressor()
            .setLabelCol("redshift")
            .setFeaturesCol("features")
            .setMaxDepth(4)


        // Split the data into training and test sets
        val Array(trainingData, testData) = df3.randomSplit(Array(0.9, 0.1))

        // Pipeline consists only in the tree
        val pipeline = new Pipeline()
            .setStages(Array(dt))

        // Train model. This also runs the indexer.
        val model = pipeline.fit(trainingData)

        // Make predictions.
        val predictions = model.transform(testData)

        // Select (prediction, true label) and compute test error.
        val evaluator = new RegressionEvaluator()
            .setLabelCol("redshift")
            .setPredictionCol("prediction")
            .setMetricName("rmse")
        val rmse = evaluator.evaluate(predictions)
        println(s"Root Mean Squared Error (RMSE) on test data = $rmse")


//        val treeModel = model.stages(1).asInstanceOf[DecisionTreeRegressionModel]
//        println(s"Learned regression tree model:\n ${treeModel.toDebugString}")

        // https://stackoverflow.com/questions/29716949/can-spark-use-multicore-properly

        /*
        How do I submit Spark jobs to an Amazon EMR cluster from a remote machine or edge node?
        https://aws.amazon.com/it/premiumsupport/knowledge-center/emr-submit-spark-job-remote-cluster/

        How to run Python Spark code on Amazon Aws?
        https://stackoverflow.com/questions/40443659/how-to-run-python-spark-code-on-amazon-aws

        spark-submit from outside AWS EMR cluster
        https://stackoverflow.com/questions/50750470/spark-submit-from-outside-aws-emr-cluster


         */
    }
}