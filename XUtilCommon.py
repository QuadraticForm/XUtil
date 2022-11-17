import bpy

def draw_btn(layout, btnClass):
    layout.operator(operator = btnClass.bl_idname, text = btnClass.bl_label)

