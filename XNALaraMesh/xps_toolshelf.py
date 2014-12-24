# -*- coding: utf-8 -*-

import bpy
from XNALaraMesh import import_xnalara_model

from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty

class XPSToolsObjectPanel(bpy.types.Panel):
    '''XPS Toolshelf'''
    bl_idname = 'OBJECT_PT_xps_tools_object'
    bl_label = 'XPS Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'XPS'
    bl_context = 'objectmode'

    def draw(self, context):
        #active_obj = context.active_object
        mesh_obj = next((obj for obj in context.selected_objects if obj.type == 'MESH'), None)
        armature_obj = next((obj for obj in context.selected_objects if obj.type == 'ARMATURE'), None)

        layout = self.layout
        col = layout.column()

        col.label('Import:')
        #c = col.column()
        r = col.row(align=True)
        r1c1=r.column(align=True)
        r1c1.operator("xps_tools.import_model", text='Model', icon='NONE')
        r1c2=r.column(align=True)
        r1c2.operator('xps_tools.import_pose', text='Pose')
        if armature_obj is not None:
            r1c2.enabled = True
        else:
            r1c2.enabled = False

        #col.separator()
        col = layout.column()

        col.label(text="Export:")
        c = col.column()
        r = c.row(align=True)
        r2c1=r.column(align=True)
        r2c1.operator('xps_tools.export_model', text='Model')
        if mesh_obj is not None:
            r2c1.enabled = True
        else:
            r2c1.enabled = False
        
        r2c2=r.column(align=True)
        r2c2.operator('xps_tools.export_pose', text='Pose')
        if armature_obj is not None:
            r2c2.enabled = True
        else:
            r2c2.enabled = False

        #col.separator()
        col = layout.column()

        col.label('Hide Bones:')
        c = col.column(align=True)
        r = c.row(align=True)
        r.operator('xps_tools.bones_hide_by_name', text='Unused')
        r.operator('xps_tools.bones_hide_by_vertex_group', text='Vertex Group')
        r = c.row(align=True)
        #r.operator('xps_tools.set_cycles_rendering', text='Cycles')
        r.operator('xps_tools.bones_show_all', text='Show All')

        #col.separator()
        col = layout.column()

        col.label('View:')
        c = col.column(align=True)
        r = c.row(align=True)
        r.operator('xps_tools.set_glsl_shading', text='GLSL')
        r.operator('xps_tools.set_shadeless_glsl_shading', text='Shadeless')
        r = c.row(align=True)
        #r.operator('xps_tools.set_cycles_rendering', text='Cycles')
        r.operator('xps_tools.reset_shading', text='Reset')



class SetGLSLShading_Op(bpy.types.Operator):
    '''GLSL Shading Display'''
    bl_idname = 'xps_tools.set_glsl_shading'
    bl_label = 'GLSL View'
    bl_description = 'Change Display to GLSL'
    bl_options = {'PRESET'}

    def execute(self, context):
        bpy.ops.xps_tools.reset_shading()
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        for mesh_ob in filter(lambda obj: obj.type == 'MESH', context.scene.objects):
            for mat_slot in mesh_ob.material_slots:
                if mat_slot.material:
                    mat_slot.material.use_shadeless = False

        context.area.spaces[0].viewport_shade='TEXTURED'
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        return {'FINISHED'}

class SetShadelessGLSLShading_Op(bpy.types.Operator):
    bl_idname = 'xps_tools.set_shadeless_glsl_shading'
    bl_label = 'Shadeless GLSL View'
    bl_description = 'Set Materials to Shadeless'
    bl_options = {'PRESET'}

    def execute(self, context):
        bpy.ops.xps_tools.reset_shading()
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        for mesh_ob in filter(lambda obj: obj.type == 'MESH', context.scene.objects):
            for mat_slot in mesh_ob.material_slots:
                if mat_slot.material:
                    mat_slot.material.use_shadeless = True

        try:
            bpy.context.scene.display_settings.display_device = 'None'
        except TypeError:
            pass # Blender was built without OpenColorIO
        context.area.spaces[0].viewport_shade='TEXTURED'
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        return {'FINISHED'}

class SetCyclesRendering_Op(bpy.types.Operator):
    bl_idname = 'xps_tools.set_cycles_rendering'
    bl_label = 'Cycles'
    bl_description = 'Convert blender render shader to Cycles shader'
    bl_options = {'PRESET'}

    def execute(self, context):
        bpy.ops.xps_tools.reset_shading()
        bpy.context.scene.render.engine = 'CYCLES'
        for mesh_ob in filter(lambda obj: obj.type == 'MESH', context.scene.objects):
            cycles_converter.convertToCyclesShader(mesh_ob)
        context.area.spaces[0].viewport_shade='MATERIAL'
        return {'FINISHED'}

class ResetShading_Op(bpy.types.Operator):
    bl_idname = 'xps_tools.reset_shading'
    bl_label = 'Reset View'
    bl_description = ''
    bl_options = {'PRESET'}

    def execute(self, context):
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        for mesh_ob in filter(lambda obj: obj.type == 'MESH', context.scene.objects):
            for mat_slot in mesh_ob.material_slots:
                if mat_slot.material:
                    mat_slot.material.use_shadeless = False
                    mat_slot.material.use_nodes = False

        bpy.context.scene.display_settings.display_device = 'sRGB'
        context.area.spaces[0].viewport_shade='SOLID'
        bpy.context.scene.game_settings.material_mode = 'MULTITEXTURE'
        return {'FINISHED'}

class SetShadelessMaterials_Op(bpy.types.Operator):
    bl_idname = 'xps_tools.set_shadeless_materials'
    bl_label = 'GLSL View'
    bl_description = 'set the materials of selected objects to shadeless.'
    bl_options = {'PRESET'}

    def execute(self, context):
        for obj in context.selected_objects:
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    mat_slot.material.use_shadeless = True
        return {'FINISHED'}

class ArmatureBonesHideByName_Op(bpy.types.Operator):
    bl_idname = 'xps_tools.bones_hide_by_name'
    bl_label = 'Hide bones by name'
    bl_description = 'Move bones starting with "unused" to the armature layer 2'
    bl_options = {'PRESET'}

    def execute(self, context):
        meshes_obs = filter(lambda obj: obj.type == 'MESH', context.scene.objects)
        import_xnalara_model.hideBonesByName(meshes_obs)
        return {'FINISHED'}

class ArmatureBonesHideByVertexGroup_Op(bpy.types.Operator):
    bl_idname = 'xps_tools.bones_hide_by_vertex_group'
    bl_label = 'Hide bones by weight'
    bl_description = 'Move bones that do not alter any mesh to the armature layer 2'
    bl_options = {'PRESET'}

    def execute(self, context):
        meshes_obs = filter(lambda obj: obj.type == 'MESH', context.scene.objects)
        import_xnalara_model.hideBonesByVertexGroup(meshes_obs)
        return {'FINISHED'}

class ArmatureBonesShowAll_Op(bpy.types.Operator):
    bl_idname = 'xps_tools.bones_show_all'
    bl_label = 'Show all Bones'
    bl_description = 'Move all bones to the armature layer 1'
    bl_options = {'PRESET'}

    def execute(self, context):
        meshes_obs = filter(lambda obj: obj.type == 'MESH', context.scene.objects)
        import_xnalara_model.showAllBones(meshes_obs)
        return {'FINISHED'}

#
# Registration
#
def register():
    bpy.utils.register_class(XPSToolsObjectPanel)
    bpy.utils.register_class(SetGLSLShading_Op)
    bpy.utils.register_class(SetShadelessGLSLShading_Op)
    bpy.utils.register_class(SetCyclesRendering_Op)
    bpy.utils.register_class(ResetShading_Op)
    bpy.utils.register_class(SetShadelessMaterials_Op)
    bpy.utils.register_class(ArmatureBonesHideByName_Op)
    bpy.utils.register_class(ArmatureBonesHideByVertexGroup_Op)
    bpy.utils.register_class(ArmatureBonesShowAll_Op)
   

def unregister():

    bpy.utils.unregister_class(XPSToolsObjectPanel)
    bpy.utils.unregister_class(SetGLSLShading_Op)
    bpy.utils.unregister_class(SetShadelessGLSLShading_Op)
    bpy.utils.unregister_class(SetCyclesRendering_Op)
    bpy.utils.unregister_class(ResetShading_Op)
    bpy.utils.unregister_class(SetShadelessMaterials_Op)
    bpy.utils.unregister_class(ArmatureBonesHideByName_Op)
    bpy.utils.unregister_class(ArmatureBonesHideByVertexGroup_Op)
    bpy.utils.unregister_class(ArmatureBonesShowAll_Op)


if __name__ == "__main__":
    register()

