#! /usr/bin/python

import argparse
import copy
import sys

class Block(object):
    """A group of symbols in a contiguous grouping."""
    def __init__(self, set):
        self._set = set

    def __repr__(self):
        return str(self._set)

    def calculate_perimeter(self):
        to_return = 0
        for (x, y) in self._set:
            for coord in [(x + 1, y), 
                          (x - 1, y), 
                          (x, y + 1),
                          (x, y - 1)]:
                if coord not in self._set:
                    to_return += 1
        return to_return

    def calculate_area(self):
        return len(self._set)

class Map(object):
    """A map of a jobsite."""
    def __init__(self, map):
        self._map = map

    def find_blocks(self):
        # Once a tile's been put into some group, it shouldn't be put in any
        # other group; mark them to reflect this
        marked = set()
        to_return = {}
        for x in xrange(len(self._map)):
            for y in xrange(len(self._map[x])):
                # O(1) lookup is a big help here
                if (x, y) not in marked:
                    contiguous_characters = \
                        self.find_contiguous_characters(x, y)
                    marked |= contiguous_characters
                    if not to_return.has_key(self._map[x][y]):
                        to_return[self._map[x][y]] = []
                    to_return[self._map[x][y]]\
                        .append(
                            Block(contiguous_characters))
        return to_return

    def find_contiguous_characters(self, seek_x, seek_y, found=None):
        seek_char = self._map[seek_x][seek_y]
        if found == None:
            found = set()
        found.add((seek_x, seek_y))
        for (x, y) in [(seek_x - 1, seek_y), (seek_x + 1, seek_y), 
                       (seek_x, seek_y - 1), (seek_x, seek_y + 1)]:
               # Don't include tiles outside of the map
            if (0 <= x < len(self._map)) \
               and (0 <= y < len(self._map[x])) \
               # Only include tiles for the character we're looking for
               and (seek_char == self._map[x][y]) \
               # If we've already included a tile, don't include it again
               and not (x, y) in found:
                    found |= self.find_contiguous_characters(x, y, found)
        return found

    @staticmethod
    def parse(infile):
        map = []
        for line in infile:
            # Don't include '\n' in the line
            map.append(list(line[:-1]))
        # Now I have a two-dimensional array addressed by [Y][X], want to 
        # rotate it so it's addressed by [X][Y]; lowest Y is at bottom
        # This is optional, the computer doesn't care, but it made 
        # debugging easier to use standard Cartesian coordinates
        return Map([list(z) for z in zip(*reversed(map))])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate the sizes of '\
                                                 'various aspects of a job '\
                                                 'site.')

    parser.add_argument('-i', '--input', action='store', default=None, 
                        dest='input', help='Input file to use.  If not '
                                            'provided, uses stdin.')
    parser.add_argument('-o', '--output', action='store', default=None, 
                        dest='output', help='Output file to use.  If not '
                                            'provided, uses stdout.')
    parser.add_argument('-s', '--scale-factor', action='store', default=10,
                        dest='scale_factor', help='How many feet to consider'
                                                  'there to be on a side of '
                                                  'a character')

    args = parser.parse_args()

    with (open(args.input) if args.input is not None else sys.stdin) \
         as infile:
        with (open(args.output, 'w')
              if args.output is not None
              else sys.stdout)\
             as outfile:
            m = Map.parse(infile)
            blocks = m.find_blocks()

            header = "Block Count, Length & Area Report"
            header += "\n" + ("=" * len(header)) + "\n"
            outfile.write(header)
            for char, associated_blocks in blocks.items():
                outfile.write(
                    '{char}: Total SF ({area}), '
                    'Total Circumference LF ({perimeter}) '
                    '- Found {num_blocks} blocks\n'
                    .format(char=char, 
                            area=sum([block.calculate_area() 
                                      for block in associated_blocks])
                                 * (args.scale_factor ** 2),
                            perimeter=sum([block.calculate_perimeter() 
                                           for block in associated_blocks])
                                      * args.scale_factor,
                            num_blocks=len(associated_blocks)
                            ))
