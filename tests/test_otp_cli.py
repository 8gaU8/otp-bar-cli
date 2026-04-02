import importlib
from pathlib import Path

import pytest

module = importlib.import_module("otp-cli")


def test_load_config(tmp_path: Path) -> None:
    config_content = """
    [tokens.user1]
    secret = "SECRET1"
    priority = 1

    [tokens.user2]
    secret = "SECRET2"
"""
    config_path = tmp_path / "config.toml"
    config_path.write_text(config_content)
    expected = [
        module.OTPConfig(account="user1", secret="SECRET1", priority=1),
        module.OTPConfig(account="user2", secret="SECRET2", priority=None),
    ]
    assert module.load_config(config_path) == expected


def test_get_token() -> None:
    # ここではoathtoolがインストールされていることを前提としています。
    # テスト用のシークレットを使用して、トークンが正しく生成されるかを確認します。
    secret = "YOURTOKENHERE"  # "Hello!"のBase32エンコード
    token = module.get_token(secret)
    assert len(token) == 6, "TOKEN must be 6 digits long"
    assert token.isdigit(), "TOKEN must be numeric"


def test_get_token_invalid_secret() -> None:
    invalid_secret = "0"
    with pytest.raises(RuntimeError, match="oathtool failed with error:"):
        module.get_token(invalid_secret)


def test_tomlib_import() -> None:
    # tomllibが正しくインポートされているかを確認するテスト
    try:
        import tomllib  # noqa: F401
    except ImportError:
        pytest.fail(
            "tomllib could not be imported, ensure Python 3.11 or later is used"
        )
