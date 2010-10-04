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
        #self['name'] = bytes.decode(fields[1])
        self['name'] = fields[1]
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
    #filepath = path.split(file)[-1]
    #print(filepath)
    header = sknHeader()
    header.fromFile(sknFid)

    materials = []
    if header['numMaterials'] > 0:
        materials.append(sknMaterial())
        materials[-1].fromFile(sknFid)

    buf = sknFid.read(struct.calcsize('<2i'))
    numIndices, numVertices = struct.unpack('<2i', buf)
    #print(numIndices, numVertices)

    #For some files, numIndices and numVertices aren't put after the first
    #material and our unpacking above results in bogus values.  In these
    #cases numIndices and numVertices will have some bogus huge value due to
    #improper unpacking - check against this.  If true, use the values in the
    #material header.  These files have matIndex = 2 and are unreadable atm.
    
    if header['numMaterials'] > 0 and materials[-1]['matIndex'] == 2:
        print('WARNING:  This skin has matIndex = 2 and is currently unreadable')
        if abs(numIndices) > 20e3 or abs(numVertices) > 10e3:
            numIndices = materials[0]['numIndices']
            numVertices = materials[0]['numVertices']
            sknFid.seek(-(struct.calcsize('<2i')),1)
    #print(numIndices, numVertices)

    indices = []
    vertices = []
    for k in range(numIndices):
        buf = sknFid.read(struct.calcsize('<h'))
        indices.append(struct.unpack('<h', buf))

    for k in range(numVertices):
        vertices.append(sknVertex())
        vertices[-1].fromFile(sknFid)

    #fpos = sknFid.tell()
    #fsize = stat(file).st_size
    #buf = sknFid.read()
    #print(buf)
    sknFid.close()

    #print('numObjects: %d numMaterials: %d rbytes %d %s' %(header['numObjects'], header['numMaterials'], fsize - fpos, filepath))
    #filename = path.split(file)[-1]
    return header, materials, indices, vertices

class dummyContext(object):
    def __init__(self):
        self.scene = None

def skn2obj(header, materials, indices, vertices):
    objStr=""
    if header['numMaterials'] > 0:
        objStr+="g mat_%s\n" %(materials[0]['name'])
    for vtx in vertices:
        objStr+="v %f %f %f\n" %(vtx['position'])
        objStr+="vn %f %f %f\n" %(vtx['normal'])
        objStr+="vt %f %f\n" %(vtx['texcoords'][0], 1-vtx['texcoords'][1])

    tmp = int(len(indices)/3)
    for idx in range(tmp):
        a = indices[3*idx][0] + 1
        b = indices[3*idx + 1][0] + 1
        c = indices[3*idx + 2][0] + 1
        objStr+="f %d/%d/%d" %(a,a,a)
        objStr+=" %d/%d/%d" %(b,b,b)
        objStr+=" %d/%d/%d\n" %(c,c,c)

    return objStr

def buildMesh(filepath):
    import os.path
    from io_scene_obj import import_obj
    import bpy
    (header, materials, indices, vertices) = importSKN(filepath)
    print(materials)
    if header['numMaterials'] > 0 and materials[0]['matIndex'] == 2:
        print('ERROR:  Skins with matIndex = 2 are currently unreadable.  Exiting')
        return {'FINISHED'}
    objStr = skn2obj(header, materials, indices, vertices)
    objFile = os.path.splitext(filepath)[0]+'.obj'

    objFid = open(objFile, 'w')
    objFid.write(objStr)
    objFid.close()

    context = dummyContext()
    context.scene = bpy.data.scenes[0]

    import_obj.load(None, context, objFile, CREATE_FGONS=False,
        CREATE_SMOOTH_GROUPS = False, CREATE_EDGES = False,
        SPLIT_OBJECTS = False, SPLIT_GROUPS = False, ROTATE_X90 = False,
        IMAGE_SEARCH=False, POLYGROUPS = False)

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
