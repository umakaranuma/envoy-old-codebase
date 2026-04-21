from django.db import models
from datetime import datetime
from mServices import QueryBuilderService
from envoy_bu_crm_api.quotation.services.send_mail_service import SendMail
from mServices.ValidatorService import ValidatorService

class RiskLevel(models.IntegerChoices):
    LOW = 1, "Low"
    MEDIUM = 2, "Medium"
    HIGH = 3, "High"


class Status(models.IntegerChoices):
    Requested = 1, "Requested"
    Received = 2, "Received"
    Issued = 3, "Issued"


class EndorsementStatus(models.IntegerChoices):
    Settled = 1, "Settled"
    Pending = 2, "Pending"


def handle_entity(entity_data, entity_id=None, user=None, created_at=None):

    now = datetime.now()

    if entity_id:
        # Update the existing entity
        update_data = {
            **entity_data,
            "updated_by_id": user.id if user else None,
            "updated_at": now,
        }
        QueryBuilderService("core_entities").where("id", entity_id).update(update_data)
        return entity_id
    else:
        # Create a new entity
        create_data = {
            **entity_data,
            "created_by_id": user.id if user else None,
            "created_at": created_at if created_at else now,
        }
        entity = QueryBuilderService("core_entities").insert(create_data)
        return entity["id"]


# def handle_entity_notes(entity_id, notes, is_update=False):
#     if not notes:
#         return None

#     qb = QueryBuilderService("core_entity_notes")

#     if is_update:
#         note = notes[0]
#         updated = qb.where("entity_id", entity_id).update(
#             {
#                 "notes": note.get("note"),
#                 "is_high_priority": 0,
#                 "added_at": note.get("created_at") or datetime.now(),
#                 "created_by_id": note.get("created_by_id")
#             }
#         )
#     else:
#         inserted = []
#         for note in notes:
#             inserted.append(
#                 qb.insert({
#                     "notes": note.get("note"),
#                     "entity_id": entity_id,
#                     "is_high_priority": 0,
#                     "added_at": note.get("created_at") or datetime.now(),
#                     "created_by_id": note.get("created_by_id")
#                 })
#             )
#         updated = inserted

#     return updated


def get_recipient_email_by_customer_id(customer_id):
    primary_contact = (
        QueryBuilderService("core_contacts")
        .where("id", customer_id)
        .select("id")
        .first()
    )
    if not primary_contact or not primary_contact.get("id"):
        return None, "Primary contact not found."

    contact = (
        QueryBuilderService("core_contacts")
        .where("id", primary_contact["id"])
        .select("email")
        .first()
    )
    if not contact or not contact.get("email"):
        return None, "Email not found for contact."

    return contact["email"], None


def send_approval_email_helper(recipient_email, subject, body, links=None):
    print("Sending email to:", recipient_email)

    # Step 1: Sanitize and validate links
    links = links or []
    base_url = 'https://exporter.utilities.apptimus.lk/'
    fixed_links = []

    for link in links:
        if not (link.startswith("http://") or link.startswith("https://")):
            fixed_links.append(base_url.rstrip('/') + '/' + link.lstrip('/'))
        else:
            fixed_links.append(link)

    # Step 2: Validate each link
    link_errors = {}
    for idx, link in enumerate(fixed_links):
        validation = ValidatorService.validate({"link": link}, {"link": "required|url"})
        if validation:
            link_errors[str(idx)] = validation["link"]

    if link_errors:
        return {
            "success": False,
            "error": {"email_data": [{"links": link_errors}]},
            "message": "Validation Error"
        }

    # Step 3: Build email payload
    email_payload = [{
        "recipient_email": recipient_email,
        "subject": subject,
        "body": body,
        "priority": "high",
        "links": fixed_links,
    }]

    # Step 4: Send email
    send_mail = SendMail()
    result = send_mail.send_email(email_payload)

    # Step 5: Interpret result from notifier service
    if isinstance(result, dict) and result.get("email_data"):
        for item in result["email_data"]:
            if "links" in item:
                return {
                    "success": False,
                    "error": result,
                    "message": "Validation Error"
                }

    if not isinstance(result, dict) or not result.get("success", True):
        return {
            "success": False,
            "error": result,
            "message": "Email sending failed"
        }

    return {
        "success": True,
        "data": result,
        "message": "Approval mail sent successfully"
    }


def handle_entity_docs(entity_id, docs, is_update=False):
    if not docs:
        return None

    qb = QueryBuilderService("core_entity_docs")

    if is_update:
        updated_rows = []
        for doc in docs:
            updated = (
                qb.where("entity_id", entity_id)
                .update(
                    {
                        "doc": doc.get("doc"),
                        "name": doc.get("name"),
                        # "type": doc.get("type"),
                    }
                )
            )
            updated_rows.append(updated)
        return updated_rows
    else:
        inserted_rows = []
        for doc in docs:
            inserted = qb.insert(
                {
                    "entity_id": entity_id,
                    "doc": doc.get("doc"),
                    "name": doc.get("name"),
                    "type": doc.get("type"),
                }
            )
            inserted_rows.append(inserted)
        return inserted_rows

def handle_entity_notes_by_id(id, notes):
    if not notes:
        return None

    qb = QueryBuilderService("core_entity_notes")

    updated = qb.where("id", id).update(
            {"notes": notes, "is_high_priority": 0, "added_at": datetime.now()}
        )


    return updated

def _format_date_fields(record):
    """
    Convert any datetime or ISO-string fields ending with '_at' in the record
    into a YYYY-MM-DD date string, dropping time and timezone info.
    """
    for key, value in list(record.items()):
        if not (key.endswith('_at') or key.endswith('_date')):
            continue

        ts = value
        if not ts:
            continue

        # Parse string timestamps if necessary
        if isinstance(ts, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):  # common formats
                try:
                    ts = datetime.strptime(ts, fmt)
                    break
                except ValueError:
                    continue
            else:
                try:
                    ts = datetime.fromisoformat(ts)
                except Exception:
                    continue

        # If ts is now a datetime, format date-only
        if isinstance(ts, datetime):
            record[key] = ts.date().isoformat()
            
            

def handle_entity_notes(entity_id, notes, is_update=False):
    if not notes:
        return None

    qb = QueryBuilderService("core_entity_notes")

    if is_update:
        note = notes[0]
        # Try to update first
        updated = qb.where("entity_id", entity_id).update({
            "notes": note.get("note"),
            "is_high_priority": 0,
            "added_at": note.get("created_at") or datetime.now(),
            "created_by_id": note.get("created_by_id")
        })

        # If update failed (e.g. no matching record), insert instead
        if not updated:
            updated = qb.insert({
                "notes": note.get("note"),
                "entity_id": entity_id,
                "is_high_priority": 0,
                "added_at": note.get("created_at") or datetime.now(),
                "created_by_id": note.get("created_by_id")
            })

    else:
        # Just insert all notes
        updated = []
        for note in notes:
            inserted_id = qb.insert({
                "notes": note.get("note"),
                "entity_id": entity_id,
                "is_high_priority": 0,
                "added_at": datetime.now(),
                "created_by_id": None
            })
            updated.append(inserted_id)

    return updated

def replace_empty_strings_with_none(data: dict, keys: list) -> dict:
    """
    Replace empty string values with None for specified keys in a dictionary.

    :param data: The original dictionary (e.g., request.data)
    :param keys: List of keys to check and replace if value is ''
    :return: The updated dictionary with '' replaced by None
    """
    for key in keys:
        if data.get(key) == '':
            data[key] = None
    return data
