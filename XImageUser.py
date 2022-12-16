# made for https://blender.stackexchange.com/q/84328/935
# show places in blender where an image is in use.
# also provide a way to clear the usage of the images.

import bpy

class ClearAllBackgroundImages(bpy.types.Operator):
    bl_idname = 'image.clear_all_background_images'
    bl_label = 'Clear the use of all 3DView background images'

    def execute(self, context):
        for scr in bpy.data.screens:
            for a in scr.areas:
                for sp in a.spaces:
                    if sp.type == 'VIEW_3D':
                        for bi in sp.background_images:
                            bi.image = None
        return {'FINISHED'}

class ClearAllBrushImages(bpy.types.Operator):
    bl_idname = 'image.clear_all_brush_images'
    bl_label = 'Clear the use of all images by brushes'

    def execute(self, context):
        for b in bpy.data.brushes:
            b.texture.image = None
        return {'FINISHED'}

class ClearAllEmptyImages(bpy.types.Operator):
    bl_idname = 'image.clear_all_empty_images'
    bl_label = 'Clear the use of all empties displaying images'

    def execute(self, context):
        for o in bpy.data.objects:
            if o.type == 'EMPTY':
                o.data = None
        return {'FINISHED'}

class ClearAllImageEditorImages(bpy.types.Operator):
    bl_idname = 'image.clear_all_image_editor_images'
    bl_label = 'Clear active images in UV/Image editors'

    def execute(self, context):
        for scr in bpy.data.screens:
            for a in scr.areas:
                for sp in a.spaces:
                    if sp.type == 'IMAGE_EDITOR':
                        sp.image = None
        return {'FINISHED'}

class ClearAllCompositorNodeImages(bpy.types.Operator):
    bl_idname = 'image.clear_all_compositor_images'
    bl_label = 'Clear images used in the compositor'

    def execute(self, context):
        for scn in bpy.data.scenes:
            if scn.use_nodes:
                for n in scn.node_tree.nodes:
                    if n.type == 'IMAGE':
                        n.image = None
        return {'FINISHED'}

class ClearAllCyclesMaterialImages(bpy.types.Operator):
    bl_idname = 'image.clear_all_cycles_material_images'
    bl_label = 'Clear images used in cycles materials'

    def execute(self, context):
        for m in bpy.data.materials:
            if m.use_nodes:
                for n in m.node_tree.nodes:
                    if n.type == 'TEX_IMAGE':
                        n.image = None
        return {'FINISHED'}

class ClearAllTextureImages(bpy.types.Operator):
    bl_idname = 'image.clear_all_texture_images'
    bl_label = 'Clear the use of all images by textures'

    def execute(self, context):
        for t in bpy.data.textures:
            t.image = None
        return {'FINISHED'}

def show_background_use(layout, img):

    # xuxing: this is unusable now, return
    return

    in_use = False
    for scr in bpy.data.screens:
        for a in scr.areas:
            for sp in a.spaces:
                if sp.type == 'VIEW_3D':
                    for bi in sp.background_images:
                        if bi.image == img:
                            in_use = True
                            row = layout.row()
                            row.label(text='{} -- View {}'.format(
                                        scr.name, bi.view_axis))
    if not in_use:
        row = layout.row()
        row.label(text='None')
    return in_use

def show_compositor_use(layout, img):
    in_use = False
    for scn in bpy.data.scenes:
        if scn.use_nodes:
            for n in scn.node_tree.nodes:
                if n.type == 'IMAGE' and n.image == img:
                    in_use = True
                    row = layout.row()
                    row.label(text='Compositor '+n.name)
    if not in_use:
        row = layout.row()
        row.label(text='None')
    return in_use

def show_cycles_material_use(layout, img):
    in_use = False
    for m in bpy.data.materials:
        if m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type == 'TEX_IMAGE' and n.image == img:
                    in_use = True
                    row = layout.row()
                    row.label(text=m.name)
    if not in_use:
        row = layout.row()
        row.label(text='None')
    return in_use

def show_uvimage_editor_use(layout, img):
    in_use = False
    for scr in bpy.data.screens:
        for a in scr.areas:
            for sp in a.spaces:
                if sp.type == 'IMAGE_EDITOR':
                    if sp.image == img:
                        in_use = True
                        row = layout.row()
                        row.label(text=scr.name)
    if not in_use:
        row = layout.row()
        row.label(text='None')
    return in_use

class ShowImageUsers(bpy.types.Panel):
    bl_idname = 'IMAGE_PT_show_users'
    bl_label = "Image User"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):
        layout = self.layout

        img = context.space_data.image
        if img == None:
            box = layout.box()
            box.label(text='No image active!')
            return
        if img.type != 'RENDER_RESULT' and img.type != 'COMPOSITING':
            
            # 3DView backgrounds

            box = layout.box()
            box.label(text='3DView backgrounds')
            if show_background_use(layout, img):
                box.operator(ClearAllBackgroundImages.bl_idname, text='Clear All')
            
            # Empties with image
            
            box = layout.box()
            box.label(text='Empties with image')
            in_use = False
            for o in bpy.data.objects:
                if o.type == 'EMPTY' and o.data == img:
                    in_use = True
                    row = box.row()
                    row.label(text=o.name)
            if not in_use:
                row = box.row()
                row.label(text='None')
            else:
                box.operator(ClearAllEmptyImages.bl_idname, text='Clear All')

            # Textures with image

            box = layout.box()
            box.label(text='Textures with image')
            in_use = False
            for t in bpy.data.textures:
                if hasattr(t, 'image'):
                    if t.image == img:
                        in_use = True
                        row = box.row()
                        row.label(text=t.name)
            if not in_use:
                row = box.row()
                row.label(text='None')
            else:
                box.operator(ClearAllTextureImages.bl_idname, text='Clear All')

            # Cycles Materials with image

            box = layout.box()
            box.label(text='Cycles Materials with image')
            if show_cycles_material_use(box, img):
                box.operator(ClearAllCyclesMaterialImages.bl_idname, text='Clear All')

            # Compositor image nodes
            
            box = layout.box()
            box.label(text='Compositor image nodes')
            if show_compositor_use(box, img):
                box.operator(ClearAllCompositorNodeImages.bl_idname, text='Clear All')

            # UV/Image Editors

            box = layout.box()
            box.label(text='UV/Image Editors')
            if show_uvimage_editor_use(box, img):
                box.operator(ClearAllImageEditorImages.bl_idname, text='Clear All')

def initialize():
    bpy.utils.register_class(ClearAllBackgroundImages)
    bpy.utils.register_class(ClearAllBrushImages)
    bpy.utils.register_class(ClearAllCompositorNodeImages)
    bpy.utils.register_class(ClearAllCyclesMaterialImages)
    bpy.utils.register_class(ClearAllEmptyImages)
    bpy.utils.register_class(ClearAllImageEditorImages)
    bpy.utils.register_class(ClearAllTextureImages)
    bpy.utils.register_class(ShowImageUsers)

def uninitialize():
    bpy.utils.unregister_class(ShowImageUsers)
    bpy.utils.unregister_class(ClearAllBackgroundImages)
    bpy.utils.unregister_class(ClearAllBrushImages)
    bpy.utils.unregister_class(ClearAllCompositorNodeImages)
    bpy.utils.unregister_class(ClearAllCyclesMaterialImages)
    bpy.utils.unregister_class(ClearAllEmptyImages)
    bpy.utils.unregister_class(ClearAllImageEditorImages)
    bpy.utils.unregister_class(ClearAllTextureImages)