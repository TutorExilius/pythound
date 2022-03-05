from pathlib import Path

from pythound.sound_manager import Player

try:
    # initial player with volume of 95
    sound_player = Player(player_volume=95)

    # set speed of player
    sound_player.settings.set_speed(0.8)

    # add sound and initialize sound object
    sound = sound_player.add_sound(Path("example.mp3"))

    # set speed of individual sound
    sound.settings.set_speed(0.5)

    # set volume of individual sound
    sound.settings.set_volume(70)

    # play sound async, start on sec 20
    sound_player.play(
        sound, start_on_sec=20
    )

    # wait for sound (synced)
    sound_player.wait_for(sound)
finally:
    sound_player.stop_all()
