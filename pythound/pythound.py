from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

import psutil


class Sound:
    def __init__(self, file_path: Path) -> None:
        self.file_path: Path = file_path
        self.process: Optional[psutil.Process] = None
        self.loops = None


class PyThound:
    def __init__(self, app="ffplay"):
        self.app_name: str = app
        self.app_args: List[str] = []
        self.sound_files: List[Sound] = []  # {sound_id:

        if self.app_name == "ffplay":
            self.app_args = ["-nodisp", "-autoexit", "-loglevel", "quiet"]

    def add_sound(self, file_path: Path) -> Sound:
        new_sound = Sound(file_path)
        self.sound_files.append(new_sound)
        return new_sound

    def play(self, sound: Sound, loop: int = 0) -> None:
        """
        loop:
            0 = no loop
            n = loop n times
            -1 = infinite loop
        """
        if not sound.process:
            app_params = [self.app_name]
            app_params.extend(self.app_args)

            if loop != 0:
                app_params.extend(["-loop", str(loop)])

            app_params.append(str(sound.file_path))

            process = subprocess.Popen(app_params)
            print(f"Play '{sound.file_path}'.", flush=True)

            ps_process = psutil.Process(pid=process.pid)
            sound.process = ps_process
        elif sound.process.status() == psutil.STATUS_RUNNING:
            print(
                f"Error in playing '{sound.file_path}', sound is already playing.",
                flush=True,
            )
        elif sound.process.status() == psutil.STATUS_SUSPENDED:
            print(
                f"Error in playing '{sound.file_path}', sound is paused, continue with: continue_sound().",
                flush=True,
            )
        else:
            self._reset_process_state(sound)

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
        sound.process = None

        try:
            process.terminate()
        except:
            pass

        try:
            process.kill()
        except:
            pass
