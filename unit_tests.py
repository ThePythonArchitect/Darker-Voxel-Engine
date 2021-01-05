#run all unit tests, dispaying results to the command prompt
from source.main import Main

class Unit_Tests:

    def __init__(self):
        
        self.total_tests = 2
        self.total_fails = 0

        #create test object once here then call it from the unit test methods
        self.test_main = Main()
        #start the application
        self.test_main.start()

        return

    def run(self):

        print(f"Running {self.total_tests} unit tests...")
        print()

        #call unit test methods from here
        self.total_fails += self.test_main_init()
        self.total_fails += self.test_camera()


        #display results here
        print()
        print()
        if self.total_fails == 0:
            print(f"Unit tests complete.  All tests passed.")
        else:
            print(f"Unit tests complete.  {self.total_fails} tests failed.")


        #close pyglet window
        self.test_main.quit()
        

        return

    def test_main_init(self):

        #ensure that all other classes are created
        #and that a pyglet windows is created

        #0 means success, 1 means fail
        result = 0

        #ensure window is created
        if not hasattr(self.test_main, 'window'):
            print("Pyglet window failed to start in main.__init__")
            result = 1
            

        #ensure that sub classes are created
        if not hasattr(self.test_main, 'graphics'):
            print("Graphics class wasn't initialized in main.__init__")
            result = 1

        if not hasattr(self.test_main, 'physics'):
            print("Physics class wasn't initialized in main.__init__")
            result = 1

        if not hasattr(self.test_main, 'camera'):
            print("Camera class wasn't initialized in main.__init__")
            result = 1

        if not hasattr(self.test_main, 'sound'):
            print("Sound class wasn't initialized in main.__init__")
            result = 1

        if not hasattr(self.test_main, 'storage'):
            print("Storage class wasn't initialized in main.__init__")
            result = 1

        return result

    def test_camera(self):

        #0 = pass, 1 = fail
        result = 0

        #test the parse strafe input function?


        return

if __name__ == "__main__":
    unit_tests = Unit_Tests()
    unit_tests.run()
