from datetime import datetime, timedelta, timezone

from content_factory.visual_monitoring import (
    GoldenCase,
    MonitoringObservation,
    MonitoringThresholds,
    backtest_threshold_pair,
    evaluate_golden_set,
    estimate_hierarchical_rate,
    inject_binary_degradation,
    sparse_category_backtest,
)


def _historical_rows(*, days: int = 90) -> list[MonitoringObservation]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows: list[MonitoringObservation] = []
    categories = (
        ("animals/reptiles", 0.08),
        ("animals/mammals", 0.10),
        ("vehicles/ships", 0.09),
    )
    index = 0
    for day in range(days):
        for category, fpr in categories:
            for _ in range(6):
                actual_positive = index % 10 < 6
                if not actual_positive:
                    predicted_positive = (index % 100) < int(fpr * 100)
                else:
                    predicted_positive = True
                rows.append(
                    MonitoringObservation(
                        timestamp=start + timedelta(days=day),
                        category=category,
                        actual_positive=actual_positive,
                        predicted_positive=predicted_positive,
                        query=category,
                    )
                )
                index += 1
    return rows


def test_hierarchical_estimate_shrinks_tiny_category_toward_parent():
    reference = _historical_rows(days=30)
    tiny = [
        MonitoringObservation(
            timestamp=datetime(2026, 2, 1, tzinfo=timezone.utc),
            category="animals/reptiles",
            actual_positive=False,
            predicted_positive=True,
        )
    ]
    estimate = estimate_hierarchical_rate(
        tiny,
        reference,
        category="animals/reptiles",
        metric="fpr",
        parent_map={
            "animals/reptiles": "animals",
            "animals/mammals": "animals",
        },
        prior_strength=20,
    )
    assert estimate.effective_samples == 1
    assert estimate.posterior_mean < estimate.raw_rate


def test_injected_fpr_degradation_is_detectable():
    stable = _historical_rows(days=90)
    onset = datetime(2026, 3, 15, tzinfo=timezone.utc)
    degraded = inject_binary_degradation(
        stable,
        onset=onset,
        metric="fpr",
        delta=0.50,
        category="vehicles/ships",
        seed=7,
    )
    thresholds = MonitoringThresholds(
        warning_delta=0.05,
        critical_delta=0.10,
        warning_probability=0.95,
        critical_probability=0.99,
        monte_carlo_draws=1200,
        min_effective_samples=20,
    )
    result = backtest_threshold_pair(
        stable_observations=stable,
        degraded_observations=degraded,
        onset=onset,
        category="vehicles/ships",
        metric="fpr",
        thresholds=thresholds,
    )
    assert result.stable_critical_false_positive_rate < 0.05
    assert result.warning_detection_rate == 1.0
    assert result.warning_median_delay_days is not None
    assert result.critical_detection_rate == 0.0


def test_sparse_backtest_keeps_critical_false_alerts_low():
    reference = _historical_rows(days=90)
    rare = [
        MonitoringObservation(
            timestamp=datetime(2026, 4, 1, tzinfo=timezone.utc) + timedelta(days=i),
            category="animals/reptiles",
            actual_positive=(i % 5 != 0),
            predicted_positive=True,
        )
        for i in range(5)
    ]
    thresholds = MonitoringThresholds(
        warning_delta=0.05,
        critical_delta=0.10,
        warning_probability=0.95,
        critical_probability=0.99,
        monte_carlo_draws=600,
        min_effective_samples=10,
    )
    results = sparse_category_backtest(
        category_observations=rare,
        reference_observations=reference,
        category="animals/reptiles",
        metric="fpr",
        thresholds=thresholds,
        sample_sizes=(5, 10, 20),
        trials=100,
    )
    assert {row.sample_size for row in results} == {5, 10, 20}
    assert all(row.critical_false_alert_rate <= 0.01 for row in results if row.trials)


def test_golden_regression_blocks_promotion():
    result = evaluate_golden_set(
        [
            GoldenCase("HN-001", expected_accept=True, observed_accept=True),
            GoldenCase("HN-002", expected_accept=False, observed_accept=True),
        ]
    )
    assert result["failed"] == 1
    assert result["regressions"] == ["HN-002"]
    assert result["promotion_blocked"] is True


def test_strong_degradation_reaches_critical():
    stable = _historical_rows(days=90)
    onset = datetime(2026, 3, 15, tzinfo=timezone.utc)
    degraded = inject_binary_degradation(
        stable,
        onset=onset,
        metric="fpr",
        delta=0.30,
        category="vehicles/ships",
        seed=7,
    )
    thresholds = MonitoringThresholds(
        warning_delta=0.05,
        critical_delta=0.10,
        warning_probability=0.95,
        critical_probability=0.99,
        monte_carlo_draws=1200,
        min_effective_samples=20,
    )
    result = backtest_threshold_pair(
        stable_observations=stable,
        degraded_observations=degraded,
        onset=onset,
        category="vehicles/ships",
        metric="fpr",
        thresholds=thresholds,
        window_days=7,
    )
    assert result.critical_detection_rate == 1.0
    assert result.critical_median_delay_days is not None
    assert result.critical_median_delay_days <= 14
