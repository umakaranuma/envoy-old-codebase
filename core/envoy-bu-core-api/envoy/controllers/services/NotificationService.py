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

            # 2. Validate that at least customer_id or user_id is provided
            if not customer_id and not user_id:
                return ResponseService.response(
                    "VALIDATION_ERROR", None, "Either Customer ID or User ID must be provided.")

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

            # 4. Create notification-user link (for customer or user)
            notification_user_data = {
                "notification_id": notification["id"] if notification else None,
                "is_read": False,
                "is_clear": False,
                "read_at": None,
            }
            
            # Add customer_id or user_id based on which is provided
            if customer_id:
                notification_user_data["customer_id"] = customer_id
            if user_id:
                notification_user_data["user_id"] = user_id
            
            print("notification_user_data", notification_user_data)
            try:
                QueryBuilderService("core_notification_users").insert(notification_user_data)
            except Exception as user_insert_exc:
                print("Notification user insert error:", user_insert_exc)

            # Push real-time event so frontend can refetch /api/all-notifications (SSE)
            try:
                from envoy.controllers.notification_live import broadcast_new_notification
                if user_id:
                    broadcast_new_notification(user_id)
            except Exception as broadcast_exc:
                print("Notification broadcast (SSE) error:", broadcast_exc)

            return ResponseService.response(
                "SUCCESS", notification, "Notification generated successfully.")
        except Exception as e:
            print("NotificationService error in service:", e)
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", None, f"Failed to generate notification: {str(e)}")


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