"""

This class is a wrapper around vertex array object
.
It is used specifically to create quad surfaces on the GPU.

Vertex attribute:
    (x, y, z) spacial cordinates (4 bytes + 4 bytes + 4 bytes)
    (u, v) texture cordinates (4 bytes + 4 bytes)
    (i) lighting (4 byte)
    24 bytes total
    1 MB can fit 43,690 vertices
    which totals 10,922 quads

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
        #so now memory size represents how many bytes are to be allocated
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

    def bind_vao(self, id):

        #proper openGL etiquette to bind the vao before each operation
        #then unbind afterwards.  it also helps avoid weird bugs
        gl.glBindVertexArray(id)

        return

    def unbind_vao(self):

        #proper openGL etiquette to bind the vao before each operation
        #then unbind afterwards.  it also helps avoid weird bugs test
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

    def define_vertex_layout(self, number_of_values, data_type, location, offset, id):

        #defines how the data will be defined in the VAO
        #
        ##Parameter 1:
        #the number of values that are provided with the current attribute
        #for instance, if the position is defined in 3D space, that requires
        #3 floats, therefore byte_count would equal 3.
        #
        #Parameter 2:
        #the gl datatype of the given attribute (ie gl.GL_FLOAT or gl.GL_UNSIGNED_INT)
        #
        #Parameter 3:
        #the location that is defined in the vertex shader
        #
        #Parameter 4:
        #how many bytes into the buffer to begin reading
        #for this attribute
        #
        #Parameter 5:
        #the id of the target vertex buffer
        #
        #Returns nothing.

        #the self.vertex_stride needs to be set before this function is called
        #check to see if it has been to give a valid error
        if self.vertex_stride == None:
            assert False, "set_vertex_stride(value) needs to be called before define_vertex_layout()"

        #set the buffer that we just created as the primary
        #vertex buffer in the openGL context
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, id)

        #enable the attribute before we define it
        gl.glEnableVertexAttribArray(location)

        #define how the data will be laid out in the vertex buffer
        gl.glVertexAttribPointer(
            location,
            number_of_values,
            datatype,
            gl.GL_FALSE,
            self.vertex_stride,
            ctypes.c_void_p(offset)
        )

        #unbind the vertex buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        return

    def allocate_vertex_buffer(self, id, draw_type=gl.GL_STATIC_DRAW):

        #alloctes space on the vertex buffer on the GPU
        #
        #Parameter 1:
        #the id of the target vertex buffer
        #
        #Parameter 2:
        #the type of drawing mode openGL should use for the data
        #
        #returns nothing

        #bind the vertex buffer of the given id
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, id)
        
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            self.memory_size,
            0,
            self.draw_types[draw_type]
        )

        #unbind the target vertex buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        return

    def upload_vertex_data(self, array, datatype=gl.GL_FLOAT):

        #uploads data into the vertex buffer on the GPU
        #this syncs the CPU and GPU
        #
        #Parameter 1:
        #a 1 dimensional array of data
        #
        #Parameter 2:
        #the ctypes data type of the given array
        #
        #returns nothing
        
        #vertex buffer in the openGL context
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer_id)

        #convert the array to a c array
        #otherwise opengl wont accept it
        c_array = (datatype * len(array))(*array)

        #self.vertex_buffer_offset determines the starting address
        #that the array will be placed in the GPU's vertex buffer
        gl.glBufferSubData(
            gl.GL_ARRAY_BUFFER,
            self.vertex_buffer_offset,
            ctypes.sizeof(c_array),
            c_array
        )
        #set the new offset to be the next empty address
        #self.vertex_buffer_offset += sizeof(c_array)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        return

    def draw(self, count, id):

        #draw from the vertex buffer
        #
        #Parameter 1:
        #the amount of quads in the vertex buffer to draw
        #
        #Parameter 2:
        #the id of the target vertex buffer to draw from
        #
        #returns nothing

        #convert the count variable to a ctype
        #multiplied by 4 since we are drawing quads
        #1 quad = 4 vertices
        c_count = ctypes.c_int(count * 4)

        #bind the target vertex buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, id)

        #now the draw commond from opengl
        gl.glDrawArrays(
            gl.GL_QUADS,
            0,
            c_count,
            )

        return
