from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from random import Random
from statistics import median
from typing import Iterable, Literal

MetricName = Literal["fpr", "fnr", "human_reject_rate"]
Severity = Literal["GREEN", "WARNING", "CRITICAL"]


@dataclass(frozen=True)
class MonitoringObservation:
    timestamp: datetime
    category: str
    actual_positive: bool
    predicted_positive: bool
    query: str = ""
    hard_negative_id: str | None = None


@dataclass(frozen=True)
class MonitoringThresholds:
    warning_delta: float = 0.05
    critical_delta: float = 0.10
    warning_probability: float = 0.95
    critical_probability: float = 0.99
    prior_strength: float = 20.0
    parent_mix: float = 0.75
    monte_carlo_draws: int = 4000
    min_effective_samples: int = 10

    def __post_init__(self) -> None:
        if not 0.0 < self.warning_delta < self.critical_delta <= 1.0:
            raise ValueError("threshold deltas must satisfy 0 < warning < critical <= 1")
        if not 0.5 <= self.warning_probability < self.critical_probability < 1.0:
            raise ValueError("alert probabilities must satisfy 0.5 <= warning < critical < 1")
        if self.prior_strength <= 0:
            raise ValueError("prior_strength must be positive")
        if not 0.0 <= self.parent_mix <= 1.0:
            raise ValueError("parent_mix must be within [0, 1]")
        if self.monte_carlo_draws < 100:
            raise ValueError("monte_carlo_draws must be >= 100")
        if self.min_effective_samples < 1:
            raise ValueError("min_effective_samples must be >= 1")


@dataclass(frozen=True)
class RateEstimate:
    numerator: float
    denominator: float
    raw_rate: float
    posterior_mean: float
    posterior_alpha: float
    posterior_beta: float
    effective_samples: float


@dataclass(frozen=True)
class MonitoringAlert:
    severity: Severity
    metric: MetricName
    category: str
    observed_rate: float
    baseline_rate: float
    delta: float
    probability_above_warning: float
    probability_above_critical: float
    effective_samples: float


@dataclass(frozen=True)
class ThresholdBacktestResult:
    warning_delta: float
    critical_delta: float
    stable_warning_false_positive_rate: float
    stable_critical_false_positive_rate: float
    warning_detection_rate: float
    critical_detection_rate: float
    warning_median_delay_days: float | None
    critical_median_delay_days: float | None
    warning_p90_delay_days: float | None
    critical_p90_delay_days: float | None


@dataclass(frozen=True)
class SparseRobustnessResult:
    sample_size: int
    warning_false_alert_rate: float
    critical_false_alert_rate: float
    trials: int


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    expected_accept: bool
    observed_accept: bool
    category: str = ""


def _metric_event(observation: MonitoringObservation, metric: MetricName) -> tuple[bool, bool]:
    if metric == "fpr":
        eligible = not observation.actual_positive
        event = eligible and observation.predicted_positive
    elif metric == "fnr":
        eligible = observation.actual_positive
        event = eligible and not observation.predicted_positive
    elif metric == "human_reject_rate":
        eligible = observation.predicted_positive
        event = eligible and not observation.actual_positive
    else:
        raise ValueError(f"unsupported metric: {metric}")
    return event, eligible


def rate_counts(
    observations: Iterable[MonitoringObservation],
    metric: MetricName,
) -> tuple[int, int]:
    numerator = 0
    denominator = 0
    for observation in observations:
        event, eligible = _metric_event(observation, metric)
        denominator += int(eligible)
        numerator += int(event)
    return numerator, denominator


def _global_rate(observations: list[MonitoringObservation], metric: MetricName) -> float:
    numerator, denominator = rate_counts(observations, metric)
    return numerator / denominator if denominator else 0.0


def estimate_hierarchical_rate(
    current: Iterable[MonitoringObservation],
    reference: Iterable[MonitoringObservation],
    *,
    category: str,
    metric: MetricName,
    parent_map: dict[str, str] | None = None,
    prior_strength: float = 20.0,
    parent_mix: float = 0.75,
) -> RateEstimate:
    current_rows = [row for row in current if row.category == category]
    reference_rows = list(reference)
    parent = parent_map.get(category) if parent_map else None
    parent_rows = (
        [row for row in reference_rows if row.category == parent]
        if parent
        else []
    )

    global_rate = _global_rate(reference_rows, metric)
    parent_rate = _global_rate(parent_rows, metric) if parent_rows else global_rate
    prior_mean = parent_mix * parent_rate + (1.0 - parent_mix) * global_rate
    alpha0 = max(prior_mean * prior_strength, 1e-6)
    beta0 = max((1.0 - prior_mean) * prior_strength, 1e-6)

    numerator, denominator = rate_counts(current_rows, metric)
    alpha = alpha0 + numerator
    beta = beta0 + denominator - numerator
    posterior_mean = alpha / (alpha + beta)
    return RateEstimate(
        numerator=float(numerator),
        denominator=float(denominator),
        raw_rate=(numerator / denominator if denominator else 0.0),
        posterior_mean=posterior_mean,
        posterior_alpha=alpha,
        posterior_beta=beta,
        effective_samples=float(denominator),
    )


def posterior_probability_above(
    alpha: float,
    beta: float,
    threshold: float,
    *,
    draws: int = 4000,
    seed: int = 0,
) -> float:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("probability threshold must be within [0, 1]")
    if alpha <= 0 or beta <= 0:
        raise ValueError("beta posterior parameters must be positive")
    if draws < 100:
        raise ValueError("draws must be >= 100")

    rng = Random(seed)
    above = sum(rng.betavariate(alpha, beta) > threshold for _ in range(draws))
    return above / draws


def evaluate_alert(
    current: Iterable[MonitoringObservation],
    reference: Iterable[MonitoringObservation],
    *,
    category: str,
    metric: MetricName,
    thresholds: MonitoringThresholds,
    parent_map: dict[str, str] | None = None,
    seed: int = 0,
) -> MonitoringAlert:
    estimate = estimate_hierarchical_rate(
        current,
        reference,
        category=category,
        metric=metric,
        parent_map=parent_map,
        prior_strength=thresholds.prior_strength,
        parent_mix=thresholds.parent_mix,
    )
    baseline_estimate = estimate_hierarchical_rate(
        reference,
        reference,
        category=category,
        metric=metric,
        parent_map=parent_map,
        prior_strength=thresholds.prior_strength,
        parent_mix=thresholds.parent_mix,
    )
    warning_cutoff = min(1.0, baseline_estimate.posterior_mean + thresholds.warning_delta)
    critical_cutoff = min(1.0, baseline_estimate.posterior_mean + thresholds.critical_delta)

    warning_probability = posterior_probability_above(
        estimate.posterior_alpha,
        estimate.posterior_beta,
        warning_cutoff,
        draws=thresholds.monte_carlo_draws,
        seed=seed,
    )
    critical_probability = posterior_probability_above(
        estimate.posterior_alpha,
        estimate.posterior_beta,
        critical_cutoff,
        draws=thresholds.monte_carlo_draws,
        seed=seed + 1,
    )

    severity: Severity = "GREEN"
    if estimate.effective_samples >= thresholds.min_effective_samples:
        if critical_probability >= thresholds.critical_probability:
            severity = "CRITICAL"
        elif warning_probability >= thresholds.warning_probability:
            severity = "WARNING"

    return MonitoringAlert(
        severity=severity,
        metric=metric,
        category=category,
        observed_rate=estimate.posterior_mean,
        baseline_rate=baseline_estimate.posterior_mean,
        delta=estimate.posterior_mean - baseline_estimate.posterior_mean,
        probability_above_warning=warning_probability,
        probability_above_critical=critical_probability,
        effective_samples=estimate.effective_samples,
    )


def _window_ends(start: datetime, end: datetime, *, step: timedelta) -> list[datetime]:
    values: list[datetime] = []
    cursor = start
    while cursor <= end:
        values.append(cursor)
        cursor += step
    return values


def _rolling_alerts(
    observations: list[MonitoringObservation],
    *,
    reference: list[MonitoringObservation],
    start: datetime,
    end: datetime,
    window: timedelta,
    category: str,
    metric: MetricName,
    thresholds: MonitoringThresholds,
    parent_map: dict[str, str] | None,
    seed_offset: int,
) -> list[tuple[datetime, MonitoringAlert]]:
    rows = sorted(observations, key=lambda row: row.timestamp)
    alerts: list[tuple[datetime, MonitoringAlert]] = []
    for index, window_end in enumerate(_window_ends(start, end, step=timedelta(days=1))):
        window_start = window_end - window
        current = [
            row for row in rows
            if window_start <= row.timestamp <= window_end
        ]
        if not current:
            continue
        alert = evaluate_alert(
            current,
            reference,
            category=category,
            metric=metric,
            thresholds=thresholds,
            parent_map=parent_map,
            seed=seed_offset + index * 10,
        )
        alerts.append((window_end, alert))
    return alerts


def backtest_threshold_pair(
    *,
    stable_observations: Iterable[MonitoringObservation],
    degraded_observations: Iterable[MonitoringObservation],
    onset: datetime,
    category: str,
    metric: MetricName,
    thresholds: MonitoringThresholds,
    stability_split: datetime | None = None,
    window_days: int = 7,
    parent_map: dict[str, str] | None = None,
) -> ThresholdBacktestResult:
    if window_days < 1:
        raise ValueError("window_days must be >= 1")
    stable = sorted(stable_observations, key=lambda row: row.timestamp)
    degraded = sorted(degraded_observations, key=lambda row: row.timestamp)
    if not stable or not degraded:
        raise ValueError("backtest requires stable and degraded observations")

    split = stability_split or stable[len(stable) // 2].timestamp
    stable_reference = [row for row in stable if row.timestamp < split]
    stable_test = [row for row in stable if row.timestamp >= split]
    if not stable_reference or not stable_test:
        raise ValueError("stability split must leave reference and test observations")

    stable_start = min(row.timestamp for row in stable_test)
    stable_end = max(row.timestamp for row in stable_test)
    stable_alerts = _rolling_alerts(
        stable_test,
        reference=stable_reference,
        start=stable_start,
        end=stable_end,
        window=timedelta(days=window_days),
        category=category,
        metric=metric,
        thresholds=thresholds,
        parent_map=parent_map,
        seed_offset=1_000,
    )
    stable_warning = sum(
        alert.severity in {"WARNING", "CRITICAL"} for _, alert in stable_alerts
    )
    stable_critical = sum(
        alert.severity == "CRITICAL" for _, alert in stable_alerts
    )
    stable_denominator = len(stable_alerts)

    degraded_reference = [row for row in degraded if row.timestamp < onset]
    post = [row for row in degraded if row.timestamp >= onset]
    if not degraded_reference or not post:
        raise ValueError("degraded backtest needs observations before and after onset")
    degraded_end = max(row.timestamp for row in post)
    degraded_alerts = _rolling_alerts(
        post,
        reference=degraded_reference,
        start=onset,
        end=degraded_end,
        window=timedelta(days=window_days),
        category=category,
        metric=metric,
        thresholds=thresholds,
        parent_map=parent_map,
        seed_offset=2_000,
    )

    warning_hits = [
        ts for ts, alert in degraded_alerts
        if alert.severity in {"WARNING", "CRITICAL"}
    ]
    critical_hits = [
        ts for ts, alert in degraded_alerts
        if alert.severity == "CRITICAL"
    ]
    warning_delays = (
        [(warning_hits[0] - onset).total_seconds() / 86400.0]
        if warning_hits
        else []
    )
    critical_delays = (
        [(critical_hits[0] - onset).total_seconds() / 86400.0]
        if critical_hits
        else []
    )

    def _p90(values: list[float]) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        index = min(len(ordered) - 1, int(0.90 * (len(ordered) - 1)))
        return ordered[index]

    return ThresholdBacktestResult(
        warning_delta=thresholds.warning_delta,
        critical_delta=thresholds.critical_delta,
        stable_warning_false_positive_rate=(
            stable_warning / stable_denominator if stable_denominator else 0.0
        ),
        stable_critical_false_positive_rate=(
            stable_critical / stable_denominator if stable_denominator else 0.0
        ),
        warning_detection_rate=1.0 if warning_delays else 0.0,
        critical_detection_rate=1.0 if critical_delays else 0.0,
        warning_median_delay_days=median(warning_delays) if warning_delays else None,
        critical_median_delay_days=median(critical_delays) if critical_delays else None,
        warning_p90_delay_days=_p90(warning_delays),
        critical_p90_delay_days=_p90(critical_delays),
    )


def inject_binary_degradation(
    observations: Iterable[MonitoringObservation],
    *,
    onset: datetime,
    metric: Literal["fpr", "fnr"],
    delta: float,
    category: str | None = None,
    seed: int = 0,
) -> list[MonitoringObservation]:
    if not 0.0 < delta <= 1.0:
        raise ValueError("degradation delta must be within (0, 1]")
    rows = list(observations)
    baseline = [
        row for row in rows
        if row.timestamp < onset
        and (row.category == category if category is not None else True)
    ]
    base_numerator, base_denominator = rate_counts(baseline, metric)
    base_rate = base_numerator / base_denominator if base_denominator else 0.0
    target_rate = min(0.999, base_rate + delta)

    rng = Random(seed)
    mutated = list(rows)
    candidates = [
        index for index, row in enumerate(mutated)
        if row.timestamp >= onset
        and (row.category == category if category is not None else True)
    ]
    rng.shuffle(candidates)

    if metric == "fpr":
        eligible = [
            index for index in candidates
            if not mutated[index].actual_positive
        ]
        target_events = min(
            len(eligible),
            max(0, round(target_rate * len(eligible))),
        )
        for index in eligible[:target_events]:
            row = mutated[index]
            mutated[index] = MonitoringObservation(
                timestamp=row.timestamp,
                category=row.category,
                actual_positive=row.actual_positive,
                predicted_positive=True,
                query=row.query,
                hard_negative_id=row.hard_negative_id,
            )
    else:
        eligible = [
            index for index in candidates
            if mutated[index].actual_positive
        ]
        target_events = min(
            len(eligible),
            max(0, round(target_rate * len(eligible))),
        )
        for index in eligible[:target_events]:
            row = mutated[index]
            mutated[index] = MonitoringObservation(
                timestamp=row.timestamp,
                category=row.category,
                actual_positive=row.actual_positive,
                predicted_positive=False,
                query=row.query,
                hard_negative_id=row.hard_negative_id,
            )
    return mutated


def sparse_category_backtest(
    *,
    category_observations: Iterable[MonitoringObservation],
    reference_observations: Iterable[MonitoringObservation],
    category: str,
    metric: MetricName,
    thresholds: MonitoringThresholds,
    sample_sizes: Iterable[int] = (5, 10, 20, 30, 50),
    trials: int = 500,
    parent_map: dict[str, str] | None = None,
    seed: int = 0,
) -> list[SparseRobustnessResult]:
    pool = [row for row in category_observations if row.category == category]
    reference = list(reference_observations)
    if not pool:
        raise ValueError("sparse backtest requires category observations")
    if trials < 1:
        raise ValueError("trials must be >= 1")

    results: list[SparseRobustnessResult] = []
    for sample_size in sample_sizes:
        if sample_size < 1:
            raise ValueError("sample sizes must be positive")
        rng = Random(seed + sample_size)
        warning_hits = 0
        critical_hits = 0
        for trial in range(trials):
            sample = [rng.choice(pool) for _ in range(sample_size)]
            alert = evaluate_alert(
                sample,
                reference,
                category=category,
                metric=metric,
                thresholds=thresholds,
                parent_map=parent_map,
                seed=seed + sample_size * 10_000 + trial,
            )
            warning_hits += alert.severity in {"WARNING", "CRITICAL"}
            critical_hits += alert.severity == "CRITICAL"
        results.append(
            SparseRobustnessResult(
                sample_size=sample_size,
                warning_false_alert_rate=warning_hits / trials,
                critical_false_alert_rate=critical_hits / trials,
                trials=trials,
            )
        )
    return results


def evaluate_golden_set(cases: Iterable[GoldenCase]) -> dict[str, object]:
    rows = list(cases)
    failures = [
        row.case_id
        for row in rows
        if row.expected_accept != row.observed_accept
    ]
    return {
        "total": len(rows),
        "passed": len(rows) - len(failures),
        "failed": len(failures),
        "regressions": failures,
        "promotion_blocked": bool(failures),
    }
