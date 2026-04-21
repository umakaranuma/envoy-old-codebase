import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SQLToExcelExporter:
    def __init__(self):
        self.base_url = "https://exporter.utilities.apptimus.lk"
        self.url = f"{self.base_url}/api/envoy/export/sql-to-excel"
        
        # Create session with connection pooling and retry logic
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def export(self, payload: dict):
        try:
            # Use session with optimized settings
            resp = self.session.post(
                self.url, 
                json=payload,
                timeout=(10, 120)  # 10s connect, 120s read timeout
            )
            resp.raise_for_status()
            data = resp.json()

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

        except requests.exceptions.Timeout:
            return {
                "status": "ERROR",
                "data": None,
                "message": "Export service timeout - request took too long"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "ERROR",
                "data": None,
                "message": "Export service connection error - service unavailable"
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "data": None,
                "message": f"Export error: {str(e)}"
            }
