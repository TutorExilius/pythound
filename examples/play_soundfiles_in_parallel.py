import time
from pathlib import Path
from time import sleep

from pythound.sound_manager import Player

try:
    # initialize player instance
    sound_player = Player()

    # add sound and initialize sound object
    background_music = sound_player.add_sound(
        Path(__file__).parent / "soundfiles/pachelbel_canon_example.mp3"
    )

    # play initialized sound
    sound_player.play(
        background_music, loop=0
    )  # will play background music endloss (async)

    time.sleep(2)  # sleep 2 seconds

    # add sound and initialize sound object
    sound_effect = sound_player.add_sound(
        Path(__file__).parent / "soundfiles/sound_effect.mp3"
    )

    sound_player.play(sound_effect, loop=2)  # will play sound effect twice (async)

    sleep(10)  # sleep 10 seconds

finally:  # end of script will immediately stop async sound
    sound_player.stop_all()
