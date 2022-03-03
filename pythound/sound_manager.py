from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

import psutil


class FFPLAY_Properties:
    def __init__(
            self,
            parent: str,
            volume: Optional[int] = None,
            speed: Optional[float] = None,
    ):
        self._parent = parent
        self.volume = volume
        self.speed = speed

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, value: Optional[int]) -> None:
        if value is None:
            if self._parent != "Sound":
                print("It is not possible to set the player volume to None.")
                return
        else:
            if value > 100:
                print("Volumes above 100 are treated as 100.", flush=True)
                value = 100
            elif value < 0:
                print("Negative volumes are treated as 0.", flush=True)
                value = 0

        self._volume = value
        print(f"Set {self._parent} sound volume to {value}.", flush=True)

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: Optional[float]) -> None:
        if value is None:
            if self._parent != "Sound":
                print("It is not possible to set the player speed to None.")
                return
        else:
            if value > 100:
                value = 100
                print("Speed above 100 is treated as 100.", flush=True)
            elif value < 0.5:
                value = 0.5
                print("Speed less than 0.5 is treated as 0.5", flush=True)

        self._speed = value
        print(f"Set {self._parent} speed to {value}.", flush=True)


class Sound:
    def __init__(
            self,
            app_name: str,
            sound_file_path: Path,
            sound_volume: Optional[int] = None,
            sound_speed: Optional[float] = None,
    ) -> None:
        self.app_name = app_name
        self.sound_file_path: Path = sound_file_path
        self.process: Optional[psutil.Process] = None
        self._loop: Optional[int] = None

        if self.app_name == "ffplay":
            self._properies = FFPLAY_Properties(
                parent="Sound",
                volume=sound_volume,
                speed=sound_speed,
            )

    @property
    def volume(self) -> int:
        return self._properies.volume

    @volume.setter
    def volume(self, value: int) -> None:
        self._properies.volume = value

    @property
    def speed(self) -> float:
        return self._properies.speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._properies.speed = value


class Player:
    def __init__(
            self, app_name="ffplay", player_volume: int = 100, player_speed: float = 1.0
    ) -> None:
        self.app_name: str = app_name
        self.sound_files: List[Sound] = []  # {sound_id:
        self._app_args: List[str] = []

        if self.app_name == "ffplay":
            self._app_args = ["-nodisp", "-autoexit", "-loglevel", "quiet"]
            self._properies = FFPLAY_Properties(
                parent="Player",
                volume=player_volume or 100,
                speed=player_speed or 1.0,
            )

    @property
    def volume(self) -> int:
        return self._properies.volume

    @volume.setter
    def volume(self, value: int) -> None:
        self._properies.volume = value

    @property
    def speed(self) -> float:
        return self._properies.speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._properies.speed = value

    def add_sound(
            self,
            sound_file_path: Path,
            initial_sound_volume: Optional[int] = None,
            initial_sound_speed: Optional[int] = None,
    ) -> Sound:
        new_sound = Sound(
            self.app_name,
            sound_file_path=sound_file_path,
            sound_volume=initial_sound_volume,
            sound_speed=initial_sound_speed,
        )
        self.sound_files.append(new_sound)
        return new_sound

    def play(self, sound: Sound, loop: int = 0) -> None:
        """
        loop:
            0 = no loop
            n = loop n times
            -1 = infinite loop
        """

        if sound.process:
            self._reset_process_state(sound)

        app_params = [self.app_name]
        app_params.extend(self._app_args)

        volume = sound.volume if sound.volume else self.volume
        app_params.extend(["-volume", str(volume)])

        if loop != 0:
            app_params.extend(["-loop", str(loop)])

        speed = sound.speed if sound.speed else self.speed
        app_params.extend(["-af", f"atempo={speed}"])

        app_params.append(str(sound.sound_file_path))

        process = subprocess.Popen(app_params)
        print(f"Play '{sound.sound_file_path}'.", flush=True)

        ps_process = psutil.Process(pid=process.pid)
        sound.process = ps_process
        sound._loop = loop

    def wait_for(self, sound: Sound) -> None:
        if not sound.process or sound.process.status() != psutil.STATUS_RUNNING:
            return

        if sound._loop != -1:
            sound.process.wait()
        else:
            print(
                "Error in wait_for(): can't wait for a sound, which is in endless loop.",
                flush=True,
            )

    def stop(self, sound: Sound) -> None:
        if not sound.process:
            return

        self._reset_process_state(sound)
        print(f"Stop '{sound.sound_file_path}'.", flush=True)

    def stop_all(self) -> None:
        for sound in self.sound_files:
            self.stop(sound)

    def continue_sound(self, sound: Sound) -> None:
        if not sound.process:
            print(
                f"Error in continuing '{sound.sound_file_path}', sound is not paused OR is a sound effect, which can't be continued.",
                flush=True,
            )
            return

        if sound.process.status() == psutil.STATUS_RUNNING:
            print(
                f"Error in contining '{sound.sound_file_path}', sound is already playing.",
                flush=True,
            )
        elif sound.process.status() in (
                psutil.STATUS_STOPPED,
                psutil.STATUS_PARKED,
                psutil.STATUS_DISK_SLEEP,
        ):
            sound.process.resume()
            print(f"Continue '{sound.sound_file_path}'.", flush=True)
        else:
            self._reset_process_state(sound)

    def pause_sound(self, sound: Sound) -> None:
        if not sound.process:
            print(
                f"Error in pausing '{sound.sound_file_path}', sound is not playing OR is a sound effect, which can't paused.",
                flush=True,
            )
            return

        if sound.process.status() == psutil.STATUS_RUNNING:
            sound.process.suspend()
            print(f"Pause '{sound.sound_file_path}'.", flush=True)
        elif sound.process.status() == psutil.STATUS_SUSPENDED:
            print(
                f"Error in pausing '{sound.sound_file_path}', sound is already paused.",
                flush=True,
            )
        else:
            self._reset_process_state(sound)

    def _reset_process_state(self, sound: Sound) -> None:
        if sound.process is None:
            return

        process = sound.process
        sound._loop = None
        sound.process = None

        try:
            process.terminate()
        except:
            pass

        try:
            process.kill()
        except:
            pass
