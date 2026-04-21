import requests

def mapping_attributes_service(file_data):
    try:
        sheet_utility_url = "https://exporter.utilities.apptimus.lk/api/app/export/excel-to-json/"
        response = requests.post(sheet_utility_url, json=file_data)
        response_data = response.json()

        # Define the table fields mapping using actual crmf_invoices model fields
        system_field_name = {
            "0": "id",
            "1": "invoice_number",
            "2": "invoice_date",
            "3": "credit_age_days",
            "4": "credit_period_days",
            "5": "due_date",
            "6": "invoice_amount",
            "7": "paid_amount",
            "8": "outstanding_amount",
            "9": "remarks",
            "10": "issued_policy_id",
            "11": "endorsement_id",
            "12": "invoice_type",
            "13": "entity_id",
            "14": "insurer_id",
            "15": "insured_id",
            "16": "last_paid_date",
            "17": "transaction_type_id",
            "18": "product_id"
        }

        # Create the final array with three objects
        final_response = [
            response_data["result"]["headers"],  # First object: excel_field_name
            system_field_name,  # Second object: system_field_name
            response_data  # Third object: excel_data
        ]

        return {
            "success": True,
            "message": "Data transformed successfully",
            "result": {
                "excel_field_name": final_response[0],
                "system_field_name": final_response[1],
                "excel_data": final_response[2]
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "result": None
        }