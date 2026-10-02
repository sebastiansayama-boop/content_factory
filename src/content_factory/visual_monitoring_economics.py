from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

MonitoringMethod = Literal["simple_threshold", "hierarchical_bayesian", "hybrid"]


@dataclass(frozen=True)
class EconomicAssumptions:
    period_days: float
    decisions_per_day: float
    review_hourly_cost: float
    review_minutes_per_alert: float
    false_alert_cost: float
    missed_drift_cost: float
    bad_decision_cost: float
    affected_traffic_fraction: float
    drift_incidents_per_period: float
    infrastructure_cost_by_method: Mapping[str, float]

    def __post_init__(self) -> None:
        for name in (
            "period_days",
            "decisions_per_day",
            "review_hourly_cost",
            "review_minutes_per_alert",
            "false_alert_cost",
            "missed_drift_cost",
            "bad_decision_cost",
            "drift_incidents_per_period",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be >= 0")
        if not 0.0 <= self.affected_traffic_fraction <= 1.0:
            raise ValueError("affected_traffic_fraction must be within [0, 1]")
        if not self.infrastructure_cost_by_method:
            raise ValueError("infrastructure_cost_by_method must not be empty")


@dataclass(frozen=True)
class EconomicPerformance:
    method: MonitoringMethod
    stable_false_alerts_per_1k: float
    detection_rate: float
    median_detection_delay_days: float | None
    compute_cost_per_1k: float

    def __post_init__(self) -> None:
        if self.stable_false_alerts_per_1k < 0:
            raise ValueError("stable_false_alerts_per_1k must be >= 0")
        if not 0.0 <= self.detection_rate <= 1.0:
            raise ValueError("detection_rate must be within [0, 1]")
        if self.median_detection_delay_days is not None and self.median_detection_delay_days < 0:
            raise ValueError("median_detection_delay_days must be >= 0")
        if self.compute_cost_per_1k < 0:
            raise ValueError("compute_cost_per_1k must be >= 0")


@dataclass(frozen=True)
class EconomicCost:
    method: MonitoringMethod
    total_cost: float
    cost_per_1k_decisions: float
    infrastructure_cost: float
    compute_cost: float
    human_review_cost: float
    false_alert_cost: float
    missed_drift_cost: float
    detection_delay_cost: float

    @property
    def variable_cost(self) -> float:
        return (
            self.compute_cost
            + self.human_review_cost
            + self.false_alert_cost
            + self.missed_drift_cost
            + self.detection_delay_cost
        )


@dataclass(frozen=True)
class BreakEvenPoint:
    method_a: MonitoringMethod
    method_b: MonitoringMethod
    volume_decisions_per_day: float | None
    cost_difference_at_zero_volume: float
    daily_variable_cost_difference: float


@dataclass(frozen=True)
class EconomicSweepPoint:
    decisions_per_day: float
    costs: Mapping[MonitoringMethod, float]
    lowest_cost_method: MonitoringMethod


def _cost_at_volume(
    performance: EconomicPerformance,
    assumptions: EconomicAssumptions,
    decisions_per_day: float,
) -> EconomicCost:
    if decisions_per_day < 0:
        raise ValueError("decisions_per_day must be >= 0")

    volume = decisions_per_day * assumptions.period_days
    false_alerts = volume / 1000.0 * performance.stable_false_alerts_per_1k
    detected_incidents = (
        assumptions.drift_incidents_per_period * performance.detection_rate
    )
    missed_incidents = (
        assumptions.drift_incidents_per_period * (1.0 - performance.detection_rate)
    )
    review_alerts = false_alerts + detected_incidents
    review_cost = (
        review_alerts
        * assumptions.review_minutes_per_alert
        / 60.0
        * assumptions.review_hourly_cost
    )
    false_alert_cost = false_alerts * assumptions.false_alert_cost
    missed_drift_cost = missed_incidents * assumptions.missed_drift_cost

    delay_days = performance.median_detection_delay_days or 0.0
    affected_decisions_per_day = (
        decisions_per_day * assumptions.affected_traffic_fraction
    )
    detection_delay_cost = (
        detected_incidents
        * delay_days
        * affected_decisions_per_day
        * assumptions.bad_decision_cost
    )

    infrastructure_cost = assumptions.infrastructure_cost_by_method.get(
        performance.method, 0.0
    )
    compute_cost = volume / 1000.0 * performance.compute_cost_per_1k

    total = (
        infrastructure_cost
        + compute_cost
        + review_cost
        + false_alert_cost
        + missed_drift_cost
        + detection_delay_cost
    )
    return EconomicCost(
        method=performance.method,
        total_cost=total,
        cost_per_1k_decisions=(
            total / volume * 1000.0 if volume > 0 else float("inf")
        ),
        infrastructure_cost=infrastructure_cost,
        compute_cost=compute_cost,
        human_review_cost=review_cost,
        false_alert_cost=false_alert_cost,
        missed_drift_cost=missed_drift_cost,
        detection_delay_cost=detection_delay_cost,
    )


def evaluate_economic_cost(
    performance: EconomicPerformance,
    assumptions: EconomicAssumptions,
) -> EconomicCost:
    return _cost_at_volume(
        performance,
        assumptions,
        assumptions.decisions_per_day,
    )


def compare_economic_costs(
    performances: Mapping[MonitoringMethod, EconomicPerformance],
    assumptions: EconomicAssumptions,
) -> dict[MonitoringMethod, EconomicCost]:
    unsupported = set(performances) - {
        "simple_threshold",
        "hierarchical_bayesian",
        "hybrid",
    }
    if unsupported:
        raise ValueError(f"unsupported methods: {sorted(unsupported)}")
    return {
        method: evaluate_economic_cost(performance, assumptions)
        for method, performance in performances.items()
    }


def find_break_even_volume(
    performance_a: EconomicPerformance,
    performance_b: EconomicPerformance,
    assumptions: EconomicAssumptions,
) -> BreakEvenPoint:
    zero_a = _cost_at_volume(performance_a, assumptions, 0.0)
    zero_b = _cost_at_volume(performance_b, assumptions, 0.0)
    diff0 = zero_a.total_cost - zero_b.total_cost

    one_a = _cost_at_volume(performance_a, assumptions, 1.0)
    one_b = _cost_at_volume(performance_b, assumptions, 1.0)
    daily_delta = (one_a.total_cost - zero_a.total_cost) - (
        one_b.total_cost - zero_b.total_cost
    )

    if abs(daily_delta) < 1e-12:
        volume = None
    else:
        candidate = -diff0 / daily_delta
        volume = candidate if candidate >= 0 else None

    return BreakEvenPoint(
        method_a=performance_a.method,
        method_b=performance_b.method,
        volume_decisions_per_day=volume,
        cost_difference_at_zero_volume=diff0,
        daily_variable_cost_difference=daily_delta,
    )


def sweep_economic_cost(
    performances: Mapping[MonitoringMethod, EconomicPerformance],
    assumptions: EconomicAssumptions,
    volumes_per_day: list[float],
) -> list[EconomicSweepPoint]:
    if not volumes_per_day:
        raise ValueError("volumes_per_day must not be empty")

    points: list[EconomicSweepPoint] = []
    for volume in volumes_per_day:
        costs = {
            method: _cost_at_volume(performance, assumptions, volume).total_cost
            for method, performance in performances.items()
        }
        lowest = min(costs, key=costs.get)
        points.append(
            EconomicSweepPoint(
                decisions_per_day=volume,
                costs=costs,
                lowest_cost_method=lowest,
            )
        )
    return points


def find_cost_frontier(
    performances: Mapping[MonitoringMethod, EconomicPerformance],
    assumptions: EconomicAssumptions,
    volumes_per_day: list[float],
) -> list[tuple[float, MonitoringMethod]]:
    points = sweep_economic_cost(performances, assumptions, volumes_per_day)
    frontier: list[tuple[float, MonitoringMethod]] = []
    for point in points:
        if not frontier or frontier[-1][1] != point.lowest_cost_method:
            frontier.append((point.decisions_per_day, point.lowest_cost_method))
    return frontier


def build_performance_from_backtest(
    *,
    method: MonitoringMethod,
    stable_false_positive_rate: float,
    detection_rate: float,
    median_delay_days: float | None,
    compute_cost_per_1k: float,
) -> EconomicPerformance:
    if not 0.0 <= stable_false_positive_rate <= 1.0:
        raise ValueError("stable_false_positive_rate must be within [0, 1]")
    return EconomicPerformance(
        method=method,
        stable_false_alerts_per_1k=stable_false_positive_rate * 1000.0,
        detection_rate=detection_rate,
        median_detection_delay_days=median_delay_days,
        compute_cost_per_1k=compute_cost_per_1k,
    )
