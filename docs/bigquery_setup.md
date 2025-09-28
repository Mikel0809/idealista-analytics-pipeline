# BigQuery Setup Guide

This guide helps you set up the necessary BigQuery datasets and permissions for the Madrid Real Estate Analytics Pipeline.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. A GCP project with billing enabled
3. BigQuery API enabled in your project

## Step 1: Set Up Authentication

1. Install the Google Cloud CLI:
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   ```

2. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. Set your project:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

## Step 2: Create Required Datasets

The pipeline requires the following datasets in BigQuery:

1. Open a terminal and run:

```bash
# Create raw data dataset
bq mk --dataset --location=EU YOUR_PROJECT_ID:raw_data

# Create dbt datasets
bq mk --dataset --location=EU YOUR_PROJECT_ID:dbt_base
bq mk --dataset --location=EU YOUR_PROJECT_ID:dbt_staging
bq mk --dataset --location=EU YOUR_PROJECT_ID:dbt_intermediate
bq mk --dataset --location=EU YOUR_PROJECT_ID:dbt_mart
```

Replace `YOUR_PROJECT_ID` with your actual GCP project ID.

## Step 3: Configure dbt Profile

1. Make sure you have a `~/.dbt/profiles.yml` file:
   ```bash
   mkdir -p ~/.dbt
   cp dbt/profiles.yml.example ~/.dbt/profiles.yml
   ```

2. Edit `~/.dbt/profiles.yml` and update:
   - `project` - Your GCP project ID
   - `dataset` - Default dataset (dbt_staging)
   - `location` - Your preferred location (EU)

Example:
```yaml
idealista_analytics:
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: your-gcp-project-id
      dataset: dbt_staging
      threads: 1
      timeout_seconds: 300
      location: EU
      priority: interactive
      retries: 1
  target: dev
```

## Step 4: Configure Environment Variables

1. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update:
   ```
   BIGQUERY_PROJECT_ID=your-gcp-project-id
   BIGQUERY_DATASET=raw_data
   BIGQUERY_LOCATION=EU
   ```

## Step 5: Verify Setup

Run the following command to verify your BigQuery setup:

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify BigQuery connection
python -c "from google.cloud import bigquery; client = bigquery.Client(); print(f'Connected to {client.project}')"

# Verify dbt connection
cd dbt && dbt debug
```

If everything is set up correctly, you should see successful connection messages.

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:
```bash
# Reset application default credentials
gcloud auth application-default revoke
gcloud auth application-default login
```

### Permission Issues

Ensure your account has the following roles:
- BigQuery Data Editor
- BigQuery Job User

You can add these roles with:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member=user:YOUR_EMAIL --role=roles/bigquery.dataEditor
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member=user:YOUR_EMAIL --role=roles/bigquery.jobUser
```

### Dataset Location Issues

All datasets must be in the same location. If you get location errors, verify all datasets are in the same region.
