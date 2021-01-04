"""

This class is used to represent sectors of the game world.
It contains block data as 3D arrays, cordinates.
It also contains the ability to generate greedy meshes.

"""

import numpy



class Sector:

    def __init__(self, cordinates):

        #the cordinates of the sector within the world cordinates
        #this is a tuple that represents the corner of the sector
        self.cordinates = cordinates
        #32 x 32 x 32 array of shorts (2 bytes) to store block data
        #each short represents a unique block's id
        #this gives 65,000+ unique block types
        #without RLE, this comes to 65KB per sector of main memory
        self.blocks = numpy.ndarray((32, 32, 32), dtype=np.short)
        #this list represents the cordinates of each generated quad
        #that resides in GPU memory pertaining to this sector
        self.gpu_mappings = []

        return

    def generate_mesh(self):

        #generate a greedy mesh for this sector

        return