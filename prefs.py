import bpy
from bpy.props import EnumProperty
from bpy.utils import previews
from bpy.app.translations import pgettext_iface as iface_

import os
from pathlib import Path
from .t3dn_bip import previews

G_PV_COLL = {}
G_ICON_ID = {}  # name:id


def get_prefs():
    return bpy.context.preferences.addons.get(__package__).preferences


def enum_logo_items(self, context):
    items = []
    for i, (key, value) in enumerate(G_ICON_ID.items()):
        items.append((key + '.png', key, '', value, i))

    return items


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # logo
    logo: EnumProperty(name='Logo', items=enum_logo_items, default=0)
    logo_dark: EnumProperty(name='Dark', items=enum_logo_items, default=5)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        row.separator(factor=2)
        col1 = row.column()
        col1.label(text='Default')
        col1.template_icon_view(self, 'logo', scale_popup=3)
        col2 = row.column()
        col2.label(text=iface_("Dark") + iface_("Mode"))
        col2.template_icon_view(self, 'logo_dark', scale_popup=3)
        row.separator(factor=2)


def register_icon():
    icon_dir = Path(__file__).parent.joinpath('res', 'logos')
    mats_icon = []

    for file in os.listdir(str(icon_dir)):
        if file.endswith('.png'):
            mats_icon.append(icon_dir.joinpath(file))
    # 注册
    pcoll = previews.new()

    for icon_path in mats_icon:
        pcoll.load(icon_path.name[:-4], str(icon_path), 'IMAGE')
        G_ICON_ID[icon_path.name[:-4]] = pcoll.get(icon_path.name[:-4]).icon_id

    G_PV_COLL['sbb_pv'] = pcoll


def unregister_icon():
    for pcoll in G_PV_COLL.values():
        previews.remove(pcoll)
    G_PV_COLL.clear()

    G_ICON_ID.clear()


def register():
    register_icon()
    bpy.utils.register_class(Preferences)


def unregister():
    unregister_icon()
    bpy.utils.unregister_class(Preferences)
