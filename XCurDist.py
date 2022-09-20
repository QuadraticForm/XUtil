import bpy
from distutils import dist
import math

x_cur_dist = 0

# 按钮
class XCurDistButton(bpy.types.Operator):
    bl_idname = "xutil.cur_dist_button"
    bl_label = "Calc distance to cursor"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object.mode == 'OBJECT'

    def execute(self, context):

        global x_cur_dist

        obj_pos = bpy.context.active_object.matrix_world.translation
        cur_pos = bpy.context.scene.cursor.location

        x_cur_dist = math.dist(obj_pos, cur_pos)
        print("Haha: "+ str(x_cur_dist))

        return {'FINISHED'}        

# 面板
class XCurDistPanel(bpy.types.Panel):
    bl_label = "Cur Dist"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):

        global x_cur_dist

        row = self.layout.row()        
        row.label(text = "Distance to cursor: " + str(x_cur_dist))

        row = self.layout.row()
        row.operator("xutil.cur_dist_button", text="Calc Dist") 

# 模组初始化
classes = (
    XCurDistButton,
    XCurDistPanel,
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)
    #bpy.types.Scene.HairProps = bpy.props.PointerProperty(type=HairProps)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    #del(bpy.types.Scene.HairProps)