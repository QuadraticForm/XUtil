from ast import Not
import bpy
from distutils import dist
import os

# 按钮
class XClearSystemConsoleOp(bpy.types.Operator):
    bl_idname = "xutil.clear_system_console"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        if os.name == "nt":
            os.system("cls") 
        else:
            os.system("clear") 

        return {'FINISHED'}

# 按钮
class XClearInfoWindowOp(bpy.types.Operator):
    bl_idname = "xutil.clear_info_window"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        # this can't be used in window otherthan info window
        # TODO how to override this context?

        bpy.ops.info.select_all(action='SELECT')
        bpy.ops.info.report_delete()

        return {'FINISHED'}

# 面板
class XMiscPanel(bpy.types.Panel):
    bl_label = "Misc"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):

        row = self.layout.row()
        row.operator("script.reload", text="Reload Scripts")

        row = self.layout.row()
        row.operator("xutil.clear_system_console", text="Clear System Console")

        #row = self.layout.row()
        #row.operator("xutil.clear_info_window", text="Clear Info Window")



# 模组初始化
classes = (
    XClearSystemConsoleOp,
    XClearInfoWindowOp,
    XMiscPanel,
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)