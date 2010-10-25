= Requirements = 
This is an addon for the Blender3D 2.5 branch.  It has been tested to work
on 2.54

Blender homepage:  http://www.blender.org

Daily builds:      http://www.graphicall.org

= Installing =
To install, copy the io_scene_lol folder and contents
to the scripts/addons directory of your blender install.
{{{
blender/2.54/scripts/addons
}}}

==USING==
These scripts can be used two ways, through the blender UI and from a python console within blender.

===As a Blender Plugin===
The prefered way to use these scripts is through Blender's own UI and the plugin interface.  Open up Blender's user preferences
http://imgur.com/b8Wv4.png

and select 'Addons', then 'Import/Export'.  Find the Leauge of Legends addon and click the small box to the right to enable it.  If you want this addon to load upon starting Blender, click 'Save as Default', otherwise just close the window.  

Now you have import/export options under the File menu

To import a character mesh into blender, choose File>import>League of Legends and navigate to the directory containing your desired character (Now would be a good time to make a backup of the mesh you'll overwrite eventually).  Select the mesh file (.skn), skeleton file (.skl) and optionally the skin texture (.dds).  The files that will be imported are listed on the left.  If you mistakenly chose the wrong file, just click the appropriate one before clicking 'Import'

===From python console within blender===
Access a python console from within blender.  After placing the io_scene_lol folder into the blender addons directory the scripts will be within blender's python path.

'>>' denotes the python console prompt.

import the plugin scripts:

>>import io_scene_lol

Say you wanted to import Gankplank.  Gankplank is the 'Pirate'
model in the `HeroPak_client` directory.  The default Gankplank
model has three base components:

 * Pirate.skn:		The model mesh
 * Pirate.skl:		The model skeleton
 * Pirate.dds:		The model skin (texture)

To import this model use the import_char() function.  First
set up some convenience variables:

>>base = 'c:\\path\\to\\DATA\\Characters\\Pirate'
>>skn  = 'Pirate.skn'
>>skl  = 'Pirate.skl'
>>tex  = 'Pirate.dds'

>>io_scene_lol.import_char(base, skn, skl, tex)

The model should now be imported.  import_char has a few other
options too.  For more info type

>>help(io_scene_lol.import_char)

To export a character model use the export_char(filename) command:

>>io_scene_lol.export_char(filename)