import bpy
from distutils import dist
import math
import copy

def get_active_hair() -> bpy.types.ParticleSystem:
    # get the depsgraph and the evaluated object   
    deps_graph = bpy.context.evaluated_depsgraph_get()
    evaluated_object = bpy.context.object.evaluated_get(deps_graph)
    # assume context object has a particle system (warning, no check), use active
    return evaluated_object.particle_systems.active

def mirror_hair():
    particle_system = get_active_hair()

    # Variable to hold hair-verticies-coordinats
    hairs = []

    # At current frame
    # For each particle (hair)
    #   For each vertex
    #     Store XYZ coordinates
    for p in particle_system.particles:
        hair = []
        for v in p.hair_keys:
            hair.append([v.co[0], v.co[1], v.co[2]])
        if (hair[0][0] > 0):
            hairs.append(hair)

    def calc_pn_dist(v1, v2) -> float:
        sum = 0
        for i in range(0, 3):
            if i == 0:
                sum += math.pow(-v1[i] - v2[i], 2)
            else:
                sum += math.pow(v1[i] - v2[i], 2)
        return math.sqrt(sum)

    # for each positive hair
    for positive_h in hairs:
        min_dist = 10000
        min_h = None

        # find the closest negative hair
        for cur_h in particle_system.particles:
            if cur_h.hair_keys[0].co[0] < 0:
                negative_pos = cur_h.hair_keys[0].co
                cur_dist = calc_pn_dist(positive_h[0], cur_h.hair_keys[0].co)    
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    min_h = cur_h
        
        # snap
        if min_h != None:
            for pk, nk in zip(positive_h, min_h.hair_keys):
                nk.co[0] = -pk[0]
                nk.co[1] = pk[1]
                nk.co[2] = pk[2]

    # Update view and UI
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)

def hair_auto_weight():

    particle_system = get_active_hair()

    print("setting weight for hairs in system: " + particle_system.name)

    # For each visible hair
    #   For each vertex
    #     Overwrite XYZ coordinates
    for hair in particle_system.particles:
        numKeys = len(hair.hair_keys)
        for i in range(0, numKeys):
            v = hair.hair_keys[i]

            v.weight = 1 - i / float(numKeys - 1)

    # Update view and UI
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)

# 按钮
class x_mirror_hair_op(bpy.types.Operator):
    bl_idname = "xutil.x_mirror_hair_op"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):

        mirror_hair()

        return {'FINISHED'}  

# 按钮
class x_hair_auto_weight_op(bpy.types.Operator):
    bl_idname = "xutil.x_hair_auto_weight_op"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):

        hair_auto_weight()   

        return {'FINISHED'}  

# 面板
class x_hair_panel(bpy.types.Panel):
    bl_label = "Hair"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):

        row = self.layout.row()
        row.operator("xutil.x_mirror_hair_op", text="X Mirror Hair")

        row = self.layout.row()
        row.operator("xutil.x_hair_auto_weight_op", text="Hair Auto Weight")

# 模组初始化
classes = (
    x_mirror_hair_op,
    x_hair_auto_weight_op,
    x_hair_panel,
)

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)
    #bpy.types.Scene.HairProps = bpy.props.PointerProperty(type=HairProps)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    #del(bpy.types.Scene.HairProps)