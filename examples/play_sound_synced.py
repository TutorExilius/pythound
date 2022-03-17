from pathlib import Path

from pythound.sound_manager import Player

try:
    # initialize player instance
    sound_player = Player()

    # add sound and initialize sound object
    sound = sound_player.add_sound(
        Path(__file__).parent / "soundfiles/pachelbel_canon_example.mp3"
    )

    # play initialized sound
    sound_player.play(sound)  # will play async!

    sound_player.wait_for(sound)  # SYNC - will wait till sound is finished playing

finally:  # end of script will immediately stop async sound
    sound_player.stop_all()
