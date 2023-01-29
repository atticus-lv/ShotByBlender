from pathlib import Path


def main(input_path, output_path,
         label_output_path: str | None = None,
         title_left: str = 'BLENDER',
         title_right: str = '75mm f/1.8 Filmic Cycles',
         text_time: str | None = None,
         text_stats: str | None = None,
         dark_mode: bool = False,
         custom_logo_path: str | None = None):
    """Add watermark to image"""
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont

    ori_img = Image.open(input_path)
    width, height = ori_img.size

    config = get_config(width, height)
    bg_col, title_col, tips_col, line_col = get_color(dark_mode=dark_mode)

    scale = config['expand_scale']

    new_img = Image.new('RGBA', (width, int(height * scale)), bg_col)  # expand the img bottom to draw
    new_img.paste(ori_img, (0, 0))  # fill in the original image

    height = int(height * (scale - 1))
    label_img = Image.new('RGBA', (width, height), bg_col)  # expand the img bottom to draw
    DrawImg = ImageDraw.Draw(label_img)

    # -----------------draw label and title-----------------
    title_font_size = height * config['font_scale']
    tips_font_size = title_font_size * 0.7
    if text_stats is None and text_time is None:
        title_font_size *= 1.25
        tips_font_size *= 1.25

    font_path1, font_path2, logo_path = get_res_paths(dark_mode=dark_mode)
    boldFont = ImageFont.truetype(font_path1, int(title_font_size))
    lightFont = ImageFont.truetype(font_path2, int(tips_font_size))

    side_padding = width * config['padding']
    y_mid = height / 2
    y_title = y_mid - title_font_size * 1.25  # 1.25
    loc_x_r_title = width - side_padding - DrawImg.textsize(title_right, font=boldFont)[0]

    if text_stats is None and text_time is None:
        y_title += title_font_size * 0.5
    else:
        loc_x = side_padding
        loc_y = y_title + title_font_size * 1.5  # 0.5 + 1.25
        # draw both side
        if text_stats and text_time:
            DrawImg.text((loc_x, loc_y), text_time, font=lightFont, fill=tips_col)
            DrawImg.text((loc_x_r_title, loc_y), text_stats, font=lightFont, fill=tips_col)
        # draw on only right side
        elif text_stats is None and text_time:
            DrawImg.text((loc_x_r_title, loc_y), text_time, font=lightFont, fill=tips_col)
        else:
            DrawImg.text((loc_x_r_title, loc_y), text_stats, font=lightFont, fill=tips_col)

    DrawImg.text((side_padding, y_title), title_left, font=boldFont, fill=title_col)
    DrawImg.text((loc_x_r_title, y_title), title_right, font=boldFont, fill=title_col)

    # -----------------draw logo-----------------
    if custom_logo_path is not None:
        p = Path(custom_logo_path)
        if p.exists() and p.expanduser().is_file() and p.suffix in ['.png', '.jpg', '.jpeg', 'JPG', 'JPEG', 'PNG']:
            logo_path = custom_logo_path

    logo = Image.open(logo_path)
    logo.convert('RGBA')
    logo_scale = config['logo_scale']
    logo_height = int(height * logo_scale)
    logo_width = int(logo.size[0] * logo_height / logo.size[1])
    logo = logo.resize((logo_width, logo_height), Image.ANTIALIAS)
    # paste logo image next to right text
    loc_logo_x = int(width - side_padding * 2 - DrawImg.textsize(title_right, font=boldFont)[0] - logo.size[0])
    loc_logo_y = int(y_mid - logo_height / 2)
    label_img.paste(logo, (loc_logo_x, loc_logo_y), logo)

    # -----------------draw line-----------------
    # draw a line shape between right text and logo
    line_start = int((loc_logo_x + logo.size[0] + loc_x_r_title) / 2), int(loc_logo_y + logo.size[1] * 0.1)
    line_end = int((loc_logo_x + logo.size[0] + loc_x_r_title) / 2), int(loc_logo_y + logo.size[1] * 0.9)
    DrawImg.line([line_start, line_end], fill=line_col, width=int(logo.size[1] / 20))

    # paste label_img to new_img and save
    new_img.paste(label_img, (0, ori_img.size[1]), label_img)
    new_img.save(output_path)
    if label_output_path is not None:
        label_img.save(label_output_path)

    copy_img_metadata(input_path, output_path)


def get_config(width, height):
    radio = width / height

    if radio > 1:
        config = {
            "expand_scale": 1.16,
            "font_scale": 0.16,
            "padding": 0.025,
            "logo_scale": 0.4
        }
    elif radio > 0.5:
        config = {
            "expand_scale": 1.11,
            "font_scale": 0.18,
            "padding": 0.04,
            "logo_scale": 0.4
        }
    else:
        config = {
            "expand_scale": 1.05,
            "font_scale": 0.18,
            "padding": 0.04,
            "logo_scale": 0.4
        }
    return config


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


def get_res_paths(dark_mode=False):
    d = Path(__file__).parent.joinpath('res')
    boldFont = str(d.joinpath('fonts', 'MiSans-Demibold.ttf'))
    lightFont = str(d.joinpath('fonts', 'MiSans-Medium.ttf'))
    logo_path = str(d.joinpath('logos', 'blender.png' if not dark_mode else 'blender_w.png'))

    return boldFont, lightFont, logo_path


def copy_img_metadata(src_path, dist_path):
    """tEXt"""
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo

    src_img = Image.open(src_path)
    dist_img = Image.open(dist_path)

    metadata = PngInfo()
    for k, v in src_img.text.items():
        metadata.add_text(k, str(v))

    dist_img.save(dist_path, pnginfo=metadata)
