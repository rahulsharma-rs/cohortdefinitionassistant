# GCP Cloud Run Deployment Guide (GitHub & Secret Manager)

This guide helps you deploy the **Cohort Definition Assistant** to Google Cloud Run using continuous deployment from GitHub and secure secret management.

---

## 1. Setup Secrets in Secret Manager

Instead of using plain environment variables, we use **Secret Manager** to securely store API keys.

1.  Go to the [Secret Manager Console](https://console.cloud.google.com/security/secret-manager).
2.  **Create Secret**:
    - **Name**: `GOOGLE_API_KEY`
    - **Value**: Paste your Gemini API key.
3.  (Optional) Repeat for `OPENAI_API_KEY`.
4.  **Permissions**:
    - Ensure the [Cloud Run Service Account](https://console.cloud.google.com/iam-admin/iam) (typically `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`) has the **Secret Manager Secret Accessor** role for these secrets.

---

---

## 2. Setup Cloud Storage Volume (Option A: Recommended)

Instead of downloading files, you can mount your GCS bucket directly as a local disk using **Cloud Storage Fuse**.

1.  Go to the [Cloud Storage Console](https://console.cloud.google.com/storage/browser).
2.  **Create Bucket**: e.g., `my-clinical-catalog-data`.
3.  **Upload Data**: 
    - **Option 1 (Easiest)**: Just upload your `.csv` files. The app will automatically build the `cohort.db` and vector index folder inside the bucket the very first time it starts (this initial setup will take 3-5 minutes, but subsequent starts will be instant).
    - **Option 2 (Recommended for 0 downtime)**: Upload the `.csv` files **AND** your local `database/cohort.db` file and the entire `database/storage/` folder. This skips the initial 5-minute build entirely.
    *(Do **NOT** upload `EHR_Population_catelogue.txt`; it is already included in your code repository).*
4.  **Permissions**:
    - Ensure the [Cloud Run Service Account](https://console.cloud.google.com/iam-admin/iam) has the **Storage Object Viewer** role for this bucket.

---

### 4. Deploy to Cloud Run using the GCP UI

1.  Go to the [Cloud Run Console](https://console.cloud.google.com/run).
2.  Click **Create Service**.
3.  **Deploy one revision from an existing container image** (We will use GitHub).
    - Choose **Continuously deploy from a repository**.
    - Click **SET UP WITH CLOUD BUILD**.
    - Connect your GitHub Repository containing this code.
    - Set the branch to `main`.
    - Build Type: **Dockerfile**.
    - Source location: `/Dockerfile`.
    - Click **Save**.
4.  **Service settings**:
    - Choose a region (e.g., `us-central1`).
    - Under **Authentication**, choose **Allow unauthenticated invocations** (Or require authentication if internal only).
    - Expand **Container, Volumes, Networking, Security**:
    - **Volume Mounts**:
        1. Click **Add Volume Mount**.
        2. **Volume**: `clinical-data`.
        3. **Mount Path**: `/mnt/gcs/clinical-data`.
    - **Environment Variables**: Add:
        - `GOOGLE_API_KEY`: (Reference from Secret Manager).
        - `LLM_PROVIDER`: `google`.
        - `CATALOG_DIR`: `/mnt/gcs/clinical-data` (Important: points the app to the mount).
        - `VECTOR_DB_PATH`: `/mnt/gcs/clinical-data/storage` (Critical for instant cold-starts).
        - `SQLITE_DB_PATH`: `/mnt/gcs/clinical-data/cohort.db`
    - **Resources**: Increase memory to **2 GiB** or **4 GiB**.
5.  Click **Create**.

---

## 3. Benefits of this Method

- **Automated Builds**: Every `git push` to your main branch triggers a fresh build and deployment.
- **Improved Security**: Your API keys are never stored in plain text or build logs.
- **Scalability**: Cloud Run handles all traffic scaling and container management automatically.

> [!NOTE]
> The first deployment might take 5-8 minutes as Cloud Build processes the Node.js frontend build and Python backend setup defined in your `Dockerfile`.

---

## 3. Verify Deployment

Once the service is created, GCP will provide a URL (e.g., `https://cohort-assistant-xxxx.a.run.app`). 

1.  Open the URL in your browser.
2.  Test the cohort refinement process.
3.  Check the **Logs** tab in Cloud Run if you encounter any errors (e.g., initialization issues).

> [!IMPORTANT]
> Because Cloud Run is serverless, the first request (cold start) may take longer as the application initializes the SQLite database and builds the vector search index from the catalog CSVs. Increasing the memory to 2GiB or 4GiB helps significantly.
