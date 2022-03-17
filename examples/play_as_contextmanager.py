# player has implemented a context manager,
# which calls the stop_all() automatically on exiting the context

from time import sleep
from pathlib import Path

from pythound.sound_manager import Player

with Player() as sound_player:
    # add sound and initialize sound object
    sound = sound_player.add_sound(
        Path(__file__).parent / "soundfiles/pachelbel_canon_example.mp3"
    )

    # play initialized sound
    sound_player.play(sound)  # will play async!

    sleep(10)  # sleep 10 seconds
