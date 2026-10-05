from __future__ import annotations
import re
from dataclasses import asdict, dataclass
from typing import Any, Literal

Verdict = Literal["PASS", "REVIEW", "FAIL"]
RepairAction = Literal["NONE", "WEAKEN_SCOPE", "NARROW_PERIOD"]

@dataclass(frozen=True)
class ScopeSpec:
    population: str
    coverage: int
    quantifier: str
    segment: tuple[str, ...]
    period_start: int | None
    period_end: int | None
    geography: tuple[str, ...]
    stage: tuple[str, ...]
    basis: str
    explicit: bool = False
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class ScopeExpansion:
    claim_id: str
    text: str
    claim_scope: ScopeSpec
    evidence_scope: ScopeSpec
    expansions: tuple[dict[str, Any], ...]
    scope_index: int
    verdict: Verdict
    repair_action: RepairAction
    reason: str
    def to_dict(self): return asdict(self)

COVERAGE = {"named_entity":0, "subset":1, "segment":2, "broad_population":3, "whole_domain":4}
POP = {"named_entity":0, "game":1, "game_segment":2, "game_population":3, "game_industry":4, "entertainment_industry":5, "domain":6}
POP_PATTERNS = (
    (r"\b(?:игров(?:ая|ой|ую)\s+индустри|индустрию)\b","game_industry",4),
    (r"\b(?:рынок|рынка|рынке)\s+(?:компьютерных|видеоигр|игр)\b","game_population",3),
    (r"\b(?:все|всех|вся|всей)\s+(?:игры|игр)\b","game_population",3),
    (r"\b(?:игр|игры|игра|видеоигр|компьютерн(?:ые|ых))\b","game",1),
)
QUANT = (
    ("all",(r"\bвсе\b",r"\bвсех\b",r"\bвся\b",r"\bвсей\b",r"\bкажд",r"\ball\b",r"\bevery\b")),
    ("many",(r"\bмногие\b",r"\bбольшинство\b",r"\bmany\b",r"\bmost\b")),
    ("some",(r"\bнекотор",r"\bчасть\b",r"\bотдельн",r"\bsome\b",r"\bselected\b")),
)
SEG = (("pc",(r"\bpc\b",r"\bперсональн(?:ых|ые)\s+компьютер",r"\bпк\b")),("console",(r"\bконсол",r"\bприставк")),("arcade",(r"\bаркад",r"\barcade\b")),("mobile",(r"\bмобильн",r"\bmobile\b")),("online",(r"\bсетев",r"\bonline\b")))
STAGE = (("distribution",(r"\bраспростран",r"\bдистрибуц",r"\bпродаж",r"\bdistribution\b")),("production",(r"\bразработ",r"\bсоздан",r"\bпроизводств",r"\bdevelopment\b")),("monetization",(r"\bмонетизац",r"\bfree-to-play",r"\bподписк")),("interaction",(r"\bсетев",r"\bигрок",r"\bmultiplayer\b",r"\bонлайн\b")))
GEO = (("global",(r"\bглобальн",r"\bво всем мире",r"\bпо всему миру",r"\bмиров",r"\bglobal\b")),("us",(r"\bсша\b",r"\bамерикан",r"\busa\b")),("japan",(r"\bяпон",r"\bjapan\b")),("europe",(r"\bевроп",r"\beurope\b")))
YEAR = re.compile(r"\b(?:1[0-9]{3}|20[0-9]{2})\b")

def fold(s): return " ".join(str(s or "").casefold().split())
def has(t,p): return any(re.search(x,t) for x in p)
def years(t):
    y=[int(x) for x in YEAR.findall(t)]
    return (min(y),max(y)) if y else (None,None)

def extract(text, basis="surface_fallback", explicit=False):
    t=fold(text); population, level, coverage_name="named_entity",0,"named_entity"
    for pattern,population,level in POP_PATTERNS:
        if re.search(pattern,t):
            coverage_name = "whole_domain" if population=="game_industry" else ("broad_population" if level>=3 else "subset")
            break
    coverage=COVERAGE[coverage_name]
    quant="unspecified"
    for q,p in QUANT:
        if has(t,p): quant=q; break
    if quant=="all": coverage=min(4,coverage+1)
    start,end=years(t)
    return ScopeSpec(population,coverage,quant,tuple(n for n,p in SEG if has(t,p)),start,end,tuple(n for n,p in GEO if has(t,p)),tuple(n for n,p in STAGE if has(t,p)),basis,explicit)

def from_item(item,text_key):
    s=item.get("scope_spec")
    if isinstance(s,dict):
        return ScopeSpec(str(s.get("population") or "named_entity"),COVERAGE.get(str(s.get("coverage") or "named_entity"),0),str(s.get("quantifier") or "unspecified"),tuple(str(x) for x in s.get("segment",[])),s.get("period_start"),s.get("period_end"),tuple(str(x) for x in s.get("geography",[])),tuple(str(x) for x in s.get("stage",[])),"structured",True)
    declared=str(item.get("scope") or "").strip()
    return extract(declared,"declared_scope",True) if declared else extract(item.get(text_key,""))

def union(scopes):
    if not scopes: return extract("")
    p=max(scopes,key=lambda x:POP.get(x.population,0))
    return ScopeSpec(p.population,max(x.coverage for x in scopes),"many" if any(x.quantifier in {"many","all"} for x in scopes) else "some",tuple(dict.fromkeys(v for x in scopes for v in x.segment)),min((x.period_start for x in scopes if x.period_start is not None),default=None),max((x.period_end for x in scopes if x.period_end is not None),default=None),tuple(dict.fromkeys(v for x in scopes for v in x.geography)),tuple(dict.fromkeys(v for x in scopes for v in x.stage)),"union",all(x.explicit for x in scopes))

def compare(c,e):
    ex=[]
    d=POP.get(c.population,0)-POP.get(e.population,0)
    if d>0: ex.append({"axis":"population","from":e.population,"to":c.population,"delta":min(3,d)*3,"reason":"claim population is broader"})
    d=c.coverage-e.coverage
    if d>0: ex.append({"axis":"coverage","from":e.coverage,"to":c.coverage,"delta":min(3,d)*3,"reason":"claim coverage is broader"})
    if e.quantifier in {"some","many"} and c.quantifier=="all": ex.append({"axis":"quantifier","from":e.quantifier,"to":"all","delta":3,"reason":"subset-to-universal expansion"})
    if e.period_start is not None and c.period_start is not None and c.period_start<e.period_start: ex.append({"axis":"time","from":e.period_start,"to":c.period_start,"delta":1,"reason":"claim starts earlier"})
    if e.period_end is not None and c.period_end is not None and c.period_end>e.period_end: ex.append({"axis":"time","from":e.period_end,"to":c.period_end,"delta":1,"reason":"claim ends later"})
    if e.segment and not set(c.segment).issubset(e.segment): ex.append({"axis":"segment","from":list(e.segment),"to":list(c.segment),"delta":2,"reason":"claim covers additional segments"})
    if e.geography and not set(c.geography).issubset(e.geography): ex.append({"axis":"geography","from":list(e.geography),"to":list(c.geography),"delta":1,"reason":"claim covers additional geography"})
    if e.stage and not set(c.stage).issubset(e.stage): ex.append({"axis":"stage","from":list(e.stage),"to":list(c.stage),"delta":2,"reason":"claim covers additional stages"})
    return ex,sum(x["delta"] for x in ex)

def assess_scope_expansion(claim,*,evidence_items):
    cid=str(claim.get("id") or claim.get("claim_id") or "").strip(); text=str(claim.get("text") or "").strip()
    cs=from_item(claim,"text"); items=[x for x in evidence_items if isinstance(x,dict)]
    ss=[from_item(x,"excerpt") for x in items if isinstance(x.get("scope_spec"),dict)]
    if ss:
        es=union(ss)
        ex,index=compare(cs,es)
        if not ex:
            verdict,repair,reason="PASS","NONE","claim scope does not expand beyond structured evidence scope"
        elif any(x["axis"] in {"population","coverage","quantifier"} and x["delta"]>=3 for x in ex) or index>=3:
            verdict,repair,reason="FAIL","WEAKEN_SCOPE",f"scope expansion index {index} is blocking"
        else:
            verdict,repair,reason="REVIEW",("NARROW_PERIOD" if any(x["axis"]=="time" for x in ex) else "WEAKEN_SCOPE"),f"scope expansion index {index} requires review"
    else:
        # Free-form evidence excerpts do not reliably encode population scope.
        # Never infer a narrower evidence scope merely from an entity mention.
        es=extract("","evidence_scope_unknown")
        ex=[]; index=0
        if cs.coverage >= COVERAGE["broad_population"]:
            verdict,repair,reason="REVIEW","WEAKEN_SCOPE","evidence scope is unknown for a broad claim; structured scope is required"
        else:
            verdict,repair,reason="PASS","NONE","evidence scope is not structured; no unsupported expansion inferred"

    return ScopeExpansion(cid,text,cs,es,tuple(ex),index,verdict,repair,reason)

def assess_scopes(claims,*,evidence_items):
    ev={str(x.get("id") or x.get("evidence_id") or "").strip():x for x in evidence_items if isinstance(x,dict) and str(x.get("id") or x.get("evidence_id") or "").strip()}
    out=[]
    for c in claims:
        ids=[str(x).strip() for x in c.get("evidence_ids",[]) if str(x).strip()]
        out.append(assess_scope_expansion(c,evidence_items=[ev[x] for x in ids if x in ev]))
    return out

def summarize_scope_assessments(items):
    counts={x:0 for x in ("PASS","REVIEW","FAIL")}; axes={}
    for i in items:
        counts[i.verdict]+=1
        for x in i.expansions: axes[x["axis"]]=axes.get(x["axis"],0)+1
    n=max(len(items),1)
    return {"claims":len(items),"verdicts":counts,"pass_rate":round(counts["PASS"]/n,3),"review_rate":round(counts["REVIEW"]/n,3),"fail_rate":round(counts["FAIL"]/n,3),"expansions_by_axis":axes}
