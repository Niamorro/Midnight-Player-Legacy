# buttonlogic.py
class ButtonLogic:
    def __init__(self, play_function, volume_function, position_function):
        self.play_function = play_function
        self.volume_function = volume_function
        self.position_function = position_function

    def play_button_clicked(self):
        self.play_function()

    def volume_slider_changed(self):
        self.volume_function()

    def time_slider_released(self):
        self.position_function()
