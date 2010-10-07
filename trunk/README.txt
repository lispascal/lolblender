

INSTALLING:

To install, copy the io_scene_lol folder and contents
to the scripts/addons directory of your blender install.

blender/scripts/addons

USING:

There is no UI at the moment for this addon and so it must be
accessed from the python console within blender.  After placeing
the io_scene_lol folder into the blender addons directory the
scripts will be within blender's python path.

'>>' denotes the python console prompt.

import the plugin scripts:
>>import io_scene_lol


Say you wanted to import Gankplank.  Gankplank is the 'Pirate'
model in the HeroPak_client directory.  The default Gankplank
model has three base components:

Pirate.skn:		The model mesh
Pirate.skl:		The model skeleton
Pirate.dds:		The model skin (texture)

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



