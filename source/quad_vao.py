"""

This class is a wrapper around vertex array objects.
It is used specifically to create quad surfaces on the GPU.
Vertex attribute:
    (x, y, z) spacial cordinates (4 bytes + 4 bytes + 4 bytes)
    (u, v) texture cordinates (2 bytes + 2 bytes)
    (i) lighting (1 byte)
    21 bytes total
    1 MB can fit 49,932 vertices
    which totals 12,483 quads

"""

import pyglet
from pyglet import gl
import ctypes
import numpy

class Quad_Vao:

    def __init__(self, memory_size=512):

        #memory size is how much video memory is allocated
        #to this vao.  size is in MB
        #1,048,576 is how many bytes are in a MB
        self.memory_size = memory_size * 1048576

        #create an id from openGL
        self.id = ctypes.c_ulong()
        gl.glGenVertexArrays(1, ctypes.byref(self.vertex_array_id))

        #how many floats make up each vertex within the vertex buffer
        self.vertex_stride = None

        #this is the id that openGL provides
        self.vertex_buffer_id = None

        #when allocating memory on the GPU, how many bytes
        #that the system treats floats as in recorded here
        #same for ints
        self.float_size = ctypes.sizeof(ctypes.c_float)
        self.int_size = ctypes.sizeof(ctypes.c_int32)

        #this is used to track which "memory slots" are open
        #on the GPU, and which ones already contain a quad
        #this class will auto compensate for translating between
        #quads and vertices
        self.memory_slots = numpy.zeros(self.memory_size , dtype=numpy.bool_)

        return

    def bind_vao(self):

        #proper openGL etiquette to bind the vao before each operation
        #then unbind afterwards.  it also helps avoid weird bugs
        gl.glBindVertexArray(self.vertex_array_id)

        return

    def unbind_vao(self):

        #proper openGL etiquette to bind the vao before each operation
        #then unbind afterwards.  it also helps avoid weird bugs
        gl.glBindVertexArray(0)

        return

    def create_vertex_buffer(self):

        #create a pointer to a unsigned long integer
        #this needs to be passed to openGL to create an id
        vertex_buffer_id = ctypes.c_ulong()
        #create the buffer in openGL
        gl.glGenBuffers(1, ctypes.byref(vertex_buffer_id))

        return vertex_buffer_id

    def set_vertex_stride(self, value, id):

        #set the stride for the vertex buffer
        #this should be the total number of bytess that will be provided
        #to the vertex shader per attribute
        #returns nothing
        #
        #Paramter 1:
        #how many bytes per each vertex
        #
        #Parameter 2:
        #the id of the target vertex buffer
        #
        #returns nothing

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, id)
        self.vertex_stride = value
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        return

    def define_vertex_layout(self, byte_count, location, id):

        #defines how the data will be defined in the VAO
        #
        ##Parameter 1:
        #the number of bytes that are provided with the current attribute
        #for instance, if the position is defined in 3D space, that requires
        #3 floats, therefore byte_count would equal 12 (3 * 4).
        #
        #Parameter 2:
        #the location that is defined in the vertex shader
        #
        #Parameter 3:
        #the id of the target vertex buffer
        #
        #Returns nothing.

        #the self.vertex_stride needs to be set before this function is called
        #check to see if it has been to give a valid error
        if self.vertex_stride == None:
            assert False, "set_vertex_stride(value) needs to be called before define_vertex_layout()"

        #set the buffer that we just created as the primary
        #vertex buffer in the openGL context
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer_id)

        #TODO
        #redo this logic to make it more dynamic
        #right now, it can only allocate all memory once, then it becomes
        #pointless, also it doesn't check for trying to add data that exceeds
        #the memory allocated, which leads to errors pretty often

        #the self.offsets dictionary keep track of the previous locations'
        #stride.  The current locations offset should be a sum of all the
        #previous locations strides.
        previous_sum = sum(x for x in self.offsets.values())
        self.offsets[location] = number_of_values + previous_sum
        if location == 0:
            #make a pointer to the number 0
            offset = 0
        else:
            #create a pointer to the offset
            #offset = ctypes.c_float(self.offsets[location-1])
            offset = self.offsets[location-1] * self.float_length

        #enable the attribute before we define it
        gl.glEnableVertexAttribArray(location)

        #define how the data will be laid out in the vertex buffer
        gl.glVertexAttribPointer(
            location,
            number_of_values,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            self.vertex_stride,
            ctypes.c_void_p(offset)
        )
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        return
