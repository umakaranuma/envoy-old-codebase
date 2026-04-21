import requests

class SQLToExcelExporter:
    def __init__(self):
        self.base_url = "https://exporter.utilities.apptimus.lk"
        self.url = f"{self.base_url}/api/envoy/export/sql-to-excel"

    def export(self, payload: dict):
        try:
            resp = requests.post(self.url, json=payload)
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

        except Exception as e:
            return {
                "status": "ERROR",
                "data": None,
                "message": f"Export error: {str(e)}"
            }
