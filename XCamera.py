from ast import Not
import bpy
from distutils import dist
import math
import copy

def selected_camera() :
    if len(bpy.context.selected_objects) > 0:
        return bpy.context.selected_objects[0]
    else:
        return None

class XCameraProps(bpy.types.PropertyGroup):
    renderOutputPrefix: bpy.props.StringProperty(default="//Render_")
    renderOutputPostfix: bpy.props.StringProperty(default="/")

# 按钮
class XSetAsViewCamOp(bpy.types.Operator):
    bl_idname = "xutil.set_as_view_cam"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return selected_camera() is not None

    def execute(self, context):

        bpy.context.space_data.camera = selected_camera()

        return {'FINISHED'}

# 按钮
class XSetAsSceneCamOp(bpy.types.Operator):
    bl_idname = "xutil.set_as_scene_cam"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return selected_camera() is not None

    def execute(self, context):

        bpy.context.scene.camera = selected_camera()

        return {'FINISHED'}

# 按钮
class XToggleViewCamLockOp(bpy.types.Operator):
    bl_idname = "xutil.toggle_view_cam_lock"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        bpy.context.space_data.lock_camera = not bpy.context.space_data.lock_camera

        return {'FINISHED'}

# 按钮
class XAutoRenderOutputDirOp(bpy.types.Operator):
    bl_idname = "xutil.auto_render_output_dir"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.camera is not None

    def execute(self, context):

        props = bpy.context.scene.XCameraProps

        bpy.context.scene.render.filepath = props.renderOutputPrefix + bpy.context.scene.camera.name + props.renderOutputPostfix

        return {'FINISHED'}


# 面板
class XCameraPanel(bpy.types.Panel):
    bl_label = "Camera"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):

        ####

        box = self.layout.box()
        
        if selected_camera() is not None:
            row = box.row()
            row.label(text = "Selected: ")
            row.label(text = selected_camera().name)

        row = box.row()
        row.operator("xutil.set_as_view_cam", text="Set As View Cam")

        row = box.row()
        row.operator("xutil.set_as_scene_cam", text="Set As Scene Cam")

        ####

        box = self.layout.box()

        if bpy.context.space_data.camera is not None:
            row = box.row()
            row.label(text = "View Cam: ")
            row.label(text = bpy.context.space_data.camera.name)

        row = box.row()

        if bpy.context.space_data.lock_camera is True:
            row.label(text = "LOCKED")
        else:
            row.label(text = "NOT LOCKED")

        row = box.row()

        if bpy.context.space_data.lock_camera is True:
            row.operator("xutil.toggle_view_cam_lock", text="Unlock View-Cam")
        else:
            row.operator("xutil.toggle_view_cam_lock", text="Lock View-Cam")

        ####

        box = self.layout.box()

        if bpy.context.scene.camera is not None:
            row = box.row()
            row.label(text = "Scene Cam: ")
            row.label(text = bpy.context.scene.camera.name)
        
        row = box.row()
        row.label(text = "Output Dir: ")

        row = box.row()
        row.label(text = bpy.context.scene.render.filepath)

        row = box.row()
        row.prop(bpy.context.scene.XCameraProps, "renderOutputPrefix", text="Prefix")

        row = box.row()
        row.prop(bpy.context.scene.XCameraProps, "renderOutputPostfix", text="Postfix")

        row = box.row()
        row.operator("xutil.auto_render_output_dir", text = "Auto Output Path: Prefix + camera name + Postfix")


# 模组初始化
classes = (
    XCameraProps,
    XSetAsViewCamOp,
    XSetAsSceneCamOp,
    XToggleViewCamLockOp,
    XAutoRenderOutputDirOp,
    XCameraPanel,
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.XCameraProps = bpy.props.PointerProperty(type=XCameraProps)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del(bpy.types.Scene.XCameraProps)