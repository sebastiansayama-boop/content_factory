import json
from pathlib import Path
from content_factory.scope_expansion_qc import assess_scope_expansion, assess_scopes, summarize_scope_assessments

def ev(evidence_id="e1", excerpt="Некоторые игры на PC распространялись цифровым способом."):
    return {"id":evidence_id,"source_id":"s1","excerpt":excerpt}

def test_subset_to_industry_is_blocked():
    a=assess_scope_expansion({"id":"c1","text":"Игровая индустрия перешла к цифровой дистрибуции.","evidence_ids":["e1"]},evidence_items=[{**ev(),"scope_spec":{"population":"game","coverage":"subset","quantifier":"some","segment":["pc"]}}])
    assert a.verdict=="FAIL"
    assert a.repair_action=="WEAKEN_SCOPE"
    assert any(x["axis"] in {"population","coverage","quantifier"} for x in a.expansions)

def test_bounded_claim_matches_subset_evidence():
    a=assess_scope_expansion({"id":"c2","text":"Некоторые игры на PC распространялись цифровым способом.","evidence_ids":["e1"]},evidence_items=[ev()])
    assert a.verdict=="PASS"

def test_structured_scope_catches_platform_expansion():
    a=assess_scope_expansion({"id":"c3","text":"Игры распространялись на PC и консолях.","scope_spec":{"population":"game","coverage":"segment","quantifier":"some","segment":["pc","console"]},"evidence_ids":["e1"]},evidence_items=[{**ev(),"scope_spec":{"population":"game","coverage":"segment","quantifier":"some","segment":["pc"]}}])
    assert a.verdict=="REVIEW"
    assert any(x["axis"]=="segment" for x in a.expansions)

def test_series_calibration_current_library():
    root=Path(__file__).resolve().parents[1]
    library=json.loads((root/"library/telegram/computer-games-series.json").read_text(encoding="utf-8"))
    claims=[]; evidence=[]
    for episode in library["episodes"]:
        claims.extend(episode.get("claims",[])); evidence.extend(episode.get("evidence",[]))
    assessments=assess_scopes(claims,evidence_items=evidence)
    summary=summarize_scope_assessments(assessments)
    print("\n=== SCOPE EXPANSION QC CALIBRATION ===")
    print(json.dumps(summary,ensure_ascii=False))
    for item in assessments:
        if item.verdict!="PASS": print(json.dumps(item.to_dict(),ensure_ascii=False))
    assert summary["claims"]==51
