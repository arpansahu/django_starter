"""
Test script to verify public and private file storage behavior
Run this with: python manage.py shell < file_manager/test_storage.py
"""

from file_manager.models import PublicFile, PrivateFile
import requests

print("=" * 80)
print("TESTING FILE STORAGE CONFIGURATION")
print("=" * 80)

# Get the latest files
public_files = PublicFile.objects.all().order_by('-id')[:3]
private_files = PrivateFile.objects.all().order_by('-id')[:3]

print("\n📁 PUBLIC FILES:")
print("-" * 80)
for file in public_files:
    url = file.file.url
    print(f"\nTitle: {file.title}")
    print(f"Path: {file.file.name}")
    print(f"URL: {url}")
    
    # Test if publicly accessible
    try:
        response = requests.head(url, timeout=5, verify=False)
        if response.status_code == 200:
            print("✅ PUBLIC ACCESS: File is publicly accessible (as expected)")
        else:
            print(f"❌ PUBLIC ACCESS: Got status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error testing public access: {str(e)}")

print("\n\n🔒 PRIVATE FILES:")
print("-" * 80)
for file in private_files:
    url = file.file.url
    print(f"\nTitle: {file.title}")
    print(f"Path: {file.file.name}")
    print(f"URL: {url}")
    
    # Test if publicly accessible (should NOT be)
    try:
        response = requests.head(url, timeout=5, verify=False)
        if response.status_code == 403:
            print("✅ PRIVATE ACCESS: File is protected (as expected)")
        elif response.status_code == 200:
            print("❌ PRIVATE ACCESS: File is publicly accessible (SECURITY ISSUE!)")
        else:
            print(f"⚠️  PRIVATE ACCESS: Got status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error testing private access: {str(e)}")

print("\n" + "=" * 80)
print("CONFIGURATION SUMMARY:")
print("-" * 80)
print(f"Bucket Type: MINIO")
print(f"Public files should: Be accessible via direct URL")
print(f"Private files should: Require signed URLs or authentication")
print("=" * 80)
