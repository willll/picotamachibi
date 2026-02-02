import framebuf
from machine import Timer
from time import sleep


class Event():
    """ Models events that can happen, with timers and pop up messages """
    name = ""
    value = 0
    sprite = None
    timer = -1 # -1 means no timer set
    timer_ms = 0
    __callback = None
    message = ""
    done = False
    _timer_instance = None # holds the timer instance

    def __init__(self, name=None, sprite=None, value=None, callback=None):
        """ Create a new event """

        if name:
            self.name = name
        if sprite:
            self.sprite = sprite
        if value:
            self.value = value
        if callback is not None:
            self.__callback = callback
        # Shared popup buffer to avoid repeated large allocations.
        self._popup_buf = None
        self._popup_fb = None
        if not hasattr(Event, "_shared_popup_buf"):
            Event._shared_popup_buf = None
            Event._shared_popup_fb = None

    def popup(self, display):
        # display popup window
        # show sprite
        # show message
        popup_w = 120
        popup_h = 48
        x = (display.width - popup_w) // 2
        y = (display.height - popup_h) // 2
        if Event._shared_popup_fb is None:
            Event._shared_popup_buf = bytearray(popup_w * popup_h * 2)
            Event._shared_popup_fb = framebuf.FrameBuffer(Event._shared_popup_buf, popup_w, popup_h, framebuf.RGB565)
        fbuf = Event._shared_popup_fb
        fg = 0x0000
        bg = 0xFFFF
        fbuf.fill(bg)
        fbuf.rect(0, 0, popup_w, popup_h, fg)
        self.sprite.draw(fbuf, 8, 12)
        fbuf.text(self.message, 52, 20, fg)
        display.blit(fbuf, x, y)
#         oled.blit(fbuf, 0, 16)
        display.show()
#         oled.show()
        sleep(2)

    def tick(self):
        """ Progresses the animation on frame """

        self.timer_ms += 1
        if self.timer_ms >= self.timer:
            if self.__callback is not None:
                print("poop check callback")
                self.__callback()
                self.timer = -1
                self.timer_ms = 0
            else:
                # print("Timer Alert!")
                self.done = True

    def reset(self):
        self.done = False

    def start(self, duration):
        """ Start a timer that will run a callback routine when complete """
#         print(f"Starting Timer for {duration/1000} seconds")
        self.done = False

        if self._timer_instance:
            self._timer_instance.deinit()  # Stop any previous timer

        self._timer_instance = Timer(-1)  # Create a one-shot timer
        self._timer_instance.init(period=duration, mode=Timer.ONE_SHOT, callback=self._timer_callback)

    def _timer_callback(self, t):
        """ Internal method to handle the timer callback """
        if self.__callback:
#             print("Timer completed, executing callback.")
            self.__callback()
#         else:
#             print("Timer complete, but no callback")
        self.done = True
#         self.timer = -1
