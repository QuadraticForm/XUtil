import bpy
from distutils import dist
import math
import copy

x_cur_dist = 0

def active_object_name():
    if bpy.context.active_object:
        return bpy.context.active_object.name
    else:
        return "None"

# 按钮
# change parent but keep current local transform (transform relative to current parent)
# TODO need more testing
class XParentKeepLocal(bpy.types.Operator):
    bl_idname = "xutil.parent_keep_local_button"
    bl_label = "Parent Keep Local"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1 and context.active_object.mode == 'OBJECT'

    def execute(self, context):

        locations = []
        rotations = []
        scales = []

        # TODO need more testing

        # record local transform
        # TODO this is problematic, transform is not always local transform
        # TODO investigate what the fuck does transform mean

        for obj in bpy.context.selected_objects:
            locations.append(copy.copy(obj.location))
            rotations.append(copy.copy(obj.rotation_euler))
            scales.append(copy.copy(obj.scale))

        # change parent & reset local transform to 000
        # now transform is in local space

        bpy.ops.object.parent_no_inverse_set()

        # recover local transform

        for i, obj in enumerate(bpy.context.selected_objects):
            obj.location = locations[i]
            obj.rotation_euler = rotations[i]
            obj.scale = scales[i]

        return {'FINISHED'}        

# 面板
class XTransform(bpy.types.Panel):
    bl_label = "Transform"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):

        row = self.layout.row()        
        row.label(text = "Selected: ")

        for obj in bpy.context.selected_objects:
            row = self.layout.row()
            row.label(text = "    " + obj.name)

        row = self.layout.row()

        row.label(text = "Active: " + active_object_name())

        row = self.layout.row()
        row.operator("xutil.parent_keep_local_button", text="Parent Keep Local") 

# 模组初始化
classes = (
    XParentKeepLocal,
    XTransform,
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)
    #bpy.types.Scene.HairProps = bpy.props.PointerProperty(type=HairProps)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    #del(bpy.types.Scene.HairProps)