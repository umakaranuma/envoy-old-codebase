import json
from datetime import datetime
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from messages import Message, Error
from django.views.decorators.csrf import csrf_exempt
from envoy_bu_crm_api.quotation.services.NotificationService import NotificationService
from envoy_bu_crm_api.quotation.Controllers.QuotationController import _is_quotation_request_approval_required

@csrf_exempt
@api_view(['POST'])
def quotation_trigger(request):
    data = request.data

    rules = {
        "entity_data": "required",
        "entity_type": "required",
        "action": "required",
        "email_data": "optional",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Extract IDs
    entity_id = data.get("entity_data", {}).get("id")
    entity_type = data.get("entity_type")
    action = data.get("action")

    if not entity_id:
        return ResponseService.response("VALIDATION_ERROR", "Missing entity_id inside entity_data.", Error.VALIDATION_ERROR)

    # Extract optional email and documents
    email_data = data.get("email_data", {})
    
    # Extract documents from email_data (only documents, not defaultDocuments)
    documents = email_data.get("documents", [])

    print("Email:", email_data)
    print("Documents:", documents)

    # If this is a quotation entity and quotation_request_approval is false, mark as approved directly (no approval process)
    quotation_row = QueryBuilderService("crmq_quotations").where("entity_id", entity_id).first()
    if quotation_row and not _is_quotation_request_approval_required():
        QueryBuilderService("core_entities").where("id", entity_id).update({"approvel_status": True})
        existing_approval = QueryBuilderService("core_entity_approvals").where("entity_id", entity_id).first()
        if not existing_approval:
            user = request.user if request.user.is_authenticated else None
            QueryBuilderService("core_entity_approvals").insert({
                "entity_id": entity_id,
                "user": user.id if user else None,
                "role": None,
                "level": 1,
                "status": "approved",
                "remarks": None,
                "approved_by": user.id if user else None,
                "date": datetime.now(),
            })
        # Set quotation status to in_progress (no longer draft)
        in_progress_status = (
            QueryBuilderService("core_status")
            .select("id", "name")
            .where("type", "quotation_inprogress")
            .where("module", "quotation")
            .first()
        )
       
        if in_progress_status:
            QueryBuilderService("crmq_quotations").where("entity_id", entity_id).update({
                "status_id": in_progress_status["id"],
                "status": in_progress_status["name"],
            })
        if not email_data:
            email_data = {"subject": "No Subject", "body": "No content available."}
        cleaned_email_data = {
            "subject": email_data.get("subject", "No Subject"),
            "body": email_data.get("body", "No content available."),
        }
        storage_data = {"documents": documents, "email_data": cleaned_email_data}
        QueryBuilderService("crmq_quotations").where("entity_id", entity_id).update({"email_data": json.dumps(storage_data)})
        return ResponseService.response("SUCCESS", "Quotation created without approval (quotation_request_approval is false).", Message.DATA_CREATED)

    # Fetch approval rules
    ruleCheck = QueryBuilderService('core_entity_approval_rules')\
        .where('entity_type', entity_type)\
        .where('action', action)\
        .first()

    if not ruleCheck or not ruleCheck.get("rule"):
        QueryBuilderService('core_entities')\
            .where('id', entity_id)\
            .update({'approvel_status': True})
        return ResponseService.response("SUCCESS", "No rule found. Marked approved.", Message.DATA_CREATED)

    try:
        parsed_rule = json.loads(ruleCheck["rule"])
        rules = parsed_rule.get("rules", [])
    except Exception:
        return ResponseService.response("VALIDATION_ERROR", "Invalid rule format.", Error.VALIDATION_ERROR)

    if not rules:
        QueryBuilderService('core_entities')\
            .where('id', entity_id)\
            .update({'approvel_status': True})
        return ResponseService.response("SUCCESS", "No approval rules defined.", Message.DATA_CREATED)

    # Update approvel_status
    QueryBuilderService('core_entities')\
        .where('id', entity_id)\
        .update({'approvel_status': False})

    # Insert approvals
    sorted_rules = sorted(rules, key=lambda r: r.get("level", 0))
    min_level = sorted_rules[0]["level"]
    default_status = ruleCheck.get("default_status", "draft")

    # Collect first-level approvers for notification
    first_level_users = []
    first_level_roles = []

    for rule in sorted_rules:
        status = "pending" if rule.get("level") == min_level else default_status
        QueryBuilderService("core_entity_approvals").insert({
            "entity_id": entity_id,
            "user": rule.get("user"),
            "role": rule.get("role"),
            "level": rule.get("level"),
            "status": status,
            "remarks": None
        })
        
        # Collect first-level approvers for notifications
        if rule.get("level") == min_level:
            if rule.get("user"):
                first_level_users.append(rule.get("user"))
            if rule.get("role"):
                first_level_roles.append(rule.get("role"))

    # Send approval notifications to first-level approvers
    try:
        # Fetch quotation details for notification
        quotation_details = QueryBuilderService("crmq_quotations") \
            .select(
                "crmq_quotations.id",
                "crmq_quotations.code",
                "crmq_quotations.customer_id",
                "crmq_quotations.opportunity_type_id",
                "crmq_quotations.opportunity_id",
                "core_customers.name as customer_name",
                "crm_opportunities.title as opportunity_title"
            ) \
            .leftJoin("core_customers", "core_customers.id", "crmq_quotations.customer_id") \
            .leftJoin("crm_opportunities", "crm_opportunities.id", "crmq_quotations.opportunity_id") \
            .where("crmq_quotations.entity_id", entity_id) \
            .first()
        
        if quotation_details:
            # Get ALL opportunity types/product names
            opportunity_type_names = []
            opportunity_type_ids_str = quotation_details.get("opportunity_type_id")
            
            try:
                if isinstance(opportunity_type_ids_str, str):
                    opportunity_type_ids = json.loads(opportunity_type_ids_str)
                elif isinstance(opportunity_type_ids_str, list):
                    opportunity_type_ids = opportunity_type_ids_str
                elif opportunity_type_ids_str:
                    opportunity_type_ids = [opportunity_type_ids_str]
                else:
                    opportunity_type_ids = []
                
                if opportunity_type_ids and len(opportunity_type_ids) > 0:
                    # Fetch ALL opportunity type names
                    opp_types = QueryBuilderService("crm_opportunity_types") \
                        .select("id", "title") \
                        .whereIn("id", opportunity_type_ids) \
                        .get()
                    
                    if opp_types:
                        opportunity_type_names = [opp.get("title") for opp in opp_types if opp.get("title")]
            except Exception as e:
                print(f"Error fetching opportunity types: {str(e)}")
            
            # Get ALL service providers for this quotation
            service_provider_names = []
            try:
                service_providers = QueryBuilderService("crmq_quotation_service_providers") \
                    .select(
                        "crmq_quotation_service_providers.service_provider_id",
                        "core_service_providers.name as service_provider_name"
                    ) \
                    .leftJoin("core_service_providers", "core_service_providers.id", "crmq_quotation_service_providers.service_provider_id") \
                    .where("crmq_quotation_service_providers.quotation_id", quotation_details.get("id")) \
                    .get()
                
                if service_providers:
                    service_provider_names = [sp.get("service_provider_name") for sp in service_providers if sp.get("service_provider_name")]
            except Exception as e:
                print(f"Error fetching service providers: {str(e)}")
            
            # Format product/opportunity types for display
            product_name = ", ".join(opportunity_type_names) if opportunity_type_names else "N/A"
            service_providers_display = ", ".join(service_provider_names) if service_provider_names else "N/A"
            
            # Prepare comprehensive message
            notification_message = f"New quotation approval request {quotation_details.get('code', 'N/A')} for {quotation_details.get('customer_name', 'N/A')}"
            if opportunity_type_names:
                notification_message += f" - Products: {product_name}"
            if service_provider_names:
                notification_message += f" - Insurense: {service_providers_display}"
            
            # Send notification with all details
            NotificationService.send_approval_notification(
                approval_users=first_level_users,
                approval_roles=first_level_roles,
                request_type="quotation",
                request_id=quotation_details.get("id"),
                request_code=quotation_details.get("code", "N/A"),
                customer_name=quotation_details.get("customer_name", "N/A"),
                product_name=product_name,
                entity_id=entity_id,
                approval_url="/quotation-approval",
                additional_metadata={
                    "opportunity_id": quotation_details.get("opportunity_id"),
                    "opportunity_title": quotation_details.get("opportunity_title"),
                    "opportunity_types": opportunity_type_names,
                    "service_providers": service_provider_names,
                    "custom_message": notification_message
                }
            )
            print(f"Approval notification sent for quotation {quotation_details.get('code')} with all details")
    except Exception as notify_error:
        print(f"Failed to send approval notification: {str(notify_error)}")
        # Don't fail the main flow if notification fails

    # Set dummy email_data if not provided
    if not email_data:
        email_data = {
            "subject": "No Subject",
            "body": "No content available."
        }

    # Create cleaned email_data (remove documents and defaultDocuments)
    cleaned_email_data = {
        "subject": email_data.get("subject", "No Subject"),
        "body": email_data.get("body", "No content available.")
    }

    # Create the storage format as requested
    storage_data = {
        "documents": documents,
        "email_data": cleaned_email_data
    }

    # Save the data in the quotation table
    QueryBuilderService("crmq_quotations")\
        .where("entity_id", entity_id)\
        .update({"email_data": json.dumps(storage_data)})


    # Optionally store or send email and document metadata (example print only)
    if email_data:
        print("Storing Email Subject:", email_data.get("subject"))
        print("Storing Email Body:", email_data.get("body"))

    if documents:
        for doc in documents:
            print(f"Doc Name: {doc.get('name')} | Type: {doc.get('type')} | Path: {doc.get('doc')}")

    return ResponseService.response("SUCCESS", "Approval routing initiated with email and document data.", Message.DATA_CREATED)


