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

from . import handle, panel, props
from .install_require import ensure_require


def register():
    ensure_require()

    props.register()
    panel.register()
    handle.register()


def unregister():
    handle.unregister()
    panel.unregister()
    props.unregister()
