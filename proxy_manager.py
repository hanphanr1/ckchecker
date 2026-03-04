"""
Proxy Manager - Handles proxy rotation and management
"""
import asyncio
import random
from typing import List, Optional, Dict
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import urlparse

import aiohttp


@dataclass
class Proxy:
    """Represents a proxy server"""
    url: str
    protocol: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    is_working: bool = True
    failures: int = 0


class ProxyManager:
    """Manages proxy pool and rotation"""

    def __init__(self, proxy_file: str, max_failures: int = 3):
        self.proxy_file = proxy_file
        self.max_failures = max_failures
        self.proxies: List[Proxy] = []
        self.working_proxies: List[Proxy] = []
        self.failed_proxies: List[Proxy] = []
        self._current_index = 0
        self._lock = asyncio.Lock()
        self._load_proxies()

    def _load_proxies(self):
        """Load proxies from file"""
        try:
            with open(self.proxy_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    proxy = self._parse_proxy(line)
                    if proxy:
                        self.proxies.append(proxy)
                        self.working_proxies.append(proxy)

        except FileNotFoundError:
            print(f"Proxy file not found: {self.proxy_file}")
        except Exception as e:
            print(f"Error loading proxies: {e}")

    def _parse_proxy(self, line: str) -> Optional[Proxy]:
        """Parse proxy line into Proxy object"""
        # Supported formats:
        # ip:port
        # protocol://ip:port
        # protocol://user:pass@ip:port

        try:
            # Add protocol if not present
            if "://" not in line:
                line = f"http://{line}"

            parsed = urlparse(line)

            protocol = parsed.scheme or "http"
            host = parsed.hostname or ""
            port = parsed.port or 8080
            username = parsed.username
            password = parsed.password

            return Proxy(
                url=line,
                protocol=protocol,
                host=host,
                port=port,
                username=username,
                password=password
            )

        except Exception:
            return None

    async def get_proxy(self) -> Optional[Proxy]:
        """Get next working proxy"""
        async with self._lock:
            if not self.working_proxies:
                return None

            proxy = self.working_proxies[self._current_index]
            self._current_index = (self._current_index + 1) % len(self.working_proxies)
            return proxy

    async def get_random_proxy(self) -> Optional[Proxy]:
        """Get a random working proxy"""
        async with self._lock:
            if not self.working_proxies:
                return None
            return random.choice(self.working_proxies)

    async def mark_proxy_failed(self, proxy: Proxy):
        """Mark a proxy as failed"""
        async with self._lock:
            proxy.failures += 1

            if proxy.failures >= self.max_failures:
                proxy.is_working = False
                if proxy in self.working_proxies:
                    self.working_proxies.remove(proxy)
                if proxy not in self.failed_proxies:
                    self.failed_proxies.append(proxy)

    async def mark_proxy_success(self, proxy: Proxy):
        """Mark a proxy as working"""
        async with self._lock:
            proxy.failures = 0
            proxy.is_working = True

            if proxy in self.failed_proxies:
                self.failed_proxies.remove(proxy)
            if proxy not in self.working_proxies:
                self.working_proxies.append(proxy)

    async def test_proxy(self, proxy: Proxy, test_url: str = "https://www.netflix.com") -> bool:
        """Test if a proxy is working"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, proxy=proxy.url) as response:
                    return response.status == 200
        except Exception:
            return False

    async def test_all_proxies(self) -> Dict[str, bool]:
        """Test all proxies and return results"""
        results = {}

        async def test_single(proxy: Proxy):
            is_working = await self.test_proxy(proxy)
            results[proxy.url] = is_working
            if not is_working:
                await self.mark_proxy_failed(proxy)
            else:
                await self.mark_proxy_success(proxy)

        tasks = [test_single(p) for p in self.proxies]
        await asyncio.gather(*tasks, return_exceptions=True)

        return results

    def get_proxy_dict(self, proxy: Proxy) -> Dict:
        """Get proxy dict for aiohttp"""
        return {"proxy": proxy.url}

    @property
    def count(self) -> int:
        """Get total proxy count"""
        return len(self.proxies)

    @property
    def working_count(self) -> int:
        """Get working proxy count"""
        return len(self.working_proxies)

    def close(self):
        """Close the proxy manager"""
        # Cleanup if needed
        pass
