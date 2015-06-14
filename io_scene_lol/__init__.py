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

__in_blender__ = False
__all__ = ['lolMesh', 'lolSkeleton', '__bpy_init__']

bl_info = {
    'name': 'Import League of Legends Character files (.skn;.skl)',
    'author': 'Pascal Lis, Zac Berkowitz',
    'version': (0,7),
    'blender': (2,74,0),
    'location': 'File > Import',
    'category': 'Import/Export',
    'api': 31878,
    'wiki_url': 'https://github.com/lispascal/lolblender',
    'tracker_url':'https://github.com/lispascal/lolblender/issues'
    }

#Try importing blender API - will fail if running outside of blender
try:
    #Attempt to load everything from __bpy_init__ into the current namespace
    from .__bpy_init__ import *
    #if this was successful, we're within Blender.  Set the flag True
    __in_blender__ = True
except ImportError:
    #Don't exit if we couldn't import bpy related modules, we may be getting
    #called for something else...
    pass

if __name__ == "__main__":
    #If we're inside blender, register the plugin
    if __in_blender__:
        register()
