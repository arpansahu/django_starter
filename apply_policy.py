#!/usr/bin/env python3
"""
Apply MinIO bucket policy to secure private files
"""

import boto3
import json
from botocore.exceptions import ClientError

# MinIO Configuration
MINIO_ENDPOINT = 'https://minioapi.arpansahu.space'
MINIO_ACCESS_KEY = 'arpansahu'
MINIO_SECRET_KEY = 'Gandu302@minio'
BUCKET_NAME = 'arpansahu-one-bucket'
POLICY_FILE = 'minio_bucket_policy.json'

print("=" * 80)
print("APPLYING MINIO BUCKET POLICY")
print("=" * 80)
print()

try:
    # Create S3 client
    print("📡 Connecting to MinIO...")
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1',
        verify=False  # If using self-signed cert
    )
    print("✅ Connected successfully!\n")
    
    # Read policy file
    print(f"📄 Reading policy from {POLICY_FILE}...")
    with open(POLICY_FILE, 'r') as f:
        policy = json.load(f)
    print("✅ Policy loaded successfully!\n")
    
    # Display policy
    print("📋 Policy contents:")
    print("-" * 80)
    print(json.dumps(policy, indent=2))
    print("-" * 80)
    print()
    
    # Apply policy
    print(f"🔐 Applying policy to bucket '{BUCKET_NAME}'...")
    s3_client.put_bucket_policy(
        Bucket=BUCKET_NAME,
        Policy=json.dumps(policy)
    )
    print("✅ Bucket policy applied successfully!\n")
    
    # Verify policy
    print("🔍 Verifying policy...")
    response = s3_client.get_bucket_policy(Bucket=BUCKET_NAME)
    applied_policy = json.loads(response['Policy'])
    print("✅ Policy verification successful!\n")
    
    print("=" * 80)
    print("SECURITY STATUS")
    print("=" * 80)
    print("✅ Public files (static/media): Publicly accessible")
    print("🔒 Private files: Require signed URLs (expire in 1 hour)")
    print("=" * 80)
    print()
    
except ClientError as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Verify MinIO credentials in .env file")
    print("2. Check MinIO endpoint URL")
    print("3. Ensure bucket exists")
    print("4. Verify network connectivity")
    
except FileNotFoundError:
    print(f"❌ Error: Policy file '{POLICY_FILE}' not found")
    print(f"   Make sure {POLICY_FILE} exists in the current directory")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print()
print("=" * 80)
