from __future__ import annotations

import subprocess
from pathlib import Path
from types import TracebackType
from typing import List, Optional, Tuple, Union

import psutil


class FFPLAY_Settings:
    def __init__(self, parent_class_name: str = ""):
        self._app_name: str = "ffplay"
        self._parent_class_name = parent_class_name
        self.supported_volume_range: Tuple[int, int] = (0, 100)
        self.supported_speed_range: Tuple[float, float] = (0.5, 100.0)
        self._volume: Optional[int] = None
        self._speed: Optional[float] = None

    @property
    def app_name(self) -> str:
        return self._app_name

    @property
    def volume(self) -> Optional[int]:
        return self._volume

    def set_volume(self, volume: int) -> bool:
        min_volume, max_volume = self.supported_volume_range
        if min_volume <= volume <= max_volume:
            self._volume = volume
            print(
                f"{self.app_name} ({self._parent_class_name}): Set volume to {volume}.",
                flush=True,
            )
            return True
        else:
            supported_volume_range_str = "{} - {}".format(*self.supported_volume_range)
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
        min_speed, max_speed = self.supported_speed_range
        if min_speed <= speed <= max_speed:
            self._speed = speed
            print(
                f"{self.app_name} ({self._parent_class_name}): Set speed to {speed}.",
                flush=True,
            )
            return True
        else:
            supported_speed_range_str = "{} - {}".format(*self.supported_speed_range)
            print(
                (
                    f"{self.app_name} ({self._parent_class_name}): "
                    f"Can't set speed to {speed} "
                    f"(supported values: {supported_speed_range_str})."
                ),
                flush=True,
            )
            return False


class Sound:
    def __init__(
        self,
        app_name: str,
        sound_file_path: Path,
        sound_volume: Optional[int] = None,
        sound_speed: Optional[float] = None,
    ) -> None:
        if not sound_file_path.exists():
            raise FileNotFoundError(f"File not found: '{sound_file_path}'")

        self.sound_file_path: Path = sound_file_path
        self._process: Optional[psutil.Process] = None
        self._duration: int = 0
        self._loop: Optional[int] = None

        if app_name.lower() == "ffplay":
            self.settings = FFPLAY_Settings(self.__class__.__name__)

            if sound_volume:
                self.settings.set_volume(sound_volume)

            if sound_speed:
                self.settings.set_speed(sound_speed)


class Player:
    def __init__(
        self,
        app_name: str = "ffplay",
        player_volume: int = 100,
        player_speed: float = 1.0,
    ) -> None:
        self.sound_files: List[Sound] = []  # {sound_id:
        self._app_args: List[str] = []

        if app_name.lower() == "ffplay":
            self._app_args = ["-nodisp", "-autoexit", "-loglevel", "quiet"]
            self.settings = FFPLAY_Settings(self.__class__.__name__)
            self.settings.set_volume(player_volume)
            self.settings.set_speed(player_speed)

    def __enter__(self) -> Player:
        return self

    def __exit__(
        self,
        exc_type: Optional[BaseException],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.stop_all()

    def _get_duration(self, sound: Sound) -> int:
        duration: int = -1

        if self.settings.app_name == "ffplay":
            ffprobe_args = [
                "ffprobe",
                "-i",
                str(sound.sound_file_path),
                "-show_entries",
                "format=duration",
                "-v",
                "quiet",
                "-of",
                "csv=p=0",
            ]

            process = subprocess.Popen(ffprobe_args, stdout=subprocess.PIPE)
            out, err = process.communicate()
            out_str = out.decode(encoding="utf8").strip()

            if out_str:
                duration = int(out.decode(encoding="utf8").strip().split(".")[0])

        return duration

    def _create_process(self, sound: Sound, start_on_sec: int, loop: int) -> None:
        app_name = self.settings.app_name
        app_params = [app_name]
        app_params.extend(self._app_args)

        volume = (
            sound.settings.volume if sound.settings.volume else self.settings.volume
        )
        app_params.extend(["-volume", str(volume)])
        app_params.extend(["-loop", str(loop)])

        speed = sound.settings.speed if sound.settings.speed else self.settings.speed
        app_params.extend(["-af", f"atempo={speed}"])
        app_params.extend(["-ss", str(start_on_sec)])
        app_params.append(str(sound.sound_file_path))

        sound._process = psutil.Popen(app_params)

    def add_sound(
        self,
        sound_file_path: Union[Path, str],
        initial_sound_volume: Optional[int] = None,
        initial_sound_speed: Optional[int] = None,
    ) -> Sound:
        if isinstance(sound_file_path, str):
            sound_file_path = Path(sound_file_path)

        new_sound = Sound(
            self.settings.app_name,
            sound_file_path=sound_file_path,
            sound_volume=initial_sound_volume,
            sound_speed=initial_sound_speed,
        )

        duration = self._get_duration(new_sound)
        new_sound._duration = duration

        self.sound_files.append(new_sound)
        return new_sound

    def play(
        self,
        sound: Sound,
        loop: int = 1,
        start_on_sec: int = 0,
    ) -> None:
        """
        loop:
            n = loop n times
            0 = endless
        """

        if self.settings.app_name == "ffplay":
            if start_on_sec < 0:
                start_on_sec = 0

            if loop < 0:
                loop = 0

        sound._loop = loop

        self._reset_process_state(sound)

        self._create_process(sound=sound, start_on_sec=start_on_sec, loop=loop)
        print(f"Play '{sound.sound_file_path}'.", flush=True)

    def wait_for(self, sound: Sound) -> None:
        if sound._process is None or sound._process.status() != psutil.STATUS_RUNNING:
            return

        if sound._loop != 0:
            sound._process.wait()
        else:
            print(
                (
                    "Error in wait_for(): can't wait for a sound, "
                    "which is in endless loop."
                ),
                flush=True,
            )

    def stop(self, sound: Sound) -> None:
        if not sound._process:
            return

        self._reset_process_state(sound)
        print(f"Stop '{sound.sound_file_path}'.", flush=True)

    def stop_all(self) -> None:
        for sound in self.sound_files:
            self.stop(sound)

    def continue_sound(self, sound: Sound) -> None:
        if not sound._process:
            print(
                f"Error in continuing '{sound.sound_file_path}',"
                f"sound is not paused OR is a sound effect, which can't be continued.",
                flush=True,
            )
            return

        if sound._process.status() == psutil.STATUS_RUNNING:
            print(
                (
                    f"Error in contining '{sound.sound_file_path}', "
                    f"sound is already playing."
                ),
                flush=True,
            )
        elif sound._process.status() in (
            psutil.STATUS_STOPPED,
            psutil.STATUS_PARKED,
            psutil.STATUS_DISK_SLEEP,
            psutil.STATUS_SLEEPING,
        ):
            sound._process.resume()
            print(f"Continue '{sound.sound_file_path}'.", flush=True)
        else:
            self._reset_process_state(sound)

    def pause_sound(self, sound: Sound) -> None:
        if not sound._process:
            print(
                (
                    f"Error in pausing '{sound.sound_file_path}', "
                    f"sound is not playing OR is a sound effect, which can't paused."
                ),
                flush=True,
            )
            return

        if sound._process.status() == psutil.STATUS_RUNNING:
            sound._process.suspend()
            print(f"Pause '{sound.sound_file_path}'.", flush=True)
        elif sound._process.status() in (
            psutil.STATUS_STOPPED,
            psutil.STATUS_PARKED,
            psutil.STATUS_DISK_SLEEP,
            psutil.STATUS_SLEEPING,
        ):
            print(
                (
                    f"Error in pausing '{sound.sound_file_path}', "
                    f"sound is already paused or stopped.",
                ),
                flush=True,
            )
        else:
            self._reset_process_state(sound)

    def _reset_process_state(self, sound: Sound) -> None:
        if sound._process is None:
            return

        process = sound._process
        sound._process = None
        sound._loop = None

        try:
            process.terminate()
        except:  # noqa
            try:
                process.kill()
            except:  # noqa
                pass
