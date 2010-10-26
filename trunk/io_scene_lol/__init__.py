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

__in_blender__ = False
__all__ = ['lolMesh', 'lolSkeleton', '__bpy_init__']

#Try importing blender API - will fail if running outside of blender
try:
    #import bpy
    from .__bpy_init__ import *
    __in_blender__ = True
except ImportError:
    pass

if __name__ == "__main__":
    #If we're inside blender, register the plugin
    if __in_blender__:
        register()
