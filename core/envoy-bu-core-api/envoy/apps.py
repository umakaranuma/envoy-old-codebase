# from django.apps import AppConfig
# from django.db.models.signals import class_prepared

# class EnvoyConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "envoy"

#     def ready(self):
#         """Set table names dynamically with 'core_' prefix, excluding built-in Django models."""
#         from django.apps import apps

#         def set_table_name(sender, **kwargs):
#             """Modify table names to include 'core_' prefix."""
#             if sender._meta.app_label in ["admin", "auth", "contenttypes", "sessions"]:
#                 return  # Skip Django's built-in models

#             sender._meta.db_table = f"core_{sender.__name__.lower()}"  # Prefix all tables with "core_"

#         # Apply renaming to all currently loaded models
#         for model in apps.get_models():
#             set_table_name(model)

#         # Ensure models loaded later also get renamed
#         class_prepared.connect(set_table_name)
