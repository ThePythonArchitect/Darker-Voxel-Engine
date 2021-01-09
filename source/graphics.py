"""

This class is used to wrap the openGL API.
This should be the only class that interacts
with vao classes

"""

import pyglet
from pyglet import gl
from PIL import Image


class Graphics:

    def __init__(self, window_width, window_height):

        #save the window height and width
        self.window_width = window_width
        self.window_height = window_height

        

        return

    def set_shader_source(self):

        #TODO
        #both of these shaders need to be re-written for the
        #current version of this application
        #(kept for reference)
        self.vertex_source = (
        """
        #version 330

        uniform mat4 full_matrix;

        layout (location = 0) in vec3 position;
        layout (location = 1) in vec2 atexture_cordinates;
        layout (location = 2) in vec3 instanced_position;

        out vec4 vertex_color;
        out vec2 texture_cordinates;

        void main()
        {
            gl_Position = full_matrix * vec4(position + instanced_position, 1.0);
            texture_cordinates = atexture_cordinates;
        };
        """.encode('utf-8')
        )

        self.frag_source = (
        """
        #version 330

        uniform sampler2D texture_point;

        in vec2 texture_cordinates;

        out vec4 fragment_color;

        void main()
        {
            fragment_color = texture(texture_point, texture_cordinates);
        };
        """.encode('utf-8')
        )

        return

    def create_shaders(self):
        #sets up the vertex and fragement shaders

        #create a vertex shader and store id's
        vertex_shader_id = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        fragment_shader_id = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        
        #create a string buffer for the vertex and fragment source code
        #this is necessary since we are calling openGL commands from Python
        vertex_buffer = ctypes.create_string_buffer(self.vertex_source)
        fragment_buffer = ctypes.create_string_buffer(self.frag_source)
        
        #convert source codes to char pointers that can be passed to openGL
        c_vertex_source = ctypes.cast(
            ctypes.pointer(ctypes.pointer(vertex_buffer)),
            ctypes.POINTER(ctypes.POINTER(gl.GLchar))
        )
        c_frag_source = ctypes.cast(
            ctypes.pointer(ctypes.pointer(fragment_buffer)),
            ctypes.POINTER(ctypes.POINTER(gl.GLchar))
        )
        
        #attach the source codes to the shaders
        gl.glShaderSource(vertex_shader_id, 1, c_vertex_source, None)
        gl.glShaderSource(fragment_shader_id, 1, c_frag_source, None)
        
        #compile both shaders
        gl.glCompileShader(vertex_shader_id)
        gl.glCompileShader(fragment_shader_id)

        #create the shader executable
        self.shader = gl.glCreateProgram()
        
        #attach and link the vertex and fragment shaders
        gl.glAttachShader(self.shader, vertex_shader_id)
        gl.glAttachShader(self.shader, fragment_shader_id)
        gl.glLinkProgram(self.shader)
        
        #set openGL to use the shader that was just created
        self.clear_errors()
        gl.glUseProgram(self.shader)
        self.get_errors()
        
        #delete the unused shaders since their code is already
        #included in the shader executable
        gl.glDeleteShader(vertex_shader_id)
        gl.glDeleteShader(fragment_shader_id)

        #TODO
        #check for compilation errors on the main shader
        #and probably set a variable in self to signify if
        #it worked or not

        return

    def create_matrices(self):
        #creates the model view and projection matrices for
        #moving the camera around in 3D space
        #
        #returns nothing

        #field of view
        fov = 65
        #near clipping space
        near_clip = 0.001
        #far clipping space
        far_clip = 100000

        self.projection_matrix = glm.perspective(
            glm.radians(fov),
            self.window_width / self.window_height,
            near_clip,
            far_clip
        )

        self.full_matrix = self.projection_matrix

        self.matrix_location = gl.glGetUniformLocation(
            self.shader,
            "full_matrix".encode('utf-8')
        )

        self.upload_matrix()

        return

    def upload_matrix(self):

        #gives a matrix to the GPU
        #obviously, this syncs the CPU and GPU

        #change the matrix to be compatible with C
        flat_matrix = [y for x in self.full_matrix for y in x]
        c_matrix = (gl.GLfloat * len(flat_matrix))(*flat_matrix)

        gl.glUniformMatrix4fv(
            self.matrix_location,
            1,
            gl.GL_FALSE,
            c_matrix
        )

        #check for errors
        err = self.get_errors()
        if err != None:
            print(err)

        return

    def apply_view_matrix(self, view_matrix):

        #applies the given view matrix to the full matrix
        #
        #Parameter 1:
        #the view matrix generated from the camera class
        #
        #returns nothing

        #calculate the view + projection matrix
        #if a model matrix is used, then it should be applied here
        self.full_matrix = self.projection_matrix * view_matrix

        return

    def load_texture(self, filename):
        #load a single image in openGL
        #
        #Parameters 1:
        #filename of the image to load, including file extention
        #
        #returns nothing

        #this function is untested

        #load image from disk
        try:
            open(filename, "r")
        except FileNotFoundError:
            assert False, f"File not found: {filename}"
        image_file = Image.open(filename).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
        width, height = image_file.size[0], image_file.size[1]
        #and then convert the image data to something that openGL can make sense of
        raw_data = image_file.tobytes()
        image_data = (ctypes.c_ubyte * len(raw_data))(*raw_data)
        
        
        #enable openGL to accept 2D images
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        #create a texture id in openGL
        texture_id = ctypes.c_uint()
        gl.glGenTextures(1, ctypes.byref(texture_id))
        #set the texture to be the primary in openGL context
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

        #tell openGL how to deal with minification
        #and maximication and wrapping
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)


        #load the texture onto the GPU
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGBA,
            width,
            height,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_BYTE,
            image_data
        )
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

        self.get_errors()


        #TODO
        #error checking on file load and upload to the GPU

        return

    def enable_face_culling(self):

        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)

        return

    def enable_depth_test(self):

        gl.glEnable(gl.GL_DEPTH_TEST)

        return

    def get_errors(self):
        #checks for errors in GL

        error = gl.glGetError()
        if error != 0:
            return f'[OpenGL Error]:\n{error}'
        else:
            return None

        return

    def clear_errors(self):
        #clears all the errors in openGL

        while gl.glGetError() != 0:
            pass

        return

    def set_clearbit_color(self, color, alpha=1.0):
        #color should be a 3-float list
        #in RGB format, numbers should be between 0 and 1

        gl.glClearColor(color[0], color[1], color[2], alpha)

        return

    def clear_screen(self):

        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT | pyglet.gl.GL_DEPTH_BUFFER_BIT)

        return
