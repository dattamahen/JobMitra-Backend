@echo off
REM ─────────────────────────────────────────────────────────────
REM  JobMitra Backend — Deploy to Cloud Run (Dev)
REM  Prerequisites: gcloud CLI installed and authenticated
REM  Usage: deploy-dev.bat <GCP_PROJECT_ID>
REM ─────────────────────────────────────────────────────────────

SET PROJECT_ID=%1
IF "%PROJECT_ID%"=="" (
    echo ERROR: Pass your GCP project ID as argument
    echo Usage: deploy-dev.bat your-gcp-project-id
    exit /b 1
)

SET IMAGE=gcr.io/%PROJECT_ID%/jobmitra-backend:latest
SET SERVICE=jobmitra-backend-dev
SET REGION=us-central1

echo.
echo [1/4] Setting GCP project...
gcloud config set project %PROJECT_ID%

echo.
echo [2/4] Building and pushing Docker image...
gcloud builds submit --tag %IMAGE% .

echo.
echo [3/4] Deploying to Cloud Run...
gcloud run deploy %SERVICE% ^
  --image=%IMAGE% ^
  --region=%REGION% ^
  --platform=managed ^
  --allow-unauthenticated ^
  --port=8080 ^
  --memory=1Gi ^
  --cpu=1 ^
  --min-instances=0 ^
  --max-instances=3 ^
  --set-env-vars=APP_ENV=dev ^
  --update-secrets=MONGO_URI=MONGO_URI:latest,REDIS_URL=REDIS_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,CORS_ORIGINS=CORS_ORIGINS:latest,FRONTEND_URL=FRONTEND_URL:latest

echo.
echo [4/4] Fetching service URL...
gcloud run services describe %SERVICE% --region=%REGION% --format="value(status.url)"

echo.
echo Done! Copy the URL above (without https://) into your Squarespace CNAME record.
