# Analytics-Server Project 📊
> **Looking for the Android Client?** Check out the 
[Android SDK & Demo App Repository](https://github.com/NadavDaniel1/Analytics-Android-SDK)

A complete analytics solution including an Android SDK, a Python Backend Server, and a Cloud Database.

## 🚀 Overview
This project demonstrates a full-stack analytics architecture. It allows Android developers to easily track user events, store them locally when offline, and sync them to a remote server when online.

<img width="2816" height="1536" alt="system_design" src="https://github.com/user-attachments/assets/784f13ed-7830-43ae-a6bc-eb885c946c25" />

## 🛠 Architecture
* **Android SDK:** Written in Kotlin. Uses **Room** for offline caching and **Retrofit** for API calls.
* **Backend API:** Python **Flask** server.
* **Database:** **MongoDB Atlas** (Cloud NoSQL).
* **Visualization:** MongoDB Charts Dashboard.

## 📱 Android SDK Installation
Add the library to your project and initialize it in your `MainActivity`:

```kotlin
// Initialize the SDK
AnalyticsManager.init(this)

// Track an event
AnalyticsManager.trackEvent("Button_Clicked", mapOf("user_type" to "student"))
