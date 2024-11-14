#  doc: https://github.com/trainman419/python-cec

import cec

class TvController:
    def __init__(self):
        cec.init()
        devices = cec.list_devices()
        self.tv = devices[0]

    def set_active(self):
        cec.set_active_source()

    def turn_off(self): 
        self.tv.standby()   

    def volume_up(self, amount):
        print('in volume')
        for _ in range(amount):
            cec.volume_up()

    def volume_down(self, amount):
        for _ in range(amount):
            cec.volume_down()

    def change_volume(self, amount):
        if amount < 0:
            self.volume_down(abs(amount))
        else:
            self.volume_up(amount)




