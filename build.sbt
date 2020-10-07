name := "SpectralRegressionSpark"

version := "1.0"

scalaVersion := "2.11.8"

// https://mvnrepository.com/artifact/org.apache.spark/spark-core
libraryDependencies += "org.apache.spark" %% "spark-core" % "2.3.2"
libraryDependencies += "org.apache.spark" %% "spark-sql" % "2.3.2"
libraryDependencies += "org.apache.spark" %% "spark-mllib" % "2.3.2"

/* Fare attenzione che le versioni di scala, sbt e spark-core coincidano. In questo caso
   la versione di scala presente nel mio computer è compatibile con la versione 2.2.0 di
   spark-core. Le versioni compatibili le si possono trovare in quel link.
 */


libraryDependencies += "com.opencsv" % "opencsv" % "5.2"

