from collections import UserDict
import struct
class anmHeader(UserDict):

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<8s5i'
        self.__size__ = struct.calcsize(self.__format__)

        self['filetype'] = None
        self['three'] = None
        self['magic'] = None
        self['numBones'] = None
        self['numFrames'] = None
        self['fps'] = None

    def fromFile(self, anmFid):
        buf = anmFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)
        print(fields)

        self['filetype'] = fields[0]
        self['three'], self['magic'], self['numBones'] = fields[1:4]
        self['numFrames'], self['fps'] = fields[4:6]

class anmFrame(UserDict):

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<4f3f'
        self.__size__ = struct.calcsize(self.__format__)

        self['quat'] = [None, None, None, None]
        self['position'] = [None, None, None]

    def fromFile(self, anmFid):
        buf = anmFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        self['quat'] = fields[0:4]
        self['position'] = fields[4:7]


class anmBone(UserDict):

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<32si'
        self.__size__ = struct.calcsize(self.__format__)

        self['boneName'] = None
        self['boneID'] = None

    def fromFile(self, anmFid):
        buf = anmFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        self['boneName'] = bytes.decode(fields[0]).strip('\x00')
        self['boneID'] = fields[1]

def importANM(anmFilename):
    
    anmFid = open(anmFilename, 'rb')
    header = anmHeader()
    header.fromFile(anmFid)

    animation = []
    bone = anmBone()
    frame = anmFrame()

    for k in range(header['numFrames']):
        animation.append({})

    for k in range(header['numBones']):
        bone.fromFile(anmFid)
        name = bone['boneName']
        id = bone['boneID']
        for f in range(header['numFrames']):
            frame.fromFile(anmFid)
            animation[f][name] = {}
            animation[f][name]['boneID'] = id
            animation[f][name]['quat'] = frame['quat']
            animation[f][name]['position'] = frame['position']


    return animation

