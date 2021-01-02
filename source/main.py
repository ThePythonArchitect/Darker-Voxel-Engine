"""

Main class
Starts the application and initializes all other classes.

"""

import pyglet
from camera import Camera


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
            vsync = False
            )

        #manually call the @window.event decorator
        #this makes the self.on_draw function be called
        #everytime pyglet re-draws the screen
        self.on_draw = self.window.event(self.on_draw)

        #instantiate other classes
        self.camera = Camera()

        return

    def on_draw(self):

        #render the frame to the screen

        return

    def update_fps(self, dt):

        #update the window title with the new fps
        self.window.set_caption(f"{self.title} - FPS: {int(pyglet.clock.get_fps())}")

        return

    def update(self, dt):

        #this is called to update the game state
        #if tps is 60, then it is called 60 times per second

        return

    def start(self):

        #set the fps schedule X times per second
        pyglet.clock.schedule_interval(self.update_fps, 1)

        #set the update to be called X times per second
        pyglet.clock.schedule_interval(self.update, (1/self.tps))

        #run the application; pyglet doesn't render anything until
        #this command is called
        pyglet.app.run()

        return

    def quit(self):

        #close the pyglet window
        self.window.close()

        return



if __name__ == "__main__":
    app = Main()
    app.start()
