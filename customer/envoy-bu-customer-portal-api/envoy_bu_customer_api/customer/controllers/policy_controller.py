from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from core_models.core_models import CoreFormCustomFormElement, CoreFormSubmissionValue, Customer, EntityDocument, OpportunityFormConfig, OpportunityType, ProductCoverage, ProductDocumentType, Status, VendorProducts
from django.db.models import Count
from envoy_bu_customer_api.customer.models.coverage_details import CustomerRequestCoverageDetails
from envoy_bu_customer_api.customer.models.coverage_submission import CustomerRequestCoverage
from envoy_bu_customer_api.customer.models.customer_risk_details import CustomerRequestRiskDetails
from envoy_bu_customer_api.customer.models.document_submission import CustomerRequestDocument
from envoy_bu_customer_api.customer.models.payment_details import CustomerRequestPaymentDetails
from envoy_bu_customer_api.customer.models.policy_holder import PolicyHolder
from envoy_bu_customer_api.customer.models.customer_request import CustomerRequest, CustomerRequestRiskType, CustomerRequestVendorProduct
from mServices.ValidatorService import ValidatorService
from mServices.ResponseService import ResponseService
from mServices.QueryBuilderService import QueryBuilderService
from envoy_bu_customer_api.customer.controllers.common_controller import resolve_draft_status
from services.exporter import SQLToExcelExporter
from services.NotificationService import NotificationService
from envoy_bu_customer_api.customer.serializers import CustomerRequestSerializer



@api_view(["POST"])
@transaction.atomic
def bulk_submit_customer_requests(request):
    data = request.data
    user = request.user.get('id', 1)

    # Step 1: Validate
    rules = {
        "type": "required|in:claim,policy,quotation",
        "risk_type_ids": "required|list",
        "vendor_product_id": "nullable|integer",
        "product_group_id": "nullable|integer"
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        form_type = data["type"]
        risk_type_ids = data["risk_type_ids"]
        vendor_product_id = data.get("vendor_product_id")
        product_group_id = data.get("product_group_id")

        # Normalize to list if single int/string provided
        if isinstance(risk_type_ids, (int, str)):
            risk_type_ids = [int(risk_type_ids)]

        # Additional validation based on risk_type_ids count
        if len(risk_type_ids) > 1:
            # Multiple risk types - must provide product_group_id, not vendor_product_id
            if vendor_product_id is not None:
                return ResponseService.response("VALIDATION_ERROR", {"error": "For multiple risk types, only product_group_id is allowed, not vendor_product_id"}, "Validation Error")
            if product_group_id is None:
                return ResponseService.response("VALIDATION_ERROR", {"error": "For multiple risk types, product_group_id is required"}, "Validation Error")
        else:
            # Single risk type - must provide vendor_product_id, not product_group_id
            if product_group_id is not None:
                return ResponseService.response("VALIDATION_ERROR", {"error": "For single risk type, only vendor_product_id is allowed, not product_group_id"}, "Validation Error")
            if vendor_product_id is None:
                return ResponseService.response("VALIDATION_ERROR", {"error": "For single risk type, vendor_product_id is required"}, "Validation Error")

        # Step 2: Validate IDs
        if QueryBuilderService("crm_opportunity_types").whereIn("id", risk_type_ids).count() != len(risk_type_ids):
            return ResponseService.response("VALIDATION_ERROR", {"risk_type_ids": "Invalid risk type IDs"}, "Validation Error")

        # Validate vendor product ID only if provided
        if vendor_product_id is not None:
            if QueryBuilderService("core_vendor_products").where("id", vendor_product_id).count() != 1:
                return ResponseService.response("VALIDATION_ERROR", {"vendor_product_id": "Invalid vendor product ID"}, "Validation Error")

        # Step 3: Resolve draft status using shared helper based on type/module
        draft_status = resolve_draft_status(form_type)
        if not draft_status:
            return ResponseService.response(
                "VALIDATION_ERROR",
                None,
                f"Draft status not found for type '{form_type}'."
            )

        # Step 4: Check for existing request with same type, user, and ALL risk_type_ids
        existing_request = (
            CustomerRequest.objects
            .filter(type=form_type, created_by_id=user, status=draft_status)
            .annotate(risk_count=Count("risk_types"))
            .filter(risk_types__risk_type_id__in=risk_type_ids)
            .distinct()
            .first()
        )

        # Helper: Check if risk IDs match exactly
        def same_risks(req):
            existing_risks = set(req.risk_types.values_list("risk_type_id", flat=True))
            return existing_risks == set(risk_type_ids)

        if existing_request and same_risks(existing_request):
            # Check if vendor product or product group already exists
            existing_vendor = None
            if vendor_product_id is not None:
                existing_vendor = existing_request.vendor_products.filter(vendor_product_id=vendor_product_id).first()
            elif product_group_id is not None:
                existing_vendor = existing_request.vendor_products.filter(product_group_id=product_group_id).first()

            if not existing_vendor:
                CustomerRequestVendorProduct.objects.create(
                    customer_request=existing_request, 
                    vendor_product_id=vendor_product_id,
                    product_group_id=product_group_id
                )

            response_data = {
                "request_id": existing_request.id,
                "code": existing_request.code,
                "risk_type_ids": risk_type_ids,
                "status": draft_status.name,
                "mode": "updated"
            }
            
            if vendor_product_id is not None:
                response_data["vendor_product_id"] = vendor_product_id
            if product_group_id is not None:
                response_data["product_group_id"] = product_group_id
                
            return ResponseService.response("SUCCESS", response_data, "Customer request updated successfully.")

        # Step 5: Create new request
        latest = CustomerRequest.objects.filter(type=form_type).order_by("-id").first()
        number = int(latest.code[-4:]) + 1 if latest and latest.code and latest.code[-4:].isdigit() else 1
        type_prefix = {"claim": "CL", "policy": "PR", "quotation": "QU"}.get(form_type.lower(), "XX")
        new_code = f"{type_prefix}{number:04d}"

        customer_request = CustomerRequest.objects.create(
            type=form_type,
            code=new_code,
            created_by_id=user,
            status=draft_status
        )

        CustomerRequestRiskType.objects.bulk_create([
            CustomerRequestRiskType(customer_request=customer_request, risk_type_id=rid) for rid in risk_type_ids
        ])

        CustomerRequestVendorProduct.objects.create(
            customer_request=customer_request, 
            vendor_product_id=vendor_product_id,
            product_group_id=product_group_id
        )

        response_data = {
            "request_id": customer_request.id,
            "code": new_code,
            "risk_type_ids": risk_type_ids,
            "status": draft_status.name,
            "mode": "created"
        }
        
        if vendor_product_id is not None:
            response_data["vendor_product_id"] = vendor_product_id
        if product_group_id is not None:
            response_data["product_group_id"] = product_group_id
            
        return ResponseService.response("SUCCESS", response_data, "Customer request created successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")





@api_view(["POST"])
@transaction.atomic
def create_policy_holder(request):
    data = request.data
    # user = request.user if request.user.is_authenticated else 1
    user = request.user.get('id',1)

    # Validation rules
    rules = {
        "customer_request_id": "nullable|exists:cus_requests,id",
        "policy_holder_name": "required|string|max:255",
        "date_of_birth": "required|date",
        "gender": "required|string|max:50",
        "nic": "required|string|max:25",
        "phone_number": "required|string|max:20",
        "email": "required|email",
        "address": "required|string",
        "contact_method": "required|string|max:50",
        # "is_draft": "boolean"
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        # Check if request exists or needs to be created
        customer_request = None
        request_id = data.get("customer_request_id")

        if request_id:
            customer_request = CustomerRequest.objects.filter(id=request_id).first()

        # If no request exists, create a new one (Corporate type, no form submission)
        if not customer_request:
            form_type = "policy"

            # Resolve draft status using shared helper
            draft_status = resolve_draft_status(form_type)

            latest = CustomerRequest.objects.filter(type=form_type).order_by("-id").first()
            number = int(latest.code[-4:]) + 1 if latest and latest.code else 1
            new_code = f"PR{number:04d}"

            customer_request = CustomerRequest.objects.create(
                type=form_type,
                code=new_code,
                status=draft_status,
                created_by_id=user
            )

        # Create or update policy holder
        policy_holder, created = PolicyHolder.objects.update_or_create(
            customer_request=customer_request,
            defaults={
                "policy_holder_name": data["policy_holder_name"],
                "date_of_birth": data["date_of_birth"],
                "gender": data["gender"],
                "nic": data["nic"],
                "phone_number": data["phone_number"],
                "email": data["email"],
                "address": data["address"],
                "contact_method": data["contact_method"],
                # "is_draft": data.get("is_draft", True)
            }
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "id": policy_holder.id,
                "customer_request_id": policy_holder.customer_request.id,
                "policy_holder_name": policy_holder.policy_holder_name,
                "mode": "created" if created else "updated"
            },
            "default_create_success_message"
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET"])
def get_policy_holder_by_request(request, request_id):
    try:
        # Check if the request exists
        customer_request = CustomerRequest.objects.filter(id=request_id).first()
        if not customer_request:
            return ResponseService.response("NOT_FOUND", None, "Customer request not found.",system_code=404)

        # Fetch the policy holder linked to this request
        policy_holder = PolicyHolder.objects.filter(customer_request_id=request_id).first()
        if not policy_holder:
            return ResponseService.response("NOT_FOUND", None, "Policy holder not found for this request.",system_code=404)

        data = {
            "id": policy_holder.id,
            "customer_request_id": policy_holder.customer_request.id,
            "policy_holder_name": policy_holder.policy_holder_name,
            "date_of_birth": policy_holder.date_of_birth,
            "gender": policy_holder.gender,
            "nic": policy_holder.nic,
            "phone_number": policy_holder.phone_number,
            "email": policy_holder.email,
            "address": policy_holder.address,
            "contact_method": policy_holder.contact_method,
            # "is_draft": policy_holder.is_draft,
            "created_at": policy_holder.created_at if hasattr(policy_holder, 'created_at') else None
        }

        return ResponseService.response("SUCCESS", data, "Policy holder fetched successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
    
    


@api_view(["GET"])
def get_product_documents_with_values(request, request_id):
    try:
        # Step 1: Validate CustomerRequest
        customer_request = CustomerRequest.objects.filter(id=request_id).first()
        if not customer_request:
            return ResponseService.response("NOT_FOUND", None, "Customer request not found.", system_code=404)

        # Step 2: Get linked vendor products
        vendor_products = CustomerRequestVendorProduct.objects.select_related("vendor_product")\
            .filter(customer_request=customer_request)

        if not vendor_products.exists():
            return ResponseService.response("NOT_FOUND", None, "No vendor products found for this request.", system_code=404)

        # Step 3: Get all submitted CustomerRequestDocument values (indexed by doc_type_id)
        submitted_docs = {
            doc.document_type_id: doc
            for doc in CustomerRequestDocument.objects.filter(customer_request=customer_request)
        }

        # Step 4: Prepare result as an array of vendor products with document info
        result = []

        for vp in vendor_products:
            product = vp.vendor_product
            product_name = product.name

            doc_types = ProductDocumentType.objects.filter(vendor_product_id=product.id)

            document_list = []
            for doc in doc_types:
                submitted = submitted_docs.get(doc.id)
                document_list.append({
                    "document_type_id": doc.id,
                    "name": doc.name,
                    "is_mandatory": doc.is_mandatory,
                    "type": doc.type,
                    "value": submitted.value if submitted else None,
                    "uploaded_at": submitted.uploaded_at if submitted else None
                })

            result.append({
                "vendor_product_name": product_name,
                "documents": document_list
            })

        return ResponseService.response("SUCCESS", result, "Document types grouped by vendor product fetched successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch documents.")


# @api_view(["GET"])
# def get_product_documents_by_vendor(request):
#     try:
#         vendor_product_id = request.GET.get("vendor_product_id")

#         # Input validation
#         rules = {
#             "vendor_product_id": "required|exists:core_vendor_products,id"
#         }
#         errors = ValidatorService.validate({"vendor_product_id": vendor_product_id}, rules)
#         if errors:
#             return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#         # Select columns
#         columns = [
#             "id",
#             "name",
#             "is_mandatory",
#             "vendor_product_id",
#             "type"
#         ]

#         # Use QueryBuilderService
#         query = QueryBuilderService("core_product_document_types") \
#             .select(*columns) \
#             .where("vendor_product_id", vendor_product_id) \
#             .get()

#         return ResponseService.response("SUCCESS", query, "Product document types fetched successfully.")

#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
    


@api_view(["POST"])
@transaction.atomic
def store_customer_request_documents(request):
    data = request.data

    # Step 1: Validate input
    rules = {
        "request_id": "required|exists:cus_requests,id",
        "values": "required|dict|min:1"
    }
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation error")

    request_id = data["request_id"]
    document_values = data["values"]

    try:
        customer_request = CustomerRequest.objects.get(id=request_id)
        result_documents = []

        for doc_type_id_str, value in document_values.items():
            try:
                doc_type_id = int(doc_type_id_str)
                document_type = ProductDocumentType.objects.get(id=doc_type_id)

                doc_obj, created = CustomerRequestDocument.objects.update_or_create(
                    customer_request=customer_request,
                    document_type=document_type,
                    defaults={"value": value},
                    # is_draft=True
                )

                result_documents.append({
                    "document_type_id": doc_type_id,
                    "value": value,
                    "status": "created" if created else "updated"
                })

            except (ValueError, ProductDocumentType.DoesNotExist):
                result_documents.append({
                    "document_type_id": doc_type_id_str,
                    "value": value,
                    "status": "skipped - invalid document type"
                })

        return ResponseService.response(
            "SUCCESS",
            {
                "request_id": request_id,
                "documents": result_documents
            },
            "Customer request documents processed successfully."
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to store customer request documents."
        )
    

# @api_view(["GET"])
# def get_customer_request_documents(request, request_id):
#     try:
#         # Step 1: Validate the request exists
#         customer_request = CustomerRequest.objects.filter(id=request_id).first()
#         if not customer_request:
#             return ResponseService.response("NOT_FOUND", None, "Customer request not found.")

#         # Step 2: Fetch documents related to the request
#         documents = CustomerRequestDocument.objects.filter(customer_request_id=request_id)

#         result = []
#         for doc in documents:
#             result.append({
#                 "document_type_id": doc.document_type.id,
#                 "document_type_name": doc.document_type.name,
#                 "is_mandatory": doc.document_type.is_mandatory,
#                 "type": doc.document_type.type,
#                 "value": doc.value,
#                 "uploaded_at": doc.uploaded_at,
#             })

#         return ResponseService.response("SUCCESS", result, "Customer request documents fetched successfully.")

#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch documents.")



@api_view(["POST"])
@transaction.atomic
def store_customer_request_policy_details(request):
    data = request.data

    rules = {
        "request_id": "required|exists:cus_requests,id",
        "sum_insured": "required|numeric",
        "start_date": "required|date",
        "end_date": "required|date",
        # "is_draft": "boolean"
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        request_id = data["request_id"]
        policy_details, created = CustomerRequestCoverageDetails.objects.update_or_create(
            customer_request_id=request_id,
            defaults={
                "sum_insured": data.get("sum_insured"),
                "start_date": data["start_date"],
                "end_date": data["end_date"],
                # "is_draft": data.get("is_draft", True)
            }
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "id": policy_details.id,
                "request_id": policy_details.customer_request.id,
                "mode": "created" if created else "updated"
            },
            "Customer request policy details stored successfully."
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to store policy details.")
    


@api_view(["GET"])
def get_customer_request_policy_details(request, request_id):
    try:
        policy = CustomerRequestCoverageDetails.objects.filter(customer_request_id=request_id).first()

        if not policy:
            return ResponseService.response("NOT_FOUND", None, "Policy details not found.",system_code=404)

        data = {
            "id": policy.id,
            "request_id": policy.customer_request.id,
            "sum_insured": str(policy.sum_insured) if policy.sum_insured else None,
            "start_date": policy.start_date,
            "end_date": policy.end_date,
            # "is_draft": policy.is_draft,
            "created_at": policy.created_at
        }

        return ResponseService.response("SUCCESS", data, "Customer request policy details fetched successfully.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch policy details.")


# @api_view(["GET"])
# def get_product_coverages_by_vendor(request):
#     try:
#         vendor_product_id = request.GET.get("vendor_product_id")
#         if not vendor_product_id:
#             return ResponseService.response(
#                 "VALIDATION_ERROR", {"vendor_product_id": "This field is required."}, "Validation Error"
#             )

#         coverages = ProductCoverage.objects.filter(
#             vendor_product_id=vendor_product_id, deleted_at__isnull=True
#         ).order_by("id")

#         result = [
#             {
#                 "id": cov.id,
#                 "name": cov.name,
#                 "coverage_amount": cov.coverage_amount,
#                 "excess_amount": cov.excess_amount,
#                 "limitation": cov.limitation,
#                 "is_mandatory": cov.is_mandatory,
#                 "vendor_product_id": cov.vendor_product_id,
#             }
#             for cov in coverages
#         ]

#         return ResponseService.response("SUCCESS", result, "Product coverages fetched successfully.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Fetch failed.")




# @api_view(["POST"])
# @transaction.atomic
# def store_customer_request_coverages(request):
#     data = request.data
#     rules = {
#         "request_id": "required|exists:cus_requests,id",
#         "values": "required|dict|min:1"
#     }

#     errors = ValidatorService.validate(data, rules)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Validation error")

#     request_id = data["request_id"]
#     values = data["values"]

#     try:
#         request_obj = CustomerRequest.objects.get(id=request_id)
#         stored = []

#         for coverage_id_str, amount in values.items():
#             try:
#                 coverage_id = int(coverage_id_str)
#                 coverage = ProductCoverage.objects.get(id=coverage_id)

#                 obj, created = CustomerRequestCoverage.objects.update_or_create(
#                     customer_request=request_obj,
#                     product_coverage=coverage,
#                     defaults={"value": amount},
#                     is_draft=True
#                 )
#                 stored.append({
#                     "coverage_id": coverage_id,
#                     "value": amount,
#                     "status": "created" if created else "updated"
#                 })
#             except ProductCoverage.DoesNotExist:
#                 continue

#         return ResponseService.response("SUCCESS", {
#             "request_id": request_id,
#             "coverages": stored
#         }, "Request coverages stored successfully.")

#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to store data.")


@api_view(["GET"])
def get_customer_request_coverages(request, request_id):
    try:
        if not CustomerRequest.objects.filter(id=request_id).exists():
            return ResponseService.response("NOT_FOUND", None, "Customer request not found.")

        coverages = CustomerRequestCoverageDetails.objects.filter(customer_request_id=request_id)

        data = [
            {
                "sum_insured": cov.sum_insured,
                "start_date": cov.start_date,
                "end_date": cov.end_date,
                # "is_draft": cov.is_draft
            }
            for cov in coverages
        ]

        return ResponseService.response("SUCCESS", data, "Request coverages fetched successfully.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Fetch failed.")




@api_view(["GET"])
def get_customer_request_full_details(request, request_id):
    try:
        # 1. Get main request
        customer_request = CustomerRequest.objects.select_related("form_submission", "status").filter(id=request_id).first()

        if not customer_request:
            return ResponseService.response("NOT_FOUND", None, "Customer request not found", system_code=404)

        # 2. Get form values
        form_values_qs = CoreFormSubmissionValue.objects.select_related(
            "custom_form_element", "form_element"
        ).filter(
            form_submission=customer_request.form_submission
        )

        form_values = []
        for val in form_values_qs:
            form_values.append({
                "custom_form_element_id": val.custom_form_element_id,
                "form_element_id": val.form_element_id,
                "value": val.value,
                "label": val.custom_form_element.label if val.custom_form_element else None,
                "code": val.custom_form_element.code if val.custom_form_element else None,
                "element_title": val.form_element.title if val.form_element else None,
                "element_category": val.form_element.category if val.form_element else None,
            })

        # 3. Get documents
        documents = list(CustomerRequestDocument.objects.filter(
            customer_request=customer_request
        ).select_related("document_type").values(
            "document_type_id",
            "document_type__name",
            "value",
            "uploaded_at"
        ))

        # 4. Get coverages
        coverages = CustomerRequestCoverageDetails.objects.filter(
            customer_request=customer_request
        ).values(
            "sum_insured",
            "start_date",
            "end_date",
            # "is_draft",
            "created_at"
        ).first()
        

        # 5. Get policy holder if available
        policy_holder = None
        try:
            holder = PolicyHolder.objects.get(customer_request=customer_request)
            policy_holder = {
                "id": holder.id,
                "policy_holder_name": holder.policy_holder_name,
                "date_of_birth": holder.date_of_birth,
                "gender": holder.gender,
                "nic": holder.nic,
                "phone_number": holder.phone_number,
                "email": holder.email,
                "address": holder.address,
                "contact_method": holder.contact_method,
                # "is_draft": holder.is_draft
            }
        except PolicyHolder.DoesNotExist:
            pass

        # 6. Get associated risk_type_ids and vendor_product_ids from the junction tables
        risk_type_ids = list(CustomerRequestRiskType.objects.filter(
            customer_request=customer_request
        ).values_list("risk_type_id", flat=True))

        vendor_product_ids = list(CustomerRequestVendorProduct.objects.filter(
            customer_request=customer_request
        ).values_list("vendor_product_id", flat=True))

        # 7. Get payment details if exists
        payment_details = None
        try:
            payment = CustomerRequestPaymentDetails.objects.get(customer_request=customer_request)
            payment_details = {
                "payment_method": payment.payment_method,
                "payment_frequency": payment.payment_frequency,
                "bank_number": payment.bank_number,
                "account_holder_name": payment.account_holder_name,
                "branch": payment.branch,
                "bank_name": payment.bank_name,
                "iban_swift_code": payment.iban_swift_code,
                "estimated_amount": str(payment.estimated_amount),  # Convert Decimal to string if needed
                # "is_draft": payment.is_draft,
                "created_at": payment.created_at
            }
        except CustomerRequestPaymentDetails.DoesNotExist:
            pass

                # 9. Get risk details documents
        risk_documents = list(CustomerRequestRiskDetails.objects.filter(
            customer_request=customer_request
        ).values(
            "type",
            "document_name",
            "document_link",
            "uploaded_at"
        ))


        # 8. Combine and respond
        return ResponseService.response("SUCCESS", {
            "request_id": customer_request.id,
            "request_code": customer_request.code,
            "type": customer_request.type,
            "status": customer_request.status.name if customer_request.status else None,
            "vendor_product_ids": vendor_product_ids,
            "risk_type_ids": risk_type_ids,
            "form_submission_id": customer_request.form_submission_id,
            "form_values": form_values,
            "documents": documents,
            "coverages": coverages,
            "policy_holder": policy_holder,
            "payment_details": payment_details,
            "risk_documents": risk_documents 
        }, "Customer request full details fetched successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch request details")



@api_view(["GET"])
def get_coverage_types(request):
    try:
        # Optional: Add filtering, pagination, etc. if needed
        data = (
            QueryBuilderService("crmp_coverage_types")
            .select("*")
            .orderBy("id", "asc")
            .leftJoin(
                "core_request_types as request_type",
                "request_type.id",
                "policy_base.request_type_id",
            )
            .leftJoin(
                "core_request_types as request_type",
                "request_type.id",
                "policy_base.request_type_id",
            )
            .get()
        )

        return ResponseService.response(
            "SUCCESS", data, "Coverage types fetched successfully."
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch coverage types"
        )
    



@api_view(["POST"])
@transaction.atomic
def store_customer_request_payment_details(request):
    data = request.data

    rules = {
        "request_id": "required|exists:cus_requests,id",
        "payment_method": "required|string|max:100",
        "payment_frequency": "required|string|max:100",
        "bank_number": "required|string|max:50",
        "account_holder_name": "required|string|max:255",
        "branch": "required|string|max:100",
        "bank_name": "required|string|max:255",
        "iban_swift_code": "nullable|string|max:100",  # only optional field
        "estimated_amount": "required|numeric",
        # "is_draft": "boolean"
    }


    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        request_id = data["request_id"]
        payment_details, created = CustomerRequestPaymentDetails.objects.update_or_create(
            customer_request_id=request_id,
            defaults={
                "payment_method": data.get("payment_method"),
                "payment_frequency": data.get("payment_frequency"),
                "bank_number": data.get("bank_number"),
                "account_holder_name": data.get("account_holder_name"),
                "branch": data.get("branch"),
                "bank_name": data.get("bank_name"),
                "iban_swift_code": data.get("iban_swift_code"),
                "estimated_amount": data.get("estimated_amount"),
                # "is_draft": data.get("is_draft", True)
            }
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "id": payment_details.id,
                "request_id": payment_details.customer_request.id,
                "mode": "created" if created else "updated"
            },
            "Customer request payment details stored successfully."
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to store payment details.")


@api_view(["GET"])
def get_customer_request_payment_details(request, request_id):
    try:
        data = CustomerRequestPaymentDetails.objects.filter(customer_request_id=request_id).values(
            "payment_method",
            "payment_frequency",
            "bank_number",
            "account_holder_name",
            "branch",
            "bank_name",
            "iban_swift_code",
            "estimated_amount",
            # "is_draft",
            "created_at"
        ).first()

        if not data:
            return ResponseService.response("NOT_FOUND", None, "Payment details not found for this request.",system_code=404)

        return ResponseService.response("SUCCESS", data, "Payment details fetched successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch payment details.")



@api_view(["GET"])
def get_entity_documents_by_customer_request(request, customer_request_id):
    """
    Enhanced entity documents endpoint that supports different document types based on the 'type' parameter.
    
    Parameters:
    - customer_request_id: Customer request ID
    - type: 'group' for product group documents, 'product' for vendor product documents
    """
    try:
        # Step 1: Get CustomerRequest
        customer_request = CustomerRequest.objects.filter(id=customer_request_id).first()
        if not customer_request:
            return ResponseService.response("NOT_FOUND", None, "Customer request not found.", system_code=404)

        # Step 2: Get type parameter
        doc_type = request.GET.get("type", "product")  # Default to 'product'
        
        # Step 3: Get CustomerRequestVendorProduct records
        request_vendor_products = CustomerRequestVendorProduct.objects.filter(
            customer_request=customer_request
        )

        if not request_vendor_products.exists():
            return ResponseService.response("NOT_FOUND", None, "No vendor products found for this request.", system_code=404)

        # Step 4: Build result based on type
        result = []
        seen_products = set()  # Track seen product IDs to avoid duplicates

        if doc_type == "group":
            # Get documents from product_group_id using the same approach as product_documents_enhanced
            for rvp in request_vendor_products:
                if rvp.product_group_id:
                    # Get product group details
                    from core_models.core_models import ProductGroup
                    try:
                        product_group = ProductGroup.objects.get(id=rvp.product_group_id)
                        
                        # Step 1: Get product_ids from core_product_group_products where product_group_id = rvp.product_group_id
                        group_products = QueryBuilderService("core_product_group_products")\
                            .select("product_id")\
                            .where("product_group_id", rvp.product_group_id)\
                            .get()
                        
                        if not group_products:
                            continue
                        
                        # Extract product IDs
                        product_ids = [gp["product_id"] for gp in group_products]
                        
                        # Step 2: Get vendor_product_ids from core_products_vendor_products where product_id in product_ids
                        vendor_product_mappings = QueryBuilderService("core_product_vendor_products")\
                            .select("vendor_product_id")\
                            .whereIn("product_id", product_ids)\
                            .get()
                        
                        if not vendor_product_mappings:
                            continue
                        
                        # Extract vendor product IDs
                        vendor_product_ids = [vpm["vendor_product_id"] for vpm in vendor_product_mappings]
                        
                        # Step 3: Get entity documents from vendor products - return individual products
                        for vp_id in vendor_product_ids:
                            # Skip if we've already processed this vendor product
                            if vp_id in seen_products:
                                continue
                            
                            try:
                                vendor_product = VendorProducts.objects.get(id=vp_id)
                                docs = EntityDocument.objects.filter(entity_id=vendor_product.entity_id).values(
                                    "id", "entity_id", "doc", "name", "type"
                                )

                                result.append({
                                    "product_name": vendor_product.name,
                                    "documents": list(docs)
                                })
                                
                                # Mark this vendor product as seen
                                seen_products.add(vp_id)
                            except VendorProducts.DoesNotExist:
                                continue
                    except ProductGroup.DoesNotExist:
                        continue
        else:
            # Get documents from vendor_product_id (default behavior)
            for rvp in request_vendor_products:
                if rvp.vendor_product_id:
                    # Skip if we've already processed this vendor product
                    if rvp.vendor_product_id in seen_products:
                        continue
                    
                    # Get vendor product details
                    try:
                        vendor_product = VendorProducts.objects.get(id=rvp.vendor_product_id)
                        
                        # Get entity documents for this vendor product
                        docs = EntityDocument.objects.filter(entity_id=vendor_product.entity_id).values(
                            "id", "entity_id", "doc", "name", "type"
                        )

                        result.append({
                            "product_name": vendor_product.name,
                            "documents": list(docs)
                        })
                        
                        # Mark this vendor product as seen
                        seen_products.add(rvp.vendor_product_id)
                    except VendorProducts.DoesNotExist:
                        continue

        if not result:
            return ResponseService.response("NOT_FOUND", None, f"No documents found for type '{doc_type}'.", system_code=404)

        return ResponseService.response("SUCCESS", result, "Entity documents fetched successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch entity documents.")





@api_view(["POST"])
@transaction.atomic
def finalize_customer_request(request, request_id):
    try:
        customer_request = CustomerRequest.objects.filter(id=request_id).first()
        if not customer_request:
            return ResponseService.response("NOT_FOUND", None, "Customer request not found.", system_code=404)

        # Update main request
        customer_request.is_draft = False
        customer_request.save()

        # Update coverage details (OneToOne)
        # CustomerRequestCoverageDetails.objects.filter(customer_request=customer_request).update(is_draft=False)

        # Update coverage items (Many)
        # CustomerRequestCoverage.objects.filter(customer_request=customer_request).update(is_draft=False)

        # Update documents
        # CustomerRequestDocument.objects.filter(customer_request=customer_request).update(is_draft=False)

        # Update payment details
        # CustomerRequestPaymentDetails.objects.filter(customer_request=customer_request).update(is_draft=False)

        # Update policy holder
        # PolicyHolder.objects.filter(customer_request=customer_request).update(is_draft=False)

      

        # Notification service
        try:
            request_type = customer_request.type
            if request_type == 'policy':
                pass
            elif request_type == 'quotation':
                pass
            elif request_type == 'claim':
                pass
            customer_id = request.user.get('id', 1)
            NotificationService.generate_notification(
                type_code=request_type,  # Example notification type code
                title=f"{request_type} Request Submitted",
                meta_data=CustomerRequestSerializer(customer_request).data,
                message=f"Customer request for {request_type}. Request ID: {request_id}",
                customer_id=customer_id
            )
        except Exception as notify_exc:
            print(f"NotificationService error: {notify_exc}")

        return ResponseService.response("SUCCESS", {"request_id": request_id}, "Customer request finalized successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to finalize customer request.")

#--------------------------------
# Export Risks to Excel
#--------------------------------

@api_view(["POST"])
def export_risks_to_excel(request):
    data = request.data
    errors = ValidatorService.validate(data, {"risk_type_ids": "required|list"})
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Invalid input")

    risk_ids = data["risk_type_ids"]
    if isinstance(risk_ids, (int, str)):
        risk_ids = [int(risk_ids)]

    queries = []

    for rt_id in risk_ids:
        opp = OpportunityType.objects.filter(id=rt_id).first()
        if not opp:
            continue
        title = (opp.title or f"Risk_{rt_id}")[:31]

        config = OpportunityFormConfig.objects.filter(
            opportunity_type_id=rt_id,
            data_gethering_type=OpportunityFormConfig.ONBOARDING
        ).first()
        if not config or not config.form_id:
            continue

        elements = CoreFormCustomFormElement.objects.filter(
            panel__form_id=config.form_id
        ).select_related("element").order_by("order_number")

        if not elements.exists():
            continue

        select_parts = []
        for el in elements:
            label = el.label or el.element.title or f"Field_{el.id}"
            safe_label = label.replace('"', '""')
            select_parts.append(f'NULL AS "{safe_label}"')

        if not select_parts:
            continue

        sql = f"""SELECT {', '.join(select_parts)} LIMIT 1"""
        queries.append({"query": sql, "title": title})

    if not queries:
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, "No valid data found")

    payload = {
        "queries": queries,
        "styles": {
            "common": {
                "header": {
                    "font": {"bold": True, "color": "0000FF"},
                    "alignment": {"horizontal": "center"}
                }
            }
        }
    }

    exporter = SQLToExcelExporter()
    export_response = exporter.export(payload)

    if export_response["status"] == "SUCCESS":
        return ResponseService.response("SUCCESS", export_response["data"], export_response["message"])

    return ResponseService.response("INTERNAL_SERVER_ERROR", None, export_response["message"])





@api_view(["POST"])
@transaction.atomic
def store_customer_risk_document(request):
    data = request.data

    rules = {
        "request_id": "required|exists:cus_requests,id",
        "type": "required|in:claim,policy,quotation",
        "document_link": "required|string",
        "document_name": "nullable"
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        request_id = data["request_id"]
        document_link = data["document_link"]
        doc_type = data["type"]
        document_name = data.get("document_name", None)

        document, created = CustomerRequestRiskDetails.objects.update_or_create(
            customer_request_id=request_id,
            document_link=document_link,
            defaults={"type": doc_type,"document_name": document_name},
            
            
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "id": document.id,
                "customer_request_id": document.customer_request.id,
                "mode": "created" if created else "updated"
            },
            "Customer request document stored successfully."
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to store customer document.")



@api_view(["GET"])
def get_customer_risk_documents(request, request_id):
    try:
        query = (
            QueryBuilderService("cus_request_risk_details")
            .select("*")
            .where("customer_request_id", request_id)
            .first()
        )

        if not query:
            return ResponseService.response("NOT_FOUND", None, "No document found.", system_code=404)

        return ResponseService.response("SUCCESS", query, "Customer request document fetched successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch document.")
