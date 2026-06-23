import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

blob_service_client = None
container_client = None

def init_storage():
    global blob_service_client, container_client
    if not STORAGE_ACCOUNT_NAME or not BLOB_CONTAINER_NAME:
        print("Warning: STORAGE_ACCOUNT_NAME or BLOB_CONTAINER_NAME not set. Blob storage upload will fail.")
        return

    try:
        account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        print(f"Blob Storage Client initialized for account {STORAGE_ACCOUNT_NAME}.")
    except Exception as e:
        print(f"Failed to initialize Blob Storage Client: {e}")

def upload_artifact_blob(tenant_id: str, artifact_type: str, artifact_id: str, file_name: str, content: bytes, content_type: str) -> str:
    """Uploads bytes content to Azure Blob Storage and returns the blob path."""
    if not container_client:
        raise Exception("Azure Blob Storage client is not initialized.")
    
    blob_path = f"tenants/{tenant_id}/artifacts/{artifact_type}/{artifact_id}/{file_name}"
    blob_client = container_client.get_blob_client(blob_path)
    
    # Upload the blob (overwrite if exists)
    blob_client.upload_blob(content, overwrite=True)
    
    # Set the content type
    from azure.storage.blob import ContentSettings
    content_settings = ContentSettings(content_type=content_type)
    blob_client.set_http_headers(content_settings)

    return blob_path

def download_artifact_blob(blob_path: str) -> bytes:
    """Downloads blob content as bytes."""
    if not container_client:
        raise Exception("Azure Blob Storage client is not initialized.")
        
    blob_client = container_client.get_blob_client(blob_path)
    return blob_client.download_blob().readall()
