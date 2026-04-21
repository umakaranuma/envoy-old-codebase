# app/controllers/gmail_controller.py
import json
import os
from django.http import HttpResponse
from pydantic import ValidationError, validate_email
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.conf import settings
from envoy.controllers.approval_controller import get_bearer_token
from envoy.services import email_service as svc
from envoy.models.mail_model import GmailCredential, EmailMessage
import logging
import base64
from django.utils import timezone
from django.db import models
from django.core import signing
import time
from urllib.parse import urlencode
from django.utils.html import escape
import requests
from mServices.QueryBuilderService import QueryBuilderService


logger = logging.getLogger(__name__)

SCOPE_DESCRIPTIONS = {
    "openid": "Sign in with your Google account",
    "email": "View your email address",
    "https://www.googleapis.com/auth/userinfo.email": "See your primary Google account email",
    "https://www.googleapis.com/auth/gmail.readonly": "Read your Gmail messages and labels",
    "https://www.googleapis.com/auth/gmail.send": "Send email as you",
    "https://www.googleapis.com/auth/gmail.compose": "Create and manage drafts",
    "https://www.googleapis.com/auth/gmail.modify": "Read mail and modify labels",
}

# ---------- helpers ----------
def _mask(v: str) -> str:
    if not v:
        return ""
    if len(v) <= 8:
        return v[:2] + "…"
    return v[:4] + "…" + v[-4:]

def _get_conf(name: str, default=None):
    # Try Django settings, fallback to environment
    if hasattr(settings, name):
        val = getattr(settings, name)
        if val is not None:
            return val
    return os.environ.get(name, default)

def _parse_scopes(val):
    """
    Accepts:
      - list/tuple: returned as list
      - JSON array string: '["email","openid", ...]'
      - space/comma separated string (optionally quoted): 'email openid ...'
    Returns a list[str].
    """
    if isinstance(val, (list, tuple)):
        return list(val)
    if not isinstance(val, str):
        return []
    s = val.strip()
    # strip surrounding quotes if present
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    # JSON array?
    if s.startswith('[') and s.endswith(']'):
        try:
            arr = json.loads(s)
            return [str(x) for x in arr]
        except Exception:
            pass
    # split by whitespace or commas
    parts = []
    for chunk in s.replace(',', ' ').split():
        if chunk:
            parts.append(chunk)
    return parts

# ---------- START: auth_google_start ----------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def auth_google_start(request, mail_address: str):
    """
    Start Google OAuth flow for *this* mail_address.
    Generates Google OAuth URL with full debug visibility.
    """
    try:
        print("\n================ GOOGLE OAUTH START ================\n")

        # ---- Load config ----
        client_id = _get_conf("GOOGLE_CLIENT_ID")
        client_secret = _get_conf("GOOGLE_CLIENT_SECRET")
        redirect_uri = _get_conf("GOOGLE_REDIRECT_URI")
        scopes_raw = _get_conf("GOOGLE_SCOPES")

        print("[CONFIG]")
        print("CLIENT_ID present:", bool(client_id))
        print("CLIENT_SECRET present:", bool(client_secret))
        print("REDIRECT_URI:", redirect_uri)
        print("RAW_SCOPES:", repr(scopes_raw))

        # ---- Parse & normalize scopes ----
        scopes = _parse_scopes(scopes_raw) if scopes_raw else []
        scopes = list(dict.fromkeys(s.strip() for s in scopes if s.strip()))  # dedupe + clean

        if not scopes:
            scopes = [
                "openid",
                "email",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.modify",
            ]

        print("\n[SCOPES]")
        print("COUNT:", len(scopes))
        for s in scopes:
            print(" -", s)

        # ---- Config validation ----
        missing = []
        if not client_id:
            missing.append("GOOGLE_CLIENT_ID")
        if not client_secret:
            missing.append("GOOGLE_CLIENT_SECRET")
        if not redirect_uri:
            missing.append("GOOGLE_REDIRECT_URI")

        if missing:
            print("\n[ERROR] Missing OAuth config:", missing)
            return Response(
                {
                    "error": "GOOGLE_OAUTH_CONFIG_MISSING",
                    "missing": missing,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ---- Validate email ----
        try:
            validate_email(mail_address)
        except ValidationError:
            print("\n[ERROR] Invalid email provided:", mail_address)
            return Response(
                {"error": "INVALID_EMAIL"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print("\n[ACCOUNT TARGETING]")
        print("Login hint:", mail_address)
        print("Request user id:", request.user.id)

        # ---- Build signed state ----
        state_payload = {
            "uid": request.user.id,
            "email": mail_address,
            "ts": int(time.time()),
        }
        state = signing.dumps(state_payload, salt="google-oauth-state")

        print("\n[STATE]")
        print("State payload:", state_payload)
        print("Signed state length:", len(state))

        # ---- Build OAuth URL ----
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",      # REQUIRED for refresh_token
            "prompt": "consent",           # REQUIRED to force refresh_token
            "include_granted_scopes": "true",
            "state": state,
            "login_hint": mail_address,
        }

        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

        print("\n[OAUTH URL GENERATED]")
        print(auth_url)

        print("\n[IMPORTANT WARNINGS]")
        print("✔ Ensure callback stores token_data['access_token'], NOT id_token")
        print("✔ Ensure refresh_token is saved on FIRST consent")
        print("✔ Access tokens expire in ~1 hour")

        print("\n================ END GOOGLE OAUTH START ================\n")

        return Response(
            {
                "message": "Google OAuth authorization URL generated",
                "auth_url": auth_url,
                "state": state,
                "redirect_uri": redirect_uri,
                "scopes": scopes,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception("auth_google_start failed")
        return Response(
            {
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ---------- START: auth_google_callback ----------
@api_view(["GET"])
def auth_google_callback(request):
    """
    Handle Google OAuth callback (public endpoint).
    - Validates signed 'state' (uid + email)
    - Exchanges code for tokens
    - Enforces that the approved Google account matches the intended email
    - Saves/updates credentials
    - Returns a tiny success HTML that auto-closes
    """
    print("🔥 CALLBACK FUNCTION CALLED 🔥")
    print("🔥 CALLBACK FUNCTION CALLED 🔥")
    print("🔥 CALLBACK FUNCTION CALLED 🔥")
    try:
        print("=== OAUTH CALLBACK STARTED ===")
        print(f"Request URL: {request.get_full_path()}")
        print(f"Request params: {dict(request.query_params)}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")

        print(f"Code: {'PRESENT' if code else 'MISSING'}")
        print(f"State: {'PRESENT' if state else 'MISSING'}")
        print(f"Error: {error or 'NONE'}")
        
        if code:
            print(f"Code value: {code[:20]}...")
        if state:
            print(f"State value: {state[:50]}...")

        logger.info(
            "OAuth callback received - code: %s, state: %s, error: %s",
            "present" if code else "missing",
            "present" if state else "missing",
            error or "none",
        )

        if error:
            error_description = request.query_params.get("error_description", "Unknown error")
            logger.error("Google OAuth error: %s - %s", error, error_description)
            return Response(
                {
                    "error": "Google OAuth authorization failed",
                    "message": f"Authorization was denied: {error_description}",
                    "error_code": "GOOGLE_OAUTH_DENIED",
                    "google_error": error,
                    "google_error_description": error_description,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not code:
            print("=== MISSING AUTHORIZATION CODE ===")
            logger.error("Missing authorization code in callback")
            
            # Return debug HTML instead of JSON error
            debug_html = f"""<!doctype html>
<html>
<head><title>OAuth Debug</title></head>
<body>
    <h2>❌ OAuth Callback Debug</h2>
    <p><strong>Status:</strong> Missing authorization code</p>
    <p><strong>Request URL:</strong> {request.get_full_path()}</p>
    <p><strong>Request Params:</strong> {dict(request.query_params)}</p>
    <p><strong>Request Method:</strong> {request.method}</p>
    <p><strong>Headers:</strong> {dict(request.headers)}</p>
    <p>This means the OAuth flow did not complete properly or the redirect URI is incorrect.</p>
</body>
</html>"""
            return HttpResponse(debug_html, content_type="text/html")
        if not state:
            logger.error("Missing state parameter in callback")
            return Response(
                {
                    "error": "Missing state parameter",
                    "message": "State parameter is required for security",
                    "error_code": "MISSING_STATE_PARAMETER",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            print("=== VALIDATING STATE ===")
            print(f"State value: {state}")
            st = signing.loads(state, salt="google-oauth-state", max_age=600)  # 10 minutes
            print(f"State payload: {st}")
            user_id = st.get("uid")
            intended_email = st.get("email")
            print(f"User ID: {user_id}")
            print(f"Intended email: {intended_email}")
        except signing.BadSignature:
            print("=== STATE VALIDATION FAILED - Bad Signature ===")
            logger.error("Invalid or expired state signature")
            return Response(
                {
                    "error": "Invalid state parameter",
                    "message": "State parameter is invalid or expired",
                    "error_code": "INVALID_STATE_PARAMETER",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = st.get("uid")
        intended_email = st.get("email")
        if not user_id or not intended_email:
            logger.error("State payload missing required fields: %s", st)
            return Response(
                {
                    "error": "Invalid state parameter",
                    "message": "State payload is missing required fields",
                    "error_code": "INVALID_STATE_PARAMETER",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resolve the user
        print("=== RESOLVING USER ===")
        print(f"Looking for user ID: {user_id}")
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
            print(f"User found: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            print(f"=== USER NOT FOUND ===")
            print(f"User with ID {user_id} does not exist")
            logger.error("User with ID %s does not exist", user_id)
            return Response(
                {
                    "error": "User not found",
                    "message": "User with the provided ID does not exist",
                    "error_code": "USER_NOT_FOUND",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- Token exchange (ensure svc uses same redirect_uri) ---
        # svc should read GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI via settings or env,
        # just like start() does. If not, pass redirect explicitly.
        try:
            print("=== TOKEN EXCHANGE ===")
            print(f"Exchanging code: {code[:20]}...")
            logger.info("Starting token exchange")
            token_res = svc.exchange_code_for_tokens(code)  # pass redirect if your svc needs it
            print(f"Token response keys: {list(token_res.keys())}")
            print(f"Access token present: {'access_token' in token_res}")
            print(f"Refresh token present: {'refresh_token' in token_res}")
            logger.info("Token exchange successful")
        except Exception as e:
            print(f"=== TOKEN EXCHANGE FAILED ===")
            print(f"Error: {str(e)}")
            logger.error("Token exchange failed: %s", str(e))
            return Response(
                {
                    "error": "TOKEN_EXCHANGE_FAILED",
                    "message": "Failed to exchange authorization code for access token",
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_res.get("access_token")
        if not access_token:
            logger.error("Token response missing access_token: %s", token_res)
            return Response(
                {
                    "error": "INVALID_TOKEN_RESPONSE",
                    "message": "Google did not return a valid access token",
                    "token_response": token_res,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch user info and enforce intended email
        try:
            print("=== FETCHING USER INFO ===")
            logger.info("Fetching user info from Google")
            userinfo = svc.fetch_userinfo(access_token)
            print(f"User info: {userinfo}")
            email = userinfo.get("email")
            print(f"Email from Google: {email}")
            print(f"Intended email: {intended_email}")
            if not email:
                print("=== EMAIL NOT FOUND IN USERINFO ===")
                logger.error("Userinfo missing email: %s", userinfo)
                return Response(
                    {
                        "error": "EMAIL_NOT_FOUND",
                        "message": "Could not retrieve email from Google user info",
                        "userinfo": userinfo,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email.lower() != intended_email.lower():
                print("=== EMAIL MISMATCH ===")
                print(f"Intended: {intended_email}")
                print(f"Actual: {email}")
                logger.error("Email mismatch: intended=%s, actual=%s", intended_email, email)
                return Response(
                    {
                        "error": "EMAIL_MISMATCH",
                        "message": f"Please sign in as {intended_email}. You signed in as {email}.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            print("=== EMAIL VALIDATION PASSED ===")
            logger.info("User info retrieved and email enforced for: %s", email)

            # Save / update credentials
            try:
                print("=== SAVING CREDENTIALS ===")
                print(f"Email: {email}")
                print(f"User ID: {user.id}")
                print(f"Token response: {token_res}")
                cred = svc.upsert_credential(email, token_res, user)
                print(f"=== CREDENTIALS SAVED SUCCESSFULLY ===")
                print(f"Credential object: {cred}")
                print(f"Credential type: {type(cred)}")
                if cred:
                    print(f"Credential ID: {cred.id}")
                    print(f"System email: {cred.system_email}")
                    print(f"User: {cred.user}")
                else:
                    print("=== CREDENTIAL IS NONE ===")
                    print("The upsert_credential function returned None!")
                logger.info("Gmail credentials saved for email: %s, user_id: %s", email, user.id)
            except Exception as e:
                print(f"=== CREDENTIAL SAVE FAILED ===")
                print(f"Error: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                logger.error("Failed to save credentials: %s", str(e))
                
                # Return debug HTML instead of JSON error
                error_html = f"""<!doctype html>
<html>
<head><title>Credential Save Error</title></head>
<body>
    <h2>❌ Credential Save Error</h2>
    <p><strong>Error:</strong> {str(e)}</p>
    <p><strong>Error Type:</strong> {type(e)}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>User ID:</strong> {user.id}</p>
    <p><strong>Full Traceback:</strong></p>
    <pre style="background: #f3f4f6; padding: 10px; border-radius: 4px; overflow-x: auto;">{traceback.format_exc()}</pre>
    <p>Check the server console for more details.</p>
</body>
</html>"""
                return HttpResponse(error_html, content_type="text/html")

            # Success HTML
            print("=== GENERATING SUCCESS HTML ===")
            print(f"Credential object: {cred}")
            if cred:
                print(f"Credential ID: {cred.id}")
                print(f"Credential email: {cred.system_email}")
                email_safe = escape(cred.system_email or "")
            else:
                print("=== CREDENTIAL IS NONE - CANNOT GENERATE SUCCESS HTML ===")
                email_safe = escape(email or "")
            
            # Check database count
            from envoy.models.mail_model import GmailCredential
            try:
                total_creds = GmailCredential.objects.count()
                print(f"=== DATABASE CHECK ===")
                print(f"Total credentials in database: {total_creds}")
                print(f"Current credential ID: {cred.id}")
            except Exception as e:
                print(f"=== DATABASE CHECK FAILED ===")
                print(f"Error accessing database: {str(e)}")
                import traceback
                print(f"Database error traceback: {traceback.format_exc()}")
                total_creds = 0
            
            # Add a simple test to verify the credential exists
            try:
                test_cred = GmailCredential.objects.get(id=cred.id)
                print(f"=== CREDENTIAL VERIFICATION ===")
                print(f"Found credential: {test_cred.system_email}")
                print(f"User: {test_cred.user.username}")
            except Exception as e:
                print(f"=== CREDENTIAL VERIFICATION FAILED ===")
                print(f"Error: {str(e)}")
            
            # Retrieved credentials information
            if cred:
                retrieved_creds = f"""
                <div style="background: #e0f2fe; padding: 16px; margin: 16px 0; border-radius: 8px; border-left: 4px solid #0284c7;">
                    <h3 style="color: #0284c7; margin-top: 0;">🔑 Retrieved Credentials (Full Access - Unmasked):</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-family: monospace; font-size: 13px;">
                        <div>
                            <p><strong>Email:</strong> {cred.system_email}</p>
                            <p><strong>User:</strong> {cred.user.username} (ID: {cred.user.id})</p>
                            <p><strong>Credential ID:</strong> {cred.id}</p>
                            <p><strong>Token Expiry:</strong> {cred.token_expiry}</p>
                            <p><strong>Token URI:</strong> {cred.token_uri}</p>
                        </div>
                        <div>
                            <p><strong>Client ID:</strong></p>
                            <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto;">{cred.client_id}</pre>
                        </div>
                    </div>
                    <div style="margin-top: 16px;">
                        <p><strong>Access Token (Full):</strong></p>
                        <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.access_token}</pre>
                    </div>
                    <div style="margin-top: 16px;">
                        <p><strong>Refresh Token (Full):</strong></p>
                        <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.refresh_token or 'None'}</pre>
                    </div>
                    <div style="margin-top: 16px;">
                        <p><strong>Client Secret (Full):</strong></p>
                        <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.client_secret}</pre>
                    </div>
                </div>
                """
            else:
                retrieved_creds = f"""
                <div style="background: #fef2f2; padding: 16px; margin: 16px 0; border-radius: 8px; border-left: 4px solid #ef4444;">
                    <h3 style="color: #ef4444; margin-top: 0;">❌ Credential Save Failed:</h3>
                    <p><strong>Error:</strong> The upsert_credential function returned None</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>User ID:</strong> {user.id}</p>
                    <p>Check the server console for more details.</p>
                </div>
                """
            
            # Add a simple test message
            if cred:
                test_message = f"""
                <div style="background: #fef3c7; padding: 16px; margin: 16px 0; border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <h3 style="color: #f59e0b; margin-top: 0;">🧪 Test Information:</h3>
                    <p><strong>Callback Reached:</strong> ✅ YES</p>
                    <p><strong>Credential Created:</strong> ✅ YES</p>
                    <p><strong>Database Count:</strong> {total_creds}</p>
                    <p><strong>Credential ID:</strong> {cred.id}</p>
                    <p><strong>Email:</strong> {cred.system_email}</p>
                    <p><strong>User:</strong> {cred.user.username}</p>
                    <p><strong>Access Token (Full):</strong></p>
                    <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 11px;">{cred.access_token}</pre>
                    <p><strong>Refresh Token (Full):</strong></p>
                    <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 11px;">{cred.refresh_token or 'None'}</pre>
                </div>
                """
            else:
                test_message = f"""
                <div style="background: #fef2f2; padding: 16px; margin: 16px 0; border-radius: 8px; border-left: 4px solid #ef4444;">
                    <h3 style="color: #ef4444; margin-top: 0;">🧪 Test Information:</h3>
                    <p><strong>Callback Reached:</strong> ✅ YES</p>
                    <p><strong>Credential Created:</strong> ❌ NO (Returned None)</p>
                    <p><strong>Database Count:</strong> {total_creds}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>User ID:</strong> {user.id}</p>
                    <p><strong>Error:</strong> upsert_credential function returned None</p>
                </div>
                """
            
            # Debug information
            debug_info = f"""
            <div style="background: #f3f4f6; padding: 16px; margin: 16px 0; border-radius: 8px; font-family: monospace; font-size: 12px;">
                <h3>🔍 Debug Information (Full Credentials - Unmasked):</h3>
                <p><strong>Total Credentials in DB:</strong> {total_creds}</p>
                <p><strong>Credential ID:</strong> {cred.id}</p>
                <p><strong>System Email:</strong> {cred.system_email}</p>
                <p><strong>User ID:</strong> {cred.user.id}</p>
                <p><strong>User Name:</strong> {cred.user.username}</p>
                <p><strong>Token Expiry:</strong> {cred.token_expiry}</p>
                <p><strong>Token URI:</strong> {cred.token_uri}</p>
                <p><strong>Client ID (Full):</strong></p>
                <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 11px;">{cred.client_id}</pre>
                <p><strong>Client Secret (Full):</strong></p>
                <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 11px;">{cred.client_secret}</pre>
                <p><strong>Access Token (Full):</strong></p>
                <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.access_token}</pre>
                <p><strong>Refresh Token (Full):</strong></p>
                <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.refresh_token or 'None'}</pre>
            </div>
            """
            
            html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Connected</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 40px; }}
    .card {{ max-width: 800px; margin: 0 auto; padding: 24px; border: 1px solid #e5e7eb; border-radius: 12px; }}
    h2 {{ margin: 0 0 8px; }}
    .muted {{ color: #6b7280; margin-top: 4px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>✅ Gmail connected</h2>
    <div class="muted">Account: {email_safe}</div>
    <p>You can close this window.</p>
    {test_message}
    {retrieved_creds}
    {debug_info}
  </div>
  <script>
    (function () {{
      try {{
        window.opener && window.opener.postMessage(
          {{
            type: "GOOGLE_OAUTH_SUCCESS",
            email: "{email_safe}",
            userId: {user.id}
          }},
          "*"
        );
      }} catch (e) {{}}
      window.close();
    }})();
  </script>
</body>
</html>"""
            return HttpResponse(html, content_type="text/html", status=200)

        except Exception as e:
            logger.error("Userinfo or credential save failed: %s", str(e))
            return Response(
                {
                    "error": "USERINFO_OR_SAVE_FAILED",
                    "message": "Failed to retrieve user info or save credentials",
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        print(f"🔥 CALLBACK ERROR: {str(e)}")
        print(f"🔥 CALLBACK ERROR TYPE: {type(e)}")
        import traceback
        print(f"🔥 TRACEBACK: {traceback.format_exc()}")
        
        logger.error("Unexpected error in auth_google_callback: %s", str(e), exc_info=True)
        
        # Return debug HTML instead of JSON error
        error_html = f"""<!doctype html>
<html>
<head><title>OAuth Error</title></head>
<body>
    <h2>❌ OAuth Callback Error</h2>
    <p><strong>Error:</strong> {str(e)}</p>
    <p><strong>Error Type:</strong> {type(e)}</p>
    <p><strong>Request URL:</strong> {request.get_full_path()}</p>
    <p><strong>Request Params:</strong> {dict(request.query_params)}</p>
    <p><strong>Full Traceback:</strong></p>
    <pre style="background: #f3f4f6; padding: 10px; border-radius: 4px; overflow-x: auto;">{traceback.format_exc()}</pre>
    <p>Check the server console for more details.</p>
</body>
</html>"""
        return HttpResponse(error_html, content_type="text/html")

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def gmail_status(request):
    """
    Check Gmail integration status for a user.
    """
    try:
        email = request.query_params.get("email")
        user_id = request.user.id if hasattr(request.user, 'id') else None
        
        if not email:
            return Response(
                {
                    "error": "Email parameter required",
                    "message": "Email parameter is required to check Gmail status",
                    "error_code": "MISSING_EMAIL_PARAMETER"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter by both email and user for security
        if user_id:
            exists = GmailCredential.objects.filter(system_email=email, user_id=user_id).exists()
        else:
            exists = GmailCredential.objects.filter(system_email=email).exists()
        
        return Response(
            {
                "connected": exists,
                "email": email,
                "message": "Gmail status checked successfully"
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in gmail_status: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while checking Gmail status",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def gmail_messages(request):
    """
    Retrieve Gmail messages for a connected account.
    """
    try:
        email = request.query_params.get("email")
        if not email:
            return Response(
                {
                    "error": "Email parameter required",
                    "message": "Email parameter is required to retrieve Gmail messages",
                    "error_code": "MISSING_EMAIL_PARAMETER"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cred = GmailCredential.objects.get(system_email=email)
        except GmailCredential.DoesNotExist:
            return Response(
                {
                    "error": "Gmail not connected",
                    "message": "Gmail account is not connected. Please connect your Gmail account first.",
                    "error_code": "GMAIL_NOT_CONNECTED",
                    "connected": False,
                    "action": "connect_first"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get query parameters with defaults
        q = request.query_params.get("q", "")
        label = request.query_params.get("label", "INBOX")
        
        try:
            max_results = int(request.query_params.get("max", 10))
            if max_results <= 0 or max_results > 100:
                max_results = 10
        except ValueError:
            max_results = 10
        
        try:
            data = svc.list_messages(cred, q=q, label=label, max_results=max_results)
            logger.info(f"Gmail messages retrieved for {email}: {len(data.get('messages', []))} messages")
            
            return Response(
                {
                    "message": "Gmail messages retrieved successfully",
                    "email": email,
                    "connected": True,
                    "query": q,
                    "label": label,
                    "max_results": max_results,
                    "data": data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error retrieving Gmail messages for {email}: {str(e)}")
            return Response(
                {
                    "error": "Failed to retrieve Gmail messages",
                    "message": "An error occurred while retrieving Gmail messages",
                    "error_code": "GMAIL_MESSAGES_RETRIEVAL_FAILED",
                    "details": str(e),
                    "email": email
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in gmail_messages: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving Gmail messages",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
def test_oauth_debug(request):
    """
    Debug endpoint to check OAuth status and credentials.
    """
    try:
        from envoy.models.mail_model import GmailCredential
        
        # Get all credentials
        credentials = GmailCredential.objects.all()
        cred_list = []
        
        for cred in credentials:
            cred_list.append({
                "email": cred.system_email,
                "has_access_token": bool(cred.access_token),
                "has_refresh_token": bool(cred.refresh_token),
                "token_expiry": cred.token_expiry.isoformat() if cred.token_expiry else None,
                "client_id": cred.client_id[:20] + "..." if cred.client_id else None
            })
        
        return Response(
            {
                "message": "OAuth Debug Information",
                "total_credentials": len(cred_list),
                "credentials": cred_list,
                "google_config": {
                    "client_id_set": bool(settings.GOOGLE_CLIENT_ID),
                    "client_secret_set": bool(settings.GOOGLE_CLIENT_SECRET),
                    "redirect_uri_set": bool(settings.GOOGLE_REDIRECT_URI),
                    "scopes_set": bool(settings.GOOGLE_SCOPES)
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in test_oauth_debug: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Debug endpoint error",
                "message": "Error retrieving debug information",
                "error_code": "DEBUG_ERROR",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_email(request):
    """
    Send email via Gmail API.
    
    Request body:
    {
        "to_email": "recipient@example.com",
        "subject": "Email Subject",
        "body": "Email body content",
        "thread_id": "optional_thread_id_for_replies",
        "conversation_id": "optional_conversation_id",
        "conversation_code": "optional_conversation_code",
        "first_message_id": "optional_first_message_id",
        "from_email": "sender@example.com"
    }
    """
    try:
        # Get request data
        to_email = request.data.get("to_email")
        subject = request.data.get("subject", "")
        body = request.data.get("body")
        thread_id = request.data.get("thread_id")
        conversation_id = request.data.get("conversation_id")
        conversation_code = request.data.get("conversation_code")
        first_message_id = request.data.get("first_message_id")
        from_email = request.data.get("from_email")
        
        # Validate required fields
        if not to_email:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "to_email is required",
                    "error_code": "MISSING_TO_EMAIL"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Note: body is still required for Gmail API but not stored in our model
        if not body:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "body is required",
                    "error_code": "MISSING_BODY"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not from_email:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "from_email is required",
                    "error_code": "MISSING_FROM_EMAIL"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if Gmail is connected for the sender email
        try:
            cred = GmailCredential.objects.get(system_email=from_email)
        except GmailCredential.DoesNotExist:
            return Response(
                {
                    "error": "Gmail not connected",
                    "message": f"Gmail account {from_email} is not connected. Please connect your Gmail account first.",
                    "error_code": "GMAIL_NOT_CONNECTED",
                    "connected": False,
                    "action": "connect_first"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Create EmailMessage record
        
        
        email_message = EmailMessage.objects.create(
            to_email=to_email,
            thread_id=thread_id,
            conversation_id=conversation_id,
            conversation_code=conversation_code,
            first_message_id=first_message_id,
            user_id=request.user.id,
            from_email=from_email,
            status='pending',
            type_based_id= "direct_mail_test"
        )
        
        try:
            # Send email via Gmail API
            logger.info(f"Sending email from {from_email} to {to_email}")
            gmail_response = svc.send_email(
                credential=cred,
                to_email=to_email,
                subject=subject,
                body=body,
                thread_id=thread_id
            )
            
            # Update EmailMessage with success details
            email_message.status = 'sent'
            email_message.gmail_message_id = gmail_response.get('id')
            email_message.gmail_thread_id = gmail_response.get('threadId')
            email_message.sent_at = timezone.now()
            email_message.save()
            
            logger.info(f"Email sent successfully. Message ID: {email_message.gmail_message_id}")
            
            return Response(
                {
                    "message": "Email sent successfully",
                    "email_message_id": email_message.id,
                    "gmail_message_id": email_message.gmail_message_id,
                    "gmail_thread_id": email_message.gmail_thread_id,
                    "to_email": to_email,
                    "from_email": from_email,
                    "subject": subject,
                    "is_reply": bool(thread_id),
                    "first_message_id": email_message.first_message_id,
                    "sent_at": email_message.sent_at.isoformat() if email_message.sent_at else None
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            # Update EmailMessage with error details
            email_message.status = 'failed'
            email_message.error_message = str(e)
            email_message.save()
            
            logger.error(f"Failed to send email: {str(e)}")
            return Response(
                {
                    "error": "Failed to send email",
                    "message": "An error occurred while sending the email",
                    "error_code": "EMAIL_SEND_FAILED",
                    "details": str(e),
                    "email_message_id": email_message.id
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in send_email: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while sending email",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def email_history(request):
    """
    Get email message history for the authenticated user.
    
    Query parameters:
    - email: Filter by sender email (optional)
    - status: Filter by status (pending, sent, failed, draft) (optional)
    - limit: Number of records to return (default: 20, max: 100)
    """
    try:
        from envoy.models.mail_model import EmailMessage
        
        # Get query parameters
        email = request.query_params.get("email")
        status = request.query_params.get("status")
        limit = request.query_params.get("limit", 20)
        
        # Validate limit
        try:
            limit = int(limit)
            if limit <= 0 or limit > 100:
                limit = 20
        except ValueError:
            limit = 20
        
        # Build query
        queryset = EmailMessage.objects.filter(user_id=request.user.id)
        
        if email:
            queryset = queryset.filter(from_email=email)
        
        if status:
            queryset = queryset.filter(status=status)
        
        # Get results
        email_messages = queryset.order_by('-created_at')[:limit]
        
        # Prepare response data
        messages = []
        for msg in email_messages:
            messages.append({
                "id": msg.id,
                "to_email": msg.to_email,
                "from_email": msg.from_email,
                "thread_id": msg.thread_id,
                "conversation_id": msg.conversation_id,
                "conversation_code": msg.conversation_code,
                "first_message_id": msg.first_message_id,
                "status": msg.status,
                "gmail_message_id": msg.gmail_message_id,
                "gmail_thread_id": msg.gmail_thread_id,
                "created_at": msg.created_at.isoformat(),
                "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
                "error_message": msg.error_message,
                "retry_count": msg.retry_count
            })
        
        return Response(
            {
                "message": "Email history retrieved successfully",
                "total_messages": len(messages),
                "user_id": request.user.id,
                "filters": {
                    "email": email,
                    "status": status,
                    "limit": limit
                },
                "messages": messages
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in email_history: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving email history",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
import base64
import hashlib
import logging
import re
from datetime import datetime, timezone as dt_timezone
from typing import Optional ,Tuple
from envoy.services.email_service import (
    get_thread_messages,
    get_message_details,
    search_messages_by_conversation,
)

logger = logging.getLogger(__name__)


def _norm_addr(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.strip()
    if "<" in s and ">" in s:
        s = s[s.find("<") + 1 : s.find(">")]
    return s.strip().lower()


def _fingerprint(msg: dict) -> str:
    frm = _norm_addr(msg.get("from_email"))
    to = _norm_addr(msg.get("to_email"))
    subject = (msg.get("subject") or "").strip().lower()
    body_snip = (msg.get("body") or "")[:200].strip()
    basis = f"{frm}|{to}|{subject}|{body_snip}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()


def _ms_to_iso(ms_str: Optional[str]) -> Optional[str]:
    if not ms_str:
        return None
    try:
        ms = int(ms_str)
        return datetime.utcfromtimestamp(ms / 1000).replace(tzinfo=dt_timezone.utc).isoformat()
    except Exception:
        return str(ms_str)


def _parse_dt_for_sort(ts: Optional[str]) -> float:
    if not ts:
        return 0.0
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        pass
    try:
        return int(ts) / 1000.0
    except Exception:
        return 0.0


def _header_get(headers: list, name: str, default: str = "") -> str:
    return next((h["value"] for h in headers if h.get("name", "").lower() == name.lower()), default)


# --- new: clean latest reply and capture "On ... wrote:" time -------------
# More comprehensive regex to match various "On ... wrote:" formats
_REPLY_BREAK_RE = re.compile(r"(?mi)^\s*On .+?wrote:\s*$|^.*On .+?wrote:\s*$")
# captures like: "On Sat, Aug 9, 2025, 12:37 AM" and variations
_REPLY_TIME_CAPTURE_RE = re.compile(r"(?mi)^\s*(On\s+.+?),?\s+wrote:\s*$|^.*(On\s+.+?),?\s+wrote:\s*$")

from typing import Tuple, Optional

def _extract_reply_and_time(raw_text: str) -> Tuple[str, Optional[str]]:
    """
    Extract latest reply (before quoted 'On ... wrote:' block) and mess_time.
    - Handles inline "On ... wrote:" on same line
    - Drops lines starting with '>'
    - Normalizes weird Unicode spaces from Gmail (e.g., narrow no-break space)
    - Returns (clean_one_line_body, mess_time or None)
    """
    if not raw_text:
        return "", None

    # Normalize newlines + normalize Unicode spaces Gmail likes to use
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = (
        text
        .replace("\u00A0", " ")  # NO-BREAK SPACE
        .replace("\u202F", " ")  # NARROW NO-BREAK SPACE
        .replace("\u2009", " ")  # THIN SPACE (just in case)
    )

    # Remove fully quoted lines starting with '>'
    lines = [ln for ln in text.split("\n") if not ln.lstrip().startswith(">")]
    text = "\n".join(lines)

    # Find the first "On ... wrote:" anywhere (case-insensitive, dot matches newline)
    # We capture the middle part so we can compute a clean mess_time.
    m = re.search(r'(?is)\bOn\s+(?P<meta>.+?)\s*wrote:', text)
    mess_time: Optional[str] = None

    if m:
        # Body is everything BEFORE the quoted marker
        body_part = text[:m.start()]
        # Clean body: single spaces, trim; keep emojis as-is
        body = re.sub(r'[ \t]+', ' ', body_part.replace("\n", " ")).strip()

        # Build a cleaner mess_time from meta
        meta = m.group("meta")
        # Remove bracketed email if present
        meta = re.sub(r'<[^>]+>', '', meta).strip()
        # Collapse whitespace
        meta = re.sub(r'\s+', ' ', meta).strip()

        # Try to cut at the end of the time token, e.g., "12:59 PM"
        # Handle AM/PM with optional Unicode space
        ampm_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', meta, flags=re.I)
        if ampm_match:
            meta = meta[:ampm_match.end()].strip()
        else:
            # Fallback: a 24h time like "13:45"
            h24 = re.search(r'(\b\d{1,2}:\d{2}\b)', meta)
            if h24:
                meta = meta[:h24.end()].strip()
            # else: leave meta as-is (date-only)

        mess_time = f"On {meta}" if meta else None
        return body, mess_time

    # No quoted marker found → return cleaned original as body, no mess_time
    body = re.sub(r'[ \t]+', ' ', text.replace("\n", " ")).strip()
    return body, None

# -------------------------------------------------------------------------
from email.utils import getaddresses
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def email_thread_replies(request):
    """
    Get all email replies from a particular message thread using conversation_code.
    Fetches both local DB and Gmail API messages, de-dupes, and cleans bodies.
    Also syncs missing messages to external chat app when conversation_id is available.
    """

    # -------------------- helpers --------------------
    def _normalize_emails(value):
        """Return a set of lowercase bare emails from an address header/string."""
        if not value:
            return set()
        return {addr.lower() for _, addr in getaddresses([value]) if addr}

    def _classify_status(from_val, to_like_val, identity_emails):
        """
        sent:     if From ∈ identity
        received: if any(To/Cc/Delivered-To) ∈ identity and From ∉ identity
        unknown:  otherwise
        """
        from_set = _normalize_emails(from_val)
        to_set   = _normalize_emails(to_like_val)
        if from_set & identity_emails:
            return "sent"
        if to_set & identity_emails:
            return "received"
        return "unknown"

    def _extract_clean_body_and_time(md):
        """
        Given a Gmail message detail `md`, return (clean_body, mess_time).
        Uses your existing _extract_reply_and_time(body_text).
        """
        import base64, re, html

        payload = md.get("payload", {})
        body_text = ""

        def decode_body_data(data):
            try:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                try:
                    return base64.urlsafe_b64decode(data).decode("latin-1", errors="replace")
                except Exception:
                    return str(base64.urlsafe_b64decode(data), errors="replace")

        # Prefer text/plain; fallback to text/html
        if payload.get("body", {}).get("data"):
            body_text = decode_body_data(payload["body"]["data"])
        elif "parts" in payload:
            for part in payload.get("parts", []):
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    body_text = decode_body_data(part["body"]["data"])
                    break
            if not body_text:
                for part in payload.get("parts", []):
                    if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
                        html_text = decode_body_data(part["body"]["data"])
                        html_text = html.unescape(html_text)
                        body_text = re.sub(r"<[^>]+>", "", html_text)
                        body_text = re.sub(r"\s+", " ", body_text).strip()
                        break

        clean_body, mess_time = _extract_reply_and_time(body_text)
        return clean_body, mess_time

    # ---- Chat API config + auth helpers
    CHAT_API_BASE = getattr(settings, "CHAT_API_BASE", "https://dev-chat-app.apptimus.lk/api")

    def _redact_token(tok: str) -> str:
        if not tok:
            return ""
        if len(tok) <= 10:
            return tok[:2] + "…"
        return tok[:4] + "…" + tok[-4:]

    def _get_chat_token(req):
        # 1) query param
        qp = req.query_params.get("idp_access_token")
        if qp:
            return qp.strip()
        # 2) Authorization header from caller
        auth = req.META.get("HTTP_AUTHORIZATION") or req.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1].strip()
        # 3) settings fallback
        return getattr(settings, "CHAT_API_TOKEN", None)

    def _chat_headers(token: str):
        h = {"Accept": "application/json", "Content-Type": "application/json"}
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    try:
        conversation_code = request.query_params.get("conversation_code")
        limit = request.query_params.get("limit", 50)
        include_gmail_data = request.query_params.get("include_gmail_data", "false").lower() == "true"
        include_gmail_messages = request.query_params.get("include_gmail_messages", "true").lower() == "true"

        if not conversation_code:
            return Response(
                {
                    "error": "Missing required parameter",
                    "message": "conversation_code parameter is required",
                    "error_code": "MISSING_PARAMETER",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            limit = int(limit)
            if limit <= 0 or limit > 200:
                limit = 50
        except ValueError:
            limit = 50

        queryset = (
            EmailMessage.objects.filter(conversation_code=conversation_code, user_id=request.user.id)
            .order_by("created_at")
        )

        messages = []
        gmail_messages = []
        thread_ids = set()

        # conversation_id and thread-level first_message_id from DB
        conversation_id = (
            queryset.exclude(conversation_id__isnull=True)
            .values_list("conversation_id", flat=True)
            .first()
        )
        logger.info(f"[chat-sync] conversation_id for code {conversation_code}: {conversation_id}")

        thread_first_message_id = (
            queryset.exclude(first_message_id__isnull=True)
            .values_list("first_message_id", flat=True)
            .first()
        )

        # identity emails for local classification
        identity_local = set()
        user_email = getattr(request.user, "email", None)
        if user_email:
            identity_local.add(user_email.lower())

        # ---- Local messages
        failed_messages = []
        for msg in queryset:
            computed_status = _classify_status(
                getattr(msg, "from_email", None),
                getattr(msg, "to_email", None),
                identity_local,
            )
            final_status = computed_status if computed_status != "unknown" else (getattr(msg, "status", None) or "unknown")

            message_data = {
                "id": msg.id,
                "to_email": getattr(msg, "to_email", None),
                "from_email": getattr(msg, "from_email", None),
                "thread_id": getattr(msg, "thread_id", "") or "",
                "conversation_id": getattr(msg, "conversation_id", None),
                "conversation_code": msg.conversation_code,
                "first_message_id": getattr(msg, "first_message_id", None),
                "status": final_status,
                "created_at": (msg.created_at.isoformat() if getattr(msg, "created_at", None) else None),
                "sent_at": (msg.sent_at.isoformat() if getattr(msg, "sent_at", None) else None),
                "error_message": getattr(msg, "error_message", None),
                "retry_count": getattr(msg, "retry_count", 0),
                "source": "local_database",
                "body": getattr(msg, "body", None) or getattr(msg, "message", None) or "",
                "attachments": [],  # Add empty attachments array for local messages
                "attachment_images": [],  # Add empty attachment_images array for local messages
            }

            gmail_msg_id = getattr(msg, "gmail_message_id", None)
            gmail_thread_id = getattr(msg, "gmail_thread_id", None)
            if include_gmail_data:
                message_data.update(
                    {
                        "gmail_message_id": gmail_msg_id,
                        "gmail_thread_id": gmail_thread_id,
                    }
                )

            if message_data["status"] == 'failed':
                failed_messages.append(message_data)
            else:
                messages.append(message_data)

            if gmail_thread_id:
                thread_ids.add(gmail_thread_id)
                logger.info(f"Added thread_id: {gmail_thread_id} from local message {msg.id}")

        # ---- Gmail API messages
        if include_gmail_messages:
            try:
                gmail_credentials = GmailCredential.objects.all()
                logger.info(f"Found {gmail_credentials.count()} Gmail credentials")
                
                if gmail_credentials.exists():
                    credential = gmail_credentials.first()
                    logger.info(f"Using Gmail credential for: {credential.system_email}")
                    logger.info(f"Thread IDs to fetch: {thread_ids}")

                    identity_gmail = {str(credential.system_email).lower()} if getattr(credential, "system_email", None) else set()

                    # 1) From known thread IDs
                    for thread_id in thread_ids:
                        try:
                            logger.info(f"Fetching Gmail thread: {thread_id}")
                            thread_data = get_thread_messages(credential, thread_id)
                            logger.info(f"Found {len(thread_data.get('messages', []))} messages in thread {thread_id}")
                            for gm in thread_data.get("messages", []):
                                try:
                                    md = get_message_details(credential, gm["id"])
                                    headers = md.get("payload", {}).get("headers", [])
                                    subject = _header_get(headers, "Subject", "")
                                    from_header = _header_get(headers, "From", "")
                                    to_header = _header_get(headers, "To", "")
                                    cc_header = _header_get(headers, "Cc", "")
                                    delivered_to = _header_get(headers, "Delivered-To", "")
                                    internet_message_id = _header_get(headers, "Message-Id", "").strip() or None

                                    clean_body, mess_time = _extract_clean_body_and_time(md)
                                    to_like = ", ".join([h for h in [to_header, cc_header, delivered_to] if h])
                                    status_val = _classify_status(from_header, to_like, identity_gmail)
                                    iso_ts = _ms_to_iso(md.get("internalDate"))

                                    gmail_messages.append({
                                         "id": f"gmail_{gm['id']}",
                                         "to_email": to_header,
                                         "from_email": from_header,
                                         "subject": subject,
                                         "body": clean_body,
                                         "mess_time": mess_time,
                                         "thread_id": thread_id,
                                         "conversation_id": None,
                                         "conversation_code": conversation_code,
                                         "status": status_val,
                                         "created_at": iso_ts,
                                         "sent_at": iso_ts,
                                         "error_message": None,
                                         "retry_count": 0,
                                         "source": "gmail_api",
                                         "gmail_message_id": gm["id"],
                                         "gmail_thread_id": thread_id,
                                         "internet_message_id": internet_message_id,
                                         "first_message_id": thread_first_message_id,
                                         "attachments": [],  # Add empty attachments array for Gmail messages
                                         "attachment_images": [],  # Add empty attachment_images array for Gmail messages
                                     })
                                except Exception as e:
                                    logger.warning(f"Error parsing Gmail message {gm.get('id')}: {e}")
                                    continue
                        except Exception as e:
                            logger.warning(f"Error fetching Gmail thread {thread_id}: {e}")
                            continue

                    # 2) Search by conversation code
                    try:
                        logger.info(f"Searching Gmail for conversation code: {conversation_code}")
                        search_results = search_messages_by_conversation(credential, conversation_code, max_results=20)
                        logger.info(f"Found {len(search_results.get('messages', []))} messages by conversation search")
                        for gm in search_results.get("messages", []):
                            try:
                                md = get_message_details(credential, gm["id"])
                                headers = md.get("payload", {}).get("headers", [])
                                subject = _header_get(headers, "Subject", "")
                                from_header = _header_get(headers, "From", "")
                                to_header = _header_get(headers, "To", "")
                                cc_header = _header_get(headers, "Cc", "")
                                delivered_to = _header_get(headers, "Delivered-To", "")
                                internet_message_id = _header_get(headers, "Message-Id", "").strip() or None

                                clean_body, mess_time = _extract_clean_body_and_time(md)
                                to_like = ", ".join([h for h in [to_header, cc_header, delivered_to] if h])
                                status_val = _classify_status(from_header, to_like, identity_gmail)
                                iso_ts = _ms_to_iso(md.get("internalDate"))

                                gmail_messages.append({
                                    "id": f"gmail_{gm['id']}",
                                    "to_email": to_header,
                                    "from_email": from_header,
                                    "subject": subject,
                                    "body": clean_body,
                                    "mess_time": mess_time,
                                    "thread_id": gm.get("threadId"),
                                    "conversation_id": None,
                                    "conversation_code": conversation_code,
                                    "status": status_val,
                                    "created_at": iso_ts,
                                    "sent_at": iso_ts,
                                    "error_message": None,
                                    "retry_count": 0,
                                    "source": "gmail_api_search",
                                    "gmail_message_id": gm["id"],
                                    "gmail_thread_id": gm.get("threadId"),
                                    "internet_message_id": internet_message_id,
                                    "first_message_id": thread_first_message_id,
                                    "attachments": [],  # Add empty attachments array for Gmail search messages
                                    "attachment_images": [],  # Add empty attachment_images array for Gmail search messages
                                })
                            except Exception as e:
                                logger.warning(f"Error parsing searched Gmail message {gm.get('id')}: {e}")
                                continue
                    except Exception as e:
                        logger.warning(f"Error searching Gmail messages for conversation {conversation_code}: {e}")
                        
                    # 3) Fallback search by thread IDs
                    if not gmail_messages and thread_ids:
                        logger.info("No messages found by conversation code, trying thread ID search")
                        for thread_id in thread_ids:
                            try:
                                params = {"q": f"threadId:{thread_id}", "maxResults": 20}
                                r = requests.get(
                                    "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                                    headers={"Authorization": f"Bearer {credential.access_token}"},
                                    params=params,
                                    timeout=30
                                )
                                r.raise_for_status()
                                data = r.json()
                                messages_found = data.get('messages', [])
                                logger.info(f"Found {len(messages_found)} messages for thread ID {thread_id}")
                                
                                for gm in messages_found:
                                    try:
                                        md = get_message_details(credential, gm["id"])
                                        headers = md.get("payload", {}).get("headers", [])
                                        subject = _header_get(headers, "Subject", "")
                                        from_header = _header_get(headers, "From", "")
                                        to_header = _header_get(headers, "To", "")
                                        cc_header = _header_get(headers, "Cc", "")
                                        delivered_to = _header_get(headers, "Delivered-To", "")
                                        internet_message_id = _header_get(headers, "Message-Id", "").strip() or None

                                        clean_body, mess_time = _extract_clean_body_and_time(md)
                                        to_like = ", ".join([h for h in [to_header, cc_header, delivered_to] if h])
                                        status_val = _classify_status(from_header, to_like, identity_gmail)
                                        iso_ts = _ms_to_iso(md.get("internalDate"))

                                        gmail_messages.append({
                                            "id": f"gmail_{gm['id']}",
                                            "to_email": to_header,
                                            "from_email": from_header,
                                            "subject": subject,
                                            "body": clean_body,
                                            "mess_time": mess_time,
                                            "thread_id": thread_id,
                                            "conversation_id": None,
                                            "conversation_code": conversation_code,
                                            "status": status_val,
                                            "created_at": iso_ts,
                                            "sent_at": iso_ts,
                                            "error_message": None,
                                            "retry_count": 0,
                                            "source": "gmail_api_thread_search",
                                            "gmail_message_id": gm["id"],
                                            "gmail_thread_id": thread_id,
                                            "internet_message_id": internet_message_id,
                                            "first_message_id": thread_first_message_id,
                                            "attachments": [],  # Add empty attachments array for Gmail thread search messages
                                            "attachment_images": [],  # Add empty attachment_images array for Gmail thread search messages
                                        })
                                    except Exception as e:
                                        logger.warning(f"Error parsing Gmail message {gm.get('id')}: {e}")
                                        continue
                            except Exception as e:
                                logger.warning(f"Error searching Gmail for thread ID {thread_id}: {e}")
                                continue
            except Exception as e:
                logger.warning(f"Error fetching Gmail messages: {e}")

        # ---- Combine & De-duplicate
        logger.info(f"Local messages found: {len(messages)}")
        logger.info(f"Gmail API messages found: {len(gmail_messages)}")
        
        gmail_ids = {gm.get("gmail_message_id") for gm in gmail_messages if gm.get("gmail_message_id")}
        gmail_imids = {gm.get("internet_message_id") for gm in gmail_messages if gm.get("internet_message_id")}
        gmail_fps = {_fingerprint(gm) for gm in gmail_messages}

        unique_messages = []
        seen_keys = set()

        for m in gmail_messages:
            key = m.get("gmail_message_id") or m.get("internet_message_id") or _fingerprint(m)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_messages.append(m)

        for m in messages:
            key = m.get("gmail_message_id") or _fingerprint(m)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_messages.append(m)

        logger.info(f"Total unique messages after deduplication: {len(unique_messages)}")

        if not unique_messages and failed_messages:
            logger.info("No successful messages found, including failed messages as fallback")
            unique_messages = failed_messages

        # -------------------- Chat sync (with token) --------------------
        chat_sync = {"attempted": 0, "posted": 0, "skipped_existing": 0, "errors": 0}
        existing_chat_texts = set()

        chat_token = _get_chat_token(request)
        if not chat_token:
            logger.warning("[chat-sync] Missing idp_access_token (query param/header/settings). Skipping chat fetch/post.")
        else:
            logger.info(f"[chat-sync] Using idp_access_token={_redact_token(chat_token)}")

            if conversation_id:
                # 1) Pull existing chat messages to de-dupe
                try:
                    url_get = f"{CHAT_API_BASE}/conversations/{conversation_id}/messages"
                    params = {"per_page": 200}
                    r = requests.get(url_get, headers=_chat_headers(chat_token), params=params, timeout=30)
                    r.raise_for_status()
                    resp_json = r.json() if r.content else {}
                    existing_list = ((resp_json or {}).get("data") or {}).get("data") or []
                    existing_chat_texts = {str(it.get("content", "")).strip() for it in existing_list if it.get("content")}
                    logger.info(f"[chat-sync] Existing chat messages fetched: {len(existing_chat_texts)}")
                except requests.HTTPError as e:
                    chat_sync["errors"] += 1
                    logger.warning(f"[chat-sync] Failed to fetch chat messages: {e}")
                except Exception as e:
                    chat_sync["errors"] += 1
                    logger.warning(f"[chat-sync] Exception fetching chat messages: {e}")

                # 2) Post any email messages not yet in chat
                url_post = f"{CHAT_API_BASE}/messages"
                for m in unique_messages:
                    text = (m.get("body") or "").strip()
                    if not text:
                        continue
                    chat_sync["attempted"] += 1

                    if text in existing_chat_texts:
                        chat_sync["skipped_existing"] += 1
                        continue

                    reply_msg_id = ""
                    if m.get("status") == "received":
                        reply_msg_id = m.get("first_message_id") or thread_first_message_id or ""

                    # Extract attachments from the message if available
                    attachments = ""
                    attachment_images = ""
                    
                    # Check if the message has attachment data
                    if isinstance(m, dict):
                        # Look for attachment fields in the message
                        msg_attachments = m.get("attachments", [])
                        msg_attachment_images = m.get("attachment_images", [])
                        
                        # For now, send empty strings to avoid format issues with external API
                        # TODO: Implement proper attachment handling if needed
                        if msg_attachments:
                            logger.info(f"[chat-sync] Message has {len(msg_attachments)} attachments, sending empty string to external API")
                        if msg_attachment_images:
                            logger.info(f"[chat-sync] Message has {len(msg_attachment_images)} attachment images, sending empty string to external API")
                    
                    payload = {
                        "msg": text,
                        "conversation_id": conversation_id,
                        "attachments": attachments,
                        "attachment_images": attachment_images,
                        "reply_msg_id": reply_msg_id,
                    }

                    try:
                        pr = requests.post(url_post, headers=_chat_headers(chat_token), json=payload, timeout=30)
                        if 200 <= pr.status_code < 300:
                            chat_sync["posted"] += 1
                            existing_chat_texts.add(text)
                        else:
                            chat_sync["errors"] += 1
                            logger.warning(f"[chat-sync] Failed to post message (status {pr.status_code}): {pr.text}")
                            if pr.status_code == 401:
                                break
                    except Exception as e:
                        chat_sync["errors"] += 1
                        logger.warning(f"[chat-sync] Exception while posting message: {e}")

        # ---- Sort & limit for API response
        unique_messages.sort(key=lambda x: _parse_dt_for_sort(x.get("created_at")))
        unique_messages = unique_messages[:limit]

        if not unique_messages:
            return Response(
                {
                    "error": "No messages found",
                    "message": f"No email messages found for conversation_code: {conversation_code}",
                    "error_code": "NO_MESSAGES_FOUND",
                    "conversation_code": conversation_code,
                    "conversation_id": conversation_id,
                    "chat_sync": chat_sync,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Count only non-failed messages for total
        total_messages = len([m for m in unique_messages if m.get("status") != "failed"])
        status_summary = {}
        for m in unique_messages:
            st = m.get("status", "unknown")
            status_summary[st] = status_summary.get(st, 0) + 1

        first_message = unique_messages[0]
        last_message = unique_messages[-1]

        return Response(
            {
                "message": "Email thread replies retrieved successfully",
                "conversation_code": conversation_code,
                "conversation_id": conversation_id,
                "conversation_summary": {
                    "total_messages": total_messages,
                    "status_summary": status_summary,
                    "first_message_date": first_message.get("created_at"),
                    "last_message_date": last_message.get("created_at"),
                    "conversation_duration_days": 0,
                },
                "filters": {
                    "conversation_code": conversation_code,
                    "limit": limit,
                    "include_gmail_data": include_gmail_data,
                    "include_gmail_messages": include_gmail_messages,
                },
                "sources": {
                    "local_database_count": len(messages),
                    "local_database_failed_count": len(failed_messages),
                    "gmail_api_count": len(gmail_messages),
                    "total_unique_count": len(unique_messages),
                },
                "chat_sync": chat_sync,
                "messages": unique_messages,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error in email_thread_replies: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving email thread replies",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_message(request):
    """
    Send message via external chat API and then send email via Gmail.

    Body:
      body (req), subject (opt), to_mail (req unless derived), conversation_id (opt),
      from_email (opt -> will default from core_gmailcredential), idp_access_token (from header),
      type_based_id (opt), insurer_id (opt)
    """
    def _norm_str(val):
        if val is None:
            return None
        if isinstance(val, str):
            s = val.strip()
            return s or None
        return str(val)

    try:
        # prefer Authorization header over body
        idp_access_token = get_bearer_token(request)

        body = request.data.get("body")
        subject = _norm_str(request.data.get("subject", ""))
        to_mail = _norm_str(request.data.get("to_mail"))
        from_email = _norm_str(request.data.get("from_email"))
        type_based_id = request.data.get("type_based_id", None)
        conversation_id = _norm_str(request.data.get("conversation_id"))
        insurer_id = request.data.get("insurer_id", None)
        
        # Handle attachments
        attachments = request.data.get("attachments", [])
        attachment_images = request.data.get("attachment_images", [])
        
        # Validate and clean attachments format
        if not isinstance(attachments, list):
            attachments = []
        if not isinstance(attachment_images, list):
            attachment_images = []
            
        # For external API, we need to send empty strings if no valid attachments
        # The external API expects either files or empty strings, not attachment objects
        external_attachments = ""
        external_attachment_images = ""
        
        # Only set attachments if we have valid ones (the API will handle the validation)
        if attachments and len(attachments) > 0:
            # For now, send empty string to avoid format issues
            # TODO: Implement proper file upload handling if needed
            external_attachments = ""
            logger.info(f"Attachments provided but sending empty string to external API: {len(attachments)} items")
        
        if attachment_images and len(attachment_images) > 0:
            # For now, send empty string to avoid format issues
            # TODO: Implement proper file upload handling if needed
            external_attachment_images = ""
            logger.info(f"Attachment images provided but sending empty string to external API: {len(attachment_images)} items")
        
        # Use the processed values for external API calls
        attachments_for_external = external_attachments
        attachment_images_for_external = external_attachment_images

        # ----- NEW: fallback to default shared mailbox if from_email is missing -----
        if not from_email:
            try:
                gmail_credential_row = (
                    QueryBuilderService("core_gmailcredential")
                    .select("system_email")
                    .orderBy("id", "asc")
                    .first()
                )
                if gmail_credential_row and gmail_credential_row.get("system_email"):
                    from_email = gmail_credential_row["system_email"]
                    print(f"[send_message] Using default from_email: {from_email}")
                    logger.info(f"[send_message] Using default from_email from core_gmailcredential: {from_email}")
            except Exception as e:
                logger.warning(f"[send_message] Could not load default system_email: {e}")

        # validations
        if not body:
            return Response(
                {"error": "Missing required field", "message": "body is required", "error_code": "MISSING_BODY"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not idp_access_token:
            return Response(
                {"error": "Missing required field", "message": "idp_access_token is required for external API authentication", "error_code": "MISSING_IDP_ACCESS_TOKEN"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If conversation_id is provided, try to derive addresses when missing
        if conversation_id:
            try:
                latest_email = (
                    EmailMessage.objects
                    .filter(conversation_id=conversation_id)
                    .order_by("-sent_at", "-created_at")
                    .first()
                )
                if latest_email:
                    # Derive to_mail if still missing
                    if not to_mail:
                        to_mail = latest_email.to_email
                        logger.info(f"[send_message] Derived to_mail '{to_mail}' from conversation_id {conversation_id}")
                    # Only derive from_email if STILL missing (we prefer the default shared mailbox)
                    if not from_email:
                        from_email = latest_email.from_email
                        logger.info(f"[send_message] Derived from_email '{from_email}' from conversation_id {conversation_id}")
                else:
                    logger.warning(f"[send_message] No EmailMessage found for conversation_id {conversation_id}")
            except Exception as e:
                logger.error(f"[send_message] Error deriving emails for conversation_id={conversation_id}: {e}")

        # Validate we at least have a recipient
        if not to_mail:
            return Response(
                {"error": "Missing required field", "message": "to_mail is required (not provided and could not be derived from conversation_id)", "error_code": "MISSING_TO_MAIL"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # At this point, from_email may still be None if there is no default credential configured.
        # We won't fail here; the GmailCredential lookup will give a clear 401 if not connected.

        current_user = request.user
        if not getattr(current_user, "idp_user_id", None):
            return Response(
                {"error": "User not configured", "message": "Current user does not have idp_user_id configured", "error_code": "USER_NOT_CONFIGURED"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        external_headers = {
            "Authorization": f"Bearer {idp_access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Envoy-BU-Core-API/1.0",
        }

        # ==============================
        # A) Existing conversation flow
        # ==============================
        if conversation_id:
            # 1) Send chat message to existing conversation (no group creation)
            conv_for_api = int(conversation_id) if conversation_id.isdigit() else conversation_id
            msg_payload = {
                "msg": body,
                "conversation_id": conv_for_api,
                "attachments": attachments_for_external,
                "attachment_images": attachment_images_for_external,
                "reply_msg_id": "",
            }
            
            logger.info(f"[send_message] Sending to external API - conversation_id: {conv_for_api}, attachments_count: {len(attachments)}, attachment_images_count: {len(attachment_images)}")
            try:
                r = requests.post(
                    "https://dev-chat-app.apptimus.lk/api/messages",
                    json=msg_payload,
                    headers=external_headers,
                    timeout=30,
                )
                r.raise_for_status()
                msg_data = r.json()
                if not msg_data.get("success"):
                    return Response(
                        {
                            "error": "Message sending failed",
                            "message": msg_data.get("msg", "Unknown error"),
                            "error_code": "MESSAGE_SENDING_FAILED",
                            "external_response": msg_data,
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                first_message_id = (msg_data.get("data") or {}).get("id")
            except requests.exceptions.RequestException as e:
                logger.error(f"[send_message] Chat send failed: {e}")
                error_details = f"Failed to send message: {e}"
                
                # Add more details for specific error codes
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_response = e.response.json()
                        error_details += f" - API Response: {error_response}"
                        logger.error(f"[send_message] External API error response: {error_response}")
                    except:
                        error_details += f" - Response text: {e.response.text}"
                        logger.error(f"[send_message] External API error response text: {e.response.text}")
                
                return Response(
                    {"error": "External API error", "message": error_details, "error_code": "EXTERNAL_API_ERROR"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # 2) Resolve Gmail thread_id from DB by conversation_id (prefer same from_email if available)
            try:
                q = (
                    EmailMessage.objects
                    .filter(conversation_id=conversation_id)
                    .exclude(gmail_thread_id__isnull=True)
                    .exclude(gmail_thread_id__exact="")
                )
                latest = (
                    q.filter(from_email=from_email).order_by("-sent_at", "-created_at").first()
                    if from_email else None
                ) or q.order_by("-sent_at", "-created_at").first()
                thread_id = latest.gmail_thread_id if latest else None
            except Exception as e:
                logger.error(f"[send_message] Thread lookup failed: {e}")
                thread_id = None

            if not thread_id:
                return Response(
                    {
                        "error": "THREAD_NOT_FOUND_FOR_CONVERSATION",
                        "message": "Could not resolve Gmail thread for this conversation_id. "
                                   "Ensure the conversation has a previously stored Gmail message.",
                        "error_code": "THREAD_NOT_FOUND_FOR_CONVERSATION",
                        "conversation_id": conversation_id,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 3) Send email reply in the SAME Gmail thread (no DB insert on this path)
            try:
                if not from_email:
                    # still no sender? explicit 401 to guide setup
                    return Response(
                        {
                            "error": "Gmail not connected",
                            "message": "No default sender configured. Please add a row in core_gmailcredential.",
                            "error_code": "GMAIL_NOT_CONNECTED",
                            "connected": False,
                            "action": "connect_first",
                            "group_created": False,
                            "message_sent": True,
                            "conversation_id": conversation_id,
                            "first_message_id": first_message_id,
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                cred = GmailCredential.objects.get(system_email=from_email)
            except GmailCredential.DoesNotExist:
                return Response(
                    {
                        "error": "Gmail not connected",
                        "message": f"Gmail account {from_email or '(unset)'} is not connected. Please connect your Gmail account first.",
                        "error_code": "GMAIL_NOT_CONNECTED",
                        "connected": False,
                        "action": "connect_first",
                        "group_created": False,
                        "message_sent": True,
                        "conversation_id": conversation_id,
                        "first_message_id": first_message_id,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            try:
                gmail_res = svc.send_email(
                    credential=cred,
                    to_email=to_mail,
                    subject=subject or "",
                    body=body,
                    thread_id=thread_id,  # reply
                    attachments=attachments,  # Use original attachments for Gmail
                )
                return Response(
                    {
                        "success": True,
                        "message": "Message and reply email sent successfully (existing conversation).",
                        "data": {
                            "mode": "reply_existing",
                            "conversation_id": conversation_id,
                            "first_message_id": first_message_id,
                            "gmail_message_id": gmail_res.get("id"),
                            "gmail_thread_id": gmail_res.get("threadId"),
                            "sent_at": timezone.now().isoformat(),
                            "thread_id_used": thread_id,
                            "message_data": msg_data.get("data"),
                            "from_email": from_email,
                            "to_mail": to_mail,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                logger.error(f"[send_message] Gmail reply failed: {e}")
                return Response(
                    {
                        "error": "EMAIL_SENDING_FAILED",
                        "message": f"Failed to send email via Gmail API: {e}",
                        "error_code": "EMAIL_SENDING_FAILED",
                        "group_created": False,
                        "message_sent": True,
                        "conversation_id": conversation_id,
                        "first_message_id": first_message_id,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # ==========================
        # B) New conversation flow
        # ==========================
        group_title = subject or "New Message Group"
        group_payload = {"title": group_title, "user_ids": []}

        try:
            g = requests.post(
                "https://dev-chat-app.apptimus.lk/api/group/stroe",
                json=group_payload,
                headers=external_headers,
                timeout=30,
            )
            g.raise_for_status()
            group_data = g.json()
            if group_data.get("title") == "Title cannot be empty":
                return Response({"error": "Group creation failed", "message": "Title cannot be empty", "error_code": "EMPTY_TITLE"}, status=status.HTTP_400_BAD_REQUEST)
            if group_data.get("user_ids") == "List of Users need to be provided":
                return Response({"error": "Group creation failed", "message": "List of Users need to be provided", "error_code": "EMPTY_USER_IDS"}, status=status.HTTP_400_BAD_REQUEST)
            if group_data.get("msg") != "Group has been added successfully":
                return Response({"error": "Group creation failed", "message": group_data.get("msg", "Unknown error"), "error_code": "GROUP_CREATION_FAILED", "external_response": group_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            conversation_id_created = (group_data.get("data") or {}).get("conversation_id")
            if not conversation_id_created:
                return Response({"error": "Group creation failed", "message": "No conversation_id received from group creation", "error_code": "NO_CONVERSATION_ID"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            conversation_code = (group_data.get("data") or {}).get("gsid", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"[send_message] Group create failed: {e}")
            return Response({"error": "External API error", "message": f"Failed to create group: {e}", "error_code": "EXTERNAL_API_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # send chat message
        try:
            msg_payload = {
                "msg": body, 
                "conversation_id": conversation_id_created, 
                "attachments": attachments_for_external, 
                "attachment_images": attachment_images_for_external, 
                "reply_msg_id": ""
            }
            
            logger.info(f"[send_message] Sending to external API (new conversation) - conversation_id: {conversation_id_created}, attachments_count: {len(attachments)}, attachment_images_count: {len(attachment_images)}")
            
            mr = requests.post(
                "https://dev-chat-app.apptimus.lk/api/messages",
                json=msg_payload,
                headers=external_headers,
                timeout=30,
            )
            mr.raise_for_status()
            message_data = mr.json()
            if not message_data.get("success"):
                return Response({"error": "Message sending failed", "message": message_data.get("msg", "Unknown error"), "error_code": "MESSAGE_SENDING_FAILED"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            first_message_id = (message_data.get("data") or {}).get("id")
            if not first_message_id:
                return Response({"error": "Message sending failed", "message": "No message ID received from message sending", "error_code": "NO_MESSAGE_ID"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            logger.error(f"[send_message] Chat send failed: {e}")
            error_details = f"Failed to send message: {e}"
            
            # Add more details for specific error codes
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_response = e.response.json()
                    error_details += f" - API Response: {error_response}"
                    logger.error(f"[send_message] External API error response: {error_response}")
                except:
                    error_details += f" - Response text: {e.response.text}"
                    logger.error(f"[send_message] External API error response text: {e.response.text}")
            
            return Response({"error": "External API error", "message": error_details, "error_code": "EXTERNAL_API_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # send email and store row
        try:
            if not from_email:
                return Response(
                    {
                        "error": "Gmail not connected",
                        "message": "No default sender configured. Please add a row in core_gmailcredential.",
                        "error_code": "GMAIL_NOT_CONNECTED",
                        "connected": False,
                        "action": "connect_first",
                        "group_created": True,
                        "message_sent": True,
                        "conversation_id": conversation_id_created,
                        "first_message_id": first_message_id,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            cred = GmailCredential.objects.get(system_email=from_email)
        except GmailCredential.DoesNotExist:
            return Response(
                {
                    "error": "Gmail not connected",
                    "message": f"Gmail account {from_email} is not connected. Please connect your Gmail account first.",
                    "error_code": "GMAIL_NOT_CONNECTED",
                    "connected": False,
                    "action": "connect_first",
                    "group_created": True,
                    "message_sent": True,
                    "conversation_id": conversation_id_created,
                    "first_message_id": first_message_id,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            email_message = EmailMessage.objects.create(
                to_email=to_mail,
                thread_id=None,
                conversation_id=conversation_id_created,
                conversation_code=conversation_code or "",
                first_message_id=first_message_id,
                user_id=current_user.id,
                from_email=from_email,
                status="pending",
                type_based_id=type_based_id,
                insurer_id=insurer_id,
            )

            gmail_res = svc.send_email(
                credential=cred,
                to_email=to_mail,
                subject=subject or "",
                body=body,
                thread_id=None,  # new thread
                attachments=attachments,  # Use original attachments for Gmail
            )
            email_message.gmail_message_id = gmail_res.get("id")
            email_message.gmail_thread_id = gmail_res.get("threadId")
            email_message.sent_at = timezone.now()
            email_message.status = "sent"
            email_message.save()

            return Response(
                {
                    "success": True,
                    "message": "Message and email sent successfully (new conversation).",
                    "data": {
                        "mode": "new_conversation",
                        "conversation_id": conversation_id_created,
                        "first_message_id": first_message_id,
                        "conversation_code": conversation_code,
                        "gmail_message_id": email_message.gmail_message_id,
                        "gmail_thread_id": email_message.gmail_thread_id,
                        "sent_at": email_message.sent_at.isoformat() if email_message.sent_at else None,
                        "group_data": group_data.get("data"),
                        "message_data": message_data.get("data"),
                        "from_email": from_email,
                        "to_mail": to_mail,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"[send_message] Gmail send failed: {e}")
            return Response(
                {
                    "error": "Email sending failed",
                    "message": f"Failed to send email via Gmail API: {e}",
                    "error_code": "EMAIL_SENDING_FAILED",
                    "group_created": True,
                    "message_sent": True,
                    "conversation_id": conversation_id_created,
                    "first_message_id": first_message_id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except Exception as e:
        logger.error(f"[send_message] Unexpected error: {e}", exc_info=True)
        return Response(
            {"error": "Internal server error", "message": f"An unexpected error occurred: {e}", "error_code": "INTERNAL_SERVER_ERROR"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quotation_thread_messages(request, quotation_id):
    """
    Get all thread messages for a specific quotation.
    Fetches all conversation_codes for the quotation and then gets thread replies for each.
    """
    try:
        # Construct the type_based_id format: QR-{quotation_id}
        type_based_id = f"QR-{quotation_id}"
        
        # Get all EmailMessage records for this quotation
        email_messages = EmailMessage.objects.filter(
            type_based_id=type_based_id
        ).values_list('conversation_code', flat=True).distinct()
        
        if not email_messages:
            return Response({
                "message": f"No email messages found for quotation {quotation_id}",
                "data": [],
                "quotation_id": quotation_id,
                "type_based_id": type_based_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get thread replies for each conversation_code by calling the function directly
        all_thread_replies = []
        
        for conversation_code in email_messages:
            if conversation_code:
                try:
                    logger.info(f"Processing thread-replies for conversation_code: {conversation_code}")
                    
                    # Create a mock request object for the email_thread_replies function
                    from django.test import RequestFactory
                    from django.contrib.auth.models import User
                    
                    # Create a mock request with the same user and query parameters
                    factory = RequestFactory()
                    mock_request = factory.get(f'/api/gmail/thread-replies?conversation_code={conversation_code}')
                    mock_request.user = request.user
                    mock_request.query_params = {'conversation_code': conversation_code}
                    
                    # Call the email_thread_replies function directly
                    from envoy.controllers.mail_controller import email_thread_replies
                    response = email_thread_replies(mock_request)
                    
                    if response.status_code == 200:
                        thread_data = response.data
                        
                        # Extract messages from the response
                        if isinstance(thread_data, dict) and 'messages' in thread_data:
                            messages = thread_data['messages']
                            # Add conversation_code to each message for reference
                            for message in messages:
                                message['conversation_code'] = conversation_code
                            all_thread_replies.extend(messages)
                        else:
                            logger.warning(f"Unexpected response format for conversation_code {conversation_code}: {thread_data}")
                    else:
                        logger.error(f"Thread-replies function returned status {response.status_code} for conversation_code {conversation_code}")
                        
                except Exception as e:
                    logger.error(f"Error processing thread-replies for conversation_code {conversation_code}: {str(e)}")
                    continue
        
        # Sort all messages by timestamp if available
        try:
            all_thread_replies.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        except:
            pass  # If sorting fails, keep original order
        
        return Response({
            "message": f"Successfully retrieved thread messages for quotation {quotation_id}",
            "data": all_thread_replies,
            "quotation_id": quotation_id,
            "type_based_id": type_based_id,
            "conversation_codes_found": list(email_messages),
            "total_messages": len(all_thread_replies)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in quotation_thread_messages for quotation {quotation_id}: {str(e)}")
        return Response({
            "error": "Internal server error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
