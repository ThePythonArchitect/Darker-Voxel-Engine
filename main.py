"""

Main class.  Start the application and initializes all other classes.

"""


import pyglet

class Main:

    def __init__(self, width=800, height=1200, title="0.0.10"):

        #save the title as a variable
        self.title = title

        #ticks per second
        self.tps = 60

        #create the pyglet window
        self.window = pyglet.window.Window(
            width = width,
            height = height,
            caption = title,
            fullscreen = False,
            resizable = False,
            vsync = True
            )

        return

    def update_fps(self, dt):

        #update the window title with the new fps
        self.window.set_caption(f"{self.title} - FPS: {pyglet.clock.get_fps()}")

        return

    def update(self, dt):

        return

    def start(self):

        #set the fps schedule X times per second
        pyglet.clock.schedule_interval(self.update_fps, 1)

        #set the update to be called X times per second
        pyglet.clock.schedule_interval(self.update, (1/self.tps))

        return

    def quit(self):

        #close the pyglet window
        self.window.close()

        return



if __name__ == "__main__":
    app = Main()
    app.start()
