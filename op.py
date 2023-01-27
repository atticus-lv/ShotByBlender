from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pathlib import Path

import datetime
import bpy
from bpy.props import EnumProperty, BoolProperty
from bpy.app.handlers import persistent

preset = {
    '16/9': {
        'scale': 1.2,
        'font_scale': 0.15,
        'padding': 0.025,
        'bottom_padding': 0.7,
        'logo_scale': 0.05
    },
    '1/1': {
        'scale': 1.1,
        'font_scale': 0.15,
        'padding': 0.025,
        'bottom_padding': 0.7,
        'logo_scale': 0.05
    }
}

easy_engine_name = {
    'BLENDER_EEVEE': 'Eevee',
    'BLENDER_WORKBENCH': 'Workbench',
    'CYCLES': 'Cycles'
}

src_dir = Path(__file__).parent


def get_color(dark_mode=False):
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


def auto_config(width, height):
    radio = width / height
    # get the nearest config
    tg_key = '16/9'
    diff = 1
    for key in preset:
        if abs(radio - float(key.split('/')[0]) / float(key.split('/')[1])) < diff:
            diff = abs(radio - float(key.split('/')[0]) / float(key.split('/')[1]))
            tg_key = key

    return tg_key


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

    img = bpy.data.images['Render Result']
    save_path = str(src_dir.joinpath('cache', 'render.png'))
    img.save_render(filepath=save_path)

    # add watermark
    path = save_path
    img = Image.open(path)
    width, height = img.size

    config = auto_config(width, height)
    bg_col, title_col, tips_col, line_col = get_color(dark_mode=context.scene.sbb_dark_mode)

    # expand pixel size by scale
    scale = preset[config]['scale']
    new_img = Image.new('RGB', (width, int(height * scale)), bg_col)  # expand the img bottom to draw
    new_img.paste(img, (0, 0))  # fill in the original image

    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(new_img)

    # text
    left_text = f'BLENDER {bpy.app.version_string}'
    # right_text = '75mm f/1.8 Filmic Cycles'
    cam = context.scene.camera.data
    fstop = round(cam.dof.aperture_fstop, 2)
    lens = bpy.context.scene.camera.data.lens
    cs = context.scene.view_settings.view_transform
    render_engine = easy_engine_name[context.scene.render.engine]

    right_text = f'{lens}mm f/{fstop} {cs.strip()} {render_engine}'
    text_time = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    text_stats = get_scene_stats()

    # Add Text to an image, set size
    font_size = height * (scale - 1) * preset[config]['font_scale']
    boldFont = ImageFont.truetype(str(src_dir.joinpath('fonts', 'MiSans-Demibold.ttf')), int(font_size))
    lightFont = ImageFont.truetype(str(src_dir.joinpath('fonts', 'MiSans-Medium.ttf')), int(font_size * 0.75))

    padding = width * preset[config]['padding']
    bottom_padding = font_size * 0.5 + height * (scale - 1) * preset[config]['bottom_padding']

    # Left Title Text
    I1.text((padding, height * scale - bottom_padding), left_text, font=boldFont, fill=title_col)
    # Right Title Text
    loc_x_r_text_bold = width - padding - I1.textsize(right_text, font=boldFont)[0]
    loc_y_r_text_bold = height * scale - bottom_padding
    I1.text((loc_x_r_text_bold, loc_y_r_text_bold), right_text, font=boldFont, fill=title_col)
    # Left Tips Text
    loc_x_l_text_light = padding
    loc_y_l_text_light = loc_y_r_text_bold + font_size * 1.5
    I1.text((loc_x_l_text_light, loc_y_l_text_light), text_time, font=lightFont, fill=tips_col)
    # Right Bottom Text
    I1.text((loc_x_r_text_bold, loc_y_l_text_light), text_stats, font=lightFont, fill=tips_col)

    # get logo image
    logo_path = str(src_dir.joinpath('logos', 'blender.png' if not context.scene.sbb_dark_mode else 'blender_w.png'))
    logo = Image.open(logo_path)
    logo.convert('RGBA')
    logo_scale = preset[config]['logo_scale']
    logo = logo.resize((int(width * logo_scale), int(width * logo_scale * logo.size[1] / logo.size[0])))

    # paste logo image next to right text
    loc_logo_x = int(width - padding * 2 - I1.textsize(right_text, font=boldFont)[0] - logo.size[0])
    loc_logo_y = int(height * scale - bottom_padding)
    new_img.paste(logo, (loc_logo_x, loc_logo_y), logo)

    # draw a line shape between right text and logo
    line_start = int((loc_logo_x + logo.size[0] + loc_x_r_text_bold) / 2), int(loc_logo_y)
    line_end = int((loc_logo_x + logo.size[0] + loc_x_r_text_bold) / 2), int(loc_logo_y + logo.size[1])
    I1.line([line_start, line_end], fill=line_col, width=int(width / 500))

    # Save the edited image
    out_path = str(src_dir.joinpath('output', 'watermark.png'))
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
    bl_context = 'render'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, 'sbb_watermark')

    def draw(self, context):
        layout = self.layout
        layout.active = context.scene.sbb_watermark
        scene = context.scene
        layout.prop(scene, 'sbb_dark_mode')


def register():
    bpy.types.Scene.sbb_watermark = BoolProperty(name='Watermark', default=True)
    bpy.types.Scene.sbb_dark_mode = BoolProperty(name='Dark Mode', default=False)

    bpy.app.handlers.render_post.append(add_watermark_handle)

    bpy.utils.register_class(SBB_PT_panel)


def unregister():
    bpy.utils.unregister_class(SBB_PT_panel)

    bpy.app.handlers.render_post.remove(add_watermark_handle)

    del bpy.types.Scene.sbb_watermark
    del bpy.types.Scene.sbb_dark_mode
