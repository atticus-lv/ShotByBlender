bl_info = {
    "name": "Shot By Blender",
    "author": "Atticus",
    "version": (0, 1),
    "blender": (3, 5, 0),
    "location": "Properties > Output > Format",
    "description": "Add unique watermark to your render",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
}

from . import op

def register():
    op.register()

def unregister():
    op.unregister()