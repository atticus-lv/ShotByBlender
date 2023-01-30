import bpy
from .handle import add_watermark_4_blender_img


class SBB_OT_add_watermark_2_img(bpy.types.Operator):
    bl_idname = 'sbb.add_watermark_2_img'
    bl_label = 'Add Watermark'
    bl_description = 'Add Watermark to Active Image'
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'IMAGE_EDITOR' and context.space_data.image

    def execute(self, context):
        add_watermark_4_blender_img(context.space_data.image.name, context.space_data.image.name + '_WM')
        return {'FINISHED'}


def register():
    # bpy.utils.register_class(SBB_OT_add_watermark_2_img)
    pass

def unregister():
    # bpy.utils.unregister_class(SBB_OT_add_watermark_2_img)
    pass