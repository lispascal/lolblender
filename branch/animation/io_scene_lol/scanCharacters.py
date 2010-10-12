from os import path, walk, stat
import lolSkeleton
import lolMesh
import struct 

characterDir = '/Users/zac/Desktop/LoL Modeling/Characters'

sklFiles = []
sknFiles = []

for root, dirs, files in walk(characterDir):
    for file in files:
        name, ext = path.splitext(file)
        if ext.lower() == '.skl':
            sklFiles.append(path.join(root,file))
        elif ext.lower() == '.skn':
            sknFiles.append(path.join(root,file))

        
#for file in sklFiles:
    #header, boneDict = lolSkeleton.importSKL(file)
    #filename = path.split(file)[-1]
    #print(filename, 'numObjects: %d' % (header['numObjects'], ))
#sknFiles = ['/Users/zac/Desktop/LoL Modeling/Characters/Nidalee/Nidalee.skn']
#sknFiles = ['/Users/zac/Desktop/LoL Modeling/Characters/CardMaster/CardMaster_swanky.skn']
for file in sknFiles:
    sknFid = open(file, 'rb')
    filepath = path.split(file)[-1]
    #print(file)
    header = lolMesh.sknHeader()
    header.fromFile(sknFid)
    #print(header)
    materials = []
    if header['numMaterials'] > 0:
        materials.append(lolMesh.sknMaterial())
        materials[-1].fromFile(sknFid)

    #print(materials)
    buf = sknFid.read(struct.calcsize('<2i'))
    numIndices, numVertices = struct.unpack('<2i', buf)
    #print(numIndices, numVertices)

    if abs(numIndices) > 20e3 or abs(numVertices) > 10e3:
        #print('OOPS')
        numIndices = materials[0]['numIndices']
        numVertices = materials[0]['numVertices']
        sknFid.seek(-(struct.calcsize('<2i')),1)
    #print(numIndices, numVertices)

    indices = []
    vertices = []
    for k in range(numVertices):
        vertices.append(lolMesh.sknVertex())
        vertices[-1].fromFile(sknFid)
    for k in range(numIndices):
        buf = sknFid.read(struct.calcsize('<h'))
        indices.append(struct.unpack('<h', buf))

    fpos = sknFid.tell()
    fsize = stat(file).st_size
    rbytes = fsize-fpos
    buf = sknFid.read()
    #print(buf)
    sknFid.close()

    if rbytes > 12:
        tmp = file.split(path.sep)
        shortPath = path.sep.join(tmp[-3:])
        print('numObjects: %d numMaterials: %d matIndex: %d rbytes %d %s' %(header['numObjects'], header['numMaterials'], materials[0]['matIndex'], fsize - fpos, shortPath))
    #filename = path.split(file)[-1]
    #print(filename, 'numObjects: %d' % (header['numObjects'], ))
"""
sknFiles = ['/Users/zac/Desktop/LoL Modeling/Characters/Armsmaster/Armsmaster_midnight.skn']
fileSize = stat(sknFiles[0]).st_size
sknFid = open(sknFiles[0], 'rb')
header = lolMesh.sknHeader()
header.fromFile(sknFid)
print(header)

materials = []
materials.append(lolMesh.sknMaterial())
materials[-1].fromFile(sknFid)

print(materials[0])
buf = sknFid.read(struct.calcsize('<2i'))
numIndices, numVertices = struct.unpack('<2i', buf)
print(numIndices, numVertices)
if abs(numIndices) > 20e3:
    numIndices = materials[0]['numIndices']
if abs(numVertices) > 20e3:
    numVertices = materials[0]['numVertices']
print(numIndices, numVertices)

indices = []
vertices = []

for k in range(numIndices):
    buf = sknFid.read(struct.calcsize('<h'))
    indices.append(struct.unpack('<h', buf))

for k in range(numVertices):
    vertices.append(lolMesh.sknVertex())
    vertices[-1].fromFile(sknFid)
print(sknFid.tell(), fileSize, fileSize-sknFid.tell())
"""
