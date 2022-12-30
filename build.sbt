//
// File: https://github.com/bom4v/ti-data-samples/blob/master/build.sbt
//

name := "ti-data-samples"
organization := "org.bom4v.ti"
organizationName := "Business Object Models for Verticals (BOM4V)"
organizationHomepage := Some(url("http://github.com/bom4v"))
homepage := Some(url("https://github.com/bom4v/ti-data-samples"))
startYear := Some(2019)
description := "Data Samples for BOM for Verticals"
licenses += "Apache-2.0" -> url("https://www.apache.org/licenses/LICENSE-2.0")

scmInfo := Some(
  ScmInfo(
    url("https://github.com/bom4v/ti-data-samples"),
    "https://github.com/bom4v/ti-data-samples.git"
  )
)

developers := List(
  Developer(
    id    = "denis.arnaud",
    name  = "Denis Arnaud",
    email = "denis.arnaud_ossrh@m4x.org",
    url   = url("https://github.com/denisarnaud")
  )
)

//useGpg := true

version := scala.io.Source.fromFile("VERSION").getLines.toList.head
scalaVersion := "2.12.17"
val sparkVersion = "3.3.0"

crossScalaVersions := Seq("2.12.16", "2.12.17")

update / checksums  := Nil
lazy val root = project in file(".")

/**
  * Latest releases:
  * log4j: https://logging.apache.org/log4j/2.x/download.html
  * As log4j is part of the Spark distribution, check its version from
  * the installed PySpark module, e.g.:
  * ~/.pyenv/versions/${PYTHON_VERSION}/lib/python3.9/site-packages/pyspark/jars/
  * scopt: https://github.com/scopt/scopt
  * ScalaTest / Scalactic: https://www.scalatest.org/
  * Spark-fast-test: https://github.com/MrPowers/spark-fast-tests
  */
libraryDependencies ++= Seq(
  "org.apache.logging.log4j" % "log4j-core" % "2.17.2" % "provided",
  "org.apache.logging.log4j" % "log4j-api" % "2.17.2" % "provided",
  "org.apache.logging.log4j" % "log4j-slf4j-impl" % "2.17.2" % "provided",
  "com.github.scopt" %% "scopt" % "4.1.0",
  "com.github.nscala-time" %% "nscala-time" % "2.32.0",
  "org.specs2" %% "specs2-core" % "4.19.0" % "test",
  "org.scalactic" %% "scalactic" % "3.2.14",
  "org.scalatest" %% "scalatest" % "3.2.14" % "test",
  "com.github.mrpowers" %% "spark-fast-tests" % "1.3.0" % "test"
)

// Compilation options
javacOptions ++= Seq("-source", "11")
scalacOptions ++= Seq("-deprecation", "-feature")

// Run main class
Compile / run := Defaults.runTask(
  Compile / fullClasspath,
  Compile / run / mainClass,
  Compile / run / runner
).evaluated

Compile / runMain := Defaults.runMainTask(
  Compile / fullClasspath,
  Compile / run / runner
).evaluated

/**
  * Java runtime options. These options are taken into account only when forking
  * a new JVM (we would need something like 'Compile / run / fork := true'),
  *  which is not the case by default.
  *  See https://github.com/sbt/sbt/issues/2041
  */
// Compile / run / fork := true
// Compile / run / javaOptions ++= Seq("-Xms2048M", "-Xmx4096M", "-XX:+CMSClassUnloadingEnabled")

// Tests
lazy val enablingCoverageSettings = Seq(
  Test / compile / coverageEnabled := true,
  Compile / compile / coverageEnabled := false
)
//Test / compile / coverageEnabled := true
Test / parallelExecution := false
Test / run / fork := true
Test / run / javaOptions ++= Seq("-Xms2048M", "-Xmx4096M", "-XX:+CMSClassUnloadingEnabled")

// Sonar
import sbtsonar.SonarPlugin.autoImport.sonarUseExternalConfig

sonarUseExternalConfig := true

// Assembly and packaging
ThisBuild / versionScheme := Some("early-semver")

pomIncludeRepository := { _ => false }

publishMavenStyle := true

publishTo := {
  val nexus = "https://oss.sonatype.org/"
  if (isSnapshot.value) Some("snapshots" at nexus + "content/repositories/snapshots")
  else Some("releases" at nexus + "service/local/staging/deploy/maven2")
}

