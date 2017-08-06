name := "ti-data-samples"

organization := "org.bom4v.ti"

version := "0.0.1"

scalaVersion := "2.10.6"

crossScalaVersions := Seq("2.10.6", "2.11.8")

checksums in update := Nil

libraryDependencies += "org.specs2" %% "specs2-core" % "3.9.4" % "test"

resolvers ++= Seq(
  Resolver.sonatypeRepo("releases"),
  Resolver.sonatypeRepo("snaspshots"),
  "Local repository"     at "http://localhost/mavenrepo/",
  Resolver.mavenLocal
)


javacOptions in Compile ++= Seq("-source", "1.8",  "-target", "1.8")

scalacOptions ++= Seq("-deprecation", "-feature")

publishTo := Some("TI Maven Repo" at "http://localhost/mavenrepo/")

cleanKeepFiles += target.value / "test-reports"

