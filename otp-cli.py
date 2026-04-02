#!/usr/bin/env python3


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


def main():
    # CONFIG_PATHは必要に応じて書き換え
    CONFIG_PATH = Path("~/.config/otp-bar/config.toml").expanduser()
    config_data = load_config(CONFIG_PATH)

    for data in config_data:
        token = get_token(data.secret)
        print(f"{token}: {data.account}")


if __name__ == "__main__":
    main()
