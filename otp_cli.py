import tomllib
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Any


@dataclass
class OTPConfig:
    secret: str
    priority: int | None = None


def parse_config(data: dict[str, Any]) -> dict[str, OTPConfig]:
    config_dict: dict[str, OTPConfig] = {}
    for user, config in data["tokens"].items():
        config_dict[user] = OTPConfig(**config)
    return config_dict


def load_config(path: Path) -> dict[str, OTPConfig]:
    with open(path, mode="rb") as toml_file:
        data = tomllib.load(toml_file)
    return parse_config(data)


def get_token(secret: str) -> str:
    p = Popen(["oathtool", "--totp", "-b", secret], stdout=PIPE, stderr=PIPE)
    p.wait()
    if p.returncode != 0:
        # 以上終了
        output = (
            p.stderr.read().decode("utf-8") if p.stderr is not None else "Unknown error"
        )
        raise RuntimeError(f"oathtool failed with error: {output}")
    if p.stdout is None:
        # 正常終了だが出力がない場合
        raise RuntimeError("oathtool did not produce any output")

    token = p.stdout.read().decode("utf-8").strip()
    return token


def main():

    CONFIG_PATH = Path("~/.config/otp-bar/config.toml").expanduser()
    toml_data = load_config(CONFIG_PATH)

    for user, data in toml_data.items():
        user = user.strip()
        token = get_token(data.secret)

        print(f"{token}: {user}")


if __name__ == "__main__":
    main()
