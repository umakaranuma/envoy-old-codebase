"""
Renew Gmail push watch for all configured credentials.
Run every 6 days (e.g. via cron) since watch expires after 7 days.

Set GMAIL_WATCH_TOPIC in env, e.g.:
  GMAIL_WATCH_TOPIC=projects/YOUR_PROJECT_ID/topics/gmail-notifications

Topic must be in the SAME Google Cloud project where your OAuth client and Gmail API are enabled.
"""
import os
import logging
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from envoy.models.mail_model import GmailCredential
from envoy.services.email_service import ensure_fresh_token, enable_gmail_watch

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enable or renew Gmail push watch for Pub/Sub. Run every 6 days (watch expires after 7 days)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default=None,
            help="Renew watch only for this system_email. If omitted, renew for all credentials.",
        )

    def handle(self, *args, **options):
        topic_name = (
            getattr(settings, "GMAIL_WATCH_TOPIC", None)
            or os.getenv("GMAIL_WATCH_TOPIC")
        )
        if not topic_name:
            self.stderr.write(
                "Set GMAIL_WATCH_TOPIC (e.g. projects/YOUR_PROJECT_ID/topics/gmail-notifications) in settings or env."
            )
            return

        qs = GmailCredential.objects.all()
        if options.get("email"):
            qs = qs.filter(system_email=options["email"])
        if not qs.exists():
            self.stderr.write("No Gmail credentials found.")
            return

        for cred in qs:
            try:
                cred = ensure_fresh_token(cred)
                result = enable_gmail_watch(cred, topic_name)
                # Store the returned historyId as the starting point for future push processing
                history_id = result.get("historyId")
                if history_id:
                    cred.last_history_id = str(history_id)
                    cred.save(update_fields=["last_history_id"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Watch renewed for {cred.system_email}: historyId={result.get('historyId')}, expiration={result.get('expiration')}"
                    )
                )
            except RuntimeError as e:
                err_text = str(e)
                if "invalid_grant" in err_text.lower() or "Bad Request" in err_text:
                    self.stderr.write(
                        self.style.WARNING(
                            f"{cred.system_email}: Refresh token invalid or revoked. "
                            "Re-connect this Gmail account in the app (sign in with Google again for Gmail) to get a new refresh token, then run this command again."
                        )
                    )
                else:
                    self.stderr.write(self.style.ERROR(f"{cred.system_email}: {e}"))
                logger.warning("renew_gmail_watch failed for %s: %s", cred.system_email, err_text)
            except requests.HTTPError as e:
                body = getattr(getattr(e, "response", None), "text", None) or str(e)
                self.stderr.write(
                    self.style.ERROR(
                        f"{cred.system_email}: Gmail watch API error. Response: {body}"
                    )
                )
                self.stderr.write(
                    self.style.WARNING(
                        "Ensure: (1) Topic is in the SAME project as your OAuth client / Gmail API, "
                        "(2) gmail-api-push@system.gserviceaccount.com has Pub/Sub Publisher on the topic."
                    )
                )
                logger.warning("renew_gmail_watch HTTPError for %s: %s", cred.system_email, body)
            except Exception as e:
                logger.exception("Failed to renew watch for %s", cred.system_email)
                self.stderr.write(self.style.ERROR(f"{cred.system_email}: {e}"))
