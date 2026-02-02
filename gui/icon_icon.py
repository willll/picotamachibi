class Icon():
    """ Models an icon and all the properties it requires """
    def __init__(self, filename:None, width=None, height=None, x=None, y=None, name=None, scale=1):
        """ Sets up the default values """
        self.image = None # the image data type buf
        self.x = 0
        self.y = 0
        self.__invert = False
        self.width = 16
        self.height = 16
        self._src_width = 16
        self._src_height = 16
        self.name = "Empty"
        self._pbm_data = None
        self._pbm_row_bytes = 0
        self._pbm_fg = 0xFFFF
        self._pbm_bg = 0x0000
        self.scale = scale
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if name is not None:
            self.name = name
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if filename is not None:
            self.image = self.loadicons(filename)

    @property
    def invert(self)->bool:
        """ Flips the bits in the image so white become black etc and returns the image """
        return self.__invert

    @invert.setter
    def invert(self, value:bool):
        """ Marks the icon as selected for rendering """
        self.__invert = value
        # Rendering handles selection styling.

    def loadicons(self, file):
        # Load PBM assets from /gui/bitmaps.
        filename = file
        if "/" in filename:
            filename = filename.split("/")[-1]
        if not filename.endswith(".pbm"):
            filename = filename + ".pbm"
        path = "/gui/bitmaps/" + filename
        try:
            with open(path, "rb") as f:
                magic = f.readline().strip()
                if magic != b"P4":
                    raise ValueError("PBM asset must be P4 format")
                while True:
                    line = f.readline()
                    if not line:
                        raise ValueError("PBM asset missing size")
                    if not line.startswith(b"#"):
                        dims = line.split()
                        if len(dims) >= 2:
                            src_w = int(dims[0])
                            src_h = int(dims[1])
                            break
                row_bytes = (src_w + 7) // 8
                data = f.read(row_bytes * src_h)
        except OSError as exc:
            raise OSError("PBM asset not found: " + path) from exc

        self._pbm_data = data
        self._pbm_row_bytes = row_bytes
        self._src_width = src_w
        self._src_height = src_h
        self.width = src_w * self.scale
        self.height = src_h * self.scale
        print(self.name, self.width, self.height)
        return None

    def draw(self, target, x=None, y=None):
        draw_x = self.x if x is None else x
        draw_y = self.y if y is None else y
        if self._pbm_data is None:
            if self.image is None:
                return
            if self.scale <= 1:
                target.blit(self.image, draw_x, draw_y)
                return
            for py in range(self._src_height):
                for px in range(self._src_width):
                    color = self.image.pixel(px, py)
                    target.fill_rect(
                        draw_x + (px * self.scale),
                        draw_y + (py * self.scale),
                        self.scale,
                        self.scale,
                        color,
                    )
            return

        for py in range(self._src_height):
            row_start = py * self._pbm_row_bytes
            for px in range(self._src_width):
                byte = self._pbm_data[row_start + (px >> 3)]
                bit = 7 - (px & 7)
                if (byte >> bit) & 1:
                    color = self._pbm_fg
                else:
                    color = self._pbm_bg
                target.fill_rect(
                    draw_x + (px * self.scale),
                    draw_y + (py * self.scale),
                    self.scale,
                    self.scale,
                    color,
                )

    def loadicon2(self, library, icon_data):
        __import__(library, icon_data)
        # frame_buffer = framebuf.FrameBuffer(name, self.width,self.height, framebuf.MONO_HLSB)
        # frame_buffer = bytearray(self.width * self.height // 8)
        frame_buffer = bytearray(icon_data)
        return frame_buffer
