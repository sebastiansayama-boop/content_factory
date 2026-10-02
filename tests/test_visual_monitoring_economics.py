from __future__ import annotations

import pytest

from content_factory.visual_monitoring_economics import (
    EconomicAssumptions,
    EconomicPerformance,
    build_performance_from_backtest,
    compare_economic_costs,
    find_break_even_volume,
    find_cost_frontier,
)


def _assumptions() -> EconomicAssumptions:
    return EconomicAssumptions(
        period_days=30,
        decisions_per_day=100,
        review_hourly_cost=20.0,
        review_minutes_per_alert=3.0,
        false_alert_cost=0.50,
        missed_drift_cost=150.0,
        bad_decision_cost=1.0,
        affected_traffic_fraction=0.80,
        drift_incidents_per_period=0.20,
        infrastructure_cost_by_method={
            "simple_threshold": 5.0,
            "hierarchical_bayesian": 20.0,
            "hybrid": 40.0,
        },
    )


def _performances() -> dict[str, EconomicPerformance]:
    return {
        "simple_threshold": EconomicPerformance(
            method="simple_threshold",
            stable_false_alerts_per_1k=8.0,
            detection_rate=0.80,
            median_detection_delay_days=3.0,
            compute_cost_per_1k=0.01,
        ),
        "hierarchical_bayesian": EconomicPerformance(
            method="hierarchical_bayesian",
            stable_false_alerts_per_1k=4.0,
            detection_rate=0.90,
            median_detection_delay_days=2.0,
            compute_cost_per_1k=0.03,
        ),
        "hybrid": EconomicPerformance(
            method="hybrid",
            stable_false_alerts_per_1k=5.0,
            detection_rate=0.97,
            median_detection_delay_days=0.75,
            compute_cost_per_1k=0.06,
        ),
    }


def test_economic_cost_contains_all_cost_components():
    assumptions = _assumptions()
    costs = compare_economic_costs(_performances(), assumptions)

    for cost in costs.values():
        assert cost.total_cost == pytest.approx(
            cost.infrastructure_cost
            + cost.compute_cost
            + cost.human_review_cost
            + cost.false_alert_cost
            + cost.missed_drift_cost
            + cost.detection_delay_cost
        )
        assert cost.total_cost >= cost.infrastructure_cost


def test_break_even_volume_is_computed_from_affine_cost_curves():
    assumptions = _assumptions()
    performances = _performances()

    simple_vs_bayesian = find_break_even_volume(
        performances["simple_threshold"],
        performances["hierarchical_bayesian"],
        assumptions,
    )
    bayesian_vs_hybrid = find_break_even_volume(
        performances["hierarchical_bayesian"],
        performances["hybrid"],
        assumptions,
    )

    assert simple_vs_bayesian.volume_decisions_per_day == pytest.approx(
        43.6456063907,
        rel=1e-9,
    )
    assert bayesian_vs_hybrid.volume_decisions_per_day == pytest.approx(
        142.5139220366,
        rel=1e-9,
    )


def test_cost_frontier_changes_with_traffic_in_benchmark_scenario():
    assumptions = _assumptions()
    frontier = find_cost_frontier(
        _performances(),
        assumptions,
        [10, 50, 100, 200, 500],
    )

    assert frontier == [
        (10, "simple_threshold"),
        (50, "hierarchical_bayesian"),
        (200, "hybrid"),
    ]


def test_backtest_metrics_convert_to_economic_performance():
    performance = build_performance_from_backtest(
        method="hierarchical_bayesian",
        stable_false_positive_rate=0.012,
        detection_rate=0.90,
        median_delay_days=2.5,
        compute_cost_per_1k=0.04,
    )

    assert performance.stable_false_alerts_per_1k == pytest.approx(12.0)
    assert performance.detection_rate == 0.90
    assert performance.median_detection_delay_days == 2.5
