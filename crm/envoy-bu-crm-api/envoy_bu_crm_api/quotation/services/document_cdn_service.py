import os
import requests
from typing import List, Dict, Any
from urllib.parse import quote
from .s3_presigned_service import S3PresignedService


class DocumentCDNService:
    """
    Service to handle document processing and CDN link generation for email attachments
    """
    
    @staticmethod
    def process_documents_for_email(documents: List[Dict[str, Any]]) -> List[str]:
        """
        Process documents array and return list of CDN URLs for email links
        
        Args:
            documents: List of document objects with various structures
            
        Returns:
            List of CDN URLs that can be used in email links
        """
        cdn_links = []
        
        if not isinstance(documents, list):
            return cdn_links
            
        for doc in documents:
            if not isinstance(doc, dict):
                continue
                
            cdn_url = DocumentCDNService._process_single_document(doc)
            if cdn_url:
                cdn_links.append(cdn_url)
                
        return cdn_links
    
    @staticmethod
    def _process_single_document(doc: Dict[str, Any]) -> str:
        """
        Process a single document and return its CDN URL
        
        Args:
            doc: Document object with name, doc, and optionally type fields
            
        Returns:
            CDN URL string or None if processing fails
        """
        try:
            # Get document path/URL from 'doc' field
            doc_path = doc.get('doc')
            doc_name = doc.get('name', 'unknown')
            
            print(f"\n=== Processing Document: {doc_name} ===")
            print(f"Original doc path: {doc_path}")
            
            if not doc_path:
                print(f"❌ No 'doc' field found for {doc_name}")
                return None
                
            # If it's already a full URL, return as is
            if doc_path.startswith('http://') or doc_path.startswith('https://'):
                print(f"✅ Document {doc_name} is already a full URL: {doc_path}")
                return doc_path
                
            # If it's a relative path, generate CDN URL
            if isinstance(doc_path, str) and not doc_path.startswith('/'):
                # This is a relative path, construct CDN URL
                cdn_base_url = os.getenv("CDN_BASE_URL")
                print(f"CDN_BASE_URL: {cdn_base_url}")
                
                if cdn_base_url:
                    # Remove trailing slash from base URL and ensure single slash
                    cdn_base_url = cdn_base_url.rstrip('/')
                    doc_path = doc_path.lstrip('/')
                    
                    print(f"Cleaned doc_path: {doc_path}")
                    
                    # URL encode the document path to handle spaces and special characters
                    encoded_doc_path = quote(doc_path, safe='/')
                    print(f"Encoded doc_path: {encoded_doc_path}")
                    
                    final_url = f"{cdn_base_url}/{encoded_doc_path}"
                    print(f"✅ Generated CDN URL: {final_url}")
                    
                    # Test if the URL is accessible
                    try:
                        response = requests.head(final_url, timeout=5)
                        print(f"URL accessibility test: {response.status_code} - {response.reason}")
                        if response.status_code == 200:
                            print(f"✅ URL is accessible")
                        elif response.status_code == 403:
                            print(f"❌ URL returns 403 Forbidden - File access denied")
                        elif response.status_code == 404:
                            print(f"❌ URL returns 404 Not Found - File doesn't exist")
                        else:
                            print(f"⚠️ URL returns {response.status_code} - {response.reason}")
                    except Exception as test_error:
                        print(f"⚠️ Could not test URL accessibility: {str(test_error)}")
                    
                    return final_url
                else:
                    print(f"❌ CDN_BASE_URL is not set for document {doc_name}")
                    return None
                    
            print(f"❌ Document {doc_name} path doesn't match expected format: {doc_path}")
            return None
            
        except Exception as e:
            print(f"❌ Error processing document {doc.get('name', 'unknown')}: {str(e)}")
            return None
    
    @staticmethod
    def upload_document_to_s3_and_get_cdn(doc_path: str, doc_name: str) -> str:
        """
        Upload a document from URL to S3 and return CDN URL
        
        Args:
            doc_path: URL or path to the document
            doc_name: Name of the document
            
        Returns:
            CDN URL of the uploaded document
        """
        try:
            # If it's a URL, download and upload to S3
            if doc_path.startswith('http://') or doc_path.startswith('https://'):
                s3_result = S3PresignedService.upload_stream_from_url(
                    file_url=doc_path,
                    file_name=doc_name,
                    folder="exports/quotations"
                )
                
                # Generate CDN URL
                cdn_base_url = os.getenv("CDN_BASE_URL")
                if cdn_base_url:
                    cdn_base_url = cdn_base_url.rstrip('/')
                    s3_key = s3_result['file_key'].lstrip('/')
                    # URL encode the S3 key to handle spaces and special characters
                    encoded_s3_key = quote(s3_key, safe='/')
                    return f"{cdn_base_url}/{encoded_s3_key}"
                    
            return None
            
        except Exception as e:
            print(f"Error uploading document {doc_name} to S3: {str(e)}")
            return None
