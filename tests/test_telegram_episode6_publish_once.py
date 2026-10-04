from __future__ import annotations
import os, threading
from http.server import ThreadingHTTPServer
import pytest
from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace
from tests.test_telegram_publication_smoke import _request

pytestmark = pytest.mark.external

def test_real_telegram_episode6_publication(tmp_path, monkeypatch):
    if os.environ.get("RUN_TELEGRAM_E2E") != "1":
        pytest.skip("set RUN_TELEGRAM_E2E=1")
    for name in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        if not os.environ.get(name):
            pytest.fail(f"{name} is required")
    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_API_TOKEN", "telegram-publication-smoke-token")
    monkeypatch.delenv("FACTORY_TELEGRAM_FAKE", raising=False)
    service = FactoryService()
    try:
        previous = service.content_runs.create(title="Как люди прошлого представляли будущее", brief="Как люди прошлого представляли будущее", formats=("telegram",))
        previous_result = {"brief":"Как люди прошлого представляли будущее","content_brief":{"title":"Эпизод 5"},"package":{"title":"Эпизод 5","text":"Воображаемые города стали проектами будущего.","media":[],"claims":[],"sources":[],"evidence":[],"qc":{"status":"PASSED"},"series":{"series_id":"telegram-series-future-001","title":"Как люди прошлого представляли будущее","episode":5,"previous_run_id":None,"central_question":"Когда и почему будущее стало восприниматься как открытая возможность?","unresolved":["Что изменится, когда проектирование будущего соединится с новыми машинами и технологиями?"],"next_required_transition":"Показать переход от проектирования будущих городов к роли машин и технологий в изменении повседневной жизни.","story_state":{"central_question":"Когда и почему будущее стало восприниматься как открытая возможность?","established":["Представления о будущем существовали задолго до современной фантастики.","Древние традиции могли связывать время с повторяющимися природными и космическими ритмами.","Пророчество связывало ожидание будущего с сакральным знанием и знаками.","Воображаемые места и общества стали способом мысленно представить иной порядок жизни.","Города начали описываться как проекты, которые можно было планировать и строить."],"unresolved":["Что изменится, когда проектирование будущего соединится с новыми машинами и технологиями?"],"next_required_transition":"Показать переход от проектирования будущих городов к роли машин и технологий в изменении повседневной жизни.","used_examples":["Эбенизер Говард","Тони Гарнье","Ле Корбюзье"],"claims":[],"evidence":[]}}}}
        service.content_runs.start_planning(previous.run_id); service.content_runs.save_plan(previous.run_id,{"kind":"seed","series_id":"telegram-series-future-001"}); service.content_runs.start_producing(previous.run_id); service.content_runs.save_production_result(previous.run_id,previous_result); service.content_runs.save_result(previous.run_id,previous_result); service.content_runs.approve(previous.run_id,decision_ref="episode5-library-seed"); service.content_runs.mark_published(previous.run_id,{"status":"PUBLISHED","channel":"telegram","external_id":"episode5-library-seed"})
        run=service.content_runs.create(title="Как люди прошлого представляли будущее",brief="Как люди прошлого представляли будущее",formats=("telegram",))
        text_value="""В предыдущем эпизоде будущее стало чертежом: его начали описывать как города и системы, которые можно было спроектировать заранее. Но на этом история меняется. Машины не просто помогли строить запланированный мир. Они начали менять саму скорость и масштаб перемен.

Паровая машина постепенно превратилась из отдельного технического устройства в основу промышленной системы. Усовершенствования Джеймса Уатта в XVIII веке сделали ее значительно практичнее для разных видов работы. Затем железные дороги связали города и расстояния уже не так, как их знали прежде. В 1825 году открылась железная дорога Стоктон — Дарлингтон, первая общественная железная дорога с паровой тягой.

Это важно не только как история изобретений. Раньше воображаемый город можно было представить на бумаге, но сама жизнь менялась сравнительно медленно. Машины сделали изменение среды частью повседневности: производство, транспорт и расстояния стали зависеть от технических систем.

Поэтому будущее постепенно перестает быть только проектом. Оно становится процессом, который уже идет и способен менять планы быстрее, чем человек успевает их составить.

И здесь возникает следующий вопрос: когда стало понятно, что будущее нельзя надежно спроектировать заранее?"""
        sources=[{"id":"source-watt","title":"Science and Industry Museum, James Watt","url":"https://blog.scienceandindustrymuseum.org.uk/a-grand-exposition/"},{"id":"source-stockton","title":"Science and Industry Museum, The Stephensons: Part II","url":"https://blog.scienceandindustrymuseum.org.uk/the-stephensons-part-ii/"}]
        evidence=[{"id":"e-watt","source_id":"source-watt","excerpt":"The museum documents James Watt's contribution to steam technology and the industrial development of steam power."},{"id":"e-stockton","source_id":"source-stockton","excerpt":"The museum states that the Stockton and Darlington Railway opened on 27 October 1825 as the world's first steam-powered public railway."}]
        claims=[{"id":"c-watt","text":"Усовершенствования Джеймса Уатта сделали паровую машину значительно практичнее для промышленного применения.","source_ids":["source-watt"],"evidence_ids":["e-watt"]},{"id":"c-stockton","text":"Стоктон — Дарлингтонская железная дорога открылась в 1825 году как первая общественная железная дорога с паровой тягой.","source_ids":["source-stockton"],"evidence_ids":["e-stockton"]}]
        state={"central_question":"Когда и почему будущее стало восприниматься как открытая возможность?","established":["Представления о будущем существовали задолго до современной фантастики.","Древние традиции могли связывать время с повторяющимися природными и космическими ритмами.","Пророчество связывало ожидание будущего с сакральным знанием и знаками.","Воображаемые места и общества стали способом мысленно представить иной порядок жизни.","Города начали описываться как проекты, которые можно было планировать и строить.","Машины и технические системы начали ускорять и масштабировать изменения в повседневной жизни."],"unresolved":["Когда стало понятно, что будущее нельзя надежно спроектировать заранее?"],"next_required_transition":"Показать момент, когда ускорение технических и социальных изменений сделало будущее все менее предсказуемым.","used_examples":["Эбенизер Говард","Тони Гарнье","Ле Корбюзье","Джеймс Уатт","Стоктон — Дарлингтонская железная дорога"],"claims":["c-watt","c-stockton"],"evidence":["e-watt","e-stockton"]}
        result={"brief":"Как люди прошлого представляли будущее","content_brief":{"title":"Эпизод 6"},"package":{"title":"Эпизод 6","text":text_value,"media":[],"claims":claims,"sources":sources,"evidence":evidence,"qc":{"status":"PASSED"},"series":{"series_id":"telegram-series-future-001","title":"Как люди прошлого представляли будущее","episode":6,"previous_run_id":previous.run_id,"central_question":state["central_question"],"unresolved":state["unresolved"],"next_required_transition":state["next_required_transition"],"story_state":state}}}
        service.content_runs.start_planning(run.run_id); service.content_runs.save_plan(run.run_id,{"kind":"episode6","series_id":"telegram-series-future-001","previous_run_id":previous.run_id}); service.content_runs.start_producing(run.run_id); service.content_runs.save_production_result(run.run_id,result); service.content_runs.save_result(run.run_id,result)
        ProductHandler.service=service; ProductHandler.workspace=ContentWorkspace(service); ProductHandler.content_runs=service.content_runs; ProductHandler.content_run_planner=ContentRunPlanner(ProductHandler.workspace); monkeypatch.setattr(ProductHandler,"_rate_limited",lambda *a,**k:False)
        server=ThreadingHTTPServer(("127.0.0.1",0),ProductHandler); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            base=f"http://127.0.0.1:{server.server_port}"
            status,approved=_request(base,"POST",f"/api/runs/{run.run_id}/approve",{"decision_ref":"telegram-series-episode-6-approver","channel":"telegram"}); assert status==200,approved
            pub=approved["result"]["publication"]; status,published=_request(base,"POST",f"/api/runs/{run.run_id}/publish",{"publication_id":pub["publication_id"]}); assert status==200,published
            assert published["status"]=="PUBLISHED"; assert published["response"]["telegram_ok"] is True
            assert published["response"]["text"].strip()==text_value
            final=service.content_runs.get(run.run_id); assert final.status=="PUBLISHED"; assert final.result["package"]["series"]["episode"]==6
            print("\nTELEGRAM_EPISODE_6_RUN_ID="+run.run_id)
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)
    finally:
        service.close()
