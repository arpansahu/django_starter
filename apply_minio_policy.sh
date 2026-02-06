#!/bin/bash

# Script to apply MinIO bucket policy
# This secures private files while keeping public files accessible

BUCKET_NAME="arpansahu-one-bucket"
MINIO_ENDPOINT="https://minioapi.arpansahu.space"
MINIO_ACCESS_KEY="arpansahu"
MINIO_SECRET_KEY="Gandu302@minio"
POLICY_FILE="minio_bucket_policy.json"

echo "=========================================="
echo "Applying MinIO Bucket Policy"
echo "=========================================="
echo ""

# Method 1: Using mc (MinIO Client)
echo "Method 1: Using MinIO Client (mc)"
echo "----------------------------------"
echo ""
echo "1. Install mc if not already installed:"
echo "   brew install minio/stable/mc"
echo ""
echo "2. Configure mc alias:"
echo "   mc alias set myminio $MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY"
echo ""
echo "3. Apply the policy:"
echo "   mc anonymous set-json $POLICY_FILE myminio/$BUCKET_NAME"
echo ""

# Method 2: Using AWS CLI
echo "Method 2: Using AWS CLI"
echo "-----------------------"
echo ""
echo "1. Install AWS CLI if not already installed:"
echo "   brew install awscli"
echo ""
echo "2. Apply the policy:"
echo "   aws --endpoint-url=$MINIO_ENDPOINT \\"
echo "       s3api put-bucket-policy \\"
echo "       --bucket $BUCKET_NAME \\"
echo "       --policy file://$POLICY_FILE"
echo ""

# Method 3: Using Python script
echo "Method 3: Using Python (boto3)"
echo "------------------------------"
cat << 'EOF'

import boto3
import json

s3_client = boto3.client(
    's3',
    endpoint_url='https://minioapi.arpansahu.space',
    aws_access_key_id='arpansahu',
    aws_secret_access_key='Gandu302@minio',
    region_name='us-east-1'
)

with open('minio_bucket_policy.json', 'r') as f:
    policy = json.load(f)

s3_client.put_bucket_policy(
    Bucket='arpansahu-one-bucket',
    Policy=json.dumps(policy)
)

print("✅ Bucket policy applied successfully!")

EOF

echo ""
echo "=========================================="
echo "Would you like to apply the policy now?"
echo "=========================================="
echo ""
read -p "Enter method number (1-3) or 'skip': " method

case $method in
    1)
        echo "Applying policy using mc..."
        mc alias set myminio $MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
        mc anonymous set-json $POLICY_FILE myminio/$BUCKET_NAME
        ;;
    2)
        echo "Applying policy using AWS CLI..."
        aws --endpoint-url=$MINIO_ENDPOINT \
            s3api put-bucket-policy \
            --bucket $BUCKET_NAME \
            --policy file://$POLICY_FILE
        ;;
    3)
        echo "Applying policy using Python..."
        python3 << 'PYTHON_EOF'
import boto3
import json

s3_client = boto3.client(
    's3',
    endpoint_url='https://minioapi.arpansahu.space',
    aws_access_key_id='arpansahu',
    aws_secret_access_key='Gandu302@minio',
    region_name='us-east-1'
)

with open('minio_bucket_policy.json', 'r') as f:
    policy = json.load(f)

s3_client.put_bucket_policy(
    Bucket='arpansahu-one-bucket',
    Policy=json.dumps(policy)
)

print("✅ Bucket policy applied successfully!")
PYTHON_EOF
        ;;
    *)
        echo "Skipping policy application."
        ;;
esac

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
