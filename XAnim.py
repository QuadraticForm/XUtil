from ast import Not
import bpy
from distutils import dist
from . import XUtilCommon as xuc

#
# Anim
#

class XAnimProps(bpy.types.PropertyGroup):
    timeScale: bpy.props.FloatProperty(default=1.0)
    timeOffset: bpy.props.FloatProperty(default=0)

# 按钮
class XAnimTimeScaleOp(bpy.types.Operator):
    bl_idname = "xutil.anim_time_scale"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        props = bpy.context.scene.animProps

        bpy.ops.transform.transform(mode='TIME_SCALE', value=(props.timeScale, 0, 0, 0), orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

        return {'FINISHED'}

# 按钮
class XAnimTimeOffsetOp(bpy.types.Operator):
    bl_idname = "xutil.anim_time_offset"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        props = bpy.context.scene.animProps

        bpy.ops.transform.transform(mode='TIME_TRANSLATE', value=(props.timeOffset, 0, 0, 0), orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

        return {'FINISHED'}

# 面板
class XAnimPanel(bpy.types.Panel):
    bl_label = "XAnim"
    #bl_space_type = 'VIEW_3D'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):

        row = self.layout.row()
        row.label(text = "Keyframe Transform")
        

        box = self.layout.box()

        row = box.row()
        row.prop(bpy.context.scene.animProps, "timeScale", text="Time Scale")

        row = box.row()
        row.operator("xutil.anim_time_scale", text = "Scale Selected Keyframes")


        box = self.layout.box()

        row = box.row()
        row.prop(bpy.context.scene.animProps, "timeOffset", text="Time Offset")

        row = box.row()
        row.operator("xutil.anim_time_offset", text = "Offset Selected Keyframes")


#
# NLA
#

# 按钮
class XDeleteNLATrackOp(bpy.types.Operator):
    bl_idname = "xutil.delete_nla_track"
    bl_label = "Delete NLA Track"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        anim_data = bpy.context.active_object.animation_data

        anim_data.nla_tracks.remove(anim_data.nla_tracks.active)

        return {'FINISHED'}

# NLA面板
class XNLAPanel(bpy.types.Panel):
    bl_label = "XNLA"
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):

        row = self.layout.row()

        xuc.draw_btn(row, XDeleteNLATrackOp)

#
# 模组初始化
#

classes = (
    XAnimProps,
    XAnimTimeScaleOp,
    XAnimTimeOffsetOp,
    XAnimPanel,
    XNLAPanel,
    XDeleteNLATrackOp
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.animProps = bpy.props.PointerProperty(type=XAnimProps)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del(bpy.types.Scene.animProps)