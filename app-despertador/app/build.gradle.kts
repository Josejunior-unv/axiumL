import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

// O GitHub Actions passa o número da compilação: cada APK novo tem versão maior e instala por cima do anterior.
val versao = (System.getenv("VERSAO_CODIGO") ?: "1").toInt()

android {
    namespace = "br.axiuml.acorda"
    compileSdk = 35

    defaultConfig {
        applicationId = "br.axiuml.acorda"
        minSdk = 26
        targetSdk = 35
        versionCode = versao
        versionName = "1.$versao"
    }

    // Chave fixa, guardada no repositório, para que toda versão nova instale por cima da anterior
    // sem precisar desinstalar (e perder os alarmes). Ver README.
    signingConfigs {
        create("acorda") {
            storeFile = file("acorda.keystore")
            storePassword = "acorda-despertador"
            keyAlias = "acorda"
            keyPassword = "acorda-despertador"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("acorda")
        }
        debug {
            signingConfig = signingConfigs.getByName("acorda")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        compose = true
    }

    lint {
        checkReleaseBuilds = false
        abortOnError = false
    }
}

kotlin {
    compilerOptions { jvmTarget.set(JvmTarget.JVM_17) }
}

dependencies {
    implementation(project(":nucleo"))

    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")

    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-core")

    // Leitor de código de barras e QR que não depende do Google Play Services.
    implementation("com.journeyapps:zxing-android-embedded:4.3.0")
}
