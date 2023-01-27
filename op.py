from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pathlib import Path

import datetime
import bpy
from bpy.props import EnumProperty, BoolProperty
from bpy.app.handlers import persistent
from bpy.app.translations import pgettext_iface as iface_

easy_engine_name = {
    'BLENDER_EEVEE': 'Eevee',
    'BLENDER_WORKBENCH': 'Workbench',
    'CYCLES': 'Cycles'
}

src_dir = Path(__file__).parent


def get_preset():
    import json
    preset_path = src_dir.joinpath('preset.json')
    with open(preset_path, 'r') as f:
        preset = json.load(f)

    return preset


def auto_config(width, height):
    radio = width / height
    # get the nearest config
    if radio > 1:
        return '2'
    else:
        return '1'


def get_color(dark_mode=False) -> tuple:
    bg_color = (255, 255, 255)
    title_col = (0, 0, 0)
    tips_col = (128, 128, 128)
    line_col = (220, 220, 220)

    if dark_mode:
        bg_color = (0, 0, 0)
        tips_col = (255, 255, 255)
        title_col = (255, 255, 255)
        line_col = (128, 128, 128)

    return bg_color, title_col, tips_col, line_col


def get_scene_stats() -> str:
    stats = bpy.context.scene.statistics(bpy.context.view_layer)

    if len(stats.split(sep=' | ')) == 7:
        coll, verts, faces, tris, objs, mem, ver = stats.split(sep=' | ')
    else:
        coll, obj, verts, faces, tris, objs, mem, ver = stats.split(sep=' | ')

    verts = verts.split(sep=':')[-1]
    faces = faces.split(sep=':')[-1]
    tris = tris.split(sep=':')[-1]

    d = {
        'Verts': verts,
        'Faces': faces,
        'Tris': tris,
        'Memory': mem,
    }
    s = f"Faces: {faces} | {mem}"
    return s


@persistent
def add_watermark_handle(dummy):
    if not bpy.context.scene.sbb_watermark: return

    context = bpy.context
    draw_text_time = context.scene.sbb_text_time
    draw_text_stats = context.scene.sbb_text_stats

    ori_img = bpy.data.images['Render Result']
    save_path = str(src_dir.joinpath('cache', 'render.png'))
    ori_img.save_render(filepath=save_path)

    # add watermark
    path = save_path
    ori_img = Image.open(path)
    width, height = ori_img.size

    preset = get_preset()
    config = auto_config(width, height)
    bg_col, title_col, tips_col, line_col = get_color(dark_mode=context.scene.sbb_dark_mode)

    # expand pixel size by scale
    scale = preset[config]['scale']
    new_img = Image.new('RGBA', (width, int(height * scale)), bg_col)  # expand the img bottom to draw
    new_img.paste(ori_img, (0, 0))  # fill in the original image
    # draw img
    height = int(height * (scale - 1))
    label_img = Image.new('RGBA', (width, height), bg_col)  # expand the img bottom to draw
    DrawImg = ImageDraw.Draw(label_img)

    # info
    title_left = 'BLENDER'
    if context.scene.sbb_title_version:
        title_left += f' {bpy.app.version_string}'
    # right_text = '75mm f/1.8 Filmic Cycles'
    cam = context.scene.camera.data
    fstop = round(cam.dof.aperture_fstop, 2)
    lens = bpy.context.scene.camera.data.lens
    cs = context.scene.view_settings.view_transform.strip().replace(" ", "")
    render_engine = easy_engine_name[context.scene.render.engine]

    title_right = f'{lens}mm f/{fstop} {render_engine}'
    text_time = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    text_stats = get_scene_stats()

    # Add Text to an image, set size
    title_font_size = height * 0.16
    tips_font_size = title_font_size * 0.7
    if not draw_text_stats and not draw_text_time:
        title_font_size *= 1.25
        tips_font_size *= 1.25

    boldFont = ImageFont.truetype(str(src_dir.joinpath('fonts', 'MiSans-Demibold.ttf')), int(title_font_size))
    lightFont = ImageFont.truetype(str(src_dir.joinpath('fonts', 'MiSans-Medium.ttf')), int(tips_font_size))
    logo_path = str(src_dir.joinpath('logos', 'blender.png' if not context.scene.sbb_dark_mode else 'blender_w.png'))

    side_padding = width * preset[config]['padding']



    y_mid = height / 2
    y_title = y_mid - title_font_size * 1.25  # 1.25
    loc_x_r_title = width - side_padding - DrawImg.textsize(title_right, font=boldFont)[0]

    if not draw_text_stats and not draw_text_time:
        y_title += title_font_size * 0.5
    else:
        loc_x = side_padding
        loc_y = y_title + title_font_size * 1.5  # 0.5 + 1.25
        # draw both side
        if draw_text_stats and draw_text_time:
            DrawImg.text((loc_x, loc_y), text_time, font=lightFont, fill=tips_col)
            DrawImg.text((loc_x_r_title, loc_y), text_stats, font=lightFont, fill=tips_col)
        # draw on only right side
        elif not draw_text_stats and draw_text_time:
            DrawImg.text((loc_x_r_title, loc_y), text_time, font=lightFont, fill=tips_col)
        else:
            DrawImg.text((loc_x_r_title, loc_y), text_stats, font=lightFont, fill=tips_col)

    # draw title
    DrawImg.text((side_padding, y_title), title_left, font=boldFont, fill=title_col)
    DrawImg.text((loc_x_r_title, y_title), title_right, font=boldFont, fill=title_col)

    # get logo image
    logo = Image.open(logo_path)
    logo.convert('RGBA')
    logo_scale = preset[config]['logo_scale']
    logo_height = int(height * logo_scale)
    logo_width = int(logo.size[0] * logo_height / logo.size[1])
    logo = logo.resize((logo_width, logo_height), Image.ANTIALIAS)
    # paste logo image next to right text
    loc_logo_x = int(width - side_padding * 2 - DrawImg.textsize(title_right, font=boldFont)[0] - logo.size[0])
    loc_logo_y = int(y_mid - logo_height / 2 )
    label_img.paste(logo, (loc_logo_x, loc_logo_y), logo)

    # draw a line shape between right text and logo
    line_start = int((loc_logo_x + logo.size[0] + loc_x_r_title) / 2), int(loc_logo_y+logo.size[1]*0.1)
    line_end = int((loc_logo_x + logo.size[0] + loc_x_r_title) / 2), int(loc_logo_y + logo.size[1]*0.9)
    DrawImg.line([line_start, line_end], fill=line_col, width=int(width / 500))

    # paste label_img to new_img and save
    out_path = str(src_dir.joinpath('output', 'watermark.png'))
    new_img.paste(label_img, (0, ori_img.size[1]), label_img)
    new_img.save(out_path)
    # load back to blender
    if 'Render Result_WM' in bpy.data.images:
        bpy.data.images.remove(bpy.data.images['Render Result_WM'])
    data = bpy.data.images.load(out_path)
    data.name = 'Render Result_WM'

    # change image editor to show the new image
    try:
        window = context.window_manager.windows[-1]
        for area in window.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = data
    except:
        pass


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

        layout.prop(scene, 'sbb_watermark')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.active = scene.sbb_watermark
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(scene, 'sbb_dark_mode', text=iface_("Dark") + iface_("Mode"))

        box = layout.column(align = True,heading="Label")
        box.prop(scene, 'sbb_title_version')
        box.prop(scene, 'sbb_text_time')
        box.prop(scene, 'sbb_text_stats')


def register():
    bpy.types.Scene.sbb_watermark = BoolProperty(name='Shot By Blender', default=True)
    bpy.types.Scene.sbb_dark_mode = BoolProperty(name='Dark Mode', default=False)
    bpy.types.Scene.sbb_text_time = BoolProperty(name='Time', default=True)
    bpy.types.Scene.sbb_text_stats = BoolProperty(name='Statistics', default=True)
    bpy.types.Scene.sbb_title_version = BoolProperty(name='Version', default=True)

    bpy.app.handlers.render_post.append(add_watermark_handle)

    bpy.utils.register_class(SBB_PT_panel)


def unregister():
    bpy.utils.unregister_class(SBB_PT_panel)

    bpy.app.handlers.render_post.remove(add_watermark_handle)

    del bpy.types.Scene.sbb_watermark
    del bpy.types.Scene.sbb_dark_mode
