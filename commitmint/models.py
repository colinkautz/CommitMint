from enum import Enum
from pydantic import BaseModel, Field
from typing import List


class ChangeType(str, Enum):
    FEATURE = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    STYLE = "style"
    TEST = "test"
    CHORE = "chore"
    PERF = "perf"


class FileDiff(BaseModel):
    path: str
    additions: int
    deletions: int
    changes_summary: str


class DiffAnalysis(BaseModel):
    files_changed: List[FileDiff]
    total_additions: int
    total_deletions: int
    change_summary: str


class CommitMessage(BaseModel):
    type: ChangeType
    scope: str | None = None
    subject: str = Field(..., max_length=100)
    body: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)

    def format(self, include_body: bool = True) -> str:
        scope_str = f"({self.scope})" if self.scope else ""
        msg = f"{self.type.value}{scope_str}: {self.subject}"
        if include_body and self.body:
            msg += f"\n\n{self.body}"
        return msg


class CommitOptions(BaseModel):
    options: List[CommitMessage] = Field(min_length=1, max_length=5)