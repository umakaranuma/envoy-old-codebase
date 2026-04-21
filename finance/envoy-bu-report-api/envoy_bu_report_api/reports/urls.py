from django.urls import path
from .controllers.report_controller import ReportController
from .controllers.report_type_controller import ReportTypeController
from .controllers.report_chart_controller import ReportChartController
from .controllers.report_dashboard_controller import ReportDashboardController
from .controllers.dashboard_tile_controller import DashboardTileController

urlpatterns = [
    # Report Types
    path('report-types', ReportTypeController.report_type_access, name='report_types_report_type_access'),
    path('report-types/<int:id>', ReportTypeController.report_type_one, name='report_types_report_type_one'),

    # Reports
    path('reports', ReportController.report_access, name='reports_report_access'),
    path('reports/<int:report_id>', ReportController.report_one, name='reports_report_one'),
    path('generate-query', ReportController.query_generate, name='reports_generate_query'),
    path('report-data/<int:report_id>', ReportController.get_query_data, name='reports_get_data'),
    path('export/report-to-excel', ReportController.export_report_to_excel, name='reports_export_to_excel'),
    
    # Report Charts
    path('report-charts', ReportChartController.report_chart_access, name='report_charts_report_chart_access'),
    path('report-charts/<int:id>', ReportChartController.report_chart_one, name='report_charts_report_chart_one'),
    path('report-charts/report/<int:report_id>', ReportChartController.get_by_report, name='report_charts_by_report'),
    path('report-chart-data/<int:id>', ReportChartController.get_chart_data, name='report_charts_get_data'),
    path('report-chart-data/report/<int:report_id>', ReportChartController.get_chart_data_by_report, name='report_charts_get_data_by_report'),
    
    # Dashboards
    path('dashboards', ReportDashboardController.report_dashboard_access, name='dashboards_report_dashboard_access'),
    path('dashboards/<int:id>', ReportDashboardController.report_dashboard_one, name='dashboards_report_dashboard_one'),
    
    # # Dashboard Tiles
    path('dashboard-tiles', DashboardTileController.dashboard_tile_access, name='dashboard_tiles_dashboard_tile_access'),
    path('dashboard-tiles/<int:id>', DashboardTileController.dashboard_tile_one, name='dashboard_tiles_dashboard_tile_one'),
    path('dashboard-tiles/dashboard/<int:dashboard_id>', DashboardTileController.get_by_dashboard, name='dashboard_tiles_by_dashboard'),
    path('report/html_to_doc_export', DashboardTileController.html_export, name='html_export'),
    path('report/doc-export', DashboardTileController.html_to_doc_export, name='html_to_doc_export'),
    
    # JSON to Excel export endpoint
    path('export/json-to-excel', DashboardTileController.json_to_excel_export, name='json_to_excel_export'),
]