import bpy
from .handle import add_watermark_4_blender_img

from itertools import chain, product
from pathlib import Path


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


class SBB_OT_test(bpy.types.Operator):
    bl_idname = 'sbb.test'
    bl_label = 'Test Shot By Blender'
    bl_description = 'Test'

    # bl_options = {'INTERNAL'}

    def execute(self, context):
        sbb = context.scene.sbb
        sbb.enable = True

        save_dir = Path(__file__).parent.joinpath('test')
        if not save_dir.exists():
            save_dir.mkdir(exist_ok=True)

        attrs = ['dark_mode', 'text_time', 'text_stats', 'title_version']
        # loop all type for each attr with True and False
        for attr_bools in chain.from_iterable(product([True, False], repeat=i) for i in range(1, len(attrs) + 1)):

            if len(attr_bools) != 4: continue
            # print(i)
            name = ''
            for index, attr in enumerate(attrs):
                setattr(sbb, attr, attr_bools[index])
                name += f"{attr}-{(attr_bools[index])}."

            bpy.ops.render.render()
            print("TEST: ", name)
            img = bpy.data.images['Render Result_WM']

            img.save(filepath=str(save_dir.joinpath(f'{name}.png')))

        # open dir
        bpy.ops.wm.path_open(filepath=str(save_dir))

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SBB_OT_add_watermark_2_img)
    bpy.utils.register_class(SBB_OT_test)
    # pass


def unregister():
    bpy.utils.unregister_class(SBB_OT_add_watermark_2_img)
    bpy.utils.unregister_class(SBB_OT_test)
    # pass
