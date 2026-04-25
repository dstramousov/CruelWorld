"""Runtime metrics collection for the existing debug overlay."""

from __future__ import annotations

import math

try:
    import resource
except ImportError:  # pragma: no cover
    resource = None  # type: ignore[assignment]
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ChunkDebugStats:
    """Debug-only chunk streaming status."""

    mode: str
    loaded_chunks: int
    total_chunks: int
    active_chunks: int
    chunk_width_tiles: int


@dataclass(frozen=True, slots=True)
class ObjectDebugStats:
    """Runtime object counters for the debug overlay."""

    total_objects: int
    active_objects: int
    visible_objects: int
    hazards: int
    interactables: int
    observations: int


@dataclass(frozen=True, slots=True)
class RuntimeDebugStats:
    """Runtime system statistics shown in the debug overlay."""

    fps: int
    frame_time_ms: float
    update_delta_ms: float
    memory_rss_mb: float | None
    objects: ObjectDebugStats
    chunks: ChunkDebugStats


class DebugMetrics:
    """Collects lightweight runtime metrics for the existing debug overlay."""

    def __init__(self, chunk_width_tiles: int = 64) -> None:
        """Execute init.
        
        Args:
            chunk_width_tiles: Input value used by this operation.
        """
        self.chunk_width_tiles = max(1, chunk_width_tiles)

    def collect(
        self,
        *,
        fps: int,
        raw_frame_time: float,
        update_delta_time: float,
        object_stats: ObjectDebugStats,
        map_width_tiles: int,
    ) -> RuntimeDebugStats:
        """Build a runtime metrics snapshot.

        Args:
            fps: Current frames per second.
            raw_frame_time: Raw frame time reported by the renderer.
            update_delta_time: Delta time used by simulation update.
            object_stats: Current object counters.
            map_width_tiles: Loaded map width in tiles.

        Returns:
            Runtime metrics snapshot.
        """
        # Chunk data is currently debug-only. The map still runs in full-map
        # mode, but this snapshot shows how many chunks future streaming would use.
        total_chunks = max(1, math.ceil(map_width_tiles / self.chunk_width_tiles))
        chunk_stats = ChunkDebugStats(
            mode="full_map",
            loaded_chunks=1,
            total_chunks=total_chunks,
            active_chunks=1,
            chunk_width_tiles=self.chunk_width_tiles,
        )
        return RuntimeDebugStats(
            fps=fps,
            frame_time_ms=raw_frame_time * 1000.0,
            update_delta_ms=update_delta_time * 1000.0,
            memory_rss_mb=self._read_memory_rss_mb(),
            objects=object_stats,
            chunks=chunk_stats,
        )

    @staticmethod
    def _read_memory_rss_mb() -> float | None:
        """Execute read memory rss mb.
        
        Returns:
            Result produced by this operation.
        """
        proc_status = Path("/proc/self/status")
        if proc_status.exists():
            try:
                for line in proc_status.read_text(encoding="utf-8").splitlines():
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        if len(parts) >= 2:
                            return int(parts[1]) / 1024.0
            except OSError:
                return None

        if resource is None:
            return None
        try:
            usage_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        except (OSError, ValueError):
            return None
        if usage_kb <= 0:
            return None
        return float(usage_kb) / 1024.0
