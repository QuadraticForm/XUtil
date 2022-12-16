import bpy
from distutils import dist
import math
import bmesh

x_cur_dist = 0
x_edge_length_sum = 0

# 按钮
class XCurDistButton(bpy.types.Operator):
    bl_idname = "xutil.cur_dist_button"
    bl_label = "Calc distance to cursor"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object.mode == 'OBJECT'

    def execute(self, context):

        obj_pos = bpy.context.active_object.matrix_world.translation
        cur_pos = bpy.context.scene.cursor.location

        global x_cur_dist
        x_cur_dist = math.dist(obj_pos, cur_pos)
        print("Haha: "+ str(x_cur_dist))

        return {'FINISHED'}        


# 按钮
class XEdgeLengthSumOp(bpy.types.Operator):
    bl_idname = "xutil.edge_len_sum_op"
    bl_label = "Sum selected edge length"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object.mode == 'EDIT'

    def execute(self, context):

        # Get the active mesh
        me = bpy.context.object.data

        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)

        # sum
        global x_edge_length_sum

        x_edge_length_sum = 0
        for e in bm.edges:
            if e.select:
                x_edge_length_sum += (e.verts[0].co - e.verts[1].co).magnitude
    
        bm.free()  # free and prevent further access

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

        row = self.layout.row()
        row.label(text = "Edge Length Sum: " + str(x_edge_length_sum))

        row = self.layout.row()
        row.operator(XEdgeLengthSumOp.bl_idname, text=XEdgeLengthSumOp.bl_label)
        

# 模组初始化
classes = (
    XCurDistButton,
    XEdgeLengthSumOp,
    XCurDistPanel,
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)