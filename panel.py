import bpy
from bpy.app.translations import pgettext_iface as iface_


class SBB_PT_panel(bpy.types.Panel):
    bl_label = ''
    bl_idname = 'SBB_PT_panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'
    bl_parent_id = 'RENDER_PT_format'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene.sbb, 'enable', text='Shot By Blender')

    def draw(self, context):
        layout = self.layout
        sbb = context.scene.sbb

        layout.active = sbb.enable
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(sbb, 'dark_mode', text=iface_("Dark") + iface_("Mode"))

        box = layout.column(align=True, heading="Label")
        box.prop(sbb, 'title_version')
        box.prop(sbb, 'text_time')
        box.prop(sbb, 'text_stats')

        box = layout.column(align=True, heading="Overwrite")
        box.prop(sbb, 'ow_logo')
        if sbb.ow_logo:
            box.prop(sbb, 'logo_path')


def register():
    bpy.utils.register_class(SBB_PT_panel)


def unregister():
    bpy.utils.unregister_class(SBB_PT_panel)
