from genericpath import isfile
import bpy
import math
import os.path
import os
from bpy_extras.io_utils import ImportHelper
import shutil

class XProjProps(bpy.types.PropertyGroup):
    src_proj_dir: bpy.props.StringProperty(default="//", subtype="DIR_PATH")
    target_proj_dir: bpy.props.StringProperty(default="//", subtype="DIR_PATH")

# 帮助函数

def remove_empty(src_list : list[str]) -> list[str]:
    new_list = []

    for element in src_list:
        if len(element) > 0 or not element.startswith(" "):
            new_list.append(element)

    return new_list

def remove_duplication(src_list):

    new_list = []

    for element in src_list:
        if element not in new_list:
            new_list.append(element)

    return new_list

def get_unpacked_refs() -> list[str]:

    # packed (boolean) – When true SKIP file paths for packed data.
    # local (boolean) – When true skip linked library paths.
    return remove_empty(remove_duplication(bpy.utils.blend_paths(absolute=False, packed=True, local=False)))

def get_unpacked_libs() -> list[str]:

    unpacked_libs = []

    unpacked_refs = get_unpacked_refs()

    for ref in unpacked_refs:
        if ref.endswith(".blend"):
            unpacked_libs.append(ref)

    return unpacked_libs

def is_abs_path(filepath : str) -> bool:
    return (filepath.find(":") >= 0) is True

def is_relative_path(filepath : str) -> bool:
    return filepath.startswith("//") is True

def get_current_filepath() -> str:
    return normalize_slashes(bpy.context.blend_data.filepath)

def normalize_slashes(path : str) -> str:
    path = path.replace("\\", "/")
    return path

def normalize_dir_path(path : str) -> str:

    # normalize slashes:
    # xxx/asdf\asdf 
    # xxx/asdf/asdf

    path = path.replace("\\", "/")

    # remove filename
    # xxx/abc.blend
    # xxx/

    lastDotPos = path.rfind(".")
    lastSlashPos = path.rfind("/")

    if lastSlashPos < lastDotPos:
        path = path[0: lastSlashPos]

    # add trailing slash
    # xxx
    # xxx/

    if path.endswith("/") is not True:
        path = path + "/"

    return path

def get_path_rel_to_dir(dir : str, file : str) -> tuple[bool, str]:

    # in file:  xxx/asdf.blend
    # in dir:   xxx/
    # out:      asdf.blend

    if file.startswith(dir) is not True:
        return (False, "")
    else:
        return (True, file[len(dir):])

def get_path_rel_to_proj(file : str) -> tuple[bool, str]:
    return get_path_rel_to_dir(get_abs_src_proj_dir(), file)
 
def get_abs_path(path : str) -> str:

    if path.startswith("//"):
        # bpy.path.abspath() is not good enough, 
        # some times it returns path with ../ in it
        # so os.path.abspath() is used to solve that
        #return normalize_slashes(bpy.path.abspath(path))
        return normalize_slashes(os.path.abspath(bpy.path.abspath(path)))
    else:
        return normalize_slashes(path)

def is_file(path : str) -> bool:
    return os.path.isfile(get_abs_path(path))

def get_abs_src_proj_dir() -> str:
    return normalize_dir_path(get_abs_path(bpy.context.scene.XProjProps.src_proj_dir))

def get_abs_target_proj_dir() -> str:
    return get_abs_path(bpy.context.scene.XProjProps.target_proj_dir)

def get_abs_filepaths_to_copy() -> list[str]:

    paths = get_unpacked_refs()

    abs_paths = []

    abs_paths.append(get_current_filepath())

    for path in paths:
        abs_paths.append(get_abs_path(path))

    return abs_paths

def ensure_dir(filepath : str):

    dir_path = normalize_dir_path(filepath)

    os.makedirs(dir_path, exist_ok=True)

    return



# 按钮
class XCheckUnpackedRefsOp(bpy.types.Operator):
    bl_idname = "xutil.check_unpacked_refs"
    bl_label = "Check Unpacked Refs"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        unpackedRefs = get_unpacked_refs()

        for filepath in unpackedRefs:
            self.report({"INFO"}, "Unpacked Ref: " + filepath)
            if filepath.endswith(".blend") is not True:
                self.report({"WARNING"}, "You better pack this, other file linked to this file might not know this ref, when copying proj in that file, this ref won't be copied.")
            if is_abs_path(filepath):
                self.report({"WARNING"}, "File with abs path won't be copied")
            if is_file(filepath) is not True:
                self.report({"WARNING"}, "File not exist")

        return {'FINISHED'}

# 按钮
class XCheckUnpackedLibsOp(bpy.types.Operator):
    bl_idname = "xutil.check_unpacked_libs"
    bl_label = "Check Unpacked Libs"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        unpackedLibs = get_unpacked_libs()

        for filepath in unpackedLibs:
            self.report({"INFO"}, "Unpacked Ref: " + filepath)
            if is_abs_path(filepath):
                self.report({"WARNING"}, "File with abs path won't be copied")
            if is_file(filepath) is not True:
                self.report({"WARNING"}, "File not exist")

        return {'FINISHED'}


# 按钮
class XProjCopyOp(bpy.types.Operator):
    bl_idname = "xutil.proj_copy"
    bl_label = "Project Copy"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        files_to_copy = get_abs_filepaths_to_copy()

        for filepath in files_to_copy:

            if is_file(filepath) is not True:
                self.report({"WARNING"}, "File Not Exist: " + filepath)
                continue

            self.report({"INFO"}, "Copy: " + filepath)

            (is_rel_to_proj, path_rel_to_proj) = get_path_rel_to_proj(filepath)

            if is_rel_to_proj:
                new_abs_path = get_abs_target_proj_dir() + path_rel_to_proj
                ensure_dir(new_abs_path)
                shutil.copy(filepath, new_abs_path)
                self.report({"INFO"}, "To: " + new_abs_path)
            else:
                self.report({"ERROR"}, "File Not Child Of Proj: " + filepath)

        return {'FINISHED'}


# 面板
class XProjPanel(bpy.types.Panel):
    bl_label = "Proj"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw_proj_dir_section(self, context):

        props = bpy.context.scene.XProjProps

        row = self.layout.row()
        row.label(text="Proj Dir")

        box = self.layout.box()

        row = box.row()
        row.prop(props, "src_proj_dir", text="Src Proj Dir")

        #row = box.row()
        #row.label(text="Abs Dir: " + get_abs_src_proj_dir())

        row = box.row()
        row.label(text="Current File: " + get_current_filepath())


        row = box.row()

        (isRelative, relative_path) = get_path_rel_to_dir(get_abs_src_proj_dir(), get_current_filepath())

        if isRelative:
            row.label(text="Relative Path: " + relative_path)
        else:
            row.label(text="ERROR: current file is not in Src Proj Dir")

    def draw_check_section(self, context):

        props = bpy.context.scene.XProjProps

        row = self.layout.row()
        row.label(text="Check Refs")

        box = self.layout.box()

        row = box.row()
        row.label(text="Open info window to see outputs!")

        row = box.row()
        row.operator("xutil.check_unpacked_refs", text="Check Unpacked Refs")

        row = box.row()
        row.operator("xutil.check_unpacked_libs", text="Check Unpacked Libs (blender files)")

    def draw_copy_section(self, context):

        props = bpy.context.scene.XProjProps

        row = self.layout.row()
        row.label(text="Copy")

        box = self.layout.box()

        row = box.row()
        row.prop(props, "target_proj_dir", text="Target Proj Dir")

        #row = box.row()
        #row.operator("xutil.proj_copy_check", text="Check")

        row = box.row()
        row.operator("xutil.proj_copy", text="Copy Project")

    def draw(self, context):

        self.draw_check_section(context)

        self.draw_proj_dir_section(context)

        self.draw_copy_section(context)


# 模组初始化
classes = (
    XProjProps,
    XCheckUnpackedRefsOp,
    XCheckUnpackedLibsOp,
    XProjCopyOp,
    XProjPanel,
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.XProjProps = bpy.props.PointerProperty(type=XProjProps)

def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del(bpy.types.Scene.XProjProps)