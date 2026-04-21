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
    def send_approval_notification(approval_users, approval_roles, request_type, request_id, request_code, customer_name, product_name, entity_id, approval_url, additional_metadata=None):
        """
        Send approval request notifications to approvers (users and/or roles)
        
        Args:
            approval_users: List of user IDs who need to approve
            approval_roles: List of role IDs whose members need to approve
            request_type: 'quotation' or 'policy'
            request_id: The ID of the quotation or policy request
            request_code: The display code (e.g., QR-001, PR-001)
            customer_name: Name of the customer/lead
            product_name: Name of the product/opportunity type (can be comma-separated for multiple)
            entity_id: Entity ID for constructing the approval link
            approval_url: Frontend approval screen URL
            additional_metadata: Optional dict with extra metadata (opportunity_types, service_providers, etc.)
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get or create notification type
            type_code = f"{request_type}_approval"
            notification_type = QueryBuilderService("core_notification_types") \
                .select('id') \
                .where("code", type_code) \
                .first()
            
            if not notification_type:
                notification_type = QueryBuilderService("core_notification_types").insert({
                    "code": type_code,
                    "name": f"{request_type.capitalize()} Approval Request",
                    "color": "#FF9800",
                    "created_at": current_time,
                    "updated_at": current_time
                })
                notification_type = QueryBuilderService("core_notification_types") \
                    .select('id') \
                    .where("code", type_code) \
                    .first()
            
            # Prepare notification metadata
            meta_data = {
                "request_id": request_id,
                "request_code": request_code,
                "request_type": request_type,
                "customer_name": customer_name,
                "product_name": product_name,
                "entity_id": entity_id,
                "approval_url": approval_url
            }
            
            # Add additional metadata if provided
            if additional_metadata:
                meta_data.update(additional_metadata)
            
            # Prepare notification title and message
            title = f"{request_type.capitalize()} Approval Request - {request_code}"
            
            # Use custom message if provided in additional metadata, otherwise use default
            if additional_metadata and additional_metadata.get("custom_message"):
                message = additional_metadata.get("custom_message")
            else:
                message = f"New {request_type} approval request for {customer_name} - {product_name}. Request ID: {request_code}"
            
            # Create the main notification record
            notification_data = {
                "customer_id": None,  # Approval notifications are not customer-specific
                "user_id": None,  # Will be set for each user
                "type_id": notification_type["id"] if notification_type else None,
                "title": title,
                "message": message,
                "sent_at": current_time,
                "metadata": json.dumps(meta_data),
                "created_at": current_time,
                "updated_at": current_time,
            }
            
            print(f"Sending approval notification for {request_type} {request_code}")
            
            # Send notifications to specific users
            if approval_users:
                for user_id in approval_users:
                    if user_id:
                        try:
                            notification_data["user_id"] = user_id
                            notification = QueryBuilderService("core_notifications").insert(notification_data)
                            
                            # Create notification-user link
                            QueryBuilderService("core_notification_users").insert({
                                "notification_id": notification["id"],
                                "user_id": user_id,
                                "is_read": False,
                                "is_clear": False,
                                "read_at": None,
                            })
                            print(f"Notification sent to user {user_id}")
                        except Exception as e:
                            print(f"Failed to send notification to user {user_id}: {str(e)}")
            
            # Send notifications to users belonging to specific roles
            if approval_roles:
                for role_id in approval_roles:
                    if role_id:
                        try:
                            # Get all users with this role
                            users_with_role = QueryBuilderService("core_users") \
                                .select("id") \
                                .where("role_id", role_id) \
                                .where("is_active", True) \
                                .get()
                            
                            for user in users_with_role:
                                user_id = user.get("id")
                                try:
                                    notification_data["user_id"] = user_id
                                    notification = QueryBuilderService("core_notifications").insert(notification_data)
                                    
                                    # Create notification-user link
                                    QueryBuilderService("core_notification_users").insert({
                                        "notification_id": notification["id"],
                                        "user_id": user_id,
                                        "is_read": False,
                                        "is_clear": False,
                                        "read_at": None,
                                    })
                                    print(f"Notification sent to user {user_id} (role {role_id})")
                                except Exception as e:
                                    print(f"Failed to send notification to user {user_id} in role {role_id}: {str(e)}")
                        except Exception as e:
                            print(f"Failed to get users for role {role_id}: {str(e)}")
            
            return ResponseService.response(
                "SUCCESS", None, "Approval notifications sent successfully.")
        except Exception as e:
            print(f"send_approval_notification error: {str(e)}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", None, f"Failed to send approval notifications: {str(e)}")


 # NotificationService call (safe, does not affect main flow)
        # try:
        #     NotificationService.generate_notification(
        #         type_code="policy",  # Example notification type code
        #         title="Payment Confirmation Request",
        #         meta_data={"payment_id": result, "amount": data.get("paid_amount"),"invoice_id":data.get('invoice_id')},
        #         message=f"Payment of amount {data.get('paid_amount')} received for invoice {data.get('invoice_id')}",
        #         customer_id=customer_id
        #         user_id=user.id if user else None
        #     )
        # except Exception as notify_exc:
        #     print(f"NotificationService error: {notify_exc}")