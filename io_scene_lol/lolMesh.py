# ##### BEGIN GPL LICENSE BLOCK ##### #
# lolblender - Python addon to use League of Legends files into blender
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
#from collections import UserDict
import struct
testFile = '/var/tmp/downloads/lol/Wolfman/Wolfman.skn'
    
class sknHeader():

    def __init__(self):
        #UserDict.__init__(self)
        self.__format__ = '<i2h'
        self.__size__ = struct.calcsize(self.__format__)
        self.magic = 0
        self.version = 0
        self.numObjects = 0
        self.endTab = [0,0,0]

    def fromFile(self, sknFid):
        buf = sknFid.read(self.__size__)
        (self.magic, self.version, 
                self.numObjects) = struct.unpack(self.__format__, buf)
        print("SKN version: %s" % self.version)
        print("numObjects: %s" % self.numObjects)

    def toFile(self, sknFid):
        buf = struct.pack(self.__format__, self.magic, self.version,
                self.numObjects)

        sknFid.write(buf)

    def __str__(self):
        return "{'__format__': %s, '__size__': %d, 'magic': %d, 'version': %d, 'numObjects':%d}"\
        %(self.__format__, self.__size__, self.magic, self.version, self.numObjects)

class sknMaterial():


    def __init__(self, name=None, startVertex=None,
            numVertices=None, startIndex=None, numIndices=None):
        # # UserDict.__init__(self)
        self.__format__ = '<64s4i'
        self.__size__ = struct.calcsize(self.__format__)
        
        self.name = name
        self.startVertex = startVertex
        self.numVertices = numVertices
        self.startIndex = startIndex
        self.numIndices = numIndices


    def fromFile(self, sknFid):
        buf = sknFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        #self.name = bytes.decode(fields[1])
        self.name = fields[0]
        (self.startVertex, self.numVertices) = fields[1:3]
        (self.startIndex, self.numIndices) = fields[3:5]

    def toFile(self, sknFid):
        buf = struct.pack(self.__format__, self.name,
                self.startVertex, self.numVertices,
                self.startIndex, self.numIndices)
        sknFid.write(buf)

    def __str__(self):
        return "{'__format__': %s, '__size__': %d, 'name': %s, 'startVertex': \
%d, 'numVertices':%d, 'startIndex': %d, 'numIndices': %d}"\
        %(self.__format__, self.__size__, self.name, self.startVertex,
                self.numVertices, self.startIndex, self.numIndices)



class sknMetaData():
    def __init__(self, part1=0, numIndices=None, numVertices=None, metaDataBlock=None):
        # # UserDict.__init__(self)
        self.__format__v12 = '<2i'
        self.__format__v4 = '<3i48b'
        self.__size__v12 = struct.calcsize(self.__format__v12)
        self.__size__v4 = struct.calcsize(self.__format__v4)
        
        self.part1 = part1
        self.numIndices = numIndices
        self.numVertices = numVertices
        if metaDataBlock is not None:
            self.metaDataBlock = metaDataBlock
        else:
            self.metaDataBlock = [0 for x in range(0,48)]
            self.metaDataBlock[0] = 52
            self.metaDataBlock[47] = 67

    def fromFile(self, sknFid, version):
        if version in [1,2]:
            buf = sknFid.read(self.__size__v12)
            fields = struct.unpack(self.__format__v12, buf)
            (self.numIndices, self.numVertices) = fields
        elif version in [4]:
            buf = sknFid.read(self.__size__v4)
            fields = struct.unpack(self.__format__v4, buf)
            (self.part1, self.numIndices, self.numVertices) = fields[0:3]
            self.metaDataBlock = fields[3:51]
        else:
            raise ValueError("Version %s not supported" % version)
        self.version = version


    def toFile(self, sknFid, version):
        if version in [1,2]:
            buf = struct.pack(self.__format__v12, self.numIndices,
                    self.numVertices)
            sknFid.write(buf)
        elif version in [4]:
            buf = struct.pack(self.__format__v4, self.part1,
                    self.numIndices, self.numVertices, *self.metaDataBlock[0:48])
            sknFid.write(buf)
        else:
            raise ValueError("Version %s not supported" % version)
        

    def __str__(self):
        if self.version in [1,2]:
            return "{'version': %s, '__format__': %s, '__size__': %d, 'numIndices': %d, \
                    'numVertices': %d}" % (self.version, self.__format__v12,
                    self.__size__v12, self.numIndices, self.numVertices)
        elif self.version in [4]:
            return "{'version': %s, '__format__': %s, '__size__': %d, \
                    'part1': %d, 'numIndices': %d, 'numVertices': %d, \
                    'metaDataBlock': %s}" % (self.version, self.__format__v4,
                    self.__size__v4, self.part1, self.numIndices,
                    self.numVertices, self.metaDataBlock)
        else:
            ValueError('Unsupported version number, or version not set')


class sknVertex():
    def __init__(self):
        #UserDict.__init__(self)
        self.__format__ = '<3f4b4f3f2f'
        self.__size__ = struct.calcsize(self.__format__)
        self.reset()

    def reset(self):
        self.position = [0.0, 0.0, 0.0]
        self.boneIndex = [0, 0, 0, 0]
        self.weights = [0.0, 0.0, 0.0, 0.0]
        self.normal = [0.0, 0.0, 0.0]
        self.texcoords = [0.0, 0.0]

    def fromFile(self, sknFid):
        buf = sknFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        self.position = fields[0:3]
        self.boneIndex = fields[3:7]
        self.weights = fields[7:11]
        self.normal = fields[11:14]
        self.texcoords = fields[14:16]

    def toFile(self, sknFid):
        buf = struct.pack(self.__format__,
                self.position[0], self.position[1], self.position[2],
                self.boneIndex[0],self.boneIndex[1],self.boneIndex[2],self.boneIndex[3],
                self.weights[0],self.weights[1],self.weights[2],self.weights[3],
                self.normal[0],self.normal[1],self.normal[2],
                self.texcoords[0],self.texcoords[1])
        sknFid.write(buf)

class scoObject():

    def __init__(self):
        self.name = None
        self.centralpoint = None
        self.pivotpoint = None
        self.vtxList = []
        self.faceList = []
        self.uvDict = {}
        self.materialDict = {}


def importSKN(filepath):
    sknFid = open(filepath, 'rb')
    print("Reading SKN: %s" % filepath)
    #filepath = path.split(file)[-1]
    #print(filepath)
    header = sknHeader()
    header.fromFile(sknFid)

    materials = []
    buf = sknFid.read(struct.calcsize('<i'))
    numMaterials = struct.unpack('<i', buf)[0]
    print ("number of Materials: %s" % numMaterials)
    for k in range(numMaterials):
        materials.append(sknMaterial())
        materials[-1].fromFile(sknFid)

    metaData = sknMetaData()
    metaData.fromFile(sknFid, header.version)

    indices = []
    vertices = []
    for k in range(metaData.numIndices):
        buf = sknFid.read(struct.calcsize('<h'))
        indices.append(struct.unpack('<h', buf)[0])

    for k in range(metaData.numVertices):
        vertices.append(sknVertex())
        vertices[-1].fromFile(sknFid)

    # exclusive to version two+.
    if header.version >= 2:  # stuck in header b/c nowhere else for it
        header.endTab = [struct.unpack('<3i', sknFid.read(struct.calcsize('<3i')))]

    sknFid.close()

    return header, materials, metaData, indices, vertices

def skn2obj(header, materials, indices, vertices):
    objStr=""
    if header.version > 0:
        objStr+="g mat_%s\n" %(materials[0].name)
    for vtx in vertices:
        objStr+="v %f %f %f\n" %(vtx.position)
        objStr+="vn %f %f %f\n" %(vtx.normal)
        objStr+="vt %f %f\n" %(vtx.texcoords[0], 1-vtx.texcoords[1])

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
    import bpy
    from os import path
    (header, materials, metaData, indices, vertices) = importSKN(filepath)
    ''' 
    if header.version > 0 and materials[0].numMaterials == 2:
        print('ERROR:  Skins with numMaterials = 2 are currently unreadable.  Exiting')
        return{'CANCELLED'} 
    '''
    numIndices = len(indices)
    numVertices = len(vertices)
    #Create face groups
    faceList = []
    for k in range(0, numIndices, 3):
        #faceList.append( [indices[k], indices[k+1], indices[k+2]] )
        faceList.append( indices[k:k+3] )

    vtxList = []
    normList = []
    uvList = []
    for vtx in vertices:
        vtxList.append( vtx.position[:] )
        normList.extend( vtx.normal[:] )
        uvList.append( [vtx.texcoords[0], 1-vtx.texcoords[1]] )

    #Build the mesh
    #Get current scene
    scene = bpy.context.scene
    #Create mesh
    #Use the filename base as the meshname.  i.e. path/to/Akali.skn -> Akali
    meshName = path.split(filepath)[-1]
    meshName = path.splitext(meshName)[0]
    mesh = bpy.data.meshes.new(meshName)
    mesh.from_pydata(vtxList, [], faceList)
    mesh.update()

    bpy.ops.object.select_all(action='DESELECT')
    
    #Create object from mesh
    obj = bpy.data.objects.new('lolMesh', mesh)

    #Link object to the current scene
    scene.objects.link(obj)


    #Create UV texture coords
    texList = []
    uvtexName = 'lolUVtex'
    obj.data.uv_textures.new(uvtexName)
    uv_layer = obj.data.uv_layers[-1].data  # sets layer to the above texture
    set = []
    for k, loop in enumerate(obj.data.loops):
        # data.loops contains the vertex of tris
        # k/3 = triangle #
        # k%3 = vertex number in that triangle
        v = loop.vertex_index  # "index" number
        set.append(uvList[v][0])  # u
        set.append(uvList[v][1])  # v
    uv_layer.foreach_set("uv", set)

    #Set normals
    #Needs to be done after the UV unwrapping 
    obj.data.vertices.foreach_set('normal', normList) 

    #Create material
    materialName = 'lolMaterial'
    #material = bpy.data.materials.ne(materialName)
    mesh.update() 
    #set active
    obj.select = True

    return {'FINISHED'}
    
def addDefaultWeights(boneList, sknVertices, armatureObj, meshObj):

    '''Add an armature modifier to the mesh'''
    meshObj.modifiers.new(name='Armature', type='ARMATURE')
    meshObj.modifiers['Armature'].object = armatureObj

    '''
    Blender bone deformations create vertex groups with names corresponding to
    the intended bone.  I.E. the bone 'L_Hand' deforms vertices in the group
    'L_Hand'.

    We will create a vertex group for each bone using their index number
    '''

    for id, bone in enumerate(boneList):
        meshObj.vertex_groups.new(name=bone.name)

    '''
    Loop over vertices by index & add weights
    '''
    for vtx_idx, vtx in enumerate(sknVertices):
        for k in range(4):
            boneId = vtx.boneIndex[k]
            weight = vtx.weights[k]

            meshObj.vertex_groups[boneId].add([vtx_idx],
                    weight,
                    'ADD')

def exportSKN(meshObj, output_filepath, input_filepath, BASE_ON_IMPORT, VERSION):
    import bpy

    if VERSION not in [1,2,4] and not BASE_ON_IMPORT:
        raise ValueError("Version %d not supported! Try versions 1, 2, or 4" % VERSION)

    #Go into object mode & select only the mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    meshObj.select = True

    numFaces = len(meshObj.data.loops) // 3
    
    #Build vertex index list and dictionary of vertex-uv pairs
    indices = []
    vtxUvs = {}
    for idx, loop in enumerate(meshObj.data.loops):
        vertex = loop.vertex_index
        indices.append(vertex)
        #The V coordinate need to be flipped back - it was flipped on importing.
        uv = meshObj.data.uv_layers['lolUVtex'].data[idx].uv
        vtxUvs[vertex] = [uv[0], 1-uv[1]]
        
    numIndices = len(indices)
    numVertices = len(meshObj.data.vertices)

    #Write header block
    if BASE_ON_IMPORT:
        (import_header, import_mats, import_meta_data, import_indices,
        import_vertices) = importSKN(input_filepath)
        header = import_header
        VERSION = header.version
        
        numMats = len(import_mats)
        if numMats > 1:
            raise ValueError("More than 1 material (%d); not supported" % numMats)
        matHeaders = import_mats

        meta_data = import_meta_data
        
        #override previous #verts, #idxs so no memory error!
        matHeaders[0].numIndices = numIndices
        matHeaders[0].numVertices = numVertices
        meta_data.numIndices = numIndices
        meta_data.numVertices = numVertices
    else:
        header = sknHeader()
        header.magic = 1122867
        header.version = VERSION
        header.numObjects = 1

        numMats = 1
        matHeaders = []
        mat = sknMaterial(b'test', 0, numVertices, 0, numIndices)
        matHeaders.append(mat)

        meta_data = sknMetaData(0, numIndices, numVertices)

    #create output file 
    sknFid = open(output_filepath, 'wb')
    
    #write header
    header.toFile(sknFid)
    if header.numObjects > 0:  # if materials exist
        sknFid.write(struct.pack('<1i', numMats))
        #We are writing a materials block
        for mat in matHeaders:
            mat.toFile(sknFid)

    meta_data.toFile(sknFid, VERSION)

    #write face indices
    for idx in indices:
        buf = struct.pack('<h', idx)
        sknFid.write(buf)

    #Write vertices
    sknVtx = sknVertex()
    for idx, vtx in enumerate(meshObj.data.vertices):
        sknVtx.reset()
        #get position
        sknVtx.position[0] = vtx.co[0]
        sknVtx.position[1] = vtx.co[1]
        sknVtx.position[2] = vtx.co[2]
        
        sknVtx.normal[0] = vtx.normal[0]
        sknVtx.normal[1] = vtx.normal[1]
        sknVtx.normal[2] = vtx.normal[2]

        #get weights
        #The SKN format only allows 4 bone weights,
        #so we'll choose the largest 4 & renormalize
        #if needed

        if len(vtx.groups) > 4:
            tmpList = []
            #Get all the bone/weight pairs
            for group in vtx.groups:
                tmpList.append((group.group, group.weight))

            #Sort by weight in decending order
            tmpList = sorted(tmpList, key=lambda t: t[1], reverse=True)
            
            #Find sum of four largets weights.
            tmpSum = 0
            for k in range(4):
                tmpSum += tmpList[k][1]
            
            #Spread remaining weight proportionally across bones
            remWeight = 1-tmpSum
            for k in range(4):
                sknVtx.boneIndex[k] = tmpList[k][0]
                sknVtx.weights[k] = tmpList[k][1] + tmpList[k][1]*remWeight/tmpSum

        else:
            #If we have 4 or fewer bone/weight associations,
            #just add them as is
            for vtxIdx, group in enumerate(vtx.groups):
                sknVtx.boneIndex[vtxIdx] = group.group
                sknVtx.weights[vtxIdx] = group.weight

        #Get UV's
        sknVtx.texcoords[0] = vtxUvs[idx][0]
        sknVtx.texcoords[1] = vtxUvs[idx][1]

        #writeout the vertex
        sknVtx.toFile(sknFid)
    
    if VERSION >= 2:  # some extra ints in v2+. not sure what they do, non-0 in v4?
        if header.endTab is None or len(header.endTab) < 3:
            header.endTab = [0, 0, 0]
        sknFid.write(struct.pack('<3i', header.endTab[0], header.endTab[1], header.endTab[2]))

    #Close the output file
    sknFid.close()

def importSCO(filename):
    '''SCO files contains meshes in plain text'''
    fid = open(filename, 'r')
    objects = []
    inObject = False
    
    #Loop until we reach the end of the file
    while True:
        
        line = fid.readline()
        #Check if we've reached the file end
        if line == '':
            break
        else:
            #Remove all leading/trailing whitespace & convert to lower case
            line = line.strip().lower()

        #Start checking against keywords
    
        #Are we just starting an object?
        if line.startswith('[objectbegin]') and not inObject:
            inObject = True
            objects.append(scoObject())
            continue

        #Are we ending an object?
        if line.startswith('[objectend]') and inObject:
            inObject = False
            continue

        #If we're in an object, start parsing
        #Headers appear space-deliminted
        #'Name= [name]', 'Verts= [verts]', etc.
        #Valid fields:
        #   name
        #   centralpoint
        #   pivotpoint
        #   verts
        #   faces

        if inObject:
            if line.startswith('name='):
                objects[-1].name=line.split()[-1]

            elif line.startswith('centralpoint='):
                objects[-1].centralpoint = line.split()[-1]

            elif line.startswith('pivotpoint='):
                objects[-1].pivotpoint = line.split()[-1]
            
            elif line.startswith('verts='):
                verts = line.split()[-1]
                for k in range(int(verts)):
                    vtxPos = fid.readline().strip().split()
                    vtxPos = [float(x) for x in vtxPos]
                    objects[-1].vtxList.append(vtxPos)

            elif line.startswith('faces='):
                faces = line.split()[-1]
                
                for k in range(int(faces)):
                    fields = fid.readline().strip().split()
                    nVtx = int(fields[0])
                    
                    vIds = [int(x) for x in fields[1:4]]
                    mat = fields[4]
                    uvs = [ [] ]*3
                    uvs[0] = [float(x) for x in fields[5:7]]
                    uvs[1] = [float(x) for x in fields[7:9]]
                    uvs[2] = [float(x) for x in fields[9:11]]

                    objects[-1].faceList.append(vIds)
                    #Blender can only handle material names of 16 characters or
                    #less
                    #if len(mat) > 16:
                        #mat = mat[:16]
                    
                    #Add the face index to the material
                    try:
                        objects[-1].materialDict[mat].append(k)
                    except KeyError:
                        objects[-1].materialDict[mat] = [k]

                    #Add uvs to the face index
                    for k,j in enumerate(vIds):
                        objects[-1].uvDict[j]=uvs[k]

    #Close out and return the parsed objects
    fid.close()
    return objects

def buildSCO(filename):
    import bpy
    scoObjects = importSCO(filename)

    for sco in scoObjects:

        #get scene
        scene=bpy.context.scene
        mesh = bpy.data.meshes.new(sco.name)
        mesh.from_pydata(sco.vtxList, [], sco.faceList)
        mesh.update()

        meshObj = bpy.data.objects.new(sco.name, mesh)

        scene.objects.link(meshObj)

        #print(sco.materialList)
        for matID, mat in enumerate(sco.materialDict.keys()):
            faceList = sco.materialDict[mat]
            #Blener can only handle material names of 16 chars.  Construct a
            #unique name ID using ##_name
            if len(mat) > 16:
                mat = str(matID).zfill(2) + '_' + mat[:13]

            uvtex = meshObj.data.uv_textures.new(mat)
            for k, face in enumerate(meshObj.data.faces):

                vtxIds = face.vertices[:]
                bl_tface = uvtex.data[k]
                bl_tface.uv1[0] = sco.uvDict[vtxIds[0]][0]
                bl_tface.uv1[1] = 1-sco.uvDict[vtxIds[0]][1]

                bl_tface.uv2[0] = sco.uvDict[vtxIds[1]][0]
                bl_tface.uv2[1] = 1-sco.uvDict[vtxIds[1]][1]

                bl_tface.uv3[0] = sco.uvDict[vtxIds[2]][0]
                bl_tface.uv3[1] = 1-sco.uvDict[vtxIds[2]][1]

        mesh.update()
        
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
    #        idx = vtx.boneIndex[k]
    #        if idx < 1 or idx > 26:
    #            print(i, vtx)
    #    i+=1
