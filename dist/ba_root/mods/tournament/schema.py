"""all the dataclass schema for tournament."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from server.enums import SeriesType, TournamentStage, TournamentType


@dataclass
class SeasonSchema:
    """schema for a unique season."""

    series: SeriesType = SeriesType.BO3
    type: TournamentType = TournamentType.SOLO
    stage: TournamentStage = TournamentStage.REGISTRATION
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SeasonSchema:
        return cls(
            series=SeriesType(data.get("series", SeriesType.BO3)),
            type=TournamentType(data.get("type", TournamentType.SOLO)),
            stage=TournamentStage(data.get("stage", TournamentStage.REGISTRATION)),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "series": self.series,
            "type": self.type,
            "stage": self.stage,
            "created_at": self.created_at,
        }


@dataclass
class TournamentSchema:
    """Schema for all the seasons."""

    active_season: str = "0"
    seasons: dict[str, SeasonSchema] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TournamentSchema:
        active_season = data.get("active_season", "0")
        seasons = data.get("seasons", {})
        parsed_seasons = {
            season_id: SeasonSchema.from_dict(meta)
            for season_id, meta in seasons.items()
            if isinstance(meta, dict)
        }
        return cls(active_season=active_season, seasons=parsed_seasons)

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_season": self.active_season,
            "seasons": {
                season_id: meta.to_dict() for season_id, meta in self.seasons.items()
            },
        }
