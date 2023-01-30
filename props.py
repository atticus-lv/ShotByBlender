import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, PointerProperty, StringProperty


class SBB_Props(PropertyGroup):
    enable: BoolProperty(name='Enable', default=True)
    dark_mode: BoolProperty(name='Dark Mode', default=False)
    # label
    text_time: BoolProperty(name='Time', default=True)
    text_stats: BoolProperty(name='Statistics', default=True)
    title_version: BoolProperty(name='Version', default=True)

    # overwrite
    ow_logo: BoolProperty(name='Logo', default=False)
    logo_path: StringProperty(name='Path', subtype='FILE_PATH')


def register():
    bpy.utils.register_class(SBB_Props)
    bpy.types.Scene.sbb = PointerProperty(type=SBB_Props)


def unregister():
    bpy.utils.unregister_class(SBB_Props)
    del bpy.types.Scene.sbb
