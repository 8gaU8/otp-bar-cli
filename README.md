# OTP Cli ツール

## Requirements
- oathtool
- Python >= 3.11

## Configuration


```toml
[tokens.user1]
secret = "SECRET1"
priority = 1

[tokens.user2]
secret = "SECRET2"
```

## Installation

```console
$ curl https://raw.githubusercontent.com/8gaU8/otp-bar-cli/refs/heads/main/otp-cli.py > ~/.local/bin/otp-cli.py
$ chmod +x ~/.local/bin/otp-cli.py
$ otp-cli.py
123456: user1
654123: user2

```
