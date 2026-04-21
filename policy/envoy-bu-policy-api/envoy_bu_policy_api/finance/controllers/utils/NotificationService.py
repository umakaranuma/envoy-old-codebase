from mServices.QueryBuilderService import QueryBuilderService
from mServices.ResponseService import ResponseService
from datetime import datetime
import json

class NotificationService:
    @staticmethod
    def generate_notification(type_code, title, meta_data, message, customer_id, user_id):
        try:
            print(123)
            print("notification insert data :", type_code, title, meta_data, message, customer_id, user_id)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 1. Get notification type by code
            notification_type = QueryBuilderService("core_notification_types") \
                .select('id')\
                .where("code", type_code) \
                .first()
            print("Queried notification_type:", notification_type)
            if not notification_type:
                insert_type_data = {
                    "code": type_code,
                    "name": title,
                    "color": "#4CAF50",
                    "created_at": current_time,
                    "updated_at": current_time
                }
                print("insert_type_data", insert_type_data)
                try:
                    notification_type = QueryBuilderService("core_notification_types").insert(insert_type_data)  # Create new notification type if not found
                    print("Inserted notification_type:", notification_type)
                except Exception as e:
                    print("Insert error:", e)
                # Re-query to get the id
                notification_type = QueryBuilderService("core_notification_types") \
                    .select('id')\
                    .where("code", type_code) \
                    .first()
                print("Re-queried notification_type:", notification_type)

            # 2. Get customer_id from parameter
            if not customer_id:
                return ResponseService.response(
                    "VALIDATION_ERROR", None, "Customer ID not provided.")

            # 3. Prepare notification data
            print("Current time for notification:", current_time)
            notification_data = {
                "customer_id": customer_id,
                "user_id": user_id,
                "type_id": notification_type["id"] if notification_type else None,
                "title": title,
                "message": message,
                "sent_at": current_time,
                "metadata": json.dumps(meta_data),
                "created_at": current_time,
                "updated_at": current_time,
            }
            print("notification_data", notification_data)
            try:
                notification = QueryBuilderService("core_notifications").insert(notification_data)
                print("Inserted notification:", notification)
            except Exception as insert_exc:
                print("Notification insert error:", insert_exc)
                raise

            # 4. Create notification-customer link (only customer)
            notification_user_data = {
                "notification_id": notification["id"] if notification else None,
                "customer_id": customer_id,
                "is_read": False,
                "is_clear": False,
                "read_at": None,
            }
            print("notification_user_data", notification_user_data)
            try:
                QueryBuilderService("core_notification_users").insert(notification_user_data)
            except Exception as user_insert_exc:
                print("Notification user insert error:", user_insert_exc)

            return ResponseService.response(
                "SUCCESS", notification, "Notification generated successfully.")
        except Exception as e:
            print("NotificationService error in service:", e)
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", None, f"Failed to generate notification: {str(e)}")

    @staticmethod
    def generate_detailed_notification(type_code, title, detailed_message, customer_id, user_id, 
                                    policy_data=None, payment_data=None, claim_data=None, 
                                    endorsement_data=None, links=None):
        """
        Generate detailed notification with rich content and links
        
        Args:
            type_code: Notification type code
            title: Notification title
            detailed_message: Rich formatted message with details
            customer_id: Customer ID
            user_id: User ID
            policy_data: Policy information dict
            payment_data: Payment information dict
            claim_data: Claim information dict
            endorsement_data: Endorsement information dict
            links: List of link objects with title and url
        """
        try:
            # Prepare enhanced metadata
            enhanced_metadata = {
                "timestamp": datetime.now().isoformat(),
                "type": type_code,
                "links": links or [],
                "policy": policy_data or {},
                "payment": payment_data or {},
                "claim": claim_data or {},
                "endorsement": endorsement_data or {}
            }
            
            return NotificationService.generate_notification(
                type_code=type_code,
                title=title,
                meta_data=enhanced_metadata,
                message=detailed_message,
                customer_id=customer_id,
                user_id=user_id
            )
        except Exception as e:
            print(f"Detailed notification error: {e}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", None, f"Failed to generate detailed notification: {str(e)}")

    @staticmethod
    def format_policy_issued_message(policy_number, premium_amount, product_name, 
                                    policy_doc_url=None, debit_note_url=None, policy_link=None):
        """Format policy issued notification message"""
        message_parts = [
            f"Policy Successfully Issued!",
            f"",
            f"Policy Number: {policy_number}",
            f"Premium Amount: {premium_amount}",
            f"Product: {product_name}",
            f""
        ]
        
        if policy_doc_url:
            message_parts.append(f"Policy Document: {policy_doc_url}")
        if debit_note_url:
            message_parts.append(f"Debit Note: {debit_note_url}")
            
        message_parts.extend([
            f"",
            f"Your policy is now active and coverage has begun.",
            f""
        ])
        
        if policy_link:
            message_parts.append(f"View Policy Details: {policy_link}")
            
        return "\n".join(message_parts)

    @staticmethod
    def format_payment_due_message(policy_number, product_name, due_amount, 
                                 payment_date, credit_age_days, payment_link=None):
        """Format payment due notification message"""
        message_parts = [
            f"Payment Due Reminder",
            f"",
            f"Policy Number: {policy_number}",
            f"Product: {product_name}",
            f"Due Amount: {due_amount}",
            f"Payment Date: {payment_date}",
            f""
        ]
        
        if credit_age_days > 0:
            message_parts.extend([
                f"Credit Age: {credit_age_days} days overdue",
                f"",
                f"Please make payment immediately to avoid further penalties."
            ])
        else:
            message_parts.extend([
                f"Payment is due soon",
                f"",
                f"Please make payment before the due date."
            ])
            
        message_parts.extend([
            f"",
            f"Make Payment: {payment_link}" if payment_link else ""
        ])
        
        return "\n".join(message_parts)

    @staticmethod
    def format_payment_reminder_message(policy_number, product_name, amount, 
                                       payment_date, payment_link=None):
        """Format payment reminder notification message"""
        message_parts = [
            f"Upcoming Payment Reminder",
            f"",
            f"Policy Number: {policy_number}",
            f"Product: {product_name}",
            f"Amount: {amount}",
            f"Payment Date: {payment_date}",
            f"",
            f"This is a friendly reminder that your payment is coming due.",
            f"",
            f"Make Payment: {payment_link}" if payment_link else ""
        ]
        
        return "\n".join(message_parts)

    @staticmethod
    def format_renewal_reminder_message(policy_number, product_name, expiry_date, renewal_link=None):
        """Format policy renewal reminder notification message"""
        message_parts = [
            f"Policy Renewal Reminder",
            f"",
            f"Policy Number: {policy_number}",
            f"Product: {product_name}",
            f"Expiry Date: {expiry_date}",
            f"",
            f"Your policy is approaching its expiry date.",
            f"",
            f"Renew Policy: {renewal_link}" if renewal_link else ""
        ]
        
        return "\n".join(message_parts)

    @staticmethod
    def format_payment_confirmation_message(policy_number, product_name, payment_amount, 
                                          confirmation_receipt_url=None):
        """Format payment confirmation notification message"""
        message_parts = [
            f"Payment Confirmed by Insurer",
            f"",
            f"Policy Number: {policy_number}",
            f"Product: {product_name}",
            f"Payment Amount: {payment_amount}",
            f"",
            f"Your payment has been confirmed by the insurer.",
            f""
        ]
        
        if confirmation_receipt_url:
            message_parts.append(f"Confirmation Receipt: {confirmation_receipt_url}")
            
        return "\n".join(message_parts)

    @staticmethod
    def format_claim_submitted_message(policy_id, product_name):
        """Format claim submitted notification message"""
        message_parts = [
            f"Claim Submitted",
            f"",
            f"Policy ID: {policy_id}",
            f"Product: {product_name}",
            f"",
            f"Your claim has been submitted and is under review.",
            f""
        ]
        
        return "\n".join(message_parts)

    @staticmethod
    def format_claim_status_change_message(policy_id, product_name, current_status):
        """Format claim status change notification message"""
        message_parts = [
            f"Claim Status Updated",
            f"",
            f"Policy ID: {policy_id}",
            f"Product: {product_name}",
            f"Current Status: {current_status}",
            f"",
            f"Your claim status has been updated.",
            f""
        ]
        
        return "\n".join(message_parts)

    @staticmethod
    def format_claim_settled_message(policy_id, product_name, current_status, settled_amount):
        """Format claim settled notification message"""
        message_parts = [
            f"Claim Settled",
            f"",
            f"Policy ID: {policy_id}",
            f"Product: {product_name}",
            f"Status: {current_status}",
            f"Settled Amount: {settled_amount}",
            f"",
            f"Your claim has been settled and payment processed.",
            f""
        ]
        
        return "\n".join(message_parts)

    @staticmethod
    def format_endorsement_message(policy_id, product_name, endorsement_type, 
                                  debit_credit_note=None, endorsement_value=None):
        """Format endorsement notification message"""
        message_parts = [
            f"Endorsement Processed",
            f"",
            f"Policy ID: {policy_id}",
            f"Product: {product_name}",
            f"Endorsement Type: {endorsement_type}",
            f""
        ]
        
        if endorsement_value:
            message_parts.append(f"Value: {endorsement_value}")
            
        if debit_credit_note:
            message_parts.append(f"Note: {debit_credit_note}")
            
        message_parts.extend([
            f"",
            f"Your policy endorsement has been processed successfully.",
            f""
        ])
        
        return "\n".join(message_parts)

    @staticmethod
    def format_policy_expiration_warning_message(policy_id, product_name, expiry_date, renewal_link=None):
        """Format policy expiration warning notification message"""
        message_parts = [
            f"Policy Expiration Warning",
            f"",
            f"Policy ID: {policy_id}",
            f"Product: {product_name}",
            f"Expiry Date: {expiry_date}",
            f"",
            f"Your policy is approaching its expiry date. Please take action to renew or extend your coverage.",
            f""
        ]
        
        if renewal_link:
            message_parts.append(f"Renew Policy: {renewal_link}")
            
        return "\n".join(message_parts)