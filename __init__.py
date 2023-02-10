bl_info = {
    "name": "Shot By Blender",
    "author": "Atticus",
    "version": (0, 2),
    "blender": (3, 5, 0),
    "location": "Properties > Output > Format",
    "description": "Add XIAOMI style watermark to your render",
    "warning": "Beta version",
    "wiki_url": "",
    "category": "Render",
}

from . import handle, panel, props, op, prefs
from .install_require import ensure_require


def register():
    ensure_require()

    prefs.register()
    props.register()
    panel.register()
    handle.register()
    # op.register()


def unregister():
    # op.register()
    handle.unregister()
    panel.unregister()
    props.unregister()
    prefs.unregister()
