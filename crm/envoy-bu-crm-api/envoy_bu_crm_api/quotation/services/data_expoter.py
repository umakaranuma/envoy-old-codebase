
import requests

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
        

    def export_html_to_pdf(self, html_content: str):
        if not html_content:
            return ResponseService.response('BAD_REQUEST', None, 'HTML content is empty.')

        html_content = HtmlSanitizer.sanitize(html_content)  

        payload = {"html": html_content}
        print("Sending payload to PDF export service:", payload)

        try:
            response = requests.post(self.url, json=payload)
            print("self.url",self.url)
            print("Response from PDF export service:", response)
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

        except requests.exceptions.RequestException as e:
            return ResponseService.response("ERROR", None, f"Failed to connect to PDF export service: {str(e)}")
        except ValueError as ve:
            return ResponseService.response("ERROR", None, "Invalid JSON response from PDF export service.")
        except Exception as ex:
            return ResponseService.response("ERROR", None, f"Unexpected error: {str(ex)}")

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
