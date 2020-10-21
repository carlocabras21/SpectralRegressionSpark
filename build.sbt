name := "SpectralRegressionSpark"

version := "1.0"

scalaVersion := "2.11.8"

val sparkVersion = "2.4.7"

// https://mvnrepository.com/artifact/org.apache.spark/spark-core
libraryDependencies += "org.apache.spark" %% "spark-core" % sparkVersion
libraryDependencies += "org.apache.spark" %% "spark-sql" % sparkVersion
libraryDependencies += "org.apache.spark" %% "spark-mllib" % sparkVersion

/* Fare attenzione che le versioni di scala, sbt e spark-core coincidano. In questo caso
   la versione di scala presente nel mio computer (2.11.8) è compatibile con la versione
   2.3.2 di    spark-core. Le versioni compatibili le si possono trovare in quel link.
 */


libraryDependencies += "com.opencsv" % "opencsv" % "5.2"

