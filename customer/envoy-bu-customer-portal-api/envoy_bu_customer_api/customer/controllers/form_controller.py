from math import ceil
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ResponseService as ResponseService
from mServices.ValidatorService import ValidatorService
import json
from core_models.core_models import CoreFormSubmission, CoreFormSubmissionValue, CoreTemplate, Customer, OpportunityType, Status, VendorProducts
from envoy_bu_customer_api.customer.controllers.common_controller import get_template_detail, resolve_draft_status
from envoy_bu_customer_api.customer.models.customer_request import CustomerRequest, CustomerRequestRiskType, CustomerRequestVendorProduct
from django.core.exceptions import ValidationError


@api_view(["POST"])
@transaction.atomic
def submit_generic_form(request):
    try:
        print("=== SUBMIT_GENERIC_FORM START ===")
        data = request.data
        print("Incoming data:", data)

        user = request.user
        print("User object:", user)
        print("User type:", type(user))
        
        # Get customer ID from user's entity or fallback to 1
        customer_id = user.get('id', None)
        print("Extracted customer_id:", customer_id)

        if not customer_id:
            print("Customer ID missing!")
            return ResponseService.response("UNAUTHORIZED", None, "Customer ID missing in token")


        # Step 1: Validate input
        print("=== STEP 1: VALIDATING INPUT ===")
        rules = {
            "form_id": "required|exists:core_templates,id",
            "values": "required|dict",
            "type": "required|in:claim,policy,quotation",
            "risk_type_id": "required",
            "vendor_product_id": "nullable"
        }
        print("Validation rules:", rules)

        errors = ValidatorService.validate(data, rules)
        print("Validation errors:", errors)
        if errors:
            print("Validation failed, returning error response")
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        print("=== STEP 2: EXTRACTING DATA ===")
        form_id = data["form_id"]
        form_type = data["type"]
        submitted_values = data["values"]
        print("Form ID:", form_id)
        print("Form type:", form_type)
        print("Submitted values:", submitted_values)

        # Normalize multi-select values
        risk_type_ids = data["risk_type_id"]
        vendor_product_ids = data.get("vendor_product_id", [])
        print("Risk type IDs (raw):", risk_type_ids)
        print("Vendor product IDs (raw):", vendor_product_ids)

        if isinstance(risk_type_ids, (int, str)):
            risk_type_ids = [int(risk_type_ids)]
        if isinstance(vendor_product_ids, (int, str)):
            vendor_product_ids = [int(vendor_product_ids)]
        
        print("Risk type IDs (normalized):", risk_type_ids)
        print("Vendor product IDs (normalized):", vendor_product_ids)

        # Manual validation
        print("=== STEP 3: MANUAL VALIDATION ===")
        risk_type_count = OpportunityType.objects.filter(id__in=risk_type_ids).count()
        print("Found risk types:", risk_type_count, "Expected:", len(risk_type_ids))
        if risk_type_count != len(risk_type_ids):
            print("Risk type validation failed")
            return ResponseService.response("VALIDATION_ERROR", {"risk_type_id": "Invalid risk type IDs"}, "Validation Error")
        
        if vendor_product_ids:
            vendor_product_count = VendorProducts.objects.filter(id__in=vendor_product_ids).count()
            print("Found vendor products:", vendor_product_count, "Expected:", len(vendor_product_ids))
            if vendor_product_count != len(vendor_product_ids):
                print("Vendor product validation failed")
                return ResponseService.response("VALIDATION_ERROR", {"vendor_product_id": "Invalid vendor product IDs"}, "Validation Error")

        print("=== STEP 4: GETTING TEMPLATE ===")
        template = CoreTemplate.objects.get(id=form_id)
        print("Template found:", template)

        # Step 2: Template parsing
        print("=== STEP 5: TEMPLATE PARSING ===")
        template_response = get_template_detail(template)
        print("Template response type:", type(template_response))
        print("Template response content:", template_response.content)
        
        try:
            template_data = json.loads(template_response.content)
            print("Template data parsed successfully:", template_data)
        except Exception as e:
            print("Template parsing failed with error:", str(e))
            return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

        if not template_data.get("is_success"):
            print("Template response indicates failure")
            return template_response

        elements = template_data["result"].get("elements", [])
        print("Template elements:", elements)

        # Step 3: Validate dynamic fields
        print("=== STEP 6: DYNAMIC FIELD VALIDATION ===")
        dynamic_rules = {}
        custom_messages = {}
        for element in elements:
            eid = str(element["id"])
            label = element.get("label") or f"Element {eid}"
            if element.get("is_required"):
                dynamic_rules[eid] = "required"
                custom_messages[f"{eid}.required"] = f"{label} is required."
        
        print("Dynamic rules:", dynamic_rules)
        print("Custom messages:", custom_messages)

        errors = ValidatorService.validate(submitted_values, dynamic_rules, custom_messages)
        print("Dynamic validation errors:", errors)
        if errors:
            print("Dynamic validation failed")
            return ResponseService.response("VALIDATION_ERROR", errors, "Form validation failed")

        # Step 4: Resolve draft status for this form type using shared helper
        print("=== STEP 7: RESOLVING DRAFT STATUS ===")
        draft_status = resolve_draft_status(form_type)
        print("Resolved draft status id:", (draft_status.id if draft_status else None))

        if not draft_status:
            return ResponseService.response(
                "VALIDATION_ERROR",
                None,
                f"Draft status not found for type '{form_type}'."
            )

        # Step 5: Check if draft exists with the resolved status
        print("=== STEP 8: CHECKING FOR EXISTING DRAFT ===")
        existing_request = CustomerRequest.objects.filter(
            type=form_type, created_by_id=customer_id, status=draft_status
        ).order_by("-id").first()
        print("Existing request found:", existing_request)

        # if existing_request:
        #     print("=== UPDATING EXISTING DRAFT ===")
        #     # Update existing draft
        #     submission = existing_request.form_submission
        #     print("Existing submission:", submission)
            
        #     # If no submission exists, create a new one
        #     if not submission:
        #         print("No existing submission found, creating new one")
        #         submission = CoreFormSubmission.objects.create(
        #             form=template,
        #             user=None,
        #             customer_id=customer_id
        #         )
        #         print("Created new submission for existing request:", submission)
                
        #         # Update the existing request with the new submission
        #         existing_request.form_submission = submission
        #         existing_request.save()
        #         print("Updated existing request with new submission")
        #     else:
        #         CoreFormSubmissionValue.objects.filter(form_submission=submission).delete()
        #         print("Deleted existing form submission values")

        #     values_to_create = [
        #         CoreFormSubmissionValue(
        #             form_submission=submission,
        #             custom_form_element_id=element["id"],
        #             form_element_id=element["element_id"],
        #             value=submitted_values.get(str(element["id"]))
        #         )
        #         for element in elements if str(element["id"]) in submitted_values
        #     ]
        #     print("Values to create:", values_to_create)
        #     print("Number of values to create:", len(values_to_create))
        #     if values_to_create:
        #         print("First value details:")
        #         print("  - form_submission:", values_to_create[0].form_submission)
        #         print("  - custom_form_element_id:", values_to_create[0].custom_form_element_id)
        #         print("  - form_element_id:", values_to_create[0].form_element_id)
        #         print("  - value:", values_to_create[0].value)
            
        #     CoreFormSubmissionValue.objects.bulk_create(values_to_create)
        #     print("Created new form submission values")

        #     # Clear and re-insert M2M manually
        #     CustomerRequestRiskType.objects.filter(customer_request=existing_request).delete()
        #     CustomerRequestVendorProduct.objects.filter(customer_request=existing_request).delete()
        #     print("Cleared existing M2M relationships")

        #     CustomerRequestRiskType.objects.bulk_create([
        #         CustomerRequestRiskType(customer_request=existing_request, risk_type_id=rid) for rid in risk_type_ids
        #     ])
        #     CustomerRequestVendorProduct.objects.bulk_create([
        #         CustomerRequestVendorProduct(customer_request=existing_request, vendor_product_id=vid) for vid in vendor_product_ids
        #     ])
        #     print("Created new M2M relationships")

        #     print("=== RETURNING SUCCESS FOR UPDATE ===")
        #     return ResponseService.response("SUCCESS", {
        #         "request_id": existing_request.id,
        #         "request_code": existing_request.code,
        #         "submission_id": submission.id,
        #         "submitted_at": existing_request.submitted_at,
        #         "type": form_type,
        #         "status": existing_request.status.name if existing_request.status else None,
        #         "mode": "updated"
        #     }, "default_success_message")

        # else:
        print("=== CREATING NEW REQUEST ===")
            # Create new request
        print("Creating CoreFormSubmission with:")
        print("  - form:", template)
        print("  - user: None")
        print("  - customer_id:", customer_id)
            
        submission = CoreFormSubmission.objects.create(
            form=template,
            user=None,  # Set to None as per claim controller pattern
            customer_id=customer_id
        )
        print("Created new submission:", submission)
        print("Submission ID:", submission.id)

        values_to_create = [
            CoreFormSubmissionValue(
                form_submission=submission,
                custom_form_element_id=element["id"],
                form_element_id=element["element_id"],
                value=submitted_values.get(str(element["id"]))
            )
            for element in elements if str(element["id"]) in submitted_values
        ]
        print("Values to create for new request:", values_to_create)
        CoreFormSubmissionValue.objects.bulk_create(values_to_create)
        print("Created form submission values")

        type_prefix = {
            "claim": "CR",
            "policy": "PR",
            "quotation": "QR"
        }.get(form_type.lower(), "XX")
        print("Type prefix:", type_prefix)

        latest = CustomerRequest.objects.filter(type=form_type).order_by("-id").first()
        print("Latest request:", latest)
        number = int(latest.code[-4:]) + 1 if latest and latest.code else 1
        new_code = f"{type_prefix}{number:04d}"
        print("New code:", new_code)

            # Use the previously resolved draft_status
        print("Draft status id:", (draft_status.id if draft_status else None))

        print("Creating CustomerRequest with:")
        print("  - form_submission:", submission)
        print("  - type:", form_type)
        print("  - code:", new_code)
        print("  - created_by_id:", customer_id)
        print("  - status:", draft_status)
            
        customer_request = CustomerRequest.objects.create(
            form_submission=submission,
            type=form_type,
            code=new_code,
            created_by_id=customer_id,
            status=draft_status
        )
        print("Created customer request:", customer_request)
        print("Customer request ID:", customer_request.id)

            # Add M2M manually via through-tables
        CustomerRequestRiskType.objects.bulk_create([
            CustomerRequestRiskType(customer_request=customer_request, risk_type_id=rid) for rid in risk_type_ids
        ])
        CustomerRequestVendorProduct.objects.bulk_create([
            CustomerRequestVendorProduct(customer_request=customer_request, vendor_product_id=vid) for vid in vendor_product_ids
        ])
        print("Created M2M relationships for new request")

        print("=== RETURNING SUCCESS FOR CREATE ===")
        return ResponseService.response("SUCCESS", {
            "request_id": customer_request.id,
            "request_code": customer_request.code,
            "submission_id": submission.id,
            "submitted_at": customer_request.submitted_at,
            "type": form_type,
            "status": draft_status.name if draft_status else None,
            "customer_id": customer_id,
            "mode": "created"
        }, "default_success_message")

    except Exception as e:
        print("=== EXCEPTION CAUGHT ===")
        print("Exception type:", type(e))
        print("Exception message:", str(e))
        import traceback
        print("Traceback:", traceback.format_exc())
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



@api_view(["GET"])
def list_customer_requests(request):
    try:
        user = request.user
        if isinstance(user, dict):
            customer_id = user.get("id")
        else:
            customer_id = getattr(user, "id", None)

        if not customer_id:
            return ResponseService.response("UNAUTHORIZED", None, "Customer ID missing in token")
        
        # Request parameters
        filter_json = request.GET.get("filters", '{}')
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by") or "cr.id"
        sort_dir = request.GET.get("sort_dir") or "desc"


        # Filter and search field config
        allowed_filters = [
            "cr.type", "cr.code",
            "rrt.risk_type_id", "rvp.vendor_product_id", "rvp.product_group_id"
        ]
        search_columns = [
            "cr.code", "cr.type", "st.name", "rt.title", "vp.name", "pg.name", "cu.name"
        ]
        allowed_sorting_columns = [
            "cr.id", "cr.code", "cr.type", "cr.submitted_at"
        ]

        # Query with joins (no pagination here)
        raw_data = (
            QueryBuilderService("cus_requests as cr")
            .leftJoin("core_status as st", "st.id", "cr.status_id")
            .leftJoin("cus_request_risk_types as rrt", "rrt.customer_request_id", "cr.id")
            .leftJoin("crm_opportunity_types as rt", "rt.id", "rrt.risk_type_id")
            .leftJoin("cus_request_vendor_products as rvp", "rvp.customer_request_id", "cr.id")
            .leftJoin("core_vendor_products as vp", "vp.id", "rvp.vendor_product_id")
            .leftJoin("core_product_groups as pg", "pg.id", "rvp.product_group_id")
            .leftJoin("core_customers as cu", "cu.id", "cr.created_by_id")
            .select(
                "cr.*",
                "st.name as status_name",
                "st.color as status_color",
                "rt.id as risk_type_id",
                "rt.title as risk_type_name",
                "vp.id as vendor_product_id",
                "vp.name as vendor_product_name",
                "pg.id as product_group_id",
                "pg.name as product_group_name",
                "cu.name as customer_name"
            )
            .where("cr.created_by_id", customer_id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .orderBy(sort_by, sort_dir)
            .get()
        )

        grouped = {}
        for row in raw_data:
            rid = row["id"]
            if rid not in grouped:
                grouped[rid] = {
                    "id": row["id"],
                    "code": row["code"],
                    "type": row["type"],
                    "submitted_at": row["submitted_at"],
                    "is_draft": row["is_draft"],
                    "created_by_id": row["created_by_id"],
                    "form_submission_id": row["form_submission_id"],
                    "status_id": row["status_id"],
                    "status_name": row["status_name"],
                    "status_color": row["status_color"],
                    "customer_name": row["customer_name"],
                    "risk_types": [],
                    "vendor_products": []
                }

            # Append unique risk_types
            if row["risk_type_id"] and not any(rt["id"] == row["risk_type_id"] for rt in grouped[rid]["risk_types"]):
                grouped[rid]["risk_types"].append({
                    "id": row["risk_type_id"],
                    "name": row["risk_type_name"]
                })

            # Append unique vendor_products to vendor_products array
            if row["vendor_product_id"] and not any(p["id"] == row["vendor_product_id"] and p["type"] == "vendor_product" for p in grouped[rid]["vendor_products"]):
                grouped[rid]["vendor_products"].append({
                    "id": row["vendor_product_id"],
                    "name": row["vendor_product_name"],
                    "type": "vendor_product"
                })

            # Append unique product_groups to vendor_products array
            if row["product_group_id"] and not any(p["id"] == row["product_group_id"] and p["type"] == "product_group" for p in grouped[rid]["vendor_products"]):
                grouped[rid]["vendor_products"].append({
                    "id": row["product_group_id"],
                    "name": row["product_group_name"],
                    "type": "product_group"
                })

        # Pagination
        all_data = list(grouped.values())
        total = len(all_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = all_data[start:end]

        result = {
            "total_records": total,
            "per_page": limit,
            "current_page": page,
            "last_page": ceil(total / limit),
            "data": paginated_data
        }

        return ResponseService.response("SUCCESS", result, "Customer requests fetched successfully!")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")