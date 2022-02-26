from pathlib import Path

from pythound.pythound import PyThound

try:
    sound_manager = PyThound(player_volume=90)  # set global volume to 90 %

    sound = sound_manager.add_sound(Path("example_3.mp3"))
    sound.volume = 70  # set individual sound volume to 70 %

    sound_manager.play(
        sound, loop=-1
    )  # loop: -1=infinite, 0=no loop, number > 0 = n repeats
    sound_manager.wait_for(sound)
finally:
    sound_manager.stop_all()
