#!/usr/bin/env python3
"""Create the mini-swe-agent global Groq config .env file.

This script writes the Groq API key and default model settings into the user-level
mini-swe-agent config directory so mini-swe-agent can load them automatically.
"""

import argparse
import getpass
import os
import platform
import re
import sys
from pathlib import Path

import platformdirs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update the mini-swe-agent global .env file for Groq."
    )
    parser.add_argument(
        "groq_api_key",
        nargs="?",
        help="Your Groq API key (starts with gsk_). If omitted, the script asks for it interactively.",
    )
    return parser.parse_args()


def validate_api_key(key: str) -> bool:
    return bool(re.fullmatch(r"gsk_[A-Za-z0-9_-]{16,}", key))


def get_config_dir() -> Path:
    override = os.getenv("MSWEA_GLOBAL_CONFIG_DIR")
    if override:
        return Path(override).expanduser().resolve()

    system_name = platform.system()
    if system_name == "Windows":
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / "mini-swe-agent"
        return Path(platformdirs.user_config_dir("mini-swe-agent"))
    if system_name == "Darwin":
        return Path.home() / "Library" / "Application Support" / "mini-swe-agent"
    return Path.home() / ".config" / "mini-swe-agent"


def read_existing_file(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except PermissionError:
        raise


def mask_api_key(key: str) -> str:
    return f"{key[:7]}..." if key else ""


def confirm_overwrite(path: Path) -> bool:
    while True:
        answer = input(f"The file {path} already exists. Overwrite? [y/N]: ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no", ""}:
            return False
        print("Please answer y or n.")


def write_env_file(path: Path, key: str, model_name: str) -> None:
    contents = (
        f"GROQ_API_KEY={key}\n"
        f"MSWEA_MODEL_NAME={model_name}\n"
        f"MSWEA_MODEL_API_KEY={key}\n"
    )
    path.write_text(contents, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    api_key = args.groq_api_key
    if not api_key:
        api_key = getpass.getpass("Enter your Groq API key: ").strip()

    if not validate_api_key(api_key):
        print("ERROR: Invalid Groq API key format. It must start with gsk_ and be at least 20 characters.")
        return 1

    config_dir = get_config_dir()
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        print(f"ERROR: Cannot create config directory {config_dir}: {exc}")
        return 1

    env_path = config_dir / ".env"
    existing = read_existing_file(env_path)
    if existing is not None and not confirm_overwrite(env_path):
        print("Aborted without changing the existing .env file.")
        return 0

    try:
        write_env_file(env_path, api_key, "groq/llama-3.3-70b-versatile")
    except PermissionError as exc:
        print(f"ERROR: Cannot write .env file to {env_path}: {exc}")
        return 1

    print("\nCreated or updated mini-swe-agent global config file successfully.")
    print(f"Config directory: {config_dir}")
    print(f"Config file: {env_path}")
    print("\nMasked file contents:")
    print(f"GROQ_API_KEY={mask_api_key(api_key)}")
    print("MSWEA_MODEL_NAME=groq/llama-3.3-70b-versatile")
    print(f"MSWEA_MODEL_API_KEY={mask_api_key(api_key)}")
    print("\nVerification commands:")
    print("  python -m minisweagent --help")
    print("  python -m minisweagent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
