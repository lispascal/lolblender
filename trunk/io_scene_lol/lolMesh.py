# ##### BEGIN GPL LICENSE BLOCK ##### #
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
from collections import UserDict
import struct
testFile = '/var/tmp/downloads/lol/Wolfman/Wolfman.skn'
    
class sknHeader():

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<i2h'
        self.__size__ = struct.calcsize(self.__format__)
        self.magic = None
        self.numMaterials = None
        self.numObjects = None

    def fromFile(self, sknFid):
        buf = sknFid.read(self.__size__)
        (self.magic, self.numMaterials, 
                self.numObjects) = struct.unpack(self.__format__, buf)

    def toFile(self, sknFid):
        buf = struct.pack(self.__format__, self.magic, self.numMaterials,
                self.numObjects)
        sknFid.write(buf)

class sknMaterial(UserDict):

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<i64s4i'
        self.__size__ = struct.calcsize(self.__format__)

        self.matIndex = None
        self.name = None
        self.startVertex = None
        self.numVertices = None
        self.startIndex = None
        self.numIndices = None

    def fromFile(self, sknFid):
        buf = sknFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        self.matIndex = fields[0]
        #self.name = bytes.decode(fields[1])
        self.name = fields[1]
        (self.startVertex, self.numVertices) = fields[2:4]
        (self.startIndex, self.numIndices) = fields[4:6]

    def toFile(self, sknFid):
        buf = struct.pack(self.__format__, self.matIndex, self.name,
                self.startVertex, self.numVertices,
                self.startIndex, self.numIndices)
        sknFid.write(buf)


class sknVertex(UserDict):
    def __init__(self):
        UserDict.__init__(self)
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
        self.materialList = []


def importSKN(filepath):
    sknFid = open(filepath, 'rb')
    #filepath = path.split(file)[-1]
    #print(filepath)
    header = sknHeader()
    header.fromFile(sknFid)

    materials = []
    if header.numMaterials > 0:
        materials.append(sknMaterial())
        materials[-1].fromFile(sknFid)

    buf = sknFid.read(struct.calcsize('<2i'))
    numIndices, numVertices = struct.unpack('<2i', buf)

    #For some files, numIndices and numVertices aren't put after the first
    #material and our unpacking above results in bogus values.  In these
    #cases numIndices and numVertices will have some bogus huge value due to
    #improper unpacking - check against this.  If true, use the values in the
    #material header.  These files have matIndex = 2 and are unreadable atm.
    
    if header.numMaterials > 0 and materials[-1].matIndex == 2:
        print('WARNING:  This skin has matIndex = 2 and is currently unreadable')
        if abs(numIndices) > 20e3 or abs(numVertices) > 10e3:
            numIndices = materials[0].numIndices
            numVertices = materials[0].numVertices
            sknFid.seek(-(struct.calcsize('<2i')),1)

    indices = []
    vertices = []
    for k in range(numIndices):
        buf = sknFid.read(struct.calcsize('<h'))
        indices.append(struct.unpack('<h', buf)[0])

    for k in range(numVertices):
        vertices.append(sknVertex())
        vertices[-1].fromFile(sknFid)

    sknFid.close()

    return header, materials, indices, vertices

class dummyContext(object):
    def __init__(self):
        self.scene = None

def skn2obj(header, materials, indices, vertices):
    objStr=""
    if header.numMaterials > 0:
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
    (header, materials, indices, vertices) = importSKN(filepath)
    
    if header.numMaterials > 0 and materials[0].matIndex == 2:
        print('ERROR:  Skins with matIndex = 2 are currently unreadable.  Exiting')
        return{'CANCELLED'} 

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
    uvtex = obj.data.uv_textures.new(uvtexName)
    for k, face in enumerate(obj.data.faces):
        vtxIdx = face.vertices[:]
        bl_tface = uvtex.data[k]
        bl_tface.uv1 = uvList[vtxIdx[0]]
        bl_tface.uv2 = uvList[vtxIdx[1]]
        bl_tface.uv3 = uvList[vtxIdx[2]]

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

            meshObj.vertex_groups.assign([vtx_idx],
                    meshObj.vertex_groups[boneId],
                    weight,
                    'ADD')

def exportSKN(meshObj, outFile):
    import bpy
    #Go into object mode & select only the mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    meshObj.select = True

    numFaces = len(meshObj.data.faces)
    
    #Build vertex index list and dictionary of vertex-uv pairs
    indices = []
    vtxUvs = {}
    for idx, face in enumerate(meshObj.data.faces):
        vertices = face.vertices[0:]
        indices.extend(vertices)
        #The V coordinate need to be flipped back - it was flipped on importing.
        uvs = meshObj.data.uv_textures['lolUVtex'].data[idx]

        vtxUvs[vertices[0]] = [uvs.uv_raw[0], 1-uvs.uv_raw[1]]
        vtxUvs[vertices[1]] = [uvs.uv_raw[2] ,1-uvs.uv_raw[3]]
        vtxUvs[vertices[2]] = [uvs.uv_raw[4], 1-uvs.uv_raw[5]]

    numIndices = len(indices)
    numVertices = len(meshObj.data.vertices)

    #Write header block
    header = sknHeader()
    header.magic = 1122867
    header.numMaterials = 0
    header.numObjects = 1

    #create output file 
    sknFid = open(outFile, 'wb')
    
    #write header
    header.toFile(sknFid)

    #We're not writing a materials block, so write the numIndices and
    #numVertices next
    buf = struct.pack('<2i', numIndices, numVertices)
    sknFid.write(buf)

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
                    if len(mat) > 16:
                        mat = mat[:16]
                    
                    #First time we've come across this material?  Add it to the
                    #list
                    if mat not in objects[-1].materialList:
                        objects[-1].materialList.append(mat)

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

        print(sco.materialList)
        for mat in sco.materialList:
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
