from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class InformationFlowError(ValueError):
    """Raised when the semantic production graph is incomplete or inconsistent."""


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    url: str


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_id: str
    excerpt: str
    locator: str


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    confidence: str
    source_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    scope: str
    known_unknowns: tuple[str, ...]


@dataclass(frozen=True)
class EditorialPoint:
    point_id: str
    text: str
    claim_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class ContentElement:
    element_id: str
    kind: str
    artifact_id: str
    editorial_point_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    format: str
    content_element_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class PublicationRecord:
    publication_id: str
    artifact_ids: tuple[str, ...]
    channel: str
    status: str


@dataclass(frozen=True)
class LineageEdge:
    from_id: str
    to_id: str
    relation: str


@dataclass(frozen=True)
class InformationFlow:
    """Canonical semantic graph for one content run.

    This is deliberately separate from provider execution. It answers
    "where did this artifact come from?" while runtime traces answer
    "what actually happened while producing it?"
    """

    run_id: str
    sources: tuple[Source, ...]
    evidence: tuple[Evidence, ...]
    claims: tuple[Claim, ...]
    editorial_points: tuple[EditorialPoint, ...]
    content_elements: tuple[ContentElement, ...]
    artifacts: tuple[Artifact, ...]
    publications: tuple[PublicationRecord, ...]
    edges: tuple[LineageEdge, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "sources": [asdict(item) for item in self.sources],
            "evidence": [asdict(item) for item in self.evidence],
            "claims": [asdict(item) for item in self.claims],
            "editorial_points": [asdict(item) for item in self.editorial_points],
            "content_elements": [asdict(item) for item in self.content_elements],
            "artifacts": [asdict(item) for item in self.artifacts],
            "publications": [asdict(item) for item in self.publications],
            "edges": [asdict(item) for item in self.edges],
            # Stable summary fields keep the serialized contract convenient for
            # API consumers while the typed collections remain the source of truth.
            "source_count": len(self.sources),
            "evidence_count": len(self.evidence),
            "claim_count": len(self.claims),
            "editorial_point_count": len(self.editorial_points),
            "content_element_count": len(self.content_elements),
            "artifact_count": len(self.artifacts),
            "publication_count": len(self.publications),
            "edge_count": len(self.edges),
        }


def build_information_flow(
    *,
    run_id: str,
    research: dict[str, Any],
    package: dict[str, Any],
) -> InformationFlow:
    sources = _sources(research)
    evidence = _evidence(research)
    claims = _claims(research)
    claim_by_id = {item.claim_id: item for item in claims}
    evidence_by_id = {item.evidence_id: item for item in evidence}
    source_by_id = {item.source_id: item for item in sources}
    source_ids = set(source_by_id)
    evidence_ids = set(evidence_by_id)
    for claim in claims:
        if not set(claim.source_ids).issubset(source_ids):
            raise InformationFlowError(
                f"claim {claim.claim_id} references unknown source"
            )
        if not set(claim.evidence_ids).issubset(evidence_ids):
            raise InformationFlowError(
                f"claim {claim.claim_id} references unknown evidence"
            )

    editorial_points: list[EditorialPoint] = []
    content_elements: list[ContentElement] = []
    artifacts: list[Artifact] = []
    edges: list[LineageEdge] = []

    story = package.get("story")
    brief = package.get("content_brief")
    if not isinstance(story, dict):
        raise InformationFlowError("production package must contain a story")
    story_id = str(story.get("id") or "").strip()
    if not story_id:
        raise InformationFlowError("production story requires id")

    if not isinstance(brief, dict):
        raise InformationFlowError("production package must contain an explicit content_brief")
    brief_id = str(brief.get("brief_id") or "").strip()
    if not brief_id:
        raise InformationFlowError("content_brief requires brief_id")

    selected_claim_ids = tuple(
        str(ref).strip()
        for ref in brief.get("selected_claim_refs", [])
        if isinstance(ref, str) and ref.strip()
    )
    if not selected_claim_ids:
        raise InformationFlowError("content_brief must select claims")
    if not set(selected_claim_ids).issubset(claim_by_id):
        raise InformationFlowError("content_brief references unknown claim")

    brief_points = brief.get("editorial_points")
    brief_elements = brief.get("content_elements")
    if not isinstance(brief_points, list) or not brief_points:
        raise InformationFlowError("content_brief must contain editorial_points")
    if not isinstance(brief_elements, list) or not brief_elements:
        raise InformationFlowError("content_brief must contain content_elements")

    point_by_id: dict[str, EditorialPoint] = {}
    for raw in brief_points:
        if not isinstance(raw, dict):
            raise InformationFlowError("content_brief editorial point must be an object")
        point_id = str(raw.get("point_id") or "").strip()
        point_claims = tuple(
            dict.fromkeys(ref for ref in raw.get("claim_refs", []) if isinstance(ref, str) and ref.strip())
        )
        point_evidence = tuple(
            dict.fromkeys(ref for ref in raw.get("evidence_refs", []) if isinstance(ref, str) and ref.strip())
        )
        if not point_id or not point_claims or not point_evidence:
            raise InformationFlowError("editorial point requires id, claims and evidence")
        if not set(point_claims).issubset(claim_by_id):
            raise InformationFlowError(f"editorial point {point_id} references unknown claim")
        if not set(point_evidence).issubset(evidence_by_id):
            raise InformationFlowError(f"editorial point {point_id} references unknown evidence")
        point = EditorialPoint(
            point_id=f"{run_id}:editorial:{point_id}",
            text=str(raw.get("text") or "").strip(),
            claim_ids=point_claims,
            evidence_ids=point_evidence,
        )
        if not point.text:
            raise InformationFlowError(f"editorial point {point_id} requires text")
        point_by_id[point_id] = point
        editorial_points.append(point)
        for claim_id in point_claims:
            edges.append(LineageEdge(claim_id, point.point_id, "claim_to_editorial_point"))
        for evidence_id in point_evidence:
            edges.append(LineageEdge(evidence_id, point.point_id, "evidence_to_editorial_point"))

    element_by_id: dict[str, ContentElement] = {}
    for raw in brief_elements:
        if not isinstance(raw, dict):
            raise InformationFlowError("content_brief content element must be an object")
        element_id = str(raw.get("element_id") or "").strip()
        point_refs = tuple(
            dict.fromkeys(ref for ref in raw.get("editorial_point_ids", []) if isinstance(ref, str) and ref.strip())
        )
        element_claims = tuple(
            dict.fromkeys(ref for ref in raw.get("claim_refs", []) if isinstance(ref, str) and ref.strip())
        )
        element_evidence = tuple(
            dict.fromkeys(ref for ref in raw.get("evidence_refs", []) if isinstance(ref, str) and ref.strip())
        )
        if not element_id or not point_refs or not element_claims or not element_evidence:
            raise InformationFlowError("content element requires id, editorial points, claims and evidence")
        if not set(point_refs).issubset(point_by_id):
            raise InformationFlowError(f"content element {element_id} references unknown editorial point")
        if not set(element_claims).issubset(claim_by_id):
            raise InformationFlowError(f"content element {element_id} references unknown claim")
        if not set(element_evidence).issubset(evidence_by_id):
            raise InformationFlowError(f"content element {element_id} references unknown evidence")
        element = ContentElement(
            element_id=f"{run_id}:element:{element_id}",
            kind=str(raw.get("kind") or "").strip(),
            artifact_id="",
            editorial_point_ids=tuple(point_by_id[ref].point_id for ref in point_refs),
            claim_ids=element_claims,
            evidence_ids=element_evidence,
        )
        if not element.kind:
            raise InformationFlowError(f"content element {element_id} requires kind")
        element_by_id[element_id] = element
        content_elements.append(element)
        for point_id in element.editorial_point_ids:
            edges.append(LineageEdge(point_id, element.element_id, "editorial_point_to_content_element"))
        for claim_id in element_claims:
            edges.append(LineageEdge(claim_id, element.element_id, "claim_to_content_element"))
        for evidence_id in element_evidence:
            edges.append(LineageEdge(evidence_id, element.element_id, "evidence_to_content_element"))

    for asset in package.get("package", []):
        if not isinstance(asset, dict):
            raise InformationFlowError("every production asset must be an object")
        artifact_id = str(asset.get("id") or "").strip()
        fmt = str(asset.get("format") or "").strip()
        if not artifact_id or not fmt:
            raise InformationFlowError("every production asset requires id and format")

        claim_ids = tuple(dict.fromkeys(ref for ref in asset.get("claim_refs", []) if isinstance(ref, str) and ref.strip()))
        evidence_ids = tuple(dict.fromkeys(ref for ref in asset.get("evidence_refs", []) if isinstance(ref, str) and ref.strip()))
        element_refs = tuple(dict.fromkeys(ref for ref in asset.get("content_element_ids", []) if isinstance(ref, str) and ref.strip()))
        if not element_refs:
            raise InformationFlowError(f"artifact {artifact_id} must expose content_element_ids")
        if not set(element_refs).issubset(element_by_id):
            raise InformationFlowError(f"artifact {artifact_id} references unknown content element")
        for claim_id in claim_ids:
            if claim_id not in claim_by_id:
                raise InformationFlowError(f"artifact {artifact_id} references unknown claim")
            claim = claim_by_id[claim_id]
            if not evidence_ids:
                raise InformationFlowError(f"artifact {artifact_id} with claim refs must expose evidence_refs")
            if not set(claim.evidence_ids).issubset(evidence_ids):
                raise InformationFlowError(f"artifact {artifact_id} claim {claim_id} is not supported by artifact evidence")
        for evidence_id in evidence_ids:
            if evidence_id not in evidence_by_id:
                raise InformationFlowError(f"artifact {artifact_id} references unknown evidence")

        resolved_element_ids = tuple(f"{run_id}:element:{ref}" for ref in element_refs)
        artifacts.append(Artifact(
            artifact_id=artifact_id,
            format=fmt,
            content_element_ids=resolved_element_ids,
            claim_ids=claim_ids,
            evidence_ids=evidence_ids,
        ))
        for element_id in resolved_element_ids:
            edges.append(LineageEdge(element_id, artifact_id, "content_element_to_artifact"))
        for claim_id in claim_ids:
            edges.append(LineageEdge(claim_id, artifact_id, "claim_to_artifact"))
        for evidence_id in evidence_ids:
            edges.append(LineageEdge(evidence_id, artifact_id, "evidence_to_artifact"))

    for element in content_elements:
        linked_artifact = next(
            (artifact.artifact_id for artifact in artifacts if element.element_id in artifact.content_element_ids),
            None,
        )
        if linked_artifact:
            index = content_elements.index(element)
            content_elements[index] = ContentElement(
                **{**element.__dict__, "artifact_id": linked_artifact}
            )

    for source in sources:
        for evidence_item in evidence:
            if evidence_item.source_id == source.source_id:
                edges.append(LineageEdge(source.source_id, evidence_item.evidence_id, "source_to_evidence"))
    for claim in claims:
        for source_id in claim.source_ids:
            edges.append(LineageEdge(source_id, claim.claim_id, "source_to_claim"))
        for evidence_id in claim.evidence_ids:
            edges.append(LineageEdge(evidence_id, claim.claim_id, "evidence_to_claim"))
    for artifact in artifacts:
        for claim_id in artifact.claim_ids:
            edges.append(LineageEdge(claim_id, artifact.artifact_id, "claim_to_artifact"))
        for evidence_id in artifact.evidence_ids:
            edges.append(LineageEdge(evidence_id, artifact.artifact_id, "evidence_to_artifact"))

    flow = InformationFlow(
        run_id=run_id,
        sources=sources,
        evidence=evidence,
        claims=claims,
        editorial_points=tuple(editorial_points),
        content_elements=tuple(content_elements),
        artifacts=tuple(artifacts),
        publications=(),
        edges=tuple(_dedupe_edges(edges)),
    )
    validate_information_flow(flow)
    return flow


def attach_publication(
    flow: dict[str, Any],
    *,
    publication_id: str,
    artifact_ids: list[str] | tuple[str, ...],
    channel: str,
    status: str,
) -> dict[str, Any]:
    publication_id = str(publication_id).strip()
    channel = str(channel).strip()
    status = str(status).strip()
    if not publication_id or not channel or not status:
        raise InformationFlowError("publication requires id, channel and status")
    artifact_ids = tuple(dict.fromkeys(str(ref).strip() for ref in artifact_ids if str(ref).strip()))
    existing_artifacts = {
        str(item.get("artifact_id"))
        for item in flow.get("artifacts", [])
        if isinstance(item, dict) and str(item.get("artifact_id") or "").strip()
    }
    if not artifact_ids or not set(artifact_ids).issubset(existing_artifacts):
        raise InformationFlowError("publication must reference existing artifacts")
    publications = [
        dict(item)
        for item in flow.get("publications", [])
        if isinstance(item, dict) and str(item.get("publication_id") or "") != publication_id
    ]
    publications.append({
        "publication_id": publication_id,
        "artifact_ids": list(artifact_ids),
        "channel": channel,
        "status": status,
    })
    edges = [
        dict(edge)
        for edge in flow.get("edges", [])
        if not (
            str(edge.get("to_id") or "") == publication_id
            and str(edge.get("relation") or "") == "artifact_to_publication"
        )
    ]
    edges.extend({
        "from_id": artifact_id,
        "to_id": publication_id,
        "relation": "artifact_to_publication",
    } for artifact_id in artifact_ids)
    updated = {**flow, "publications": publications, "edges": edges}
    validate_information_flow_dict(updated)
    return updated


def validate_information_flow_dict(flow: dict[str, Any]) -> None:
    publications = flow.get("publications", [])
    artifacts = {
        str(item.get("artifact_id"))
        for item in flow.get("artifacts", [])
        if isinstance(item, dict)
    }
    ids = {
        str(item.get(key))
        for key in ("source_id", "evidence_id", "claim_id", "point_id", "element_id", "artifact_id", "publication_id")
        for item in (
            flow.get("sources", [])
            + flow.get("evidence", [])
            + flow.get("claims", [])
            + flow.get("editorial_points", [])
            + flow.get("content_elements", [])
            + flow.get("artifacts", [])
            + publications
        )
        if isinstance(item, dict) and str(item.get(key) or "").strip()
    }
    for publication in publications:
        if not isinstance(publication, dict):
            raise InformationFlowError("publication must be an object")
        refs = publication.get("artifact_ids")
        if not publication.get("publication_id") or not publication.get("channel") or not publication.get("status"):
            raise InformationFlowError("publication requires id, channel and status")
        if not isinstance(refs, list) or not refs or not set(refs).issubset(artifacts):
            raise InformationFlowError("publication references unknown artifact")
    for edge in flow.get("edges", []):
        if not isinstance(edge, dict):
            raise InformationFlowError("lineage edge must be an object")
        if edge.get("from_id") not in ids or edge.get("to_id") not in ids:
            raise InformationFlowError("publication lineage edge references unknown object")
        if edge.get("relation") == "artifact_to_publication" and edge.get("from_id") not in artifacts:
            raise InformationFlowError("artifact_to_publication must originate from an artifact")


def validate_information_flow(flow: InformationFlow) -> None:
    ids: set[str] = set()
    for collection in (
        flow.sources,
        flow.evidence,
        flow.claims,
        flow.editorial_points,
        flow.content_elements,
        flow.artifacts,
        flow.publications,
    ):
        for item in collection:
            item_id = _item_id(item)
            if not item_id:
                raise InformationFlowError("graph contains an object without an id")
            if item_id in ids:
                raise InformationFlowError(f"duplicate graph id: {item_id}")
            ids.add(item_id)

    source_ids = {item.source_id for item in flow.sources}
    evidence_ids = {item.evidence_id for item in flow.evidence}
    claim_ids = {item.claim_id for item in flow.claims}
    point_ids = {item.point_id for item in flow.editorial_points}
    element_ids = {item.element_id for item in flow.content_elements}
    artifact_ids = {item.artifact_id for item in flow.artifacts}

    for item in flow.evidence:
        if item.source_id not in source_ids:
            raise InformationFlowError(f"evidence {item.evidence_id} references unknown source")

    for item in flow.claims:
        if not item.source_ids or not item.evidence_ids:
            raise InformationFlowError(f"claim {item.claim_id} must have source and evidence")
        if not set(item.source_ids).issubset(source_ids):
            raise InformationFlowError(f"claim {item.claim_id} references unknown source")
        if not set(item.evidence_ids).issubset(evidence_ids):
            raise InformationFlowError(f"claim {item.claim_id} references unknown evidence")

    for item in flow.editorial_points:
        if not item.claim_ids:
            raise InformationFlowError(f"editorial point {item.point_id} has no claims")
        if not set(item.claim_ids).issubset(claim_ids):
            raise InformationFlowError(f"editorial point {item.point_id} references unknown claim")
        if not set(item.evidence_ids).issubset(evidence_ids):
            raise InformationFlowError(f"editorial point {item.point_id} references unknown evidence")

    for item in flow.content_elements:
        if not item.editorial_point_ids:
            raise InformationFlowError(f"content element {item.element_id} has no editorial point")
        if not set(item.editorial_point_ids).issubset(point_ids):
            raise InformationFlowError(f"content element {item.element_id} references unknown editorial point")
        if not set(item.claim_ids).issubset(claim_ids):
            raise InformationFlowError(f"content element {item.element_id} references unknown claim")
        if not set(item.evidence_ids).issubset(evidence_ids):
            raise InformationFlowError(f"content element {item.element_id} references unknown evidence")

    for item in flow.artifacts:
        if not item.content_element_ids:
            raise InformationFlowError(f"artifact {item.artifact_id} has no content element")
        if not set(item.content_element_ids).issubset(element_ids):
            raise InformationFlowError(f"artifact {item.artifact_id} references unknown content element")
        if not set(item.claim_ids).issubset(claim_ids):
            raise InformationFlowError(f"artifact {item.artifact_id} references unknown claim")
        if not set(item.evidence_ids).issubset(evidence_ids):
            raise InformationFlowError(f"artifact {item.artifact_id} references unknown evidence")

    valid_relations = {
        "source_to_evidence",
        "source_to_claim",
        "evidence_to_claim",
        "claim_to_editorial_point",
        "evidence_to_editorial_point",
        "editorial_point_to_content_element",
        "claim_to_content_element",
        "evidence_to_content_element",
        "content_element_to_artifact",
        "claim_to_artifact",
        "evidence_to_artifact",
        "artifact_to_publication",
    }
    for edge in flow.edges:
        if edge.from_id not in ids or edge.to_id not in ids:
            raise InformationFlowError(
                f"lineage edge references unknown object: {edge.from_id} -> {edge.to_id}"
            )
        if edge.relation not in valid_relations:
            raise InformationFlowError(f"unknown lineage relation: {edge.relation}")


def _sources(research: dict[str, Any]) -> tuple[Source, ...]:
    result = []
    for item in research.get("sources", []):
        if not isinstance(item, dict):
            raise InformationFlowError("research source must be an object")
        source_id = str(item.get("id") or "").strip()
        title = str(item.get("title") or "").strip()
        url = str(item.get("url") or "").strip()
        if not source_id or not title or not url:
            raise InformationFlowError("source requires id, title and url")
        result.append(Source(source_id, title, url))
    return tuple(result)


def _evidence(research: dict[str, Any]) -> tuple[Evidence, ...]:
    result = []
    for item in research.get("evidence", []):
        if not isinstance(item, dict):
            raise InformationFlowError("research evidence must be an object")
        values = (
            str(item.get("id") or "").strip(),
            str(item.get("source_id") or "").strip(),
            str(item.get("excerpt") or "").strip(),
            str(item.get("locator") or "").strip(),
        )
        if not values[0] or not values[1] or not values[2]:
            raise InformationFlowError("evidence requires id, source_id and excerpt")
        result.append(Evidence(*values))
    return tuple(result)


def _claims(research: dict[str, Any]) -> tuple[Claim, ...]:
    result = []
    for item in research.get("claims", []):
        if not isinstance(item, dict):
            raise InformationFlowError("research claim must be an object")
        claim_id = str(item.get("id") or "").strip()
        text = str(item.get("text") or "").strip()
        confidence = str(item.get("confidence") or "").strip().lower()
        source_ids = tuple(
            ref for ref in item.get("source_ids", [])
            if isinstance(ref, str) and ref.strip()
        )
        evidence_ids = tuple(
            ref for ref in item.get("evidence_ids", [])
            if isinstance(ref, str) and ref.strip()
        )
        unknowns = tuple(
            value for value in item.get("known_unknowns", [])
            if isinstance(value, str)
        )
        if not claim_id or not text or confidence not in {"high", "medium", "low"}:
            raise InformationFlowError("claim requires id, text and valid confidence")
        result.append(
            Claim(
                claim_id,
                text,
                confidence,
                source_ids,
                evidence_ids,
                str(item.get("scope") or "").strip(),
                unknowns,
            )
        )
    if not result:
        raise InformationFlowError("research must contain claims")
    return tuple(result)


def _item_id(item: object) -> str:
    if isinstance(item, Source):
        return item.source_id
    if isinstance(item, Evidence):
        return item.evidence_id
    if isinstance(item, Claim):
        return item.claim_id
    if isinstance(item, EditorialPoint):
        return item.point_id
    if isinstance(item, ContentElement):
        return item.element_id
    if isinstance(item, Artifact):
        return item.artifact_id
    if isinstance(item, PublicationRecord):
        return item.publication_id
    return ""


def _dedupe_edges(edges: list[LineageEdge]) -> list[LineageEdge]:
    seen: set[tuple[str, str, str]] = set()
    result = []
    for edge in edges:
        key = (edge.from_id, edge.to_id, edge.relation)
        if key not in seen:
            seen.add(key)
            result.append(edge)
    return result
