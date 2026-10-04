import org.jetbrains.kotlin.gradle.dsl.JvmTarget

// As regras do despertar, em Kotlin puro: testáveis sem celular nem emulador.
plugins {
    id("org.jetbrains.kotlin.jvm")
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

kotlin {
    compilerOptions { jvmTarget.set(JvmTarget.JVM_17) }
}

dependencies {
    // No celular quem fornece o org.json é o próprio Android; aqui ele só entra para compilar e testar.
    compileOnly("org.json:json:20240303")
    testImplementation("org.json:json:20240303")
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}
