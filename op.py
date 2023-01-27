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

    config = context.scene.sbb_config

    # expand pixel size by scale
    scale = preset[config]['scale']
    new_img = Image.new('RGB', (width, int(height * scale)), (255, 255, 255))  # expand the img bottom to draw
    new_img.paste(img, (0, 0))  # fill in the original image

    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(new_img)

    # text
    left_text = 'BLENDER3.5'
    # right_text = '75mm f/1.8 Filmic Cycles'
    cam = context.scene.camera.data
    fstop = round(cam.dof.aperture_fstop, 2)
    lens = bpy.context.scene.camera.data.lens
    cs = context.scene.view_settings.view_transform
    render_engine = easy_engine_name[context.scene.render.engine]

    right_text = f'{lens}mm f/{fstop} {cs.strip()} {render_engine}'
    text_time = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')

    title_col = (0, 0, 0)
    tips_col = (128, 128, 128)
    line_col = (220, 220, 220)

    # Add Text to an image, set size
    font_size = height * (scale - 1) * preset[config]['font_scale']
    boldFont = ImageFont.truetype(str(src_dir.joinpath('fonts', 'MiSans-Demibold.ttf')), int(font_size))
    lightFont = ImageFont.truetype(str(src_dir.joinpath('fonts', 'MiSans-Medium.ttf')), int(font_size * 0.75))

    padding = width * preset[config]['padding']
    bottom_padding = font_size * 0.5 + height * (scale - 1) * preset[config]['bottom_padding']

    # Add Text to the bottom left of the image
    I1.text((padding, height * scale - bottom_padding), left_text, font=boldFont, fill=title_col)
    # Add Text to the bottom right of the image
    loc_x_r_text_bold = width - padding - I1.textsize(right_text, font=boldFont)[0]
    loc_y_r_text_bold = height * scale - bottom_padding
    I1.text((loc_x_r_text_bold, loc_y_r_text_bold), right_text, font=boldFont, fill=title_col)
    # Add Text to the bottom of the last text
    I1.text((loc_x_r_text_bold, loc_y_r_text_bold + font_size * 1.5), text_time, font=lightFont, fill=tips_col)

    # get logo image
    logo = Image.open(str(src_dir.joinpath('logos', 'blender.png')))
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
        layout.prop(scene, 'sbb_config')


def register():
    bpy.types.Scene.sbb_watermark = BoolProperty(name='Watermark', default=True)
    bpy.types.Scene.sbb_config = EnumProperty(items=[('16/9', '16/9', '16/9'), ('1/1', '1/1', '1/1')], name='Presets',
                                              default='16/9')

    bpy.app.handlers.render_post.append(add_watermark_handle)

    bpy.utils.register_class(SBB_PT_panel)


def unregister():
    bpy.utils.unregister_class(SBB_PT_panel)

    bpy.app.handlers.render_post.remove(add_watermark_handle)

    del bpy.types.Scene.sbb_watermark
    del bpy.types.Scene.sbb_config
