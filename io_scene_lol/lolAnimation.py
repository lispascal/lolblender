# ##### BEGIN GPL LICENSE BLOCK ##### #
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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

# Based on the work in "LOLViewer" under GPLv3
# (Copyright 2011-2012 James Lammlein, Adrian Astley),
# and the previous work in this project by Zac Berkowitz on "lolBlender"
# with adaption done by Pascal Lis (github -> lispascal)
# Version 4 .anm files are in LOLViewer with the following info: 
# "Based on the reverse engineering work of Hossein Ahmadi."
# and this file makes use of that work

# <pep8 compliant>
import struct
import mathutils

class anmHeader():
    """LoL animation header format:
    id                  char[8]     8       
    version             uint        4       Version number.

    v0-3
        magic               uint        4       "magic" number
        numBones            uint        4       Number of bones
        numFrames           uint        4       Number of frames
        playbackFPS         uint        4       FPS of playback

    v4
        magic               uint        4       "magic" number
        unknown             float[3]    12
        numBones            uint        4       Number of bones
        numFrames           uint        4       Number of frames
        timePerFrame        float       4       1/fps
        offsets             uint[3]     12      offsets within file
        positionOffset      uint        4
        orientationOffset   uint        4
        indexOffset         uint        4
        offsets2            uint[3]     12      ?


    
    total size v0-3                     28 bytes
    total size v4                       76 bytes

    """

    def __init__(self):
        self.__format__i = '<8si'  # initial part
        self.__size__i = struct.calcsize(self.__format__i)
        self.__format__v03 = '<4i'  # part for version 0-3
        self.__size__v03 = struct.calcsize(self.__format__v03)
        self.__format__v4 = '<i3f2if9i'  # part for version 4
        self.__size__v4 = struct.calcsize(self.__format__v4)
        self.id = None
        self.version = None
        self.magic = None
        self.numBones = None
        self.numFrames = None
        self.playbackFPS = None

    def fromFile(self, anmFile):
        """Reads the skl header object from the raw binary file"""
        anmFile.seek(0)
        beginning = struct.unpack(self.__format__i, anmFile.read(self.__size__i))
        (self.id, self.version) = beginning
        if self.version in [0, 1, 2, 3]:  # versions 0-3
            rest = struct.unpack(self.__format__v03, anmFile.read(self.__size__v03))
            (self.magic, self.numBones, self.numFrames, self.playbackFPS) = rest
        elif self.version == 4:  # version 4
            rest = struct.unpack(self.__format__v4, anmFile.read(self.__size__v4))
            self.magic = rest[0]
            self.unknown = rest[1:4]
            self.numBones = rest[4]
            self.numFrames = rest[5]
            timePerFrame = rest[6]
            self.playbackFPS = round(1.0 / timePerFrame)
            self.offsets = rest[7:10]
            self.positionOffset = rest[10]
            self.orientationOffset = rest[11]
            self.indexOffset = rest[12]
            self.offsets2 = rest[13:16]
    
    def toFile(self, anmFile):
        """Writes the header object to a raw binary file"""
        data = struct.pack(self.__format__, self.id, self.version,
                self.magic, self.numBones, self.numFrames, self.playbackFPS)
        anmFile.write(data)


class anmBone():
    """LoL Bone structure format
    v0-3
    name        char[32]    32      name of bone (with padding \0's)
    unknown     int         4       

    frame[numberOfFrames]:
        orientation     float[4]    16
        position        float[3]    12

    total                   36 + (28 * Number of Frames)

    v4
    Animation information is separated by frame for version 4
    """
    def __init__(self):
        self.__format__i = '<32si'  # initial
        self.__size__i = struct.calcsize(self.__format__i)
        self.__format__f = '<7f'  # per frame
        self.__size__f = struct.calcsize(self.__format__f)
        self.name = None
        self.parent = None
        self.orientations = []
        self.positions = []


    def metaDataFromFile(self, anmFile, version):
        """Reads animation bone meta-data from a binary file fid"""
        if version in [0,1,2,3]:
            fields = struct.unpack(self.__format__i, 
                    anmFile.read(self.__size__i))
            self.name = bytes.decode(fields[0])
            self.unknown = fields[1]

        else:
            raise ValueError("Unhandled Bone version number", version)

    def frameDataFromFile(self, anmFile, version):
        """Reads animation bone frame data from a binary file fid"""
        if version in [0,1,2,3]:
            fields = struct.unpack(self.__format__f,
                    anmFile.read(self.__size__f))
            orientation = fields[0:4]
            position = fields[4:7]
            self.orientations.push(orientation)
            self.positions.push(position)
        else
            raise ValueError("Unhandled Bone version number", version)

            
    def toFile(self, anmFile, version):
        """Writes animation bone object to a binary file FID"""
        if version in [0,1,2,3]:
            data = struct.pack(self.__format__i, self.name, self.unknown)
            for j in range(0, len(self.orientations)):
                data += struct.pack(self.__format__f, self.orientations[j],
                        self.positions[j])
            anmFile.write(data)


def importANM(filepath):
    header = anmHeader()
    boneList= []
    
    #Wrap open in try block
    anmFid = open(filepath, 'rb')

    #Read the file header to get # of bones
    header.fromFile(anmFid)
    if header.version in [0, 1, 2, 3]:
        #Read in the bones
        for i in range(header.numBones):
            boneList.append(anmBone())
            boneList[i].metaDataFromFile(anmFid, header.version)
            for j in range(header.numFrames):
                boneList[i].frameDataFromFile(anmFid, header.version)

    elif header.version == 4:
        print("not supported yet")
    else:
        raise ValueError("ANM File Version not supported.", header.version)


    anmFid.close()
    return header, boneList


def applyANM(boneList, version):
    import bpy
    raise NotImplementedError("Function not yet implemented for any version")
    
    # Once implemented, this code will probably follow a relatively simply
    # structure to bone creation. Althought it will be:
    # go by frame->insert key frame
