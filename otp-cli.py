#!/usr/bin/env python3


import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, Popen


@dataclass
class OTPConfig:
    """OTPの設定(アカウント、シークレット、優先度)を表すクラス"""

    account: str
    secret: str
    priority: int | None = None


def load_config(path: Path) -> list[OTPConfig]:
    """config.tomlを読み取りパースする

    Args:
        path (Path): config.tomlのパス

    Returns:
        list[OTPConfig]: パースされたOTP設定のリスト
    """
    with open(path, mode="rb") as toml_file:
        data = tomllib.load(toml_file)

    config_list: list[OTPConfig] = []
    for account, config in data["tokens"].items():
        account = account.strip()
        secret = config["secret"].strip()
        priority = config.get("priority", None)

        config_list.append(
            OTPConfig(
                account=account,
                secret=secret,
                priority=priority,
            )
        )
    return config_list


def get_token(secret: str) -> str:
    """secretからOTPを生成する。oathtoolコマンドが必要

    Args:
        secret (str): OTPのシークレットキー

    Raises:
        RuntimeError: oathoolが利用できない場合

    Returns:
        str: 生成されたOTPトークン
    """

    # oathtoolを使用してTOTPトークンを生成する

    p = Popen(["oathtool", "--totp", "-b", secret], stdout=PIPE, stderr=PIPE)
    p.wait()

    # oathtoolの異常確認
    if p.returncode != 0:
        # 異常終了
        if p.stderr is not None:
            output = p.stderr.read().decode("utf-8")
        else:
            output = "Unknown error"
        raise RuntimeError(f"oathtool failed with error: {output}")
    if p.stdout is None:
        # 正常終了だが出力がない場合
        raise RuntimeError("oathtool did not produce any output")

    # 結果の取得
    token = p.stdout.read().decode("utf-8").strip()
    return token

def stderr(message: str) -> None:
    print(message, file=sys.stderr)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OTP CLI Tool")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("~/.config/otp-bar/config.toml").expanduser(),
        help="Path to the config.toml file (default: ~/.config/otp-bar/config.toml)",
    )
    parser.add_argument(
        "--account",
        "-a",
        type=str,
        help="Filter by account name (optional)",
    )
    parser.add_argument(
        "--clipboard",
        "-c",
        action="store_true",
        default=False,
        help="Copy the generated OTP to the clipboard (optional)",
    )

    return parser.parse_args()


def show_all(config_data: list[OTPConfig]) -> None:
    """全てのOTPトークンを表示する

    Args:
        config_data (list[OTPConfig]): OTP設定のリスト
    """
    for data in config_data:
        token = get_token(data.secret)
        print(f"{token}: {data.account}")


def filter_data(config_data: list[OTPConfig], account: str) -> list[OTPConfig]:
    """指定されたアカウントのOTPトークンを表示する

    Args:
        config_data (list[OTPConfig]): OTP設定のリスト
        account (str): フィルタリングするアカウント名
    """
    accounts = []
    for data in config_data:
        if account.lower() in data.account.lower():
            accounts.append(data)
    return accounts


def copy_to_clipboard(token: str) -> None:
    """OTPトークンをクリップボードにコピーする

    Args:
        token (str): コピーするOTPトークン
    """
    p = Popen(["pbcopy"], stdin=PIPE)
    p.communicate(input=token.encode("utf-8"))


def main() -> None:
    args = parse_args()
    # CONFIG_PATHは必要に応じて書き換え
    config_data = load_config(args.config)
    # filter by account if specified
    if args.account:
        config_data = filter_data(config_data, args.account)
    if not config_data:
        stderr("No matching accounts found.")
        return

    if args.clipboard:
        account = config_data[0]
        token = get_token(account.secret)
        copy_to_clipboard(token)
    show_all(config_data)


if __name__ == "__main__":
    main()
