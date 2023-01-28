import datetime
from pathlib import Path
from contextlib import contextmanager

import bpy
from bpy.app.handlers import persistent

easy_engine_name = {
    'BLENDER_EEVEE': 'Eevee',
    'BLENDER_WORKBENCH': 'Workbench',
    'CYCLES': 'Cycles'
}

src_dir = Path(__file__).parent


def get_scene_stats() -> str:
    stats = bpy.context.scene.statistics(bpy.context.view_layer)
    # print(stats)

    if len(stats.split(sep=' | ')) == 7:
        coll, verts, faces, tris, objs, mem, ver = stats.split(sep=' | ')
    else:
        coll, obj, verts, faces, tris, objs, mem, ver = stats.split(sep=' | ')

    verts = verts.split(sep=':')[-1]
    faces = faces.split(sep=':')[-1]
    tris = tris.split(sep=':')[-1]
    mem = mem.split(sep=':')[-1]

    s = f"Faces: {faces} |{mem}"
    return s


@contextmanager
def grab_blender_img(name='Render Result'):
    img = bpy.data.images[name]

    save_dir = Path(__file__).parent.joinpath('cache')
    save_path = save_dir.joinpath('render.png')
    out_path = save_dir.joinpath('output.png')
    if not save_dir.exists():
        save_dir.mkdir(exist_ok=True)
    img.save_render(filepath=str(save_path))

    yield str(save_path), str(out_path)

    if 'Render Result_WM' in bpy.data.images:
        bpy.data.images.remove(bpy.data.images['Render Result_WM'])
    data = bpy.data.images.load(str(out_path))
    data.name = 'Render Result_WM'
    # change image editor to show the new image
    try:
        window = bpy.context.window_manager.windows[-1]
        for area in window.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = data
                break
    except:
        pass


def add_watermark_4_blender_img(name='Render Result'):
    from . import add_watermark

    context = bpy.context
    sbb = context.scene.sbb
    if not sbb.enable: return

    with grab_blender_img(name) as (src_path, out_path):
        title_left = 'BLENDER'
        if sbb.title_version:
            title_left += f' {bpy.app.version_string}'

        cam = context.scene.camera.data
        fstop = round(cam.dof.aperture_fstop, 1)
        lens = str(bpy.context.scene.camera.data.lens).split('.')[0]
        # cs = context.scene.view_settings.view_transform.strip().replace(" ", "")
        render_engine = easy_engine_name.get(context.scene.render.engine, context.scene.render.engine.title())

        title_right = f'{lens}mm f/{fstop} {render_engine.upper()}'
        text_time = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        text_stats = get_scene_stats()

        add_watermark.main(
            input_path=src_path,
            output_path=out_path,
            label_output_path=out_path[:-4] + '_label.png',
            title_left=title_left,
            title_right=title_right,
            text_time=text_time if sbb.text_time else None,
            text_stats=text_stats if sbb.text_stats else None,
            dark_mode=sbb.dark_mode,
            custom_logo_path=sbb.logo_path if sbb.ow_logo else None,
        )


@persistent
def add_watermark_handle(dummy):
    add_watermark_4_blender_img()


def register():
    bpy.app.handlers.render_post.append(add_watermark_handle)


def unregister():
    bpy.app.handlers.render_post.remove(add_watermark_handle)
