from collections import UserDict
import struct
testFile = '/var/tmp/downloads/lol/Wolfman/Wolfman.skn'
class sknHeader(UserDict):

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<i2h'
        self.__size__ = struct.calcsize(self.__format__)
        self['magic'] = None
        self['numMaterials'] = None
        self['numObjects'] = None

    def fromFile(self, sknFid):
        buf = sknFid.read(self.__size__)
        (self['magic'], self['numMaterials'], 
                self['numObjects']) = struct.unpack(self.__format__, buf)

    def toFile(self, sknFid):
        buf = struct.pack(self.__format__, self['magic'], self['numMaterials'],
                self['numObjects'])
        sknFid.write(buf)

class sknMaterial(UserDict):

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<i64s4i'
        self.__size__ = struct.calcsize(self.__format__)

        self['matIndex'] = None
        self['name'] = None
        self['startVertex'] = None
        self['numVertices'] = None
        self['startIndex'] = None
        self['numIndices'] = None

    def fromFile(self, sknFid):
        buf = sknFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        self['matIndex'] = fields[0]
        self['name'] = bytes.decode(fields[1])
        (self['startVertex'], self['numVertices']) = fields[2:4]
        (self['startIndex'], self['numIndices']) = fields[4:6]


class sknVertex(UserDict):
    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<3f4b4f3f2f'
        self.__size__ = struct.calcsize(self.__format__)

        self['position'] = []
        self['boneIndex'] = None
        self['weights'] = []
        self['normal'] = []
        self['texcoords'] = []

    def fromFile(self, sknFid):
        buf = sknFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        self['position'] = fields[0:3]
        self['boneIndex'] = fields[3:7]
        self['weights'] = fields[7:11]
        self['normal'] = fields[11:14]
        self['texcoords'] = fields[14:16]


def importSKN(filepath):
    sknFid = open(filepath, 'rb')

    header = sknHeader()
    header.fromFile(sknFid)

    materials = []

    for k in range(header['numMaterials']):
        materials.append(sknMaterial())
        materials[-1].fromFile(sknFid)

    buf = sknFid.read(struct.calcsize('<2i'))
    (numIndices, numVertices) = struct.unpack('<2i', buf)

    indices = []
    for k in range(numIndices):
        idx = struct.unpack('<h', sknFid.read(struct.calcsize('<h')))
        indices.append(idx)

    vertices = []
    for k in range(numVertices):
        vertices.append(sknVertex())
        vertices[-1].fromFile(sknFid)

    return header, materials, numIndices, numVertices, indices, vertices



if __name__ == '__main__':
    (header, materials, numIndices, 
            numVertices, indices, vertices) = importSKN(testFile)

    print(header)
    print(materials)
    print(numIndices)
    print(numVertices)
    print(indices[0])
    print(vertices[0])

    #print('Checking bone indices')
    #i = 0
    #for vtx in vertices:
    #    for k in range(4):
    #        idx = vtx['boneIndex'][k]
    #        if idx < 1 or idx > 26:
    #            print(i, vtx)
    #    i+=1
