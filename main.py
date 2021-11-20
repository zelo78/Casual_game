from time import sleep
from superwires import games
from random import randrange


class BinSprite(games.Sprite):
    def __init__(self, type_name, **kwargs):
        self.type_name = type_name
        super().__init__(y=350, **kwargs)

    def update(self):
        overlapping_sprites = self.get_overlapping_sprites()
        for sprite in overlapping_sprites:
            if isinstance(sprite, WasteSprite):
                if sprite.type_name != self.type_name:
                    fatal_length = sound_fatal.get_length()
                    sound_fatal.play()
                    sleep(fatal_length)
                    games.screen.quit()
                else:
                    self.builder.handle_click(self)


class WasteSprite(games.Sprite):
    def __init__(self, image, type_name):
        self.type_name = type_name
        super().__init__(image=image, x=games.screen.width/2,
                         y=games.screen.height - 417, dx=0, dy=2)


class WasteBuilderSprite(games.Sprite):
    def __init__(self, bins, image):
        self.bins = bins
        for bin in bins:
            bin.builder = self
        self.in_removal_mode = False
        self.click_was_handled = False
        self.frames_interval = 60
        self.passed_frames = 0
        self.created_waste = 0
        self.visible_waste = []
        super().__init__(image=image, x=-200, y=-200)

    def update(self):
        # create new waste
        if self.passed_frames == 0:
            self.created_waste += 1
            new_waste = random_waste()
            self.visible_waste.append(new_waste)
            games.screen.add(new_waste)

            # speed up
            # remove 2 frames interval every 3 created waste
            if self.frames_interval > 30 and self.created_waste % 3 != 0:
                self.frames_interval -= 1

        # count interval for new waste
        self.passed_frames += 1
        if self.passed_frames == self.frames_interval:
            self.passed_frames = 0

        # if mouse was pressed...
        if games.mouse.is_pressed(0):
            if self.in_removal_mode is False:
                self.in_removal_mode = True
                self.click_was_handled = False
        elif self.click_was_handled:
            self.in_removal_mode = False

        if self.in_removal_mode and self.click_was_handled is False:
            for bin in self.bins:
                if check_point(games.mouse.x, games.mouse.y, bin):
                    self.handle_click(bin)
                    break
            self.click_was_handled = True

    def handle_click(self, bin):
        if self.visible_waste and \
           self.visible_waste[0].type_name == bin.type_name:
            lowest_waste = self.visible_waste.pop(0)
            games.screen.remove(lowest_waste)
            sound_go_to_bin.play()
        else:
            sound_error.play()


def check_point(x, y, sprite):
    return sprite.left <= x <= sprite.right and \
        sprite.top <= y <= sprite.bottom


def random_waste():
    index = randrange(3)
    return WasteSprite(image=waste_images[index], type_name=WASTE_NAMES[index])


def main():
    global WASTE_NAMES, waste_images
    # init main object
    games.init(screen_width=626, screen_height=417, fps=50)

    # Load all images
    background_image = games.load_image('background.jpg', transparent=False)
    bin_image = games.load_image('bin.png')
    waste_images = [
        games.load_image('banana.png'),
        games.load_image('bottle.png'),
        games.load_image('paper.png'),
    ]

    # Load all sounds
    global sound_go_to_bin, sound_error, sound_fatal
    sound_go_to_bin = games.load_sound('sfx_sounds_interaction10.wav')
    sound_error = games.load_sound('sfx_sounds_error13.wav')
    sound_fatal = games.load_sound('sfx_sounds_negative1.wav')

    # Set background
    games.screen.background = background_image

    # Prepare bins
    bins = []
    x_bin_positions = [106, 313, 521]
    WASTE_NAMES = ['Food', 'Bottle', 'Paper']
    for x, type_name in zip(x_bin_positions, WASTE_NAMES):
        bin = BinSprite(x=x, image=bin_image, type_name=type_name)
        bins.append(bin)
        games.screen.add(bin)

        text = games.Text(value=type_name, size=20, color=(20,255,20), x=x, y=380)
        games.screen.add(text)

    # This object maintain logic of the game
    builder = WasteBuilderSprite(bins=bins, image=bin_image)
    games.screen.add(builder)

    # run mainloop
    games.screen.mainloop()

if __name__ == '__main__':
    main()
