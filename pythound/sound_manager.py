from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

import psutil


class Sound:
    def __init__(self, file_path: Path, sound_volume: Optional[int] = None, sound_speed: int = None) -> None:
        self.file_path: Path = file_path
        self.process: Optional[psutil.Process] = None
        self._loop: Optional[int] = None
        self._volume = None  # initialize _volume before using probperty 'volume'
        self.volume: Optional[int] = sound_volume  # volume property validate
        self.speed: Optional[int] = sound_speed  # volume property validate

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, value: int) -> None:
        if self._volume != value:
            if value > 100:
                print("Volumes above 100 are treated as 100.", flush=True)
                value = 100
            elif value < 0:
                print("Negative volumes are treated as 0.", flush=True)
                value = 0

            self._volume = value
            print(f"Set sound volume to {value}.", flush=True)


class Player:
    def __init__(self, app="ffplay", player_volume: int = 100, player_speed: float = 1.0) -> None:
        self.app_name: str = app
        self.app_args: List[str] = []
        self.sound_files: List[Sound] = []  # {sound_id:
        self._volume = 100  # initialize _volume before using probperty 'volume'
        self.volume: int = player_volume  # volume property validate
        self.speed = player_speed

        if self.app_name == "ffplay":
            self.app_args = ["-nodisp", "-autoexit", "-loglevel", "quiet"]

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, value: int) -> None:
        if self._volume != value:
            if value > 100:
                print("Volumes above 100 are treated as 100.", flush=True)
                value = 100
            elif value < 0:
                print("Negative volumes are treated as 0.", flush=True)
                value = 0

            self._volume = value
            print(f"Set player volume to {value}.", flush=True)

    def add_sound(
            self,
            file_path: Path,
            initial_sound_volume: Optional[int] = None,
            initial_sound_speed: Optional[int] = None,
    ) -> Sound:
        new_sound = Sound(
            file_path,
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
        app_params.extend(self.app_args)

        volume = sound.volume if sound.volume else self.volume
        app_params.extend(["-volume", str(volume)])

        if loop != 0:
            app_params.extend(["-loop", str(loop)])

        speed = sound.speed if sound.speed else self.speed
        app_params.extend(["-af", f"atempo={speed}"])

        app_params.append(str(sound.file_path))

        process = subprocess.Popen(app_params)
        print(f"Play '{sound.file_path}'.", flush=True)

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
                flush=True
            )
            return

    def stop(self, sound: Sound) -> None:
        if not sound.process:
            return

        self._reset_process_state(sound)
        print(f"Stop '{sound.file_path}'.", flush=True)

    def stop_all(self) -> None:
        for sound in self.sound_files:
            self.stop(sound)

    def continue_sound(self, sound: Sound) -> None:
        if not sound.process:
            print(
                f"Error in continuing '{sound.file_path}', sound is not paused OR is a sound effect, which can't be continued.",
                flush=True,
            )
            return

        if sound.process.status() == psutil.STATUS_RUNNING:
            print(
                f"Error in contining '{sound.file_path}', sound is already playing.",
                flush=True,
            )
        elif sound.process.status() in (
                psutil.STATUS_STOPPED,
                psutil.STATUS_PARKED,
                psutil.STATUS_DISK_SLEEP,
        ):
            sound.process.resume()
            print(f"Continue '{sound.file_path}'.", flush=True)
        else:
            self._reset_process_state(sound)

    def pause_sound(self, sound: Sound) -> None:
        if not sound.process:
            print(
                f"Error in pausing '{sound.file_path}', sound is not playing OR is a sound effect, which can't paused.",
                flush=True,
            )
            return

        if sound.process.status() == psutil.STATUS_RUNNING:
            sound.process.suspend()
            print(f"Pause '{sound.file_path}'.", flush=True)
        elif sound.process.status() == psutil.STATUS_SUSPENDED:
            print(
                f"Error in pausing '{sound.file_path}', sound is already paused.",
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
