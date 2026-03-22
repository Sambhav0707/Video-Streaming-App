# 📹 Video Streaming Application Architecture

This project is a highly scalable, serverless-oriented **Video Streaming Service** built with a microservices architecture. It allows users to authenticate, securely upload massive video files directly to AWS, transcode them automatically into Adaptive Bitrate streams (HLS/DASH) using serverless Docker containers, and stream them securely on a cross-platform mobile app.

---

## 🏗️ Project Overview & Modules

The system is decoupled into **four distinct components** to ensure max throughput, reliability, and separated concerns:

1.  **`backend` (FastAPI + Postgres + Redis)**
    *   The core metadata hub. Mapped to **AWS Cognito** for JWT Auth.
    *   Generates AWS S3 **pre-signed URLs** to offload upload bandwidth directly to AWS instead of suffocating the Node/Python server.
    *   Implements a **Redis Cache-Aside** pattern to aggressively cache video metadata for near-instant dashboard load times.
2.  **`video_streaming_app_frontend` (Flutter + BLoC)**
    *   A rich, cross-platform client using BLoC for safe state-management.
    *   It retrieves S3 URLs, manages physical file-picking chunks, directly pushes byte streams to AWS S3, and plays back HLS `.m3u8` video formats natively using the `better_player` package.
3.  **`Consumer Service` (Python + Boto3 SQS Poller)**
    *   An isolated background listener. It long-polls an **Amazon SQS** queue connected to the S3 bucket's EventBridge.
    *   Upon receiving an "ObjectCreated" ping, it programmatically triggers the transcoder by calling `ecs.run_task` to spin up a new Fargate instance.
4.  **`Transcoder Service` (Docker + FFmpeg + AWS Fargate)**
    *   The heavy-lifter. Entirely serverless and executed on demand per video.
    *   Downloads the raw video, uses complex `FFmpeg` subprocess pipelines to generate 360p, 720p, and 1080p chunks, and uploads the final streaming playlists back to a pristine S3 bucket for the client to consume.

---

## 🗺️ System Architecture Diagrams

### 1. Video Uploading and Processing Architecture
This diagram explains the orchestration when a user uploads a new video, bypassing the local server, and how the asynchronous transcode worker is spawned organically.

![Video Uploading Architecture](./video%20uploading%20and%20processing%20.png)

### 2. Video Retrieving Architecture
This diagram outlines how the Flutter app rapidly fetches cached feeds and natively buffers the transcoded HLS chunks from the S3 Edge/CDN.

![Video Retrieving Architecture](./video%20retrieving%20.png)

---

## 🛠️ Installation & Setup Guide

### 1. Backend Setup (FastAPI)

**Prerequisites:** Python 3.10+, Docker (optional, for Redis/Postgres)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Environment Variables:**
    Copy the `.env.example` file and fill in your localized database strings and AWS Cognito keys.
    ```bash
    cp .env.example .env
    ```
3.  **Start Database Services (Optional but recommended):**
    If developing locally without managed databases, you can spin up Postgres and Redis rapidly using the provided `docker-compose.yaml` (assuming you have Docker installed).
    ```bash
    docker-compose up -d
    ```
4.  **Install Python Dependencies:**
    You can use standard `pip` or the faster `uv` package manager.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirement.txt
    ```
5.  **Run the Server:**
    FastAPI will boot with uvicorn and watch for hot-reloads.
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

### 2. Frontend Setup (Flutter)

**Prerequisites:** Flutter SDK 3.x, Android Studio / Xcode

1.  **Navigate to the frontend directory:**
    ```bash
    cd video_streaming_app_frontend
    ```
2.  **Link the Backend IP:**
    Unlike web apps, Android simulators cannot read `localhost`. You MUST go to `lib/services/upload_video_service.dart` and swap the hardcoded `backendUrl` IP address out to exactly match your Wi-Fi's IPv4 address where the FastAPI server is actively running.
    *(A `.env.example` has been provided to show how you can transition to using `flutter_dotenv` for this moving forward).*
3.  **Fetch Pub Dependencies:**
    ```bash
    flutter pub get
    ```
4.  **Launch the App:**
    Connect an emulator or physical device via USB debugging.
    ```bash
    flutter run
    ```

---

*For detailed insights regarding explicit AWS tradeoffs (EC2 vs Fargate), FFmpeg presets, SQS structures, or BLoC state mechanisms, please refer to the specific `README.md` files meticulously written inside each of the 4 individual subfolders.*
