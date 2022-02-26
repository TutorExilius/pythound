from pathlib import Path

from pythound.sound_manager import Player

try:
    sound_player = Player(player_volume=90)  # set global volume to 90 %

    sound = sound_player.add_sound(Path("example_3.mp3"))
    sound.volume = 70  # set individual sound volume to 70 %

    sound_player.play(
        sound, loop=-1
    )  # loop: -1=infinite, 0=no loop, number > 0 = n repeats
    sound_player.wait_for(sound)
finally:
    sound_player.stop_all()