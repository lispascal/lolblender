**Note: I am no longer maintaining the code within this repository. It will likely not work on newer versions of Blender, and the instructions below may no longer function correctly.**

**If you are a developer that wants to maintain this plugin, notify me and I will update this note, redirecting users to your repo.**

# lolblender

Python addon to use League of Legends files into blender, a 3d-modeling software.



# History
This project has been imported into GitHub in order to update it to the latest Blender version (2.74, should be compatible with 2.7x), available at [blender.org](http://www.blender.org/), and update it to be compatible with newer versions of League of Legends .SKN, .SKL, and other related files.

The latest commit to the trunk as of exporting can be found [here](https://github.com/lispascal/lolblender/commit/b45817c764f6fa6423bcb67e9ed1b649f6bae405), and browsed [here](https://github.com/lispascal/lolblender/tree/b45817c764f6fa6423bcb67e9ed1b649f6bae405). The latest code is probably in those Trunk and Branch folders. These contain work exclusively by Zac Berkowitz, who maintained the repository on Google Code. That code was made for Blender 2.5

After those commits, the directories were restructured. Releases will be put up once these scripts achieve their goals.

# License
This project is licensed under GPLv3. Disclaimers can be found on the source files, and also in LICENSE.txt. If there are any License violations, please contact lispascal through GitHub or create a New Issue, so they can be resolved.

# Requirements
This is an addon for Blender3D 2.7.  It has been tested for Blender 2.74 on Windows 8.1.

Blender homepage:  http://www.blender.org

Daily builds:      http://www.graphicall.org

# Installing
To install, copy the io_scene_lol folder and contents
to the scripts/addons directory of your blender install.

blender/2.74/scripts/addons

Open up Blender's user preferences
![Position of User Preferences](http://imgur.com/b8Wv4.png)

and select 'Addons', then 'Import/Export'.  Find the League of Legends addon and click the small box to the right to enable it.  If you want this addon to load upon starting Blender, click 'Save as Default', otherwise just close the window.

Now you have import/export options under the File menu

# Getting Character Models (and Textures, Skeletons, etc)
Importing characters can be done through [Skin Installer Ultimate](https://sites.google.com/site/siuupdates/)

After SIU has been installed, character models, skeletons, animations, and textures can be exported from the "==Skin Creation==" tab.  Say you wanted to import Gangplank.  Gangplank has a folder in the "Models" directory, with a subfolder for each skin.  The default Gangplank model has three base components:

 * Gangplank_2011.skn:				The model mesh
 * Gangplank_2011.skl:				The model skeleton
 * gangplank_base_2011_TX_CM.dds:	The model skin (texture)



# USING
## As a Blender Plugin
The prefered way to use these scripts is through Blender's own UI and the plugin interface.  

### Importing
To import a character mesh into blender, choose File>import>League of Legends and navigate to the directory containing your desired character (Now would be a good time to make a backup of the mesh you'll overwrite eventually).  Select the mesh file (.skn), skeleton file (.skl) and optionally the skin texture (.dds).  The files that will be imported are listed on the left.  If you mistakenly chose the wrong file, just click the appropriate one before clicking 'Import'

### Exporting
To export a character mesh from blender, it is recommended to base your model off of an existing model.

Make sure your new model has all of its vertices assigned to the appropriate vertex groups (in the mesh's Properties->Object data). The vertex groups are how the exporter chooses which bones to associate the vertices with.

For example, if you want to replace a character's weapon, choose the weapon vertex group, and click "select". This will show all the vertices currently associated with that vertex group. To change that weapon, you will need to delete these selected vertices, and assign new vertices to that group (with weight 1.00, probably). Some things to watch out for:
1. All faces need to be triangulated.
2. All faces' normals need to be facing outward (the correct direction). See Mesh->Normals->Calculate Outside.
3. New texture coordinates will be need to be chosen/created for new faces/vertices

When you are done and ready to export your model, select the mesh while in Object Mode, then press choose File>export>League of Legends(.skn). Here, you will choose what version to export to, the name of the new file, and whether you want to base it off of another file (highly recommended).

Basing it off of another file will choose the .skn version automatically for you, as well as make sure all in-file data that aren't the vertices & faces match the old file. Make sure that file is in the current selected directory.

The export file name should be typed into the bar at the top, the import file name should be put in the bar at the bottom left, and the checkbox checked. Once this is done, hit "Export .skn", and your new .skn file will be created.
