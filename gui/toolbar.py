from gui.icon_icon import Icon


class Toolbar():
    """ Models the toolbar """
    spacer = 1
    __select_color = 0xFFFF
    __bg_color = 0x0000
    __outline_margin = 1

    def __init__(self):
        # print("building toolbar")
        # Draw directly to the display to avoid a large toolbar buffer allocation.
        self.__icon_array = []
        self.__selected_item = None
        self.__selected_index = -1 # -1 means no item selected

    def additem(self, icon):
        self.__icon_array.append(icon)

    def remove(self, icon):
        self.__icon_array.remove(icon)

    @property
    def data(self):
        """ Kept for compatibility; toolbar draws directly in show(). """
        return None

    def show(self, display):
        x = 0
        display.fill_rect(0, 0, 240, 32, self.__bg_color)
        for icon in self.__icon_array:
            if type(icon) is Icon:
                icon.draw(display, x, 0)
                if icon.invert:
                    display.rect(
                        x + self.__outline_margin,
                        self.__outline_margin,
                        icon.width - (self.__outline_margin * 2),
                        icon.height - (self.__outline_margin * 2),
                        self.__select_color,
                    )
            x += icon.width + self.spacer

    def select(self, index, oled):
        """ Set the item in the index to inverted """
        # for item in self.__icon_array:
        #     item.invert = False
        self.__icon_array[index].invert = True
        self.__selected_index = index
        self.show(oled)

    def unselect(self, index, oled):
        self.__icon_array[index].invert = False
        self.__selected_index = -1
        self.show(oled)

    @property
    def selected_item(self):
        """ Returns the name of the currently selected icon """
        self.__selected_item = self.__icon_array[self.__selected_index].name
        return self.__selected_item
