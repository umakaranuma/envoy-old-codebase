# your_app/management/commands/seed_core_form_elements.py
from django.core.management.base import BaseCommand

from envoy.models.form_elements import CoreFormElement


class Command(BaseCommand):
    help = "Seed core_form_elements with default elements"

    def handle(self, *args, **options):
        self.stdout.write("Seeding core_form_elements...")

        elements = [
            (1, "Short Answer", "Frequently Used", "input_individual", "SORT_ANSWER", None, None),
            (2, "Multiple Choice", "Frequently Used", "input_individual", "MULTI_CHOICE", None, None),
            (3, "Email Input", "Frequently Used", "input_individual", "EMAIL_INPUT", None, None),
            (4, "Heading", "Display Text", "display", "HEADING", None, None),
            (5, "Paragraph", "Display Text", "display", "PARAGRAPH", None, None),
            (6, "Banner", "Display Text", "display", "BANNER", None, None),
            (7, "Dropdown", "Choices", "input_individual", "DROPDOWN", None, None),
            (8, "Picture Choice", "Choices", "input_individual", "PICTURE_CHOICE", None, None),
            (9, "Multiple Select", "Choices", "input_individual", "MULTI_SELECT", None, None),
            (10, "Switch", "Choices", "input_individual", "SWITCH", None, None),
            (11, "Check Box", "Choices", "input_individual", "MULTI_CHOICE", None, None),
            (12, "Radio Box", "Choices", "input_individual", "RADIO_BOX", None, None),
            (13, "Date Picker", "Date & Time", "input_individual", "DATE_PICKER", None, None),
            (14, "Time Picker", "Date & Time", "input_individual", "TIME_PICKER", None, None),
            (15, "Date & Time", "Date & Time", "input_individual", "DATE_TIME", None, None),
            (16, "Date Range", "Date & Time", "input_group", "DATE_RANGE", None, None),
            (17, "From", "Date & Time", "input_individual", "DATE_RANGE_FROM_DATE", 16, 1),
            (18, "To", "Date & Time", "input_individual", "DATE_RANGE_TO_DATE", 16, 2),
            (19, "Ranking", "Rating & Ranking", "input_individual", "RANKING", None, None),
            (20, "Star Rating", "Rating & Ranking", "input_individual", "STAR_RATING", None, None),
            (21, "Slider", "Rating & Ranking", "input_individual", "SLIDER", None, None),
            (22, "Option Scale", "Rating & Ranking", "input_individual", "OPTION_SCALE", None, None),
            (23, "Short Answer", "Text", "input_individual", "SORT_ANSWER", None, None),
            (24, "Long Answer", "Text", "input_individual", "LONG_ANSWER", None, None),
            (25, "Phone", "Contact Info", "input_individual", "PHONE_INPUT", None, None),
            (26, "Email", "Contact Info", "input_individual", "EMAIL_INPUT", None, None),
            (27, "Address", "Contact Info", "input_individual", "ADDRESS", None, None),
            (28, "Numbers", "Numbers", "input_individual", "NUMBERS", None, None),
            (29, "Currency", "Numbers", "input_individual", "CURRENCY", None, None),
            (30, "URL Input", "Miscellaneous", "input_individual", "URL_INPUT", None, None),
            (31, "Color Picker", "Miscellaneous", "input_individual", "COLOR_PICKER", None, None),
            (32, "Password", "Miscellaneous", "input_individual", "PASSWORD", None, None),
            (33, "File Upload", "Miscellaneous", "input_individual", "FILE_UPLOAD", None, None),
            (34, "Signature", "Miscellaneous", "input_individual", "SIGNATURE", None, None),
            (35, "Voice Recording", "Miscellaneous", "input_individual", "VOICE_RECORDING", None, None),
            (36, "Submission Picker", "Miscellaneous", "input_individual", "SUBMISSION_PICKER", None, None),
            (37, "Location Coordinate", "Miscellaneous", "input_group", "LOCATION", None, None),
            (38, "Latitude", "Miscellaneous", "input_individual", "LOCATION_LATITUDE", 37, 1),
            (39, "Longitude", "Miscellaneous", "input_individual", "LOCATION_LONGITUDE", 37, 2),
            (40, "Captcha", "Miscellaneous", "input_individual", "CAPTCHA", None, None),
            (41, "Subform", "Miscellaneous", "input_individual", "SUBFORM", None, None),
            (42, "Section Collapse", "Navigation & Layout", "display", "SECTION_COLLAPSE", None, None),
            (43, "Divider", "Navigation & Layout", "display", "DIVIDER", None, None),
            (44, "Panel", "Navigation & Layout", "display", "PANEL", None, None),
            (45, "HTML", "Navigation & Layout", "display", "HTML", None, None),
            (46, "Image", "Media", "display", "IMAGE_VIEWER", None, None),
            (47, "Video", "Media", "display", "VIDEO_VIEWER", None, None),
            (48, "PDF Viewer", "Media", "display", "PDF_VIEWER", None, None),
            (49, "Line Break", "Display Text", "display", "LINE_BREAK", None, None),
        ]

        for item in elements:
            id_, title, grp, cat, code, group_id, order_num = item
            CoreFormElement.objects.update_or_create(
                id=id_,
                defaults={
                    "title": title,
                    "element_group": grp,
                    "category": cat,
                    "code": code,
                    "group_id": group_id,
                    "group_element_order_number": order_num,
                }
            )

        self.stdout.write(self.style.SUCCESS("core_form_elements seeded successfully."))
