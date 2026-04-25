from __future__ import annotations

from src.systems.debug_metrics import DebugMetrics, ObjectDebugStats


def test_debug_metrics_collects_frame_and_object_stats() -> None:
    object_stats = ObjectDebugStats(
        total_objects=10,
        active_objects=7,
        visible_objects=4,
        hazards=2,
        interactables=3,
        observations=5,
    )
    metrics = DebugMetrics(chunk_width_tiles=64)

    snapshot = metrics.collect(
        fps=60,
        raw_frame_time=1.0 / 60.0,
        update_delta_time=0.0125,
        object_stats=object_stats,
        map_width_tiles=360,
    )

    assert snapshot.fps == 60
    assert round(snapshot.frame_time_ms, 2) == 16.67
    assert snapshot.update_delta_ms == 12.5
    assert snapshot.objects is object_stats
    assert snapshot.chunks.mode == "full_map"
    assert snapshot.chunks.loaded_chunks == 1
    assert snapshot.chunks.active_chunks == 1
    assert snapshot.chunks.total_chunks == 6


def test_debug_metrics_clamps_chunk_width_to_at_least_one() -> None:
    metrics = DebugMetrics(chunk_width_tiles=0)
    snapshot = metrics.collect(
        fps=0,
        raw_frame_time=0.0,
        update_delta_time=0.0,
        object_stats=ObjectDebugStats(0, 0, 0, 0, 0, 0),
        map_width_tiles=3,
    )

    assert snapshot.chunks.chunk_width_tiles == 1
    assert snapshot.chunks.total_chunks == 3


def test_read_memory_rss_returns_none_or_positive_value() -> None:
    memory = DebugMetrics._read_memory_rss_mb()

    assert memory is None or memory > 0.0
