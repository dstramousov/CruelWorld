"""Time System module for runtime gameplay systems."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
import math

Color = tuple[int, int, int, int]


@dataclass(slots=True)
class DayNightPhaseRanges:
    """Represent the DayNightPhaseRanges runtime concept."""
    dawn_start: float
    day_start: float
    dusk_start: float
    night_start: float


@dataclass(slots=True)
class DayNightConfig:
    """Represent the DayNightConfig runtime concept."""
    enabled: bool = True
    day_duration_minutes: float = 24.0
    randomize_start_time: bool = True
    start_time_hours: float = 12.0
    phase_ranges: DayNightPhaseRanges = field(
        default_factory=lambda: DayNightPhaseRanges(
            dawn_start=5.0,
            day_start=7.0,
            dusk_start=18.0,
            night_start=20.0,
        )
    )




@dataclass(slots=True)
class TimeOfDayTintConfig:
    """Represent the TimeOfDayTintConfig runtime concept."""
    day_world: Color = (255, 255, 255, 0)
    dusk_world: Color = (255, 226, 186, 22)
    night_world: Color = (180, 196, 255, 42)
    dawn_world: Color = (198, 222, 255, 20)
    day_sky: Color = (225, 235, 255, 36)
    dusk_sky: Color = (255, 196, 140, 78)
    night_sky: Color = (96, 126, 168, 118)
    dawn_sky: Color = (176, 206, 240, 72)

@dataclass(slots=True)
class StarConfig:
    """Represent the StarConfig runtime concept."""
    enabled: bool = True
    count: int = 80
    min_alpha: int = 90
    max_alpha: int = 255
    twinkle_enabled: bool = True
    twinkle_speed_min: float = 0.8
    twinkle_speed_max: float = 2.4
    twinkle_amplitude: float = 0.35
    min_size: int = 1
    max_size: int = 2
    parallax_speed: float = 0.03
    min_y: int = 8
    max_y: int = 168


@dataclass(slots=True)
class Star:
    """Represent the Star runtime concept."""
    x: float
    y: float
    size: int
    base_alpha: int
    twinkle_speed: float
    twinkle_phase: float


class TimeSystem:
    """Manage the day-night cycle and procedural stars."""

    def __init__(self, config: dict, seed: int | None = None) -> None:
        """Execute init.
        
        Args:
            config: Input value used by this operation.
            seed: Input value used by this operation.
        """
        cycle_cfg = config.get("day_night_cycle", {})
        star_cfg = cycle_cfg.get("stars", {})
        phase_cfg = cycle_cfg.get("phase_ranges", {})

        self.config = DayNightConfig(
            enabled=bool(cycle_cfg.get("enabled", True)),
            day_duration_minutes=float(cycle_cfg.get("day_duration_minutes", 24.0)),
            randomize_start_time=bool(cycle_cfg.get("randomize_start_time", True)),
            start_time_hours=float(cycle_cfg.get("start_time_hours", 12.0)),
            phase_ranges=DayNightPhaseRanges(
                dawn_start=float(phase_cfg.get("dawn_start", 5.0)),
                day_start=float(phase_cfg.get("day_start", 7.0)),
                dusk_start=float(phase_cfg.get("dusk_start", 18.0)),
                night_start=float(phase_cfg.get("night_start", 20.0)),
            ),
        )
        tint_cfg = cycle_cfg.get("tint", {})
        self.tint_config = TimeOfDayTintConfig(
            day_world=self._parse_color(tint_cfg.get("day_world"), (255, 255, 255, 0)),
            dusk_world=self._parse_color(tint_cfg.get("dusk_world"), (255, 226, 186, 22)),
            night_world=self._parse_color(tint_cfg.get("night_world"), (180, 196, 255, 42)),
            dawn_world=self._parse_color(tint_cfg.get("dawn_world"), (198, 222, 255, 20)),
            day_sky=self._parse_color(tint_cfg.get("day_sky"), (225, 235, 255, 36)),
            dusk_sky=self._parse_color(tint_cfg.get("dusk_sky"), (255, 196, 140, 78)),
            night_sky=self._parse_color(tint_cfg.get("night_sky"), (96, 126, 168, 118)),
            dawn_sky=self._parse_color(tint_cfg.get("dawn_sky"), (176, 206, 240, 72)),
        )
        self.star_config = StarConfig(
            enabled=bool(star_cfg.get("enabled", True)),
            count=int(star_cfg.get("count", 80)),
            min_alpha=int(star_cfg.get("min_alpha", 90)),
            max_alpha=int(star_cfg.get("max_alpha", 255)),
            twinkle_enabled=bool(star_cfg.get("twinkle_enabled", True)),
            twinkle_speed_min=float(star_cfg.get("twinkle_speed_min", 0.8)),
            twinkle_speed_max=float(star_cfg.get("twinkle_speed_max", 2.4)),
            twinkle_amplitude=float(star_cfg.get("twinkle_amplitude", 0.35)),
            min_size=int(star_cfg.get("min_size", 1)),
            max_size=int(star_cfg.get("max_size", 2)),
            parallax_speed=float(star_cfg.get("parallax_speed", 0.03)),
            min_y=int(star_cfg.get("min_y", 8)),
            max_y=int(star_cfg.get("max_y", 168)),
        )
        self._rng = Random(seed)
        self.current_time_hours = self._choose_start_time()
        self.elapsed_seconds = 0.0
        self.stars: list[Star] = []

    def _choose_start_time(self) -> float:
        """Execute choose start time.
        
        Returns:
            Result produced by this operation.
        """
        if not self.config.enabled:
            return self._normalize_hours(self.config.start_time_hours)
        if self.config.randomize_start_time:
            return self._rng.uniform(0.0, 24.0)
        return self._normalize_hours(self.config.start_time_hours)

    def generate_stars(self, width: int, height: int) -> None:
        """Generate a procedural star field for the sky layer."""
        self.stars = []
        if not self.star_config.enabled:
            return

        max_y = min(max(self.star_config.min_y, self.star_config.max_y), height - 1)
        min_y = min(self.star_config.min_y, max_y)
        for _ in range(max(0, self.star_config.count)):
            self.stars.append(
                Star(
                    x=self._rng.uniform(0.0, float(max(width - 1, 1))),
                    y=self._rng.uniform(float(min_y), float(max_y)),
                    size=self._rng.randint(self.star_config.min_size, self.star_config.max_size),
                    base_alpha=self._rng.randint(self.star_config.min_alpha, self.star_config.max_alpha),
                    twinkle_speed=self._rng.uniform(
                        self.star_config.twinkle_speed_min,
                        self.star_config.twinkle_speed_max,
                    ),
                    twinkle_phase=self._rng.uniform(0.0, math.tau),
                )
            )

    def update(self, delta_time: float) -> None:
        """Advance the time-of-day state."""
        self.elapsed_seconds += delta_time
        if not self.config.enabled:
            return
        cycle_seconds = max(1.0, self.config.day_duration_minutes * 60.0)
        delta_hours = (delta_time / cycle_seconds) * 24.0
        self.current_time_hours = self._normalize_hours(self.current_time_hours + delta_hours)

    def reset_to_start_time(self) -> None:
        """Reset the cycle to the configured new-run start time."""
        self.current_time_hours = self._choose_start_time()
        self.elapsed_seconds = 0.0

    def get_phase_name(self) -> str:
        """Return the logical time-of-day phase."""
        time_value = self.current_time_hours
        ranges = self.config.phase_ranges
        if ranges.dawn_start <= time_value < ranges.day_start:
            return "dawn"
        if ranges.day_start <= time_value < ranges.dusk_start:
            return "day"
        if ranges.dusk_start <= time_value < ranges.night_start:
            return "dusk"
        return "night"

    def get_star_visibility(self) -> float:
        """Return the current star visibility in the range [0.0, 1.0]."""
        time_value = self.current_time_hours
        ranges = self.config.phase_ranges
        if ranges.day_start <= time_value < ranges.dusk_start:
            return 0.0
        if ranges.dusk_start <= time_value < ranges.night_start:
            return self._safe_inverse_lerp(ranges.dusk_start, ranges.night_start, time_value)
        if ranges.night_start <= time_value or time_value < ranges.dawn_start:
            return 1.0
        return 1.0 - self._safe_inverse_lerp(ranges.dawn_start, ranges.day_start, time_value)

    def get_star_alpha(self, star: Star) -> int:
        """Return the alpha value for a specific star."""
        visibility = self.get_star_visibility()
        if visibility <= 0.0:
            return 0

        twinkle_factor = 1.0
        if self.star_config.twinkle_enabled and visibility > 0.0:
            wave = math.sin(self.elapsed_seconds * star.twinkle_speed + star.twinkle_phase)
            twinkle_factor += wave * self.star_config.twinkle_amplitude
        alpha = star.base_alpha * visibility * max(0.1, twinkle_factor)
        return max(0, min(255, int(alpha)))

    def get_star_screen_x(self, star: Star, camera_x: float, width: int) -> int:
        """Return the screen x position of a star with parallax motion."""
        if width <= 0:
            return 0
        parallax_offset = camera_x * self.star_config.parallax_speed
        x_position = (star.x - parallax_offset) % float(width)
        return int(x_position)

    @staticmethod
    def format_time_hours(time_value: float) -> str:
        """Format fractional hours as HH:MM."""
        normalized = TimeSystem._normalize_hours(time_value)
        total_minutes = int(round(normalized * 60.0)) % (24 * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def _normalize_hours(value: float) -> float:
        """Execute normalize hours.
        
        Args:
            value: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        return value % 24.0

    @staticmethod
    def _safe_inverse_lerp(start: float, end: float, value: float) -> float:
        """Execute safe inverse lerp.
        
        Args:
            start: Input value used by this operation.
            end: Input value used by this operation.
            value: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        if math.isclose(start, end):
            return 1.0
        factor = (value - start) / (end - start)
        return max(0.0, min(1.0, factor))


    def get_world_tint(self) -> Color:
        """Return the current world tint color."""
        return self._get_interpolated_tint(target="world")

    def get_sky_tint(self) -> Color:
        """Return the current sky tint color."""
        return self._get_interpolated_tint(target="sky")

    def _get_interpolated_tint(self, target: str) -> Color:
        """Return a smoothly interpolated tint for the requested target.

        Args:
            target: Tint palette name, either ``world`` or ``sky``.

        Returns:
            Interpolated RGBA tint for the current in-game time.
        """
        palette = {
            "world": {
                "dawn": self.tint_config.dawn_world,
                "day": self.tint_config.day_world,
                "dusk": self.tint_config.dusk_world,
                "night": self.tint_config.night_world,
            },
            "sky": {
                "dawn": self.tint_config.dawn_sky,
                "day": self.tint_config.day_sky,
                "dusk": self.tint_config.dusk_sky,
                "night": self.tint_config.night_sky,
            },
        }[target]
        return self._interpolate_day_cycle_palette(palette)

    def _interpolate_day_cycle_palette(self, palette: dict[str, Color]) -> Color:
        """Interpolate a color palette around the full 24-hour cycle.

        Args:
            palette: Mapping from phase name to RGBA tint color.

        Returns:
            Smoothly interpolated RGBA tint for the current time.
        """
        ranges = self.config.phase_ranges
        time_value = self.current_time_hours
        if ranges.day_start <= time_value < ranges.dusk_start:
            return palette["day"]

        if ranges.dusk_start <= time_value < ranges.night_start:
            factor = self._safe_inverse_lerp(ranges.dusk_start, ranges.night_start, time_value)
            return self._interpolate_three_stage_palette(
                palette["day"],
                palette["dusk"],
                palette["night"],
                factor,
            )

        if ranges.dawn_start <= time_value < ranges.day_start:
            factor = self._safe_inverse_lerp(ranges.dawn_start, ranges.day_start, time_value)
            return self._interpolate_three_stage_palette(
                palette["night"],
                palette["dawn"],
                palette["day"],
                factor,
            )

        return palette["night"]

    def _interpolate_three_stage_palette(
        self,
        start: Color,
        middle: Color,
        end: Color,
        factor: float,
    ) -> Color:
        """Interpolate through a midpoint color without phase-boundary jumps.

        Args:
            start: Color at the beginning of the transition.
            middle: Color reached halfway through the transition.
            end: Color at the end of the transition.
            factor: Raw transition factor in the range [0.0, 1.0].

        Returns:
            Smoothly interpolated RGBA color.
        """
        if factor < 0.5:
            local_factor = self._smoothstep(factor * 2.0)
            return self._lerp_color(start, middle, local_factor)
        local_factor = self._smoothstep((factor - 0.5) * 2.0)
        return self._lerp_color(middle, end, local_factor)

    @staticmethod
    def _smoothstep(factor: float) -> float:
        """Return a smoothed interpolation factor.

        Args:
            factor: Raw interpolation factor.

        Returns:
            Smoothed factor clamped to the range [0.0, 1.0].
        """
        clamped = max(0.0, min(1.0, factor))
        return clamped * clamped * (3.0 - 2.0 * clamped)

    @staticmethod
    def _lerp_color(start: Color, end: Color, factor: float) -> Color:
        """Execute lerp color.
        
        Args:
            start: Input value used by this operation.
            end: Input value used by this operation.
            factor: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        clamped = max(0.0, min(1.0, factor))
        return tuple(
            int(round(start[index] + (end[index] - start[index]) * clamped))
            for index in range(4)
        )

    @staticmethod
    def _parse_color(value: object, default: Color) -> Color:
        """Execute parse color.
        
        Args:
            value: Input value used by this operation.
            default: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        if not isinstance(value, (list, tuple)) or len(value) != 4:
            return default
        try:
            return tuple(max(0, min(255, int(component))) for component in value)
        except (TypeError, ValueError):
            return default
