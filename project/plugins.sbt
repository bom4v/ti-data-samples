resolvers += Classpaths.sbtPluginReleases

addSbtPlugin("com.typesafe.sbt" % "sbt-native-packager" % "1.3.18")

// The following should be placed in ~/.sbt/1.0/plugins/gpg.sbt
//addSbtPlugin("com.jsuereth" % "sbt-pgp" % "1.1.1")

addSbtPlugin("net.virtual-void" % "sbt-dependency-graph" % "0.9.2")

addSbtPlugin("org.scoverage" % "sbt-scoverage" % "1.5.1")

addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "0.14.9")

