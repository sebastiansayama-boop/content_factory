from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .runtime import ExecutionResult, PublicationResult, WorkItem


@dataclass(frozen=True)
class GitHubContentsConfig:
    owner: str
    repo: str
    path: str
    token_env: str = "GITHUB_TOKEN"
    api_endpoint: str = "https://api.github.com"
    branch: str = "main"


class GitHubContentsPublisher:
    """Bounded publisher for Experiment-001: one mutation, no retry."""

    def __init__(self, config: GitHubContentsConfig) -> None:
        self.config = config
        if not os.getenv(config.token_env):
            raise ValueError(f"missing GitHub token: {config.token_env}")
        if not config.path.strip():
            raise ValueError("GitHub target path must not be empty")

    @property
    def target(self) -> str:
        return f"github://{self.config.owner}/{self.config.repo}/{self.config.path}"

    def publish(self, work_item: WorkItem, execution: ExecutionResult) -> PublicationResult:
        if not isinstance(execution.payload, str):
            raise ValueError("GitHub publication payload must be UTF-8 text")
        payload = {
            "message": f"factory: publish {work_item.work_item_id}",
            "content": base64.b64encode(execution.payload.encode()).decode(),
            "branch": self.config.branch,
        }
        body = self._request(
            "PUT",
            f"/repos/{self.config.owner}/{self.config.repo}/contents/{self.config.path}",
            payload,
        )
        commit = body.get("commit", {})
        content = body.get("content", {})
        commit_sha = commit.get("sha") if isinstance(commit, dict) else None
        blob_sha = content.get("sha") if isinstance(content, dict) else None
        if not isinstance(commit_sha, str) or not commit_sha:
            raise ValueError("GitHub response did not contain commit SHA")
        evidence = [f"github:commit:{commit_sha}"]
        if isinstance(blob_sha, str) and blob_sha:
            evidence.append(f"github:blob:{blob_sha}")
        return PublicationResult(
            publication_id=f"github-commit:{commit_sha}",
            output_revision_id=execution.output_revision_id,
            target=self.target,
            externally_observable=True,
            evidence_refs=tuple(evidence),
        )

    def reconcile(self) -> dict[str, object]:
        body = self._request(
            "GET",
            f"/repos/{self.config.owner}/{self.config.repo}/contents/{self.config.path}?ref={self.config.branch}",
            None,
        )
        encoded = body.get("content", "")
        if not isinstance(encoded, str):
            raise ValueError("GitHub reconciliation content is invalid")
        content = base64.b64decode(encoded.replace("\n", "")).decode("utf-8") if encoded else ""
        return {
            "exists": True,
            "path": body.get("path"),
            "blob_sha": body.get("sha"),
            "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "content": content,
        }

    def _request(self, method: str, path: str, payload: dict[str, object] | None) -> dict[str, object]:
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(
            f"{self.config.api_endpoint}{path}",
            data=data,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {os.environ[self.config.token_env]}",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
            method=method,
        )
        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read().decode()
                result = json.loads(raw) if raw else {}
                if not isinstance(result, dict):
                    raise ValueError("GitHub response must be an object")
                return result
        except HTTPError as exc:
            if method == "GET" and exc.code == 404:
                return {"exists": False}
            raise RuntimeError(f"GitHub {method} failed: HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"GitHub {method} connectivity failure") from exc
