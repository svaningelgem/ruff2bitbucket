import subprocess
from dataclasses import dataclass

__all__ = ["CapturedLine", "run"]


@dataclass
class CapturedLine:
    filename: str
    line: int = 0
    column: int = 0
    description: str = ""

    def __post_init__(self) -> None:
        self.filename = self.filename.strip()
        self.line = int(self.line)
        self.column = int(self.column)
        self.description = self.description.rstrip()


def run(*cmd: str, check: bool) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check)
