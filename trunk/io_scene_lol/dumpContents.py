#!/bin/python3.1
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
import lolMesh, lolSkeleton
def prettyPrintSkl(filename, start=0, end=-1, returnStr=True, **options):
    
    header, boneDict = lolSkeleton.importSKL(filename)
    headerStr = ""
    if(options['PRINT_HEADER']): 
        headerStr += \
        "Filetype:%s\nnumObjects:%d\nskeletonHash:%d\nnumElements:%d\n\n" % (header['fileType'], 
                header['numObjects'], header['skeletonHash'], header['numElements'])
    boneStr = ""
    if(options['PRINT_BONES']):
        if end == -1:
            end = len(boneDict)
        for id in range(start,stop):
            bone = boneDict[id]
            if bone['parent'] != -1:
                parentName = boneDict[bone['parent']]['name']
            else:
                parentName = "None"
           
            boneStr += "%d\t%s\tparent id:%d\t(%s)\n" %(id, bone['name'],
                    bone['parent'], parentName)
            boneStr += "\tscale:  %f\n" %(bone['scale'],)
            boneStr += "\tmatrix:\t %7.4f  %7.4f  %7.4f  %7.4f\n" %(bone['matrix'][0][0],
                    bone['matrix'][0][1], bone['matrix'][0][2], bone['matrix'][0][3])
            boneStr += "\t\t %7.4f  %7.4f  %7.4f  %7.4f\n" %(bone['matrix'][1][0],
                    bone['matrix'][1][1],bone['matrix'][1][2],bone['matrix'][1][3])
            boneStr += "\t\t %7.4f  %7.4f  %7.4f  %7.4f\n\n" %(bone['matrix'][2][0],
                    bone['matrix'][2][1], bone['matrix'][2][2], bone['matrix'][2][3])

    if returnStr == True:
        return headerStr+boneStr
    else:
        print(headerStr+boneStr)

def prettyPrintSkn(filename, start=0, end=-1, returnStr = True, **options):
    header, materials, indices, vertices = lolMesh.importSKN(filename)
    headerStr = ""
    if(options['PRINT_HEADER']):
        headerStr += "magic:%d\nnumMaterials:%d\nnumObjects:%d\n\n" % (header['magic'], 
            header['numMaterials'], header['numObjects']) 

    materialStr = ""
    if(options['PRINT_MATERIALS']):
        if header['numMaterials'] == 0:
            materialStr +="No material blocks present\n\n"
        else:
            for material in materials:
                materialStr += \
                "matIndex:%d\nname:%s\nstartVertex:%d\tnumVertices:%d\nstartIndex:%d\tnumIndices:%d\n\n" %\
                (material['matIndex'], bytes.decode(material['name']).strip('\x00'),material['startVertex'], \
                material['numVertices'], material['startIndex'], material['numIndices'])

    indexStr = ""
    if(options['PRINT_INDICES']):
        for indx in indices:
            indexStr += "%d\n" %(indx[0],)

    vertexStr = ""
    if(options['PRINT_VERTICES']):
        for indx, vtx in enumerate(vertices[start:stop]):
            vertexStr += \
                "%d\tpos:(%f,%f,%f)\tboneIndx:(%d,%d,%d,%d)\n"%(start+indx, 
                    vtx['position'][0], vtx['position'][1],vtx['position'][2],
                    vtx['boneIndex'][0],vtx['boneIndex'][1],vtx['boneIndex'][2],vtx['boneIndex'][3])
            vertexStr += \
                "\tnorm:(%f,%f,%f)\tweights:(%f,%f,%f,%f)\n"%\
                (vtx['normal'][0],vtx['normal'][1],vtx['normal'][2],\
                vtx['weights'][0],vtx['weights'][1],vtx['weights'][2],vtx['weights'][3])
            vertexStr += "\tuvs:(%f, %f)\n"%(vtx['texcoords'][0],vtx['texcoords'][1])

    if returnStr == True:
        return headerStr+materialStr+indexStr+vertexStr
    else:
        print(headerStr+materialStr+indexStr+vertexStr)

def cvsPrintSkl(filename, start=0, end=-1, returnStr=True, **options):
    
    header, boneDict = lolSkeleton.importSKL(filename)
    headerStr = ""
    if(options['PRINT_HEADER']): 
        headerStr += "#fileType, numObjects, skeletonHash, numElements\n"
        headerStr += \
        "%s,%d,%d,%d\n" % (header['fileType'], 
                header['numObjects'], header['skeletonHash'], header['numElements'])
    boneStr = ""
    if(options['PRINT_BONES']):
        boneStr+="#boneID, name, parentID, scale,"
        boneStr+="matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],"
        boneStr+="matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],"
        boneStr+="matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3]\n"
        if end == -1:
            end = len(boneDict)
        for id in range(start,stop):
            bone = boneDict[id]
            if bone['parent'] != -1:
                parentName = boneDict[bone['parent']]['name']
            else:
                parentName = "None"
           
            boneStr += "%d,%s,%d," %(id, bone['name'],bone['parent'])
            boneStr += "%f," %(bone['scale'],)
            boneStr += "%e,%e,%e,%e," %(bone['matrix'][0][0],
                    bone['matrix'][0][1], bone['matrix'][0][2], bone['matrix'][0][3])
            boneStr += "%e,%e,%e,%e," %(bone['matrix'][1][0],
                    bone['matrix'][1][1],bone['matrix'][1][2],bone['matrix'][1][3])
            boneStr += "%e,%e,%e,%e\n" %(bone['matrix'][2][0],
                    bone['matrix'][2][1], bone['matrix'][2][2], bone['matrix'][2][3])

    if returnStr == True:
        return headerStr+boneStr
    else:
        print(headerStr+boneStr)

def cvsPrintSkn(filename, start=0, end=-1, returnStr = True, **options):
    header, materials, indices, vertices = lolMesh.importSKN(filename)
    headerStr = ""
    if(options['PRINT_HEADER']):
        headerStr+="#magic, numMaterials, numObjects\n"
        headerStr += "%d,%d,%d\n" % (header['magic'], 
            header['numMaterials'], header['numObjects']) 

    materialStr = ""
    if(options['PRINT_MATERIALS']):
        materialStr += "#matIndex, name, startVertex, numVertices,"
        materialStr += "startIndex, numIndices\n"
        for material in materials:
            materialStr += \
            "%d,%s,%d,%d,%d,%d\n" %\
            (material['matIndex'], bytes.decode(material['name']).strip('\x00'),material['startVertex'], \
            material['numVertices'], material['startIndex'], material['numIndices'])

    indexStr = ""
    if(options['PRINT_INDICES']):
        indexStr+="#Index list"
        for indx in indices:
            indexStr += "%d," %(indx[0],)

        indexStr+="\n"

    vertexStr = ""
    if(options['PRINT_VERTICES']):
        vertexStr+="#pos_x, pos_y, pos_z,"
        vertexStr+="boneIndex_0, boneIndex_1, boneIndex_2, boneIndex_3,"
        vertexStr+="norm_x, norm_y, norm_z,"
        vertexStr+="boneWeight_0, boneWeight_1, boneWeight_2, boneWeight_3,"
        vertexStr+="uv_u, uv_v\n"
        for indx, vtx in enumerate(vertices[start:stop]):
            vertexStr += \
                "%d,%f,%f,%f,%d,%d,%d,%d,"%(start+indx, 
                    vtx['position'][0], vtx['position'][1],vtx['position'][2],
                    vtx['boneIndex'][0],vtx['boneIndex'][1],vtx['boneIndex'][2],vtx['boneIndex'][3])
            vertexStr += \
                "%f,%f,%f,%f,%f,%f,%f,"%\
                (vtx['normal'][0],vtx['normal'][1],vtx['normal'][2],\
                vtx['weights'][0],vtx['weights'][1],vtx['weights'][2],vtx['weights'][3])
            vertexStr += "%f,%f\n"%(vtx['texcoords'][0],vtx['texcoords'][1])

    if returnStr == True:
        return headerStr+materialStr+indexStr+vertexStr
    else:
        print(headerStr+materialStr+indexStr+vertexStr)
if __name__ == '__main__':
    from optparse import OptionParser
    from os import path

    parser = OptionParser()
    parser.add_option("","--csv", dest="csv", help="Output as CSV fields",
            default=False, action="store_true")
    parser.add_option("-r","--range", dest="range", help="data subset",
            default="", action="store", type="string")
    parser.add_option("-v","--by-vertex-range",dest="vertex_range", help="subset by vertex order",
            default="False", action="store_true")
    parser.add_option("","--header", dest="PRINT_HEADER", help="print header info",
            default=False, action="store_true")
    parser.add_option("","--indices", dest="PRINT_INDICES", help="print indices",
            default=False, action="store_true")
    parser.add_option("","--vertices", dest="PRINT_VERTICES", help="print vertices",
            default=False, action="store_true")
    parser.add_option("","--materials", dest="PRINT_MATERIALS", help="print materials",
            default=False, action="store_true")
    parser.add_option("","--bones", dest="PRINT_BONES", help="print bones",
            default=False, action="store_true")

    (options, args) = parser.parse_args()

    #filename = '/var/tmp/downloads/lol/Wolfman/Wolfman.skl'
    fileExt = path.splitext(args[0])[-1]
    if fileExt.lower() == '.skl':
        if options.csv:
            printFunc = cvsPrintSkl
        else:
            printFunc = prettyPrintSkl
    elif fileExt.lower() == '.skn':
        if options.csv:
            printFunc = cvsPrintSkn
        else:
            printFunc = prettyPrintSkn
    else:
        print('%s file format not recognized.  Enter a .skl or .skn file' %(fileExt,))

    
    if any([options.PRINT_HEADER, options.PRINT_INDICES,
            options.PRINT_VERTICES, options.PRINT_MATERIALS,
            options.PRINT_BONES]):
        pass
    else:
        options.PRINT_HEADER = True
        options.PRINT_INDICES = True
        options.PRINT_VERTICES = True
        options.PRINT_MATERIALS = True
        options.PRINT_BONES = True

    indexRange = options.range.split(':')
    if len(indexRange) == 1 and indexRange[0] != '':
        start = int(indexRange[0])
        stop = start + 1
    elif len(indexRange) ==2:
        if indexRange[0] != '':
            start = int(indexRange[0])
        if indexRange[1] != '':
            stop = int(indexRange[1])
    else:
        start = 0
        stop = -1

    printFunc(args[0], start=start, stop=stop, returnStr=False, **vars(options))
    #dumpMesh(args[0], printFunc, False, **vars(options))


        
