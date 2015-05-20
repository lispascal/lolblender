Warning: This file may be not quite up to date.

# lolblender
Automatically exported from [Google Code/lolblender](https://code.google.com/p/lolblender/), by Zac Berkowitz.

This project has been imported into GitHub in order to update it to the latest Blender version (2.74, should be compatible with 2.7x), available at [blender.org](http://www.blender.org/), and update it to be compatible with newer versions of League of Legends .SKN, .SKL, and other related files.

# History
The latest commit to the trunk as of exporting can be found [here](https://github.com/lispascal/lolblender/commit/b45817c764f6fa6423bcb67e9ed1b649f6bae405), and browsed [here](https://github.com/lispascal/lolblender/tree/b45817c764f6fa6423bcb67e9ed1b649f6bae405). The latest code is probably in those Trunk and Branch folders. These contain work exclusively by Zac Berkowitz, who maintained the repository on Google Code. That code was made for Blender 2.5

After those commits, restructuring was done of the directories. Releases will be put up once these scripts achieve their goals.

# License
This project is licensed under GPLv3. Disclaimers can be found on the source files, and also in LICENSE.txt. If there are any License violations, please contact me through GitHub or create a New Issue.

# Requirements
This is an addon for the Blender3D 2.7 branch.  It has been tested for Blender 2.74 on Windows 8.1.

Blender homepage:  http://www.blender.org

Daily builds:      http://www.graphicall.org

# Installing
To install, copy the io_scene_lol folder and contents
to the scripts/addons directory of your blender install.

blender/2.74/scripts/addons

# Getting Character Models (and Textures, Skeletons, etc)
Importing characters can be done through [Skin Installer Ultimate](https://sites.google.com/site/siuupdates/)

After SIU has been installed, character models, skeletons, animations, and textures can be exported from the "==Skin Creation==" tab.  Say you wanted to import Gangplank.  Gangplank has a folder in the "Models" directory, with a subfolder for each skin.  The default Gangplank model has three base components:

 * Gangplank_2011.skn:				The model mesh
 * Gangplank_2011.skl:				The model skeleton
 * gangplank_base_2011_TX_CM.dds:	The model skin (texture)



# USING
These scripts can be used two ways, through the blender UI and from a python console within blender.

## As a Blender Plugin
The prefered way to use these scripts is through Blender's own UI and the plugin interface.  Open up Blender's user preferences
![Position of User Preferences](http://imgur.com/b8Wv4.png)

and select 'Addons', then 'Import/Export'.  Find the Leauge of Legends addon and click the small box to the right to enable it.  If you want this addon to load upon starting Blender, click 'Save as Default', otherwise just close the window.  

Now you have import/export options under the File menu

To import a character mesh into blender, choose File>import>League of Legends and navigate to the directory containing your desired character (Now would be a good time to make a backup of the mesh you'll overwrite eventually).  Select the mesh file (.skn), skeleton file (.skl) and optionally the skin texture (.dds).  The files that will be imported are listed on the left.  If you mistakenly chose the wrong file, just click the appropriate one before clicking 'Import'

## From python console within blender
Access a python console from within blender.  After placing the io_scene_lol folder into the blender addons directory the scripts will be within blender's python path.

>> denotes the python console prompt.

import the plugin scripts:

>>import io_scene_lol

To import a model use the import_char() function.  First
set up some convenience variables:

>>base = 'c:\\path\\to\\DATA\\Characters\\Gangplank'
>>skn  = 'Gangplank_2011.skn'
>>skl  = 'Gangplank_2011.skl'
>>tex  = 'gangplank_base_2011_TX_CM.dds'

>>io_scene_lol.import_char(base, skn, skl, tex)

The model should now be imported.  import_char has a few other
options too.  For more info type

>>help(io_scene_lol.import_char)

To export a character model use the export_char(filename) command:

>>io_scene_lol.export_char(filename)