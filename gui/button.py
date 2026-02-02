from machine import Pin


class Button():
    """ Models a button, check the status with is_pressed """

    # The private variables
    __pressed = False
    __pin = 0
    __button_down = False

    def __init__(self, pin:int, active_low:bool=True):
        """ Sets up the button """
        pull = Pin.PULL_UP if active_low else Pin.PULL_DOWN
        self.__pin = Pin(pin, Pin.IN, pull)
        self.__pressed = False
        self.__active_low = active_low

    @property
    def is_pressed(self)->bool:
        """ Returns the current state of the button """
        pressed = self.__pin.value() == (0 if self.__active_low else 1)
        if pressed:
            self.__button_down = True
            return True
        if self.__pin.value() == 1:
            self.__button_down = False
            return False
            # if not self.__button_down:

            #     self.__button_down = False
            #     return True
            # else:
            #     return False
