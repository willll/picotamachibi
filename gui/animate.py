from os import listdir
import gc


class Animate():
    filename = None
    """ other animations types: 
        - loop
        - bounce
        - reverse
    """
    @property
    def set(self)->bool:
        return self.__set

    @set.setter
    def set(self, value:bool):
        self.__set = value
        if value: # if value is True
            self.load()
        else:
            self.unload()

    @property
    def speed(self):
        """ Returns the current speed """
        return self.__speed

    @speed.setter
    def speed(self, value:str):
        if value in ['very slow','slow','normal','fast']:
            self.__speed = value
            if value == 'very slow':
                self.__pause = 10
                self.__speed_value = 10
            if value == 'slow':
                self.__pause = 1
                self.__speed_value = 1
            if value == "normal":
                self.__pause = 0
                self.__speed_value = 0
        else:
            print(value, "is not a valid value, try 'fast','normal' or 'slow'")

    @property
    def animation_type(self):
        return self.__animation_type

    @animation_type.setter
    def animation_type(self, value):
        if value in ['default','loop','bounce','bouncing','reverse']:
            if value == 'bounce':
                self.__animation_type = 'bouncing'
            else:
                self.__animation_type = value
        else:
            print(value," is not a valid Animation type - it should be 'loop','bounce','reverse' or 'default'")

    def __init__(self, frames=None, animation_type:str=None,x:int=None,y:int=None, width:int=None, height:int=None, filename=None, scale=1):
       """ setup the animation """ 
       print(f"initialising animation: {filename}")
       self.__frames = []
       self.__current_frame = 0
       self.__speed = "normal" # Other speeds are 'fast' and 'slow' - it just adds frames or skips frames
       self.__speed_value = 0
       self.__done = False # Has the animation completed
       self.__loop_count = 1
       self.__bouncing = False
       self.__animation_type = "default"
       self.__pause = 0
       self.__set = False
       self.__x = 0
       self.__y = 0
       self.__width = 16
       self.__height = 16
       self.__scale = scale
       self.__cached = False
       self.__frame_cache = None
       self.__frame_cache_index = -1
       self.__frame_cache_fb = None
       self.__frame_cache_w = 0
       self.__frame_cache_h = 0
       self.__frame_cache_mod = None
       self.__logged_empty = False
       self.__logged_frames = False
       self.__last_logged_frame = -1
       self.__use_pbm = False
       self.__pbm_dir = None
       if x is not None:
           self.__x = x
       if y is not None:
           self.__y = y
       if width is not None:
           self.__width = width
       if height is not None:
           self.__height = height
       if frames is not None:
           self.__frames = frames
       if animation_type is not None:
            self.animation_type = animation_type
       if filename:
           self.filename = filename

    def forward(self):
        """ progress the current frame """
        if self.__speed == 'normal':
            self.__current_frame +=1

        if self.__speed in ['very slow','slow']:
            if self.__pause > 0:
                self.__pause -= 1
            else:
                self.__current_frame +=1
                self.__pause = self.__speed_value

        if self.__speed == 'fast':
            if self.__current_frame < self.frame_count +2:
                self.__current_frame +=2
            else:
                self.__current_frame +=1

    def reverse(self):
        if self.__speed == 'normal':
            self.__current_frame -=1

        if self.__speed in ['very slow','slow']:
            if self.__pause > 0:
                self.__pause -= 1
            else:
                self.__current_frame -=1
                self.__pause = self.__speed_value

        if self.__speed == 'fast':
            if self.__current_frame < self.frame_count +2:
                self.__current_frame -=2
            else:
                self.__current_frame -=1

    def load(self):
        """ load the animation files """

        # load the files from disk
        if not self.__cached:
            self.__frames = []
            try:
                pbm_files = listdir("/gui/bitmaps")
                pbm_files = sorted(f for f in pbm_files if f.endswith(".pbm"))
                self.__frames = [f for f in pbm_files if f.startswith(self.filename)]
                if self.__frames:
                    self.__use_pbm = True
                    self.__pbm_dir = "/gui/bitmaps/"
            except OSError:
                self.__frames = []
            if not self.__frames:
                self.__use_pbm = False
                self.__pbm_dir = None
            self.__cached = True

    def unload(self):
        """ free up memory """

        self.__frames = None
        self.__frame_cache = None
        self.__frame_cache_index = -1
        self.__frame_cache_fb = None
        self.__frame_cache_w = 0
        self.__frame_cache_h = 0
        self.__frame_cache_mod = None
        self.__logged_empty = False
        self.__use_pbm = False
        self.__pbm_dir = None
        self.__cached = False
        gc.collect()

    def animate(self, oled):
        """ Animates the frames based on the animation type and for the number of times specified """

        if not self.__frames:
            if self.filename:
                self.load()
            if not self.__frames:
                if not self.__logged_empty:
                    print("No frames found for", self.filename)
                    self.__logged_empty = True
                return

        current_frame = self.__current_frame # Current Frame number - used to index the frames array
        if current_frame >= len(self.__frames):
            self.__current_frame = 0
            current_frame = 0
        if self.__use_pbm:
            frame_name = self.__frames[current_frame]
            self._draw_pbm_frame(oled, self.__pbm_dir + frame_name, self.__scale)
        else:
            return

        if self.__animation_type == "loop":
            # Loop from the first frame to the last, for the number of cycles specificed, and then set done to True
            self.forward()
            if self.__current_frame == current_frame and len(self.__frames) > 1:
                self.__current_frame = (current_frame + 1) % len(self.__frames)

            if self.__current_frame > self.frame_count:
                self.__current_frame = 0
                self.__loop_count -= 1
                if self.__loop_count == 0:
                    self.__done = True

        if self.__animation_type == "bouncing":

            # Loop from the first frame to the last, and then back to the first again, then set done to True
            if self.__bouncing:

                if self.__current_frame == 0:
                    if self.__loop_count == 0:
                        self.__done = True
                    else:
                        if self.__loop_count >0:
                            self.__loop_count -=1
                            self.forward()
                            self.__bouncing = False
                    if self.__loop_count == -1:
                        # bounce infinately
                        self.forward()
                        self.__bouncing = False
                if (self.__current_frame < self.frame_count) and (self.__current_frame>0):
                    self.reverse()
            else:
                if self.__current_frame == 0:
                    if self.__loop_count == 0:
                        self.__done = True
                    elif self.__loop_count == -1:
                        # bounce infinatey
                        self.forward()
                    else:
                        self.forward()
                        self.__loop_count -= 1
                elif self.__current_frame == self.frame_count:
                    self.reverse()
                    self.__bouncing = True
                else:
                    self.forward()

        if self.__animation_type == "default":
            # loop through from first frame to last, then set done to True

            if self.__current_frame == self.frame_count:
                self.__current_frame = 0
                self.__done = True
            else:
                self.forward()
        if self.__current_frame != self.__last_logged_frame:
            self.__last_logged_frame = self.__current_frame
        if self.__frame_cache_mod is not None:
            self.__frame_cache_mod = None

    @property
    def frame_count(self):
        """ Returns the total number of frames in the animation """
        if not self.__frames:
            return 0
        return len(self.__frames)-1

    @property
    def done(self):
        """ Has the animation completed """
        if self.__done:
            self.__done = False # reset the done flag to false
            return True
        else:
            return False

    def loop(self, no:int=None):
        """ Loops the animation
        if no is None or -1 the animation will continue looping until animate.stop() is called """

        if no is not None:
            self.__loop_count = no
        else:
            self.__loop_count = -1
        self.__animation_type = "loop"

    def stop(self):
        self.__loop_count = 0
        self.__bouncing = False
        self.__done = True

    def bounce(self, no:int=None):
        """ Loops the animation forward, then backward, the number of time specified in no,
         if there is no number provided it will animate infinately """

        self.__animation_type = "bouncing"
        if no is not None:
            self.__loop_count = no
        else:
            self.__loop_count = -1

    @property
    def width(self):
        """ Gets the icon width """
        return self.__width

    @width.setter
    def width(self, value):
        """ Sets the icon width """
        self.__width = value

    @property
    def height(self):
        """ Gets the icon height """
        return self.__width

    @height.setter
    def height(self, value):
        """ Sets the icon height """
        self.__height = value

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value

    def __str__(self):
        message = f"Animate: {self.filename}, {self.__current_frame}, {self.__loop_count}, {self.__done}, x: {self.__x}, y: {self.__y}"
        return message

    def _blit_scaled(self, display, frame, scale):
        """Draw a scaled frame onto the display without allocating a scaled buffer."""
        for y in range(frame.height):
            for x in range(frame.width):
                color = frame.image.pixel(x, y)
                display.fill_rect(
                    frame.x + (x * scale),
                    frame.y + (y * scale),
                    scale,
                    scale,
                    color,
                )

    def _blit_scaled_fb(self, display, fb, width, height, scale):
        for y in range(height):
            for x in range(width):
                color = fb.pixel(x, y)
                display.fill_rect(
                    self.__x + (x * scale),
                    self.__y + (y * scale),
                    scale,
                    scale,
                    color,
                )

    def _draw_pbm_frame(self, display, path, scale):
        try:
            with open(path, "rb") as f:
                magic = f.readline().strip()
                if magic != b"P4":
                    return
                # Skip comments and read dimensions
                while True:
                    line = f.readline()
                    if not line:
                        return
                    if not line.startswith(b"#"):
                        dims = line.split()
                        if len(dims) >= 2:
                            width = int(dims[0])
                            height = int(dims[1])
                            break
                row_bytes = (width + 7) // 8
                data = f.read(row_bytes * height)
        except OSError:
            return

        # Clear previous frame area
        display.fill_rect(self.__x, self.__y, width * scale, height * scale, 0x0000)
        idx = 0
        for y in range(height):
            row_start = y * row_bytes
            for x in range(width):
                byte = data[row_start + (x >> 3)]
                bit = 7 - (x & 7)
                if (byte >> bit) & 1:
                    display.fill_rect(
                        self.__x + (x * scale),
                        self.__y + (y * scale),
                        scale,
                        scale,
                        0xFFFF,
                    )
