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

# 按钮
class XClearAllUnusedDataOp(bpy.types.Operator):
    bl_idname = "xutil.clear_all_unused_data"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        # this can't be used in window otherthan info window
        # TODO how to override this context?

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        bpy.ops.outliner.orphans_purge(do_local_ids=False, do_linked_ids=True, do_recursive=True)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)

        return {'FINISHED'}

# 按钮
class XBakeThenSaveOp(bpy.types.Operator):
    bl_idname = "xutil.bake_then_save"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        #try:
        #    bpy.ops.ptcache.bake(bake=True)
        #finally:
        #    bpy.ops.wm.save_mainfile()

        bpy.ops.ptcache.bake(bake=True)
        bpy.ops.wm.save_mainfile()

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

        row = self.layout.row()
        row.operator("xutil.clear_all_unused_data", text="Clear All Unused Data")

# 物理模拟扩展
def draw_phys_extras(self, context):

    layout = self.layout

    layout.separator()

    row = layout.row()
    row.label(text="XUtil:")

    row = layout.row()
    row.operator(XBakeThenSaveOp.bl_idname, text="Bake Then Save")

# 模组初始化
classes = (
    XClearSystemConsoleOp,
    XClearInfoWindowOp,
    XClearAllUnusedDataOp,
    XBakeThenSaveOp,
    XMiscPanel,
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.PHYSICS_PT_cloth_cache.append(draw_phys_extras)
    bpy.types.PHYSICS_PT_softbody_cache.append(draw_phys_extras)
    bpy.types.PARTICLE_PT_cache.append(draw_phys_extras)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.PHYSICS_PT_cloth_cache.remove(draw_phys_extras)
    bpy.types.PHYSICS_PT_softbody_cache.remove(draw_phys_extras)
    bpy.types.PARTICLE_PT_cache.remove(draw_phys_extras)
