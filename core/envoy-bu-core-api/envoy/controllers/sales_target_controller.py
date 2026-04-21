from rest_framework.decorators import api_view
from envoy.models import CoreSalesTarget
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json
from datetime import datetime
from calendar import month_name
from django.db.models import Avg
from django.db import connection

MONTH_ORDER = list(month_name)[1:]  # ['January', ..., 'December']

@api_view(["GET", "POST"])
def sales_target_view(request):
    if request.method == "GET":
        return list_sales_target(request)
    elif request.method == "POST":
        return create_sales_target(request)

def get_sales_targets_by_user_ids(request):
    try:
        ids_param = request.GET.get("ids", "")
        if not ids_param:
            return ResponseService.response("ERROR", [], "No user IDs provided")

        try:
            user_ids = [int(uid) for uid in ids_param.split(",") if uid.strip().isdigit()]
        except ValueError:
            return ResponseService.response("ERROR", [], "Invalid user ID format")

        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "core_sales_targets.user_id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_sorting_columns = [
            "core_sales_targets.user_id", "core_users.display_name",
            "core_sales_targets.month_target_amount", "core_sales_targets.year_target_amount"
        ]

        # Get current month and year
        now = datetime.now()
        current_month = now.strftime("%B_%Y")  # e.g. "June_2025"

        query = (
            QueryBuilderService("core_sales_targets")
            .select(
                "core_sales_targets.user_id",
                "core_users.display_name AS user_display_name",
                "core_sales_targets.month_target_amount",
            )
            .leftJoin("core_users", "core_sales_targets.user_id", "core_users.id")
            .whereIn("core_sales_targets.user_id", user_ids)
            .where("core_sales_targets.month", current_month)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        # Format the result data
        data = [
            {
                "user_id": row["user_id"],
                "user_display_name": row["user_display_name"],
                "month_target_amount": float(row.get("month_target_amount") or 0),
            }
            for row in query.get("data", [])
        ]

        return ResponseService.response("SUCCESS", {
            "data": data,
            "pagination": query.get("pagination", {})
        }, "data_retrieved_successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def list_sales_target(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})
        user_id = request.GET.get("userId", "")
        month = request.GET.get("month", "")
        year = request.GET.get("year", "")

        allowed_filters = [
            "core_sales_targets.month", "core_sales_targets.user_id",
            "core_sales_targets.year", "core_sales_targets.currency",
            "core_sales_targets.created_at"
        ]

        search_columns = ["core_sales_targets.month", "core_users.display_name"]

        sort_by = request.GET.get("sort_by", "core_sales_targets.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_sorting_columns = [
            "core_sales_targets.id", "core_sales_targets.month", "core_sales_targets.year",
            "core_sales_targets.month_target_amount", "core_sales_targets.year_target_amount",
            "core_sales_targets.month_actual_sales_amount", "core_sales_targets.year_actual_sales_amount",
            "core_sales_targets.currency", "core_sales_targets.user_id",
            "core_sales_targets.created_at", "core_sales_targets.updated_at",
            "core_users.display_name"
        ]

        all_columns = allowed_sorting_columns

        query = (
            QueryBuilderService("core_sales_targets")
            .select(*all_columns)
            .leftJoin("core_users", "core_sales_targets.user_id", "core_users.id")
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        )

        if user_id:
            query = query.where("core_sales_targets.user_id", int(user_id))
        if month:
            query = query.where("core_sales_targets.month", str(month))
        if year:
            year = query.where("core_sales_targets.year", str(year))

        query = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

        # Conditionally compute difference based on filter
        for row in query.get("data", []):
                actual_val = row.get("month_actual_sales_amount")
                target_val = row.get("month_target_amount")
                actual = float(actual_val) if actual_val is not None else 0.0
                target = float(target_val) if target_val is not None else 0.0
                row["difference"] = round(actual - target, 2)

        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
# todo
def get_yearly_sales_targets(request):
    try:
        user_id = request.GET.get("userId")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        offset = (page - 1) * limit

        if not user_id:
            return ResponseService.response("VALIDATION_ERROR", {"userId": "userId is required."}, "Validation Error")

        with connection.cursor() as cursor:
            # Total count query (for pagination metadata)
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT year
                    FROM core_sales_targets
                    WHERE user_id = %s
                    GROUP BY year, user_id
                ) AS yearly_data
            """, [user_id])
            total_count = cursor.fetchone()[0]

            # Paged result query
            cursor.execute("""
                SELECT
                    year,
                    user_id,
                    MAX(year_actual_sales_amount) AS year_actual_sales_amount,
                    MAX(year_target_amount) AS year_target_amount,
                    COALESCE(MAX(year_actual_sales_amount), 0) - COALESCE(MAX(year_target_amount), 0) AS difference
                FROM core_sales_targets
                WHERE user_id = %s
                GROUP BY year, user_id
                ORDER BY year ASC
                LIMIT %s OFFSET %s
            """, [user_id, limit, offset])

            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        data = {
            "total_records": total_count,
            "per_page": limit,
            "current_page": page,
            "last_page": (total_count + limit - 1) // limit,  # ceiling division
            "data": results
        }

        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def list_sales_target_by_year(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})
        user_id = request.GET.get("userId", "")

        allowed_filters = [
            "core_sales_targets.month", "core_sales_targets.user_id",
            "core_sales_targets.year", "core_sales_targets.currency",
            "core_sales_targets.created_at"
        ]

        search_columns = ["core_sales_targets.month", "core_users.display_name"]

        sort_by = request.GET.get("sort_by", "core_sales_targets.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_sorting_columns = [
            "core_sales_targets.id", "core_sales_targets.year", "core_sales_targets.year_target_amount",
            "core_sales_targets.month_actual_sales_amount", "core_sales_targets.year_actual_sales_amount",
            "core_sales_targets.currency", "core_sales_targets.user_id",
            "core_sales_targets.created_at", "core_sales_targets.updated_at",
            "core_users.display_name"
        ]

        all_columns = allowed_sorting_columns

        query = (
            QueryBuilderService("core_sales_targets")
            .select(*all_columns)
            .leftJoin("core_users", "core_sales_targets.user_id", "core_users.id")
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        )

        if user_id:
            query = query.where("core_sales_targets.user_id", int(user_id))

        query = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
    
def create_sales_target(request):
    try:
        data = json.loads(request.body)

        rules = {
            "month": "nullable|string|max:20",
            "year": "nullable|integer|min:1900",
            "month_target_amount": "nullable|numeric|min:0",
            "year_target_amount": "nullable|numeric|min:0",
            "month_actual_sales_amount": "nullable|numeric|min:0",
            "year_actual_sales_amount": "nullable|numeric|min:0",
            "currency": "nullable|string|max:5",
            "user_id": "required|integer|exists:core_users,id"
        }

        custom_messages = {
            "month.max": "Month cannot exceed 20 characters.",
            "year.integer": "Year must be a number.",
            "month_target_amount.numeric": "Month target amount must be a number.",
            "year_target_amount.numeric": "Year target amount must be a number.",
            "month_actual_sales_amount.numeric": "Month actual sales amount must be a number.",
            "year_actual_sales_amount.numeric": "Year actual sales amount must be a number.",
            "currency.max": "Currency code cannot exceed 5 characters.",
            "user_id.required": "User is required.",
            "user_id.exists": "Selected user does not exist."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        user_id = data["user_id"]
        year = data.get("year")
        month = data.get("month")

        # Create or update the month-level record
        sales_target, created = CoreSalesTarget.objects.update_or_create(
            user_id=user_id,
            month=month,
            year=year,
            defaults={
                "month_target_amount": data.get("month_target_amount"),
                "month_actual_sales_amount": data.get("month_actual_sales_amount"),
                "year_actual_sales_amount": data.get("year_actual_sales_amount"),
                "currency": data.get("currency")
            }
        )

        # If year_target_amount is provided, update all records for that user and year
        if data.get("year_target_amount") is not None and year is not None:
            CoreSalesTarget.objects.filter(user_id=user_id, year=year).update(
                year_target_amount=data["year_target_amount"]
            )

        message = "Sales target created successfully." if created else "Sales target updated successfully."
        return ResponseService.response("SUCCESS", None, message)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(["GET"])
def list_sales_target_graph(request):
    try:
        user_id = request.GET.get("userId", "")
        year = request.GET.get("year", "")

        if not user_id:
            return ResponseService.response("VALIDATION_ERROR", {"userId": "userId is required."}, "Validation Error")

        if year:
            # Return monthly breakdown for given year
            targets = (
                CoreSalesTarget.objects
                .filter(user_id=user_id, year=year)
                .values("id", "month", "month_target_amount", "month_actual_sales_amount")
            )

            def extract_month_name(month_with_year):
                if "_" in month_with_year:
                    return month_with_year.split("_")[0].capitalize()
                return month_with_year.capitalize()

            def get_month_index(month_name_str):
                try:
                    return MONTH_ORDER.index(month_name_str)
                except ValueError:
                    return -1  # For unrecognized months

            # Sort using extracted month names
            sorted_targets = sorted(
                targets,
                key=lambda x: get_month_index(extract_month_name(x["month"]))
            )

            graph_data = []
            for t in sorted_targets:
                full_month = extract_month_name(t.get("month", ""))
                short_month = full_month[:3] if full_month in MONTH_ORDER else ""

                target = float(t.get("month_target_amount") or 0)
                actual = float(t.get("month_actual_sales_amount") or 0)
                difference = actual - target

                graph_data.append({
                    "id": t["id"],
                    "month": short_month,
                    "target_amount": f"{target:.2f}",
                    "actual_amount": actual,
                    "difference": f"{difference:.2f}"
                })

            return ResponseService.response("SUCCESS", graph_data, "Monthly targets retrieved successfully")

        else:
            # Yearly aggregation
            totals = (
                CoreSalesTarget.objects
                .filter(user_id=user_id)
                .values("year")
                .annotate(
                    total_target_amount=Avg("year_target_amount"),
                    total_actual_amount=Avg("year_actual_sales_amount")
                )
                .order_by("year")
            )

            graph_data = []
            for t in totals:
                target = float(t["total_target_amount"] or 0)
                actual = float(t["total_actual_amount"] or 0)
                graph_data.append({
                    "year": t["year"],
                    "target_amount": f"{target:.2f}",
                    "actual_amount": actual,
                    "difference": f"{(actual - target):.2f}"
                })

            return ResponseService.response("SUCCESS", graph_data, "Yearly totals retrieved successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(["GET", "PUT", "DELETE"])
def sales_target_details(request, id):
    if request.method == "GET":
        return get_sales_target(request, id)
    elif request.method == "PUT":
        return update_sales_target(request, id)
    elif request.method == "DELETE":
        return delete_sales_target(request, id)

def get_sales_target(request, id):
    try:
        sales_target = CoreSalesTarget.objects.select_related('user').get(id=id)

        data = {
            "id": sales_target.id,
            "month": sales_target.month,
            "year": sales_target.year,
            "month_target_amount": float(sales_target.month_target_amount or 0),
            "year_target_amount": float(sales_target.year_target_amount or 0),
            "month_actual_sales_amount": float(sales_target.month_actual_sales_amount or 0),
            "year_actual_sales_amount": float(sales_target.year_actual_sales_amount or 0),
            "currency": sales_target.currency,
            "user_id": sales_target.user.id if sales_target.user else None,
            "user_display_name": sales_target.user.display_name if sales_target.user else None,
            "created_at": sales_target.created_at,
            "updated_at": sales_target.updated_at
        }

        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")

    except CoreSalesTarget.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def update_sales_target(request, id):
    try:
        sales_target = CoreSalesTarget.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "month": "required|string|max:20",
            "year": "required|integer|min:1900",
            "month_target_amount": "nullable|numeric|min:0",
            "year_target_amount": "nullable|numeric|min:0",
            "month_actual_sales_amount": "nullable|numeric|min:0",
            "year_actual_sales_amount": "nullable|numeric|min:0",
            "currency": "nullable|string|max:5",
        }

        custom_messages = {
            "month.required": "Month is required.",
            "month.max": "Month cannot exceed 20 characters.",
            "year.required": "Year is required.",
            "year.integer": "Year must be a number.",
            "currency.max": "Currency code cannot exceed 5 characters."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        sales_target.month = data["month"]
        sales_target.year = data["year"]
        sales_target.month_target_amount = data.get("month_target_amount")
        sales_target.year_target_amount = data.get("year_target_amount")
        sales_target.month_actual_sales_amount = data.get("month_actual_sales_amount")
        sales_target.year_actual_sales_amount = data.get("year_actual_sales_amount")
        sales_target.currency = data.get("currency")

        sales_target.save()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
    except CoreSalesTarget.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def delete_sales_target(request, id):
    try:
        sales_target = CoreSalesTarget.objects.get(id=id)
        sales_target.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except CoreSalesTarget.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(["GET"])
def get_sales_target_by_user_and_month(request):
    try:
        user_id = request.GET.get("userId")
        month_str = request.GET.get("month")  # Example: "June_2025"

        if not user_id or not month_str:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "userId and month are required"},
                "Validation Error"
            )

        sales_target = CoreSalesTarget.objects.filter(
            user_id=user_id,
            month=month_str
        ).first()

        if not sales_target:
            data = {
                "id": None,
                "month": month_str,
                "year": None,
                "month_target_amount": None,
                "year_target_amount": None,
                "month_actual_sales_amount": None,
                "year_actual_sales_amount": None,
                "month_difference": None,
                "year_difference": None,
                "currency": None,
                "user_id": int(user_id) if user_id.isdigit() else None
            }
            return ResponseService.response("NOT_FOUND", data, "data_not_found")

        # Calculate differences
        month_diff = None
        if sales_target.month_actual_sales_amount is not None and sales_target.month_target_amount is not None:
            month_diff = sales_target.month_actual_sales_amount - sales_target.month_target_amount

        year_diff = None
        if sales_target.year_actual_sales_amount is not None and sales_target.year_target_amount is not None:
            year_diff = sales_target.year_actual_sales_amount - sales_target.year_target_amount

        data = {
            "id": sales_target.id,
            "month": sales_target.month,
            "year": sales_target.year,
            "month_target_amount": sales_target.month_target_amount,
            "year_target_amount": sales_target.year_target_amount,
            "month_actual_sales_amount": sales_target.month_actual_sales_amount,
            "year_actual_sales_amount": sales_target.year_actual_sales_amount,
            "month_difference": month_diff,
            "year_difference": year_diff,
            "currency": sales_target.currency,
            "user_id": sales_target.user_id
        }

        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
