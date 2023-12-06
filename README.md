# Ruff2BitBucket

[ruff](https://docs.astral.sh/ruff/) is an extremely fast Python linter and code formatter, written in Rust.

[BitBucket](https://bitbucket.org/) is an Atlassian product which provides a visual git interface (basically).

With ruff2bitbucket you can run your ruff-validations and upload them as a code insight directly into BitBucket.

## Installation
```shell
pip install ruff2bitbucket
```

## Usage
Change your directory to where the configuration file is stored and run:
```shell
ruff2bitbucket [--user ...] [--pass ...]
```

⚠ It's important that you are in the right directory!

## Configuration
You should refer to the [ruff configuration docs](https://docs.astral.sh/ruff/configuration/) on how to modify your `pyproject.toml` (or `ruff.toml`, or `.ruff.toml`) in order to provide more extensive checks.

## Security
If no user or pass is passed, the environment variables are scanned for anything that looks like `USER`/`USR` and `PASS`/`PW`. When a match is found, this'll be used to attach the annotations to the current commit hash.
