
import requests
import io
import os
import time
from datetime import datetime

# Simple response formatter
class ResponseService:
    @staticmethod
    def response(status, data=None, message=""):
        return {
            "status": status,
            "data": data,
            "message": message
        }

class ExportToPdf:
    def __init__(self):
        self.application_name = 'envoy'
        self.base_url = 'https://exporter.utilities.apptimus.lk'
        self.url = f"{self.base_url}/api/{self.application_name}/export/html-to-pdf"
        

    def export_html_to_pdf(self, html_content: str, max_retries=5, initial_delay=3):
        """
        Export HTML to PDF with retry logic for service unavailability
        
        Args:
            html_content (str): HTML content to convert
            max_retries (int): Maximum number of retry attempts (default: 5)
            initial_delay (int): Initial delay in seconds before retry (default: 3)
        """
        if not html_content:
            return ResponseService.response('BAD_REQUEST', None, 'HTML content is empty.')

        html_content = HtmlSanitizer.sanitize(html_content)
        payload = {"html": html_content}

        last_error = None
        retryable_status_codes = [502, 503, 504]  # Bad Gateway, Service Unavailable, Gateway Timeout
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.url, json=payload, timeout=90)
                
                # Handle retryable HTTP errors (502, 503, 504)
                if response.status_code in retryable_status_codes:
                    if attempt < max_retries - 1:
                        delay = initial_delay * (2 ** attempt)  # Exponential backoff: 3s, 6s, 12s, 24s, 48s
                        print(f"PDF service error ({response.status_code}). Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        return ResponseService.response("ERROR", None, "PDF export service is temporarily unavailable. Please try again in a few moments.")
                
                response.raise_for_status()
                json_data = response.json()

                if json_data.get("success") and isinstance(json_data.get("result"), dict):
                    result_data = json_data["result"]
                    download_url = result_data.get("download_url")

                    if download_url:
                        result_data["download_url"] = f"{self.base_url}{download_url}"

                    return ResponseService.response("SUCCESS", result_data, json_data.get("message", "PDF generated."))
                else:
                    message = json_data.get("message", "PDF export failed.")
                    return ResponseService.response("ERROR", None, message)

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"PDF export request timed out. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    return ResponseService.response("ERROR", None, "PDF export request timed out. Please try again later.")
            
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') and e.response else None
                if status_code in retryable_status_codes and attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"PDF service error ({status_code}). Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    return ResponseService.response("ERROR", None, f"PDF export service error: {str(e)}")
            
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"PDF export connection failed. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    return ResponseService.response("ERROR", None, "Failed to connect to PDF export service. Please try again later.")
            
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"PDF export request failed. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    return ResponseService.response("ERROR", None, f"Failed to connect to PDF export service: {last_error}")
            
            except ValueError as ve:
                return ResponseService.response("ERROR", None, "Invalid JSON response from PDF export service.")
            
            except Exception as ex:
                return ResponseService.response("ERROR", None, f"Unexpected error: {str(ex)}")
        
        # If all retries failed
        return ResponseService.response("ERROR", None, f"PDF export failed after {max_retries} attempts. Please try again later.")

class ExportToCsv:
    def __init__(self):
        self.application_name = 'envoy'
        self.base_url = 'https://exporter.utilities.apptimus.lk'
        # CSV export not available - will convert HTML to JSON and use Excel endpoint
        self.url = f"{self.base_url}/api/{self.application_name}/export/json-to-excel"

    def export_html_to_csv(self, html_content: str):
        if not html_content:
            return ResponseService.response('BAD_REQUEST', None, 'HTML content is empty.')

        # Since CSV endpoint doesn't exist, convert HTML to JSON and use Excel endpoint
        json_data = self._html_to_json(html_content)
        
        payload = {"json": json_data}
        print("Sending payload to CSV export service (using Excel endpoint):", payload)
        
        try:
            response = requests.post(self.url, json=payload)
            print("CSV export URL (using Excel endpoint):", self.url)
            print("CSV export response status:", response.status_code)
            print("CSV export response:", response.text)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("success") and isinstance(json_data.get("result"), dict):
                result_data = json_data["result"]
                download_url = result_data.get("download_url")

                if download_url:
                    result_data["download_url"] = f"{self.base_url}{download_url}"

                return ResponseService.response("SUCCESS", result_data, json_data.get("message", "CSV generated."))
            else:
                message = json_data.get("message", "CSV export failed.")
                print(f"CSV export failed: {message}")
                return ResponseService.response("ERROR", None, message)

        except requests.exceptions.RequestException as e:
            print(f"CSV export request error: {str(e)}")
            return ResponseService.response("ERROR", None, f"Failed to connect to CSV export service: {str(e)}")
        except ValueError as ve:
            print(f"CSV export JSON error: {str(ve)}")
            return ResponseService.response("ERROR", None, "Invalid JSON response from CSV export service.")
        except Exception as ex:
            print(f"CSV export unexpected error: {str(ex)}")
            return ResponseService.response("ERROR", None, f"Unexpected error: {str(ex)}")

    def _html_to_json(self, html_content: str):
        """Convert HTML table to JSON format"""
        try:
            # Simple HTML table to JSON conversion
            # This is a basic implementation - you might want to use BeautifulSoup for more complex HTML
            
            # Extract table data from HTML
            import re
            
            # Find table rows
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html_content, re.DOTALL | re.IGNORECASE)
            
            json_data = []
            headers = []
            
            for i, row in enumerate(rows):
                # Extract cells from row
                cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
                
                # Clean cell content
                cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                
                if i == 0:  # First row might be headers
                    headers = cells
                else:
                    if headers:
                        # Create object with headers as keys
                        row_data = {}
                        for j, cell in enumerate(cells):
                            if j < len(headers):
                                row_data[headers[j]] = cell
                        json_data.append(row_data)
                    else:
                        # No headers, create array
                        json_data.append(cells)
            
            return json_data
            
        except Exception as e:
            print(f"Error converting HTML to JSON: {str(e)}")
            # Fallback: return simple structure
            return [{"data": "HTML conversion failed"}]

class ExportToExcel:
    def __init__(self):
        self.application_name = 'envoy'
        self.base_url = 'https://exporter.utilities.apptimus.lk'
        self.url = f"{self.base_url}/api/{self.application_name}/export/json-to-excel"

    def export_html_to_excel(self, html_content: str):
        if not html_content:
            return ResponseService.response('BAD_REQUEST', None, 'HTML content is empty.')

        # Convert HTML to JSON format for Excel export
        json_data = self._html_to_json(html_content)
        
        payload = {"json": json_data}
        print("Sending payload to Excel export service:", payload)
        
        try:
            response = requests.post(self.url, json=payload)
            print("Excel export URL:", self.url)
            print("Excel export response status:", response.status_code)
            print("Excel export response:", response.text)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("success") and isinstance(json_data.get("result"), dict):
                result_data = json_data["result"]
                download_url = result_data.get("download_url")

                if download_url:
                    result_data["download_url"] = f"{self.base_url}{download_url}"

                return ResponseService.response("SUCCESS", result_data, json_data.get("message", "Excel generated."))
            else:
                message = json_data.get("message", "Excel export failed.")
                print(f"Excel export failed: {message}")
                return ResponseService.response("ERROR", None, message)

        except requests.exceptions.RequestException as e:
            print(f"Excel export request error: {str(e)}")
            return ResponseService.response("ERROR", None, f"Failed to connect to Excel export service: {str(e)}")
        except ValueError as ve:
            print(f"Excel export JSON error: {str(ve)}")
            return ResponseService.response("ERROR", None, "Invalid JSON response from Excel export service.")
        except Exception as ex:
            print(f"Excel export unexpected error: {str(ex)}")
            return ResponseService.response("ERROR", None, f"Unexpected error: {str(ex)}")

    def _html_to_json(self, html_content: str):
        """Convert HTML table to JSON format"""
        try:
            # Simple HTML table to JSON conversion
            import re
            
            # Find table rows
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html_content, re.DOTALL | re.IGNORECASE)
            
            json_data = []
            headers = []
            
            for i, row in enumerate(rows):
                # Extract cells from row
                cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
                
                # Clean cell content
                cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                
                if i == 0:  # First row might be headers
                    headers = cells
                else:
                    if headers:
                        # Create object with headers as keys
                        row_data = {}
                        for j, cell in enumerate(cells):
                            if j < len(headers):
                                row_data[headers[j]] = cell
                        json_data.append(row_data)
                    else:
                        # No headers, create array
                        json_data.append(cells)
            
            return json_data
            
        except Exception as e:
            print(f"Error converting HTML to JSON: {str(e)}")
            # Fallback: return simple structure
            return [{"data": "HTML conversion failed"}]

# Example usage:
# export_pdf = ExportToPdf()
# html_content = "<html><body><h1>Hello World</h1></body></html>"
# result = export_pdf.export_html_to_pdf(html_content)
# print(result)
import re

class HtmlSanitizer:
    @staticmethod
    def sanitize(html: str) -> str:
        # Fix 'font - size' → 'font-size'
        html = re.sub(r'([a-zA-Z]+)\s*-\s*([a-zA-Z]+)', r'\1-\2', html)
        # Fix missing semicolon at end of style rule
        html = re.sub(r'([^;{}\s])\s*}', r'\1; }', html)
        # Remove problematic <svg> blocks (exporter might not support it)
        html = re.sub(r'<svg[\s\S]*?</svg>', '', html)
        return html

class SQLToExcelExporter:
    """Export SQL queries directly to Excel"""
    def __init__(self):
        self.base_url = "https://exporter.utilities.apptimus.lk"
        self.url = f"{self.base_url}/api/envoy/export/sql-to-excel"

    def export(self, payload: dict):
        """
        Export SQL queries to Excel
        
        Args:
            payload (dict): Payload with structure:
                {
                    "queries": [
                        {
                            "query": "SELECT ...",
                            "title": "Sheet Title"
                        }
                    ],
                    "styles": {...}  # Optional
                }
        
        Returns:
            dict: Response with status, data, and message
        """
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and data.get("result", {}).get("download_url"):
                data["result"]["download_url"] = f"{self.base_url}{data['result']['download_url']}"
                return {
                    "status": "SUCCESS",
                    "data": data["result"],
                    "message": data.get("message", "Excel generated")
                }
            
            return {
                "status": "ERROR",
                "data": None,
                "message": data.get("error") or data.get("message", "Export failed")
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "ERROR",
                "data": None,
                "message": f"Export error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "data": None,
                "message": f"Unexpected error: {str(e)}"
            }