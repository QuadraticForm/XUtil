import bpy
from math import radians
from mathutils import Vector
import mathutils
import bmesh
from random import randint, seed
from bpy.types import AddonPreferences
from bpy.props import StringProperty


class XHairCvt:

    def __init__(self, context, hair, cap):
        props = bpy.context.scene.HairProps
        self.context = context
        self.hair = hair
        self.bm = None        
        self.numSegments = props.numSegments + 1
        self.hairCap = cap
        self.placeRootOnCap = props.rootOnCap     
        self.strandRadius = props.strandRadius
        self.strandsPerGuide = props.strandsPerGuide
        self.errorMessage = None
        self.corners = []


    def selectEdge(self, edge):
        self.hair.data.edges[edge.index].select = True


    def selectVert(self, vert):
        self.hair.data.vertices[vert.index].select = True
    

    def getLoopVerts(self, corner, start_loop, direction):
        count = 0
        verts = [corner]
        start_index = start_loop.edge.index
        nextVert = get_loop_end_vert(start_loop, direction)        
        l = start_loop
        while True:
            if isCornerVert(nextVert) or count > 400:
                break
            verts.append(nextVert)    
            l = get_next_loop(l, direction)
            nextVert = get_loop_end_vert(l, direction)        
            count += 1

        verts.append(nextVert)

        return verts

    
    def getCornerVertLoops(self, corner):
        # self.selectEdge(corner.link_edges[0])
        vl = corner.link_loops[0]
        e1 = corner.link_edges[0]
        e2 = corner.link_edges[1]

        # print("v=%s e1=%s e2=%s vl=%s cl_next=%s cl_prev=%s" % (corner.index, e1.index, e2.index, vl.edge.index, vl.link_loop_next.edge.index, vl.link_loop_prev.edge.index))
        
        direction = "prev" if vl.link_loop_prev.edge == e1 else "next"
        verts1 = self.getLoopVerts(corner, e1.link_loops[0], direction)

        direction = "next" if vl.edge == e2 else "prev"
        verts2 = self.getLoopVerts(corner, e2.link_loops[0], direction)

        if len(verts1) > len(verts2):
            return verts2, verts1
        else:
            return verts1, verts2


    def createStrandsFromCorner(self, corner):
        
        strands = []

        shortVerts, longVerts1 = self.getCornerVertLoops(corner)

        nextCorner = shortVerts[-1]

        tmp, longVerts2 = self.getCornerVertLoops(nextCorner)

        try:
            self.corners.remove(longVerts1[0])
            self.corners.remove(longVerts1[-1])
            self.corners.remove(longVerts2[0])
            self.corners.remove(longVerts2[-1])
        except:
            print("Corner not in list")

        if len(longVerts1) != len(longVerts2):
            return strands

        tolerance = self.scale(0.005)
        tolerance = self.scale(0.05)

        cap = self.hairCap

        v1 = (longVerts1[0].co + longVerts2[0].co) / 2
        v2 = (longVerts1[-1].co + longVerts2[-1].co) / 2

        # bpy.ops.object.empty_add(type='PLAIN_AXES',radius=.01,location=v1)
        # bpy.ops.object.empty_add(type='PLAIN_AXES',radius=.01,location=v2)

        reverse = False
        (hit, loc, norm, face_index) = cap.closest_point_on_mesh(v1)
        if hit:
            rootV = loc
            d1 = (v1 - loc).length
            (hit, loc, norm, face_index) = cap.closest_point_on_mesh(v2)            
            if hit:
                d2 = (v2 - loc).length
                if (d1 < tolerance and d2 < tolerance and v1.z <= v2.z) or d2 < d1:
                    rootV = loc 
                    reverse = True
        
        # print("Reverse=%s" % reverse)        

        if reverse:
            longVerts1.reverse()
            longVerts2.reverse()

        if not self.placeRootOnCap:
            rootV = (longVerts1[0].co + longVerts2[0].co) / 2        

        w = 0
        # calculate max width of strand
        for i in range(0, len(longVerts1)):
            w = max(w, (longVerts1[i].co - longVerts2[i].co).length)

        verts = []
        for i in range(0, len(longVerts1)):
            verts.append((longVerts1[i].co + longVerts2[i].co) / 2)
        
        strands.append({'verts' : verts, 'width': w })

        return strands


    def populateCorners(self):
        selected = [c for c in self.bm.verts if c.select]
        if len(selected) > 3:
            self.corners = [c for c in selected if isCornerVert(c)]
        else:
            self.corners = [c for c in self.bm.verts if isCornerVert(c)]


    def scale(self, value):
        return value / self.context.scene.unit_settings.scale_length


    def interpolateCurve(self, verts, numSegments):
        newCurve = []        
        length = calculate_curve_length(verts)        
        step = 1 / (numSegments - 1)
        newCurve.append(verts[0])
        t = step
        while t < 1:
            v = calc_point_at_distance(verts, length * t)
            newCurve.append(v)    
            t += step
        newCurve.append(verts[len(verts) - 1])
        return newCurve


    def convert(self):

        self.bm = bmesh.new()   # create an empty BMesh
        self.bm.from_mesh(self.hair.data)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()

        self.populateCorners()

        print("Detected card count:%s" % (len(self.corners) / 4))

        strands = []
        avgWidth = 0.0

        while len(self.corners) > 0:
            cardStrands = self.createStrandsFromCorner(self.corners[0])
            for s in cardStrands:
                avgWidth += s['width']             
                verts = s['verts']
                interp = self.interpolateCurve(verts, self.numSegments)
                strands.append(interp)

        avgWidth = avgWidth / len(strands)
        print("Main Strand Count:%s" % len(strands))

        hairName = "ParticleHair"
        
        material_slot_index = -1
        for i, ms in enumerate(self.hairCap.material_slots):
            if ms.name == hairName:
                mat = ms.material
                material_slot_index = i
                print("Found material at index %s" % material_slot_index)
                break

        if material_slot_index < 0:
            mat = createHairMaterial(hairName)
            material_slot_index = len(self.hairCap.material_slots)
            self.hairCap.data.materials.append(mat)

        # xx todo optimize this, do not gen that much strands in the first place?
        if self.strandsPerGuide > 1:
            numGuides = len(strands) / self.strandsPerGuide
            seed(1)
            while len(strands) > numGuides:
                del strands[randint(0,len(strands)-1)]

        if len(strands) == 0:
            self.errorMessage = "Conversion Failed"            
            return

        render_amount = len(strands)
            
        self.addHairParticleSystem(strands, "hair", self.strandsPerGuide, material_slot_index+1, avgWidth, avgWidth / 2.0)

        self.hair.hide_set(True)        


    def addHairParticleSystem(self, strands, name, child_count, material_slot_index, root_width, tip_width):
        psys = self.hairCap.modifiers.new(name, 'PARTICLE_SYSTEM').particle_system
        pset = psys.settings
        pset.type = 'HAIR'
        pset.use_strand_primitive = True
        pset.radius_scale = 0.1
        pset.hair_step = self.numSegments - 1
        pset.count = len(strands)
        pset.path_start = 0
        pset.path_end = 1
        pset.hair_length = self.scale(.15)
        pset.display_step = 6
        pset.render_step = 6

        pset.root_radius = self.scale(root_width)
        pset.tip_radius = self.scale(tip_width)

        pset.material = material_slot_index

        # Children
        if child_count > 0:
            pset.rendered_child_count = child_count
            pset.child_type = 'SIMPLE'
            pset.child_nbr = child_count
            pset.child_length = .95
            pset.child_length_threshold = .5
            pset.child_radius = self.scale(self.strandRadius)
            pset.child_roundness = .3

            pset.clump_factor = .8
            pset.clump_shape = .3

        bpy.ops.object.mode_set(mode='OBJECT')

        psys.use_hair_dynamics = False

        psys = updateHair(self.context, self.hairCap, psys)

        # print("Particle Count:%s" % len(psys.particles))
        for m, hair in enumerate(psys.particles):
            verts = strands[m]
            hair.location = verts[0]
            for n,v in enumerate(hair.hair_keys):
                v.co = verts[n]

        psys = updateHair(self.context, self.hairCap, psys)
        setEditProperties(self.context, self.hairCap)


def get_next_loop(start_loop, direction):
    if direction == "prev": # clockwise
        return start_loop.link_loop_prev.link_loop_radial_prev.link_loop_prev
    return start_loop.link_loop_next.link_loop_radial_next.link_loop_next


def get_loop_end_vert(lp, direction):
    if (direction == "prev"):
        return lp.vert
    return lp.edge.other_vert(lp.vert)

def isCornerVert(vert):
    return len(vert.link_edges) == 2

def updateHair(context, obj, psys):
    if bpy.app.version < (2,80,0):
        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        return psys
    else:
        dg = context.evaluated_depsgraph_get()
        return obj.evaluated_get(dg).particle_systems.active


def setEditProperties(context, obj):
    scn = context.scene
    activateObject(context, obj)
    bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
    pedit = scn.tool_settings.particle_edit
    pedit.use_emitter_deflect = False
    pedit.use_preserve_length = False
    pedit.use_preserve_root = False
    obj.data.use_mirror_x = False
    pedit.select_mode = 'POINT'
    bpy.ops.transform.translate()
    bpy.ops.object.mode_set(mode='OBJECT')


def activateObject(context, ob):
    try:
        if context.object:
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
    except RuntimeError:
        print("Could not activate", context.object)
    context.view_layer.objects.active = ob    


def calc_point_at_distance(verts, distance):
    i = 0
    v = verts[0]
    t = 0
    pt = 0
    while i < (len(verts) - 1):
        l = (verts[i+1] - verts[i]).length
        t += l
        if t >= distance and l != 0:
            v = verts[i].lerp(verts[i+1], (distance - pt) / l)
            return v
        pt = t
        i += 1
    return verts[len(verts)-1]


def calculate_curve_length(verts):
    length = 0
    for i in range(1, len(verts)):
        length += (verts[i] - verts[i-1]).length
    return length


def select_face(obj, index):
    # bpy.ops.object.mode_set(mode="EDIT")
    # bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    bm.faces[index].select = True



class NodeLayout:
    def __init__(self, tree, columns, rows):
        self.tree = tree
        self.y_offset = 500
        self.x_offset = 0
        self.rows = rows
        self.columns = columns

    def getY(self, rowIndex):
        y = self.y_offset
        i = 0
        while i < rowIndex and i < len(self.rows):
            y -= self.rows[i]
            i += 1
        return y

    def getX(self, columnIndex):
        x = self.x_offset
        i = 0
        while i < columnIndex and i < len(self.columns):
            x += self.columns[i]
            i += 1
        return x

    def addNode(self, columnIndex, rowIndex, stype):
        node = self.tree.nodes.new(type = stype)
        node.location = (self.getX(columnIndex), self.getY(rowIndex))
        return node


def createHairMaterial(hairName):
    mat = bpy.data.materials.new(hairName)
    mat.use_nodes= True
    mat.blend_method = 'HASHED'
    mat.shadow_method = 'HASHED'
    mat.node_tree.nodes.clear()
    layout = NodeLayout(mat.node_tree, [300,300,300,300], [400, 200, 200])    
    links = mat.node_tree.links

    # Cycles
    hair = layout.addNode(0, 0, 'ShaderNodeBsdfHairPrincipled')
    hair.parametrization = 'MELANIN'
    hair.inputs['Melanin'].default_value = .8
    hair.inputs['Melanin Redness'].default_value = .1
    hair.inputs['Roughness'].default_value = .2
    hair.inputs['Radial Roughness'].default_value = .3
    hair.inputs['Coat'].default_value = .55
    hair.inputs['Random Color'].default_value = .5
    
    output = layout.addNode(3, 0, 'ShaderNodeOutputMaterial')
    output.target = "CYCLES"
    links.new(hair.outputs['BSDF'], output.inputs['Surface'])    

    # Eevee
    diffuse = layout.addNode(0, 1, 'ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = [0,0,0,1]

    mix1 = layout.addNode(1, 1, 'ShaderNodeMixShader')
    mix1.inputs[0].default_value = .1 # fac
    mix2 = layout.addNode(2, 1, 'ShaderNodeMixShader')
    mix2.inputs[0].default_value = .7 # fac

    glossy = layout.addNode(0, 2, "ShaderNodeBsdfGlossy")
    glossy.inputs['Color'].default_value = [1,1,1,1]

    transparent = layout.addNode(1, 2, "ShaderNodeBsdfTransparent")

    links.new(diffuse.outputs['BSDF'], mix1.inputs[1])    
    links.new(glossy.outputs['BSDF'], mix1.inputs[2])    

    links.new(mix1.outputs[0], mix2.inputs[1])    
    links.new(transparent.outputs['BSDF'], mix2.inputs[2])    

    eevee = layout.addNode(3, 1, 'ShaderNodeOutputMaterial')
    eevee.target = "EEVEE"

    links.new(mix2.outputs['Shader'], eevee.inputs['Surface'])    

    return mat



class HairProps(bpy.types.PropertyGroup):
    numSegments: bpy.props.IntProperty(min=2, max=20, default=10, description="Number of segments per hair particle")
    rootOnCap: bpy.props.BoolProperty(default=False, description="Place the root particle keys at the nearest point on the hair cap")
    strandRadius: bpy.props.FloatProperty(min=0.001, max=.02, default=0.008, precision=4, description="Value that will be used as child particle radius. Use values between .003 and .01")
    strandsPerGuide: bpy.props.IntProperty(min=1, max=1000, default=10, description="Randomly pick guides from strands")


class ConvertHairOperator(bpy.types.Operator):
    bl_idname = "xutil.convert_hair"
    bl_label = "Convert Hair"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2 and context.active_object.mode == 'OBJECT'
        # return context.active_object is not None and context.active_object.mode == 'OBJECT'

    def execute(self, context):
        hair = context.selected_objects[0]
        cap = context.selected_objects[1]
        activateObject(context, hair)
        converter = XHairCvt(context, hair, cap)
        converter.convert()
        if converter.bm is not None:
            converter.bm.free()
        if converter.errorMessage is not None:
            self.report({'WARNING'},converter.errorMessage)
        return {'FINISHED'}        


class XHairCvtPanel(bpy.types.Panel):
    bl_label = "HairCvt"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XUtil"

    def draw(self, context):

        ctx = bpy.context

        selected_hair_name = ""
        selected_scalp_name = ""

        if len(ctx.selected_objects) > 0:
            select_hair_name = ctx.selected_objects[0].name
        
        if len(ctx.selected_objects) > 1:
            select_scalp_name = ctx.selected_objects[1].name

        row = self.layout.row()
        row.label(text="Selected Hair: " + selected_hair_name)

        row = self.layout.row()
        row.label(text="Selected Scalp: " + selected_scalp_name)

        props = bpy.context.scene.HairProps      

        row = self.layout.row()        
        row.prop(props, "numSegments", text="Segments")
        row = self.layout.row()        
        row.prop(props, "strandRadius", text="Strand radius")

        row = self.layout.row()        
        row.prop(props, "strandsPerGuide", text="Strands Per Guide")

        row = self.layout.row()
        row.operator("xutil.convert_hair", text="Convert Hair")


classes = (
    HairProps,
    ConvertHairOperator,
    XHairCvtPanel,
)


def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.HairProps = bpy.props.PointerProperty(type=HairProps)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del(bpy.types.Scene.HairProps)