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
        #print(fields)

        self['filetype'] = fields[0]
        self['three'], self['magic'], self['numBones'] = fields[1:4]
        self['numFrames'], self['fps'] = fields[4:6]

class anmFrame(UserDict):
    '''
    pos:  float[3]  position of the bone (tail?)
    '''

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<4f3f'
        self.__size__ = struct.calcsize(self.__format__)

        self['quat'] = [None, None, None, None]
        self['position'] = [None, None, None]

    def fromFile(self, anmFid):
        buf = anmFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        #self['quat'] = [fields[4], fields[0], fields[1], fields[2]]
        self['quat'] = fields[0:4]
        self['pos'] = fields[4:7]


class anmBone(UserDict):

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<32si'
        self.__size__ = struct.calcsize(self.__format__)

        self['boneName'] = None
        self['boneType'] = None

    def fromFile(self, anmFid):
        buf = anmFid.read(self.__size__)
        fields = struct.unpack(self.__format__, buf)

        self['boneName'] = bytes.decode(fields[0]).strip('\x00')
        self['boneType'] = fields[1]

def importANM(anmFilename):
    from collections import OrderedDict
    '''Returns an anmHeader object and a list containing the animation:
    
    animation[boneIndex][frameNumber] = {'boneType':boneType,
            'name':name, 'pos':pos, 'quat':quat}

        where 
        boneType:       int         type of bone (2 = root, 0 = ordinary, )
        name:           str         name of bone
        pos:            float[3]    postion of bone
        quat:           float[4]    quaternion of bone
        '''
    
    anmFid = open(anmFilename, 'rb')
    header = anmHeader()
    header.fromFile(anmFid)

    animation = OrderedDict()
    bone = anmBone()
    frame = anmFrame()

    for k in range(header['numBones']):
        bone.fromFile(anmFid)
        name = bone['boneName']
        boneType = bone['boneType']
        animation[name] = {'boneType': boneType, 'pos':[], 'quat':[]}
        for f in range(header['numFrames']):
            frame.fromFile(anmFid)
            animation[name]['pos'].append(frame['pos'])
            animation[name]['quat'].append(frame['quat'])

    anmFid.close()
    return header, animation
def buildBoneHeirarchy(rootBone):
    heirarchy = [[rootBone]]
    children = rootBone.children
    heirarchy.append(children)
    k = 0
    while True:
        children = []
        numParents = len(heirarchy[-1])
        for bone in heirarchy[-1]:
            thisBoneChildren = bone.children
            if len(thisBoneChildren) > 0:
                children.extend(thisBoneChildren)
            else:
                numParents -= 1

        if numParents == 0 or k > 20:
            break
        else:
            heirarchy.append(children)
        k+=1
    return heirarchy


def buildANM(filename=None, armObj=None):
    import bpy
    from mathutils import Quaternion, Vector, Matrix
    from time import sleep
    armObj = bpy.data.objects['lolArmature']
    filename =\
    '/var/tmp/downloads/lol/Characters/Wolfman/Animations/Wolfman_Attack1.anm'
    #'/Users/zac/Desktop/LoL Modeling/Characters/Wolfman/Animations/Wolfman_attack1.anm'
    header, animation = importANM(filename)
    #bpy.ops.object.mode_set(mode='EDIT')
    #bpy.ops.object.select_all()
    #bpy.ops.armature.parent_clear('DISCONNECT')
    #Generate keyframes
    #for f in range(header['numFrames']):
        
        #bpy.ops.anim.change_frame(frame = f)

        #set frame = f
        #create keyframe

    #generate boneIdx:{name, pos} dictionary
    #Animations appear to be prerotated -90x?
    restPose = {}
    for bone in armObj.data.bones:
        rotationMatrix = bone.matrix.rotation_part()
        quat = rotationMatrix.to_quat()
        rotationMatrixInv = Matrix(rotationMatrix)
        rotationMatrixInv = rotationMatrixInv.invert()
        restPose[bone.name] = {'pos':bone.tail, 
                'rotMatrix':rotationMatrix.resize4x4(),
                'rotMatrixInv':rotationMatrixInv.resize4x4(),
                'quat':quat}

    #redo animation list

    #Go into pose mode
    bpy.ops.object.mode_set(mode='POSE', toggle=False)

    #For each frame, loop through bones:
    #for f in range(header['numFrames']):

    #Create heirarchy
    rootBone = armObj.data.bones[0]
    boneLevelHeirary = buildBoneHeirarchy(rootBone)

    #for f in range(header['numFrames']):
    for f in range(1):
        #Change to frame # f
        bpy.ops.anim.change_frame(frame=f)
        k=0
        for boneLevel in boneLevelHeirary:#[:1]:

            for bone in boneLevel:
                boneName = bone.name
                pBone = armObj.pose.bones[boneName]
                aBone = armObj.data.bones[boneName]

                #Check if this bone has animation data for it, skip if it
                #doesn't
                if boneName not in animation.keys():
                    print('Couldn\'t find bone %s in animation data'%
                            (boneName,))
                    continue
                
                #Get new location
                newLoc = Vector(animation[boneName]['pos'][f])# - \
                    #restPose[boneName]['pos']
                
                #Get new Quaternion
                '''
                newQ = Quaternion()
                newQ.x = animation[boneName]['quat'][f][1]
                newQ.y = animation[boneName]['quat'][f][2]
                newQ.z = animation[boneName]['quat'][f][3]
                newQ.angle = animation[boneName]['quat'][f][0]# * 3.14159/180.0
                '''
                w,x,y,z = animation[boneName]['quat'][f][:]
                frameQ = Quaternion((w,x,y,z))
                #oldQ = pBone.rotation_quaternion
                oldQ = aBone.matrix.to_quat()
                print(oldQ)
                #newQ = oldQ.inverse() * frameQ*oldQ
                newQ = frameQ

                #newQ   = Quaternion(animation[boneName]['quat'][f]) #- \
                #        restPose[boneName]['quat']
                if boneName == 'ROOT':
                    print(restPose[boneName]['quat'])
                    print(animation[boneName]['quat'][f])
                    print(newQ)
                    print('\n')
                    print(restPose[boneName]['pos'])
                    print(newLoc)
                    print('\n')
                    
                '''
                #From io_anim_bvh.py
                frameLoc = Vector(animation[boneName]['pos'][f])
                transVec = frameLoc - restPose[boneName]['pos']

                #frameQ = Quaternion(animation[boneName]['quat'][f])
                frameQ = Quaternion()
                frameQ.x, frameQ.y, frameQ.z =\
                    animation[boneName]['quat'][f][:3]
                frameQ.w = animation[boneName]['quat'][f][3]

                frameRotationMatrix = frameQ.to_matrix().resize4x4()

                restRotationMatrix = restPose[boneName]['rotMatrix']
                restRotationMatrixInv = restPose[boneName]['rotMatrixInv']


                newRotationMatrix = restRotationMatrixInv * \
                        frameRotationMatrix * restRotationMatrix

                newQ = newRotationMatrix.to_quat()

                newLoc = restRotationMatrixInv * Matrix.Translation(transVec)
                newLoc = newLoc.translation_part()
                ''' 


                pBone.rotation_quaternion = newQ
                pBone.keyframe_insert("rotation_quaternion")

                pBone.location = newLoc
                pBone.keyframe_insert("location")
                print(boneName)

    bpy.ops.object.mode_set(mode='POSE', toggle=True)
    #set frame = 0
    #set pose = rest



