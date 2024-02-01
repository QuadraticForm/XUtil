import bpy

from bpy.types import Operator

# -------------------------------------------------------------------
#   Helper    
# -------------------------------------------------------------------

# -------------------------------------------------------------------
#   Operators    
# -------------------------------------------------------------------

class XEnableAllShapeKeysOp(Operator):
    bl_idname = "xutil_shapekey_tools.enable_all"
    bl_label = "Enable All"
    bl_description = "Enable all Shape Keys"

    def execute(self, context):       
        for shapekey in context.object.data.shape_keys.key_blocks:
            shapekey.mute = False

        self.report({'INFO'}, "All enabled")     
        return {'FINISHED'}

class XDisableAllShapeKeysOp(Operator):
    bl_idname = "xutil_shapekey_tools.disable_all"
    bl_label = "Disable All"
    bl_description = "Disable all Shape Keys"

    def execute(self, context):       
        for shapekey in context.object.data.shape_keys.key_blocks:
            shapekey.mute = True

        self.report({'INFO'}, "All Shape Keys disabled")        
        return {'FINISHED'}

def mirror_sk_name(shape_key_name : str) -> str:
    # left
    if shape_key_name.endswith(".l") or shape_key_name.endswith("_l"):
        return shape_key_name[0: len(shape_key_name) - 1] + "r"
    
    if shape_key_name.endswith(".L") or shape_key_name.endswith("_L"):
        return shape_key_name[0: len(shape_key_name) - 1] + "R"
    
    if shape_key_name.endswith("left"):
        return shape_key_name[0: len(shape_key_name) - 4] + "right"

    if shape_key_name.endswith("Left"):
        return shape_key_name[0: len(shape_key_name) - 4] + "Right"
    
    # right
    if shape_key_name.endswith(".r") or shape_key_name.endswith("_r"):
        return shape_key_name[0: len(shape_key_name) - 1] + "l"
    
    if shape_key_name.endswith(".R") or shape_key_name.endswith("_R"):
        return shape_key_name[0: len(shape_key_name) - 1] + "L"
    
    if shape_key_name.endswith("right"):
        return shape_key_name[0: len(shape_key_name) - 5] + "left"
    
    if shape_key_name.endswith("Right"):
        return shape_key_name[0: len(shape_key_name) - 5] + "Left"
    
    #other
    return shape_key_name + "_Mirror"

def mirror_sk(topo_mirror : bool) -> bool:

    # 0. get current shape key info

    obj = bpy.context.active_object
    this_sk = obj.active_shape_key
    this_obj_data : bpy.types.Mesh = obj.data
    shape_keys = this_obj_data.shape_keys.key_blocks

    # 1. determine other side shape key name

    other_sk_name = mirror_sk_name(this_sk.name)

    if len(other_sk_name) == 0:
        return False

    # 2. reset other side shape key, and set active

    other_sk = shape_keys.get(other_sk_name)
    if other_sk:
        obj.shape_key_remove(other_sk)
    other_sk = obj.shape_key_add(name=other_sk_name, from_mix=False)

    obj.active_shape_key_index = len(shape_keys) - 1

    # 3. make other side shape key == this shape key

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.blend_from_shape(shape=this_sk.name, blend=1.0, add=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # 4. call mirror

    bpy.ops.object.shape_key_mirror(use_topology=topo_mirror)

    return True

class XShapeKeyMirrorLeftRightOp(Operator):
    bl_idname = "xutil_shapekey_tools.mirror_left_right"
    bl_label = "Mirror Left/Right"
    bl_description = "Mirror the current shape key to the other side"

    def execute(self, context):       
        
        mirror_sk(topo_mirror=False)

        return {'FINISHED'}
    
class XShapeKeyMirrorLeftRightTopoOp(Operator):
    bl_idname = "xutil_shapekey_tools.mirror_left_right_topo"
    bl_label = "Mirror Left/Right (Topology)"
    bl_description = "Mirror the current shape key to the other side"

    def execute(self, context):       
        
        mirror_sk(topo_mirror=True)

        return {'FINISHED'}

def set_all_weight(weight : float):
    # 获取活跃的对象
    obj = bpy.context.active_object

    # 检查是否有选中的对象，并且该对象是网格对象
    if obj and obj.type == 'MESH':
    # 设置所有形状关键帧的权重
        for shape_key in obj.data.shape_keys.key_blocks:
            # 这里设置为你想要的权重值
            shape_key.value = weight
    else:
        print("请选中一个网格对象！")   

class XAllShapeKeysToZeroOp(Operator):
    bl_idname = "xutil_shapekey_tools.all_to_zero"
    bl_label = "all 0"
    bl_description = "set all weight to 0"

    def execute(self, context):       
        for shapekey in context.object.data.shape_keys.key_blocks:
            shapekey.value = 0

        return {'FINISHED'}

class XAllShapeKeysToOneOp(Operator):
    bl_idname = "xutil_shapekey_tools.all_to_one"
    bl_label = "all 1"
    bl_description = "set all weight to 1"

    def execute(self, context):       
        for shapekey in context.object.data.shape_keys.key_blocks:
            shapekey.value = 1

        return {'FINISHED'}


# -------------------------------------------------------------------
#   UI    
# -------------------------------------------------------------------

def draw_ui(self, context):

    scn = context.scene
    layout = self.layout

    layout.separator()
    layout.use_property_decorate = False  # No animation.
    layout.use_property_split = False
    
    layout.separator()

    row = layout.row()
    row.label(text="XUtil Shape Key Tools:")

    row = layout.row(align=True)
    row.operator(XEnableAllShapeKeysOp.bl_idname, icon="RESTRICT_VIEW_OFF")
    row.operator(XDisableAllShapeKeysOp.bl_idname, icon="RESTRICT_VIEW_ON")

    row = layout.row(align=True)
    row.operator(XShapeKeyMirrorLeftRightOp.bl_idname, icon="MOD_MIRROR")
    row.operator(XShapeKeyMirrorLeftRightTopoOp.bl_idname, icon="MOD_MIRROR")

    row = layout.row(align=True)
    row.operator(XAllShapeKeysToZeroOp.bl_idname)
    row.operator(XAllShapeKeysToOneOp.bl_idname)

# -------------------------------------------------------------------
# register    
# -------------------------------------------------------------------

classes = (
    XEnableAllShapeKeysOp,
    XDisableAllShapeKeysOp,
    XShapeKeyMirrorLeftRightOp,
    XShapeKeyMirrorLeftRightTopoOp,
    XAllShapeKeysToZeroOp,
    XAllShapeKeysToOneOp
)


def initialize():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    bpy.types.DATA_PT_shape_keys.append(draw_ui)

def uninitialize():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
    bpy.types.DATA_PT_shape_keys.remove(draw_ui)