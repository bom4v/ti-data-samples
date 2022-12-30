resolvers += Classpaths.sbtPluginReleases

// https://github.com/sbt/sbt-maven-resolver
addSbtPlugin("org.scala-sbt" % "sbt-maven-resolver" % "0.1.0")

// https://github.com/scoverage/sbt-scoverage
addSbtPlugin("org.scoverage" % "sbt-scoverage" % "2.0.2")

// https://github.com/sonar-scala/sbt-sonar
addSbtPlugin("com.sonar-scala" % "sbt-sonar" % "2.3.0")

// https://github.com/sbt/sbt-assembly
addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "2.0.0")

//addSbtPlugin("com.typesafe.sbt" % "sbt-native-packager" % "1.3.18")

// The following should be placed in ~/.sbt/1.0/plugins/gpg.sbt
//addSbtPlugin("com.jsuereth" % "sbt-pgp" % "1.1.1")

