"""

Camera class
Used to
    accept parsed input
    calculate view matrix
    provide an easy API to camera operations


"""

#this is pyglm
import glm



class Camera:

    def __init__(self, x=0.0, y=0.0, z=0.0):

        #setup camera variables that will remain through each tick

        #view matrix
        self.view_matrix = glm.lookAt(
            glm.vec3(x, y, z+1.0), #camera position
            glm.vec3(x, y, z), #where the camera is looking
            glm.vec3(x, y+1.0, z+1.0) #camera's up direction
        )

        
        #used to keep track of rotation of the camera only if enable_roll
        #is set to false, otherwise only quaternions are used
        self.rotation = glm.vec2()

        #input buffer used to apply all input per tick at the same
        #time, after the tick's input is applied, everything is set
        #back to 0
        self.input_buffer = {
            "strafe_left": 0,
            "strafe_right": 0,
            "strafe_down": 0,
            "strafe_up": 0,
            "strafe_forward": 0,
            "strafe_backward": 0,
            "rotate_down": 0,
            "rotate_up": 0,
            "rotate_left": 0,
            "rotate_right": 0,
            "roll_left": 0,
            "roll_right": 0
        }

        #the speeds for strafing and turning the camera
        self.strafe_speed = 2
        self.rotation_speed = 2.25

        #used to make the camera movement smoother
        self.input_spread = 4
        self.spread_input_buffer = [[0.0, 0.0, 0.0] for x in range(self.input_spread)]
        self.spread_counter = 0
        self.rotating_camera = False

        #whether or not the ability to roll the camera is enabled
        self.enable_roll = False

        #this is only used if enabled_roll is set to False
        #it controlls how far the camera can look up and down, max it like pi/2 for
        #preventing the camera from looking straight up and down
        self.camera_lock_value = 1.75

        #controls if moving the mouse up turns the camera up or down
        self.invert_y = False

        return

    def toggle_invert_y(self):

        self.invert_y = not self.invert_y

        return

    def parse_strafe_input(self, dt):

        #reads data from the input buffer and returns
        #a glm.vec3 of the delta input for strafing

        #the translation vector
        translation = glm.vec3(0.0, 0.0, 0.0)

        #loop through input buffer and apply each strafe direction
        #to the translation vector
        translation[0] += (self.strafe_speed * self.input_buffer["strafe_left"]) * dt
        translation[0] -= (self.strafe_speed * self.input_buffer["strafe_right"]) * dt
        translation[1] += (self.strafe_speed * self.input_buffer["strafe_down"]) * dt
        translation[1] -= (self.strafe_speed * self.input_buffer["strafe_up"]) * dt
        translation[2] += (self.strafe_speed * self.input_buffer["strafe_forward"]) * dt
        translation[2] -= (self.strafe_speed * self.input_buffer["strafe_backward"]) * dt

        return translation

    def parse_rotation_input(self, dt):
        #reads input from the input buffer and returns a list
        #that represents the delta changes to the cameras rotations

        #calculate the rotation in with all 6 degrees of freedom
        delta_rotation = [0.0, 0.0, 0.0]

        #this is used to compensate for the window being wider
        #than it is tall.  should be changed to be calculated
        #dynamically
        inverse_aspect_ratio = 1.6

        #this is simply used to apply the invert y axis
        #without going through a if statement
        invert_int = ((self.invert_y * 2)-1)

        #loop through the input buffer and get each the rotation for
        #each axis
        delta_rotation[0] -= (self.rotation_speed * self.input_buffer["rotate_down"]) * dt * invert_int
        delta_rotation[0] += (self.rotation_speed * self.input_buffer["rotate_up"]) * dt * invert_int
        delta_rotation[1] -= ((self.rotation_speed * self.input_buffer["rotate_left"]) * inverse_aspect_ratio) * dt
        delta_rotation[1] += ((self.rotation_speed * self.input_buffer["rotate_right"]) * inverse_aspect_ratio) * dt
            
        #and the rolls
        if self.enable_roll:
            delta_rotation[2] += (self.rotation_speed * self.input_buffer["roll_left"]) * dt
            delta_rotation[2] -= (self.rotation_speed * self.input_buffer["roll_right"]) * dt

        
        return delta_rotation

    def smooth_rotation(self, delta_rotation):

        #used to make the camera control feel smoother
        #by applying controls over several updates

        #divide each part of delta rotation by the spread
        split_rotation = [x / self.input_spread for x in delta_rotation]
        #add this to each part of the spread buffer
        for x in range(self.input_spread):
            for y in range(3):
                self.spread_input_buffer[x][y] += split_rotation[y]
        
        #increment spread counter
        self.spread_counter += 1
        if self.spread_counter == self.input_spread:
            self.spread_counter = 0
        #return the spread buffer at index spread counter
        #try this
        #returned_rotation = self.spread_input_buffer[self.spread_counter].copy()
        #or
        summed_rotation = [0.0, 0.0, 0.0]
        for x in self.spread_input_buffer:
            for y in range(3):
                summed_rotation[y] += x[y]
        returned_rotation = [x/3 for x in summed_rotation]
        
        self.spread_input_buffer[self.spread_counter] = [0.0, 0.0, 0.0]


        return returned_rotation

    def update(self, dt):

        #should be called every tick in the gameplay loop
        #in order to update the view matrix

        #get the delta rotation quaternion
        delta_rotation = self.smooth_rotation(self.parse_rotation_input(dt))

        if self.enable_roll:
            #6 DoF camera
            #create a rotation quaternion for each axis
            x_rotation = glm.angleAxis(delta_rotation[0], glm.vec3(1, 0, 0))
            y_rotation = glm.angleAxis(delta_rotation[1], glm.vec3(0, 1, 0))
            z_rotation = glm.angleAxis(delta_rotation[2], glm.vec3(0, 0, 1))

            #combine the quaternions of each axis together
            delta_rotation_quat = glm.normalize(z_rotation * x_rotation * y_rotation)
        else:
            #FPS style camera
            #record rotations in an absolute rotation
            #x axis
            self.rotation[0] += delta_rotation[0]
            #z axis
            self.rotation[1] += delta_rotation[1]
            #y axis is skipped, no rolling

            #ensure that the camera doesn't go above looking straight up or down
            if self.rotation[0] < -self.camera_lock_value:
                self.rotation[0] = -self.camera_lock_value
            if self.rotation[0] > self.camera_lock_value:
                self.rotation[0] = self.camera_lock_value
            #create a rotation quaternion for each axis
            x_rotation = glm.angleAxis(self.rotation[0], glm.vec3(1, 0, 0))
            y_rotation = glm.angleAxis(self.rotation[1], glm.vec3(0, 1, 0))
            #combine the quaternions of each axis together
            delta_rotation_quat = glm.normalize(x_rotation * y_rotation)
        
        #apply the rotation to a matrix
        orientation_matrix = glm.mat4_cast(delta_rotation_quat)

        #get the translation matrix by parsing the strafing input
        delta_translation = self.parse_strafe_input(dt)



        if self.enable_roll:
            #now the translation vector should contain all the strafing
            #translations, therefore a translation matrix is calculated
            translation_matrix = glm.translate(
                glm.mat4(),
                glm.vec3(delta_translation)
            )
            #apply everything
            self.view_matrix = translation_matrix * (orientation_matrix * self.view_matrix)
        else:
            #ensures that the camera can move, since movement is no longer being stored in the view matrix
            delta_translation_rotated = self.get_orientation() * glm.vec4(delta_translation, 0)
            self.last_position += glm.vec3(delta_translation_rotated)
            previous_position_matrix = glm.translate(
                glm.mat4(),
                self.last_position
                )
            self.view_matrix = orientation_matrix * previous_position_matrix
        
        #reset input buffer
        self.reset_input_buffer()

        return

    def reset_input_buffer(self):

        #resets all the booleans in the input buffer to False
        self.input_buffer = {key: 0 for key in self.input_buffer}

        return

    def get_pos(self):

        temp_matrix = glm.inverse(self.view_matrix)

        return glm.vec3([ temp_matrix[3][0], temp_matrix[3][1], temp_matrix[3][2] ])

    def set_pos(self, new_position):

        temp_matrix = glm.inverse(self.view_matrix)

        temp_matrix[3][0] = new_position[0]
        temp_matrix[3][1] = new_position[1]
        temp_matrix[3][2] = new_position[2]
        
        self.view_matrix = glm.inverse(temp_matrix)

        return

    def get_orientation(self):

        temp_matrix = glm.inverse(glm.mat3(self.view_matrix))

        return glm.quat_cast(temp_matrix)

    def set_orientation(self, new_quat):

        #new_quat should be the new quaternion orientation
        #that should be the camera rotation

        #convert quaternion to a 4x4 matrix
        new_orientation = glm.mat4_cast(glm.normalize(new_quat))

        #get the current position of the camera
        position = self.get_pos()

        #set the new orientation to the view matrix
        #then apply the position
        self.view_matrix = new_orientation
        self.set_pos(*position)

        return