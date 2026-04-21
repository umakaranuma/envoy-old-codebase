from mServices.QueryBuilderService import QueryBuilderService
from mServices.ResponseService import ResponseService
from datetime import datetime
import json

class NotificationService:
    @staticmethod
    def generate_notification(type_code, title, meta_data, message, customer_id, entity_id=None):
        try:
            print(123)
            # 1. Get notification type by code
            notification_type = QueryBuilderService("core_notification_types") \
                .select('id')\
                .where("code", type_code) \
                .first()
            if not notification_type:
                return ResponseService.response(
                    "NOT_FOUND", None, f"Notification type '{type_code}' not found.")

            # 2. Get customer_id from parameter
            if not customer_id:
                return ResponseService.response(
                    "VALIDATION_ERROR", None, "Customer ID not provided.")

            # 3. If entity_id is not provided, fetch it from core_customers
            if not entity_id:
                customer = (
                    QueryBuilderService('core_customers')
                    .select('entity_id')
                    .where('id', customer_id)
                    .first()
                )
                entity_id = customer.get('entity_id') if customer else None

            # 4. Get agent from DB using customer_id and entity_id logic
            agent = (
                QueryBuilderService("core_users")
                .leftJoin('crm_opportunities','crm_opportunities.sales_agent_id','core_users.id')
                .select("display_name","core_users.email as email","contact_no","core_users.id","picture","cover_pic")
                .where("crm_opportunities.customer_id", customer_id)
                .first()
            )
            if not agent and entity_id:
                agent = (
                    QueryBuilderService("core_users")
                    .leftJoin('core_entities','core_entities.created_by_id','core_users.id')
                    .select("display_name","email","contact_no","core_users.id")
                    .where("core_entities.id", entity_id)
                    .first()
                )
            if not agent:
                return ResponseService.response(
                    "NOT_FOUND", None, "Agent not found for the given customer or entity.")

            user_id = agent.get('id')
            print(user_id)
            if not user_id:
                return ResponseService.response(
                    "VALIDATION_ERROR", None, "Agent user_id not found.")

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(1111111111111111, now)

            # 5. Create notification
            notification_data = {
                "customer_id": customer_id,
                "user_id": user_id,
                "type_id": notification_type["id"],
                "title": title,
                "message": message,
                "sent_at": now,
                "metadata": json.dumps(meta_data),
                "created_at": now,
                "updated_at": now,
            }
            print("notification_data",notification_data)
            try:
                notification = QueryBuilderService("core_notifications").insert(notification_data)
                print("Inserted notification:", notification)
            except Exception as insert_exc:
                print("Insert error:", insert_exc)
                raise

            # 6. Create notification-user link (only user_id)
            notification_user_data = {
                "notification_id": notification["id"],
                "user_id": user_id,
                "is_read": False,
                "is_clear": False,
                "read_at": None,
            }
            print("notification_user_data",notification_user_data)
            QueryBuilderService("core_notification_users").insert(notification_user_data)

            return ResponseService.response(
                "SUCCESS", notification, "Notification generated successfully.")
        except Exception as e:
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
        #     )
        # except Exception as notify_exc:
        #     print(f"NotificationService error: {notify_exc}")