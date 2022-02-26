from pathlib import Path

from pythound.pythound import PyThound

try:
    sound_manager = PyThound()
    sound = sound_manager.add_sound(Path("example_3.mp3"))
    sound_manager.play(
        sound, loop=-1
    )  # loop: -1=infinite, 0=no loop, number > 0 = n repeats
finally:
    sound_manager.stop_all()
