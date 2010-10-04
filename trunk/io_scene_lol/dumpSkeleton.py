#!/bin/python3.1

#from io_scene_lol.lolSkeleton import sklHeader, sklBone, importSKL
from lolSkeleton import sklHeader, sklBone, importSKL
def prettyPrint(header, boneDict, returnStr = True):
    
    headerStr = \
    "Filetype:%s\nnumObjects:%d\nskeletonHash:%d\nnumElements:%d\n\n" % (header['fileType'], 
            header['numObjects'], header['skeletonHash'], header['numElements'])
    boneStr = ""
    for id, bone in boneDict.items():
        if bone['parent'] != -1:
            parentName = boneDict[bone['parent']]['name']
        else:
            parentName = "None"
        boneStr += "id:%d\t%s\tparent id:%d\t(%s)\n" %(id, bone['name'],
                bone['parent'], parentName)
        boneStr += "scale:  %f\n" %(bone['scale'],)
        boneStr += "matrix:\t %7.4f  %7.4f  %7.4f  %7.4f\n" %(bone['matrix'][0][0],
                bone['matrix'][0][1], bone['matrix'][0][2], bone['matrix'][0][3])
        boneStr += "\t %7.4f  %7.4f  %7.4f  %7.4f\n" %(bone['matrix'][1][0],
                bone['matrix'][1][1],bone['matrix'][1][2],bone['matrix'][1][3])
        boneStr += "\t %7.4f  %7.4f  %7.4f  %7.4f\n" %(bone['matrix'][2][0],
                bone['matrix'][2][1], bone['matrix'][2][2], bone['matrix'][2][3])
        boneStr += "\n"

    if returnStr == True:
        return headerStr+boneStr
    else:
        print(headerStr+boneStr)

def csvPrint(header, boneDict, returnStr = True):
    headerStr='%s,%d,%d,%d\n' % (header['fileType'], header['numObjects'],
            header['skeletonHash'], header['numElements'])
    boneStr = ""
    for id, bone in boneDict.items():
        boneStr+="%d,%s,%d,%e," %(id, bone['name'], bone['parent'], bone['scale'])
        boneStr+="%e,%e,%e,%e," %(bone['matrix'][0][0], bone['matrix'][0][1],
                bone['matrix'][0][2], bone['matrix'][0][3])
        boneStr+="%e,%e,%e,%e," %(bone['matrix'][1][0], bone['matrix'][1][1],
                bone['matrix'][1][2], bone['matrix'][1][3])
        boneStr+="%e,%e,%e,%e\n" %(bone['matrix'][2][0], bone['matrix'][2][1],
                bone['matrix'][2][2], bone['matrix'][2][3])

    if returnStr == True:
        return headerStr+boneStr
    else:
        print(headerStr+boneStr)

def dumpSkeleton(filepath, printFunc, returnStr):
    header, boneDict = importSKL(filepath)

    printFunc(header, boneDict, returnStr)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("","--csv", dest="csv", help="Output as CSV fields",
            default=False, action="store_true")

    (options, args) = parser.parse_args()

    print(options)
    print(args)
    #filename = '/var/tmp/downloads/lol/Wolfman/Wolfman.skl'
    if options.csv:
        printFunc = csvPrint
    else:
        printFunc = prettyPrint

    dumpSkeleton(args[0], printFunc, False)


        
