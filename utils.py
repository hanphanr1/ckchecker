"""
Utilities - Helper functions for the Netflix checker
"""
import os
import re
import random
import logging
from typing import List, Tuple, Optional
from pathlib import Path


# User agents for requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger("netflix_checker")
    logger.setLevel(logging.INFO)

    # Console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    # Add handler if not already added
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


def get_random_user_agent() -> str:
    """Get a random user agent string"""
    return random.choice(USER_AGENTS)


def load_combos(file_path: str) -> List[Tuple[str, str]]:
    """
    Load combos from file

    Args:
        file_path: Path to combo file

    Returns:
        List of (email, password) tuples
    """
    combos = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse combo
                parsed = parse_combo(line)
                if parsed:
                    combos.append(parsed)

    except FileNotFoundError:
        print(f"Combo file not found: {file_path}")
    except Exception as e:
        print(f"Error loading combos: {e}")

    return combos


def parse_combo(line: str) -> Optional[Tuple[str, str]]:
    """
    Parse a combo line into email and password

    Supported formats:
    - email:password
    - email;password

    Args:
        line: Combo line to parse

    Returns:
        (email, password) tuple or None if invalid
    """
    # Try different separators
    for separator in [':', ';', '|']:
        if separator in line:
            parts = line.split(separator, 1)
            if len(parts) == 2:
                email = parts[0].strip()
                password = parts[1].strip()

                # Basic validation
                if email and password and '@' in email:
                    return (email, password)

    return None


def save_result(file_path: str, content: str):
    """
    Save result to file

    Args:
        file_path: Path to output file
        content: Content to save
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content + '\n')
    except Exception as e:
        print(f"Error saving result: {e}")


def get_results_file(status: str, output_dir: str = ".") -> str:
    """
    Get the path to a results file

    Args:
        status: Account status (valid, invalid, locked, challenge, error)
        output_dir: Output directory

    Returns:
        Path to the results file
    """
    # Map status to filename
    file_mapping = {
        "valid": "hits.txt",
        "invalid": "invalid.txt",
        "locked": "locked.txt",
        "challenge": "errors.txt",  # Save challenges with errors
        "error": "errors.txt"
    }

    filename = file_mapping.get(status, "errors.txt")
    return os.path.join(output_dir, filename)


def ensure_directory(path: str):
    """Ensure a directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)


def format_combo(email: str, password: str) -> str:
    """Format combo for output"""
    return f"{email}:{password}"


def read_file_lines(file_path: str) -> List[str]:
    """Read lines from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
