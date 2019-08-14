# Table of Contents
[LookdevTools](#LookdevTools)  
[Installation](#Installation)   
[&nbsp;&nbsp;&nbsp;&nbsp;Windows](#Windows)   
[&nbsp;&nbsp;&nbsp;&nbsp;Linux](#Linux)   
[Tools](#Tools)   
[&nbsp;&nbsp;&nbsp;&nbsp;Maya Surfacing Projects](#Maya-Surfacing-Projects)  
[&nbsp;&nbsp;&nbsp;&nbsp;Katana Surfacing Projects](#Katana-Surfacing-Projects)  
[Macros and Gizmos](#Macros-and-Gizmos)  
[&nbsp;&nbsp;&nbsp;&nbsp;Katana](#Katana)   
[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Material Lookdev](#Material-Lookdev)   
[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TextureSet Loader](#TextureSet-Loader)   
[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Texture Locatization](#Texture-Locatization)   
[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Interactive Filters](#Interactive-Filters)   
[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Grey Shaders Overrides](#Grey-Shaders-Overrides)   
[&nbsp;&nbsp;&nbsp;&nbsp;Nuke](#Nuke)   
[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AOV correct](#AOV-Correct)   
[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lightgroups correct](#Lightgroups-Correct)   
[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lightgroups ContactSheet](#Lightgroups-ContactSheet)   
[Writing tools](#Writing-tools)   
[&nbsp;&nbsp;&nbsp;&nbsp;Example plugin](#Example-plugin)   
[Credits](#Credits)   


# LookdevTools
A tool set for maya, katana, renderman, and nuke for surfacing and look development.  
It aims to be the missing glue between maya (uv prepping and organizing), mari/painter, and maya/katana rendering. Covering most of the repeatitive tasks, letting you focus on the surfacing.   

The rendering tools are based on Pixar Renderman.

# Installation
##### Root
<pre>set LOOKDEVTOOLS_ROOT=%PYTHONPATH%;/path/to/the/tools"</pre>
##### Python
<pre>set PYTHONPATH=%PYTHONPATH%;%LOOKDEVTOOLS_ROOT%/"</pre>
##### Katana Tools
Add this to your katana launcher
<pre>set EZ_KATANA_TOOLS=%LOOKDEVTOOLS_ROOT%/katana/katana_tools
set EZ_KATANA_SHELVES=%LOOKDEVTOOLS_ROOT%/katana/katana_shelves
set KATANA_RESOURCES=%KATANA_RESOURCES%;%EZ_KATANA_TOOLS%;%EZ_KATANA_SHELVES%</pre>
##### Nuke Tools
<pre>set NUKE_PATH=%NUKE_PATH%;%LOOKDEVTOOLS_ROOT%/nuke/plugins</pre>
##### Mari
<pre>soon</pre>
##### Substance Painter
<pre>soon</pre>

# Tools

## Maya Surfacing Projects
This tools allows you to organize and group your maya meshes into different surfacing projects, and surfacing objects.
Also handles projects export to alembic files, and surfacing objects merging.
The attributes added to the meshes transforms allows the assignment of materials and textureSets programatically (currently katana only, see katana shelves).

<img width="50%" src="docs/images/mayaEZSurfacing.png" alt="EZSurfacing Tools" style="" /><img width="50%" src="docs/images/mayaEZSurfacing2.png" alt="Surfacing Tools" style="" />
The pixar cabin, and kitchens shown here ready for surfacing

<img width="48%" src="docs/images/mayaEZSurfacing_export.gif" alt="EZSurfacing Tools" style="" /><img width="48%" src="docs/images/mayaEZSurfacing_create.gif" alt="EZSurfacing Tools" style="" />

## Hierarchical Structure
* Surfacing_projectA
  * Surfacing_objectA
    * mesh1
    * mesh2
    * mesh3
  * Surfacing_objectA
      * mesh1
      * mesh2
      * mesh3
* Surfacing_projectB
  * Surfacing_objectB
    * mesh4
    * mesh5

##### SurfacingObject  
All meshses inside a SurfacingObject will be merged to a single geometry for export.
The SurfacingObject will also be exported individually to a folder, named after the SurfacingProject they belong
```
SurfacingObject meshes are important for Mari where the amount of different meshes can impact your
performance,as Mari is optimized for one single mesh. The more meshes, the slower Mari will be,
It is not recommended using more than 6 meshes (or surfacing Objects) inside a Mari project.
```

##### SurfacingObject:
This will export as single alembic, containing its SurfacingObject as single meshes. 
Tipically this is the file you will bring to Mari or Substance Painter to create a single project.

###### Note
If using substance painter -using uDim- meshes inside an SurfacingObject should be contained inside a single uDim!
All SurfacingObjects inside a SurfacingProject should not overlap.

## Katana Surfacing Projects

Run EZCollections from the shelve to automaticaly create collections based on the EZ attributes found in the scene graph.
Create either the Surfacing Project, or the Surfacing Object collections.
A node must be selected before running, this node will be used as the scene point where to process and examine the scene graph locations.   

It can also be used to create collections of all unique values for any give attribute

<img width="40%" src="docs/images/katanaEZCollectionsShelves.jpg" alt="EZSurfacing Tools" style="margin-right: 10px;" />

Collection, viewport colors and material assignments are based on attribute values at locations as in.
```
/root/world//*{attr("geometry.arbitrary.myCustomAttribute") == value
```
The attributes used from this tools are
```
geometry.arbitrary.surfacing_project
geometry.arbitrary.surfacing_object
```
<img width="100%" src="docs/images/katanaEZCollections2.png" alt="EZSurfacing Tools" style="margin-right: 10px;" />

# Macros and Gizmos

## Katana

### Material Lookdev
Quickly isolate materials from the scene and visualize them.
Use the default Shaderball (cloth geo optional), or connect your own geometry.  
Requires a gaffer input.

<img width="50%" src="docs/images/mayaEZPrmanMaterialLookdev.png" alt="EZSurfacing Tools" style="margin-right: 10px;" />

### TextureSet Loader
This macro allows to load multiple texture files using tokens or keywords.
Load materials or texture sets from substance, megascans, or mari with ease, in a single node.

Using the ```<element>``` keyword for each map, and ```_MAPID_``` for renderman to pick up uDIMs if an atlas style is selected.  
It also accepts a manifold input (of any type), for tiling.

```
Metal_PaintedSteelBase_<element>.tex   
woodenTable_<element>._MAPID_.tex
```

Each texture set element (for ie: baseColor, or normal) can be added to the list.

<img width="50%" src="docs/images/katanaPrmanTextureSet.png" alt="EZSurfacing Tools" style="margin-right: 10px;" />


### Texture locatization
Opscript to search and replace paths in all PxrTexture nodes inside a network material at scenegraph location's ```.material.nodes```

<img width="50%" src="docs/images/katanaTextureLocatization.png" alt="EZSurfacing Tools" style="margin-right: 10px;" />

### Interactive Filters
Miscelaneous interactive filters for renderman 22
* resolution half, third
* quality presets
* save n threads
* scanning options
* use it
* Integrators: occlusion, occlusion with albedo, direct lighting, and default
* subdmeshes to poly (aka: ignore subdivisions)
* Grey shader override, and diffuseColor override for all materials

<img width="50%" src="docs/images/katanaPrmanInteractiveFilters.gif" alt="EZSurfacing Tools" style="" />

##### Grey shaders overrides
###### grey_shader:
This replaces all your shaders with a 0.18 standard material. 

###### grey_albedo:
This filter overrides only the diffuseColor with a 0.18 grey color.
Keeping all other materials values and maps, like specular, roughness, normals, diplacements, etc.

<img width="50%" src="docs/images/katanaPrmanInteractiveFilterGreyAlbedo.jpg"      alt="EZSurfacing Tools" style="margin-right: 10px;" />

## Nuke
### AOV Correct
Select a nuke layer, and color correct it

<img width="50%" src="docs/images/nukeAovCorrect.png"      alt="EZSurfacing Tools" style="margin-right: 10px;" />

### Lightgroups Correct
Select a lightgroup layer from the preset menu, and mute/solo/color correct it

<img width="50%" src="docs/images/nukeLigthgroupsCorrect.png"      alt="EZSurfacing Tools" style="margin-right: 10px;" />

### Lightgroups contactSheet
Creates a contact sheet of all the default lightgroups

<img width="50%" src="docs/images/nukeLigthgroupsContactSheet.jpg"      alt="EZSurfacing Tools" style="margin-right: 10px;" />

## Writing tools
### Developing Plugins
See yapsy documentation for more info   
http://yapsy.sourceforge.net/

### Example plugin
ExamplePlugIn.plugin_layout QtWidget is what you need to populate in order to add and show an UI.

<pre>tools/plugins/example_plugin/__init__.py</pre>

```
class ExamplePlugIn(IPlugin):
    '''Example plugin'''
    name = "Example Plugin"

    plugin_layout = None

    def __init__ (self):
        logging.info('PLUGIN: example_plugin loaded')
        # Load dcc python packages inside a try, to catch the application
        # environment, this will be replaced by IPlugin Categories
        try:
            import pymel.core as pm
        except:
            logging.warning('PLUGIN: KatanaSurfacingProjects ui not loaded, katana libs not found')
            self.plugin_layout = QtWidgets.QWidget()
            self.label_ui = QtWidgets.QLabel(self.plugin_layout)
            self.label_ui.setText('Plugin not available in this application')
        else:
        # Plugin begins
```


<pre>tools/plugins/example_plugin.yapsy-plugin</pre>
```
[Core]
Name = Example plugin
Module = example_plugin

[Documentation]
Author = Ezequiel Mastrasso
Version = 1.0
Website = //ezequielm.com
Description = This is an example plugin configure, with UI entry points.
```

## Credits
Ezequiel Mastrasso  
Anant Gupta

### Shader Ball
Mathieu Maurel   
https://www.artstation.com/artwork/wKveZ

### Texture Patterns
Elias Wick   
https://polycount.com/discussion/186513/free-checker-pattern-texture

### Pixar kitchen surfacing
Surfacing, lighting, rendering was done by Ezequiel Mastrasso.
This images are part of the original speed surfacing exercise that give birth to these tools.  

However the look and style is based on the original winner of the pixar Kitchen challenge  
Fabio Rossi Sciedlarczyk (scied)