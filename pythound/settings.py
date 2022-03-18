import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SupportedApps(str, Enum):
    FFPLAY = "ffplay"


class Settings:
    def __init__(
            self,
            parent_class_name: str = "",
            use_app: SupportedApps = SupportedApps.FFPLAY,
    ):
        self._parent_class_name = parent_class_name

        self._app_name = use_app
        self._app_configs = self._load_config()

        self._volume: Optional[int] = None

        volume: Optional[int] = self._app_configs.get("INITIAL_PLAYER_VOLUME")

        if volume is None:
            volume = 100

        self.set_volume(volume)

        self._speed: Optional[float] = None

        speed: Optional[float] = self._app_configs.get("INITIAL_PLAYER_SPEED")

        if speed is None:
            speed = 1.0

        self.set_speed(speed)

    @property
    def app_name(self) -> SupportedApps:
        return self._app_name

    @property
    def volume(self) -> Optional[int]:
        return self._volume

    def _load_config(
            self,
    ) -> Dict[str, Any]:
        if self.app_name == SupportedApps.FFPLAY:
            from pythound.app_configs import ffplay_config as config

            return {k: v for k, v in vars(config).items() if not k.startswith("_")}

        return {}

    def get_app_args(self) -> List[Optional[str]]:
        app_path = self._app_configs["APP_PATH"]

        if app_path is not None:
            app_path = Path(app_path)

            if not app_path.exists():
                raise FileNotFoundError(f"App not found: '{app_path}'")

            app = app_path
        else:
            app = self.app_name

        if self.app_name == SupportedApps.FFPLAY:
            if isinstance(app, Path):
                app = str(app)

            if re.search(r"\s", app):
                app = f"'{app}'"

            return [app, "-nodisp", "-autoexit", "-loglevel", "quiet"]

        return []

    def set_volume(self, volume: int) -> bool:
        min_volume, max_volume = self._app_configs["SUPPORTED_VOLUME_RANGE"]
        if min_volume <= volume <= max_volume:
            self._volume = volume
            print(
                f"{self.app_name} ({self._parent_class_name}): Set volume to {volume}.",
                flush=True,
            )
            return True
        else:
            supported_volume_range_str = f"{min_volume} - {max_volume}"
            print(
                (
                    f"{self.app_name} ({self._parent_class_name}): "
                    f"Can't set volume to {volume} "
                    f"(supported values: {supported_volume_range_str})."
                ),
                flush=True,
            )
            return False

    @property
    def speed(self) -> Optional[float]:
        return self._speed

    def set_speed(self, speed: float) -> bool:
        min_speed, max_speed = self._app_configs["SUPPORTED_SPEED_RANGE"]
        if min_speed <= speed <= max_speed:
            self._speed = speed
            print(
                f"{self.app_name} ({self._parent_class_name}): Set speed to {speed}.",
                flush=True,
            )
            return True
        else:
            supported_speed_range_str = f"{min_speed} - {max_speed}"
            print(
                (
                    f"{self.app_name} ({self._parent_class_name}): "
                    f"Can't set speed to {speed} "
                    f"(supported values: {supported_speed_range_str})."
                ),
                flush=True,
            )
            return False
