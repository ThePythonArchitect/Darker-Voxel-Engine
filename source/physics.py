"""

This class is responsible for collision detection,
storing sectors (that in turn store block data),
and for updating block data such as when block are
added or removed.

"""


from sector import Sector
from block import Block


class Physics:

    def __init__(self):

        #all the sectors are stored here
        self.sectors = []

        return

    def remove_block(self, cordinate):

        #removes the block at the given cordinate

        return

    def add_block(self, cordinate, block_id):

        #changes the block at the given cordinate to the given id

        return

    def generate_sector(self, cordinate):

        #generates a sector with the terrain generator

        return

    def block_at(self, cordinate):

        #returns whether or not there is a solid block
        #at the given cordinate

        return