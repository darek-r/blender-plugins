# SPDX-License-Identifier: GPL-2.0-or-later

bl_info = {
    "name": "Blender Add Mesh Plugin",
    "author": "darek-r",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Blender Add Mesh Plugin",
    "description": "If you want to use this plugin modify it for your own purpose ",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import (
    FloatProperty,
    PointerProperty,
    BoolProperty,
)
from bpy_extras import object_utils
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper

# Based on BoltFactory Plugin by Aaron Keith
class BlenderMeshAdd(Operator, AddObjectHelper):
    bl_idname = "mesh.bl_mesh_add"
    bl_label = "Blender Add Mesh Plugin"
    bl_description = "Add mesh"
    bl_options = {'REGISTER', 'UNDO'}

    # This can be useful if there will be few variants of objects
    blenderMeshPlugin: BoolProperty(name="blenderMeshPlugin",
                                    default=True,
                                    description="blenderMeshPlugin")
    # Indicating change that must be applied to mesh
    change: BoolProperty(name="Change",
                         default=False,
                         description="change Plugin parameters")

    # Parameters of mesh for further adjustment
    pp_Value1: FloatProperty(attr='pp_Value1',
                             name='Value 1',
                             default=1.0,
                             description='Set the Value 1')

    pp_Value2: FloatProperty(attr='pp_Value2',
                             name='Value 2',
                             default=1.0,
                             description='Set the Value 2')

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, 'pp_Value1')
        col.separator()
        col.prop(self, 'pp_Value2')
        col.separator()

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):

        if bpy.context.mode == "OBJECT":
            if context.selected_objects != [] and context.active_object and \
                    (context.active_object.data is not None) \
                    and ('blenderMeshPlugin' in context.active_object.data.keys()) \
                    and self.change:

                obj = context.active_object

                # This will COPY and preserve smooth choices
                use_auto_smooth = bool(obj.data.use_auto_smooth)
                use_smooth = bool(obj.data.polygons[0].use_smooth)

                # This is simply square with pp_Value1 property
                verts = [Vector((self.pp_Value1, 0, 0)),
                         Vector((1, 0, 0)),
                         Vector((1, 1, 0)),
                         Vector((0, 1, 0))
                    ]
                faces = [[0, 1, 2, 3]]
                edges = []

                mesh = bpy.data.meshes.new(name='Mesh from Blender Plugin')
                mesh.from_pydata(verts, edges, faces)

                # Modify existing mesh data object by replacing geometry (but leaving materials etc)
                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.to_mesh(obj.data)
                bm.free()

                # Preserve flat/smooth choice. New mesh is flat by default
                obj.data.use_auto_smooth = use_auto_smooth
                if use_smooth:
                    bpy.ops.object.shade_smooth()

                bpy.data.meshes.remove(mesh)

                try:
                    bpy.ops.object.vertex_group_remove(all=True)
                except:
                    pass

            else:
                # This is simply square with second pp_Value2 property
                # Finally all mesh code should look the same (above and below)
                verts = [Vector((0, self.pp_Value2, 0)),
                         Vector((1, 0, 0)),
                         Vector((1, 1, 0)),
                         Vector((0, 1, 0))
                         ]
                faces = [[0, 1, 2, 3]]
                edges = []

                mesh = bpy.data.meshes.new(name='Mesh from Blender Plugin')
                mesh.from_pydata(verts, edges, faces)
                # mesh.validate(verbose=True)

                obj = object_utils.object_data_add(context, mesh, operator=self)

            obj.data["blenderMeshPlugin"] = True
            obj.data["change"] = False
            for prm in plugin_parameters():
                obj.data[prm] = getattr(self, prm)

        if bpy.context.mode == "EDIT_MESH":
            obj = context.edit_object

            # Changes in EDIT MODE produce a different result (intended)
            verts = [Vector((0, 0, 0)),
                     Vector((self.pp_Value2, 0, 0)),
                     Vector((1, 1, 0)),
                     Vector((0, 1, 0))
                     ]
            faces = [[0, 1, 2, 3]]
            edges = []

            mesh = bpy.data.meshes.new(name='Mesh from Blender Plugin')
            mesh.from_pydata(verts, edges, faces)

            bm = bmesh.from_edit_mesh(obj.data)  # Access edit mode's mesh data
            bm.from_mesh(mesh)  # Append new mesh data
            bmesh.update_edit_mesh(obj.data)  # Flush changes (update edit mode's view)

            bpy.data.meshes.remove(mesh)  # Remove temporary mesh

        return {'FINISHED'}


# Register section:
def pl_contex_menu(self, context):
    bl_label = 'Blender Add Mesh Plugin'

    obj = context.object
    layout = self.layout

    if obj.data is not None and 'blenderMeshPlugin' in obj.data.keys():
        props = layout.operator("mesh.bl_mesh_add", text="Change Plugin Parameters")
        props.change = True
        for prm in plugin_parameters():
            setattr(props, prm, obj.data[prm])
        layout.separator()


def pl_main_func(self, context):
    layout = self.layout
    layout.separator()
    op = self.layout.operator(BlenderMeshAdd.bl_idname, text="Blender Add Mesh", icon="MOD_SCREW")
    op.change = False


classes = (
    BlenderMeshAdd,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_mesh_add.append(pl_main_func)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(pl_contex_menu)


def unregister():

    bpy.types.VIEW3D_MT_object_context_menu.remove(pl_contex_menu)
    bpy.types.VIEW3D_MT_mesh_add.remove(pl_main_func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def plugin_parameters():
    pl_params = [
                "pp_Value1",
                "pp_Value2",
        ]
    return pl_params


if __name__ == "__main__":
    register()
