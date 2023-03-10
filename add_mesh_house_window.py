# SPDX-License-Identifier: GPL-2.0-or-later

bl_info = {
    "name": "Add House Window Mesh Plugin",
    "author": "darek-r",
    "version": (0, 2, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Add House Window Object",
    "description": "Generates house window object and allows further size modification ",
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
class AddHouseWindowMesh(Operator, AddObjectHelper):
    bl_idname = "mesh.house_window"
    bl_label = "Add House Window Object"
    bl_description = "Add mesh"
    bl_options = {'REGISTER', 'UNDO'}

    # This can be useful if there will be few variants of objects
    houseWindow: BoolProperty(name="houseWindow",
                              default=True,
                              description="houseWindow")
    # Indicating change that must be applied to mesh
    change: BoolProperty(name="Change",
                         default=False,
                         description="change Plugin parameters")

    # Parameters of mesh for further adjustment
    pp_Width: FloatProperty(attr='pp_Width',
                            name='Width',
                            default=1.0,
                            min=0.001,
                            description='Width of window')

    pp_Height: FloatProperty(attr='pp_Height',
                             name='Height',
                             default=1.0,
                             min=0.001,
                             description='Height of window')

    pp_Depth: FloatProperty(attr='pp_Depth',
                            name='Depth',
                            default=0.1,
                            min=0.001,
                            description='Depth of window')

    pp_FrameWidth: FloatProperty(attr='pp_FrameWidth',
                                 name='Frame Width',
                                 default=0.1,
                                 min=0.0001,
                                 description='Frame width (FrameWidth * 2 < Width)')

    # Add face without duplicates
    @staticmethod
    def add_face(vertices, faces, vectors):

        # True until we find proof it isn't
        face_exists = True

        # List of face vertices
        v_index = []

        # Check vertices table for already existing vectors, if not add new one
        for v in vectors:
            try:
                v_index_temp = vertices.index(v)
                v_index.append(v_index_temp)
            except ValueError:
                vertices.append(v)
                v_index.append(len(vertices)-1)
                face_exists = False     # Vertex doesn't exist so face either

        # Check faces array for duplicate
        if face_exists:
            new_face = v_index.copy()
            new_face.sort()
            for f in faces:
                old_face = f.copy()
                old_face.sort()
                if old_face == new_face:
                    return "DUPLICATE"

        faces.append(v_index)
        return "SUCCESS"

    def generate_window_model(self):
        vertices = []
        faces = []

        # Frame width should be two times smaller than window width
        if self.pp_FrameWidth * 2 > self.pp_Width:
            self.pp_FrameWidth = self.pp_Width / 2 - 0.0001

        if self.pp_FrameWidth * 2 > self.pp_Height:
            self.pp_FrameWidth = self.pp_Height / 2 - 0.0001

        # Simple window
        # Front
        self.add_face(vertices, faces, [Vector((0, 0, 0)),
                                        Vector((self.pp_Width, 0, 0)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, 0, self.pp_FrameWidth)),
                                        Vector((self.pp_FrameWidth, 0, self.pp_FrameWidth))])
        self.add_face(vertices, faces,
                      [Vector((0, 0, self.pp_Height)),
                       Vector((self.pp_Width, 0, self.pp_Height)),
                       Vector((self.pp_Width - self.pp_FrameWidth, 0, self.pp_Height - self.pp_FrameWidth)),
                       Vector((self.pp_FrameWidth, 0, self.pp_Height - self.pp_FrameWidth))])
        self.add_face(vertices, faces,
                      [Vector((0, 0, 0)),
                       Vector((self.pp_FrameWidth, 0, self.pp_FrameWidth)),
                       Vector((self.pp_FrameWidth, 0, self.pp_Height - self.pp_FrameWidth)),
                       Vector((0, 0, self.pp_Height))])
        self.add_face(vertices, faces,
                      [Vector((self.pp_Width - self.pp_FrameWidth, 0, self.pp_FrameWidth)),
                       Vector((self.pp_Width, 0, 0)),
                       Vector((self.pp_Width, 0, self.pp_Height)),
                       Vector((self.pp_Width - self.pp_FrameWidth, 0, self.pp_Height - self.pp_FrameWidth))])

        # Back
        self.add_face(vertices, faces, [Vector((0, self.pp_Depth, 0)),
                                        Vector((self.pp_Width, self.pp_Depth, 0)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, self.pp_Depth, self.pp_FrameWidth)),
                                        Vector((self.pp_FrameWidth, self.pp_Depth, self.pp_FrameWidth))])
        self.add_face(vertices, faces,
                      [Vector((0, self.pp_Depth, self.pp_Height)),
                       Vector((self.pp_Width, self.pp_Depth, self.pp_Height)),
                       Vector((self.pp_Width - self.pp_FrameWidth, self.pp_Depth, self.pp_Height - self.pp_FrameWidth)),
                       Vector((self.pp_FrameWidth, self.pp_Depth, self.pp_Height - self.pp_FrameWidth))])
        self.add_face(vertices, faces,
                      [Vector((0, self.pp_Depth, 0)),
                       Vector((self.pp_FrameWidth, self.pp_Depth, self.pp_FrameWidth)),
                       Vector((self.pp_FrameWidth, self.pp_Depth, self.pp_Height - self.pp_FrameWidth)),
                       Vector((0, self.pp_Depth, self.pp_Height))])
        self.add_face(vertices, faces,
                      [Vector((self.pp_Width - self.pp_FrameWidth, self.pp_Depth, self.pp_FrameWidth)),
                       Vector((self.pp_Width, self.pp_Depth, 0)),
                       Vector((self.pp_Width, self.pp_Depth, self.pp_Height)),
                       Vector((self.pp_Width - self.pp_FrameWidth,
                               self.pp_Depth, self.pp_Height - self.pp_FrameWidth))])

        # Depth fill
        self.add_face(vertices, faces, [Vector((0, self.pp_Depth, 0)),
                                        Vector((0, 0, 0)),
                                        Vector((0, 0, self.pp_Height)),
                                        Vector((0, self.pp_Depth, self.pp_Height))])
        self.add_face(vertices, faces, [Vector((0, self.pp_Depth, 0)),
                                        Vector((0, 0, 0)),
                                        Vector((self.pp_Width, 0, 0)),
                                        Vector((self.pp_Width, self.pp_Depth, 0))])
        self.add_face(vertices, faces, [Vector((self.pp_Width, self.pp_Depth, 0)),
                                        Vector((self.pp_Width, 0, 0)),
                                        Vector((self.pp_Width, 0, self.pp_Height)),
                                        Vector((self.pp_Width, self.pp_Depth, self.pp_Height))])
        self.add_face(vertices, faces, [Vector((0, self.pp_Depth, self.pp_Height)),
                                        Vector((0, 0, self.pp_Height)),
                                        Vector((self.pp_Width, 0, self.pp_Height)),
                                        Vector((self.pp_Width, self.pp_Depth, self.pp_Height))])

        self.add_face(vertices, faces, [Vector((self.pp_FrameWidth, self.pp_Depth, self.pp_FrameWidth)),
                                        Vector((self.pp_FrameWidth, 0, self.pp_FrameWidth)),
                                        Vector((self.pp_FrameWidth, 0, self.pp_Height - self.pp_FrameWidth)),
                                        Vector((self.pp_FrameWidth, self.pp_Depth,
                                                self.pp_Height - self.pp_FrameWidth))])
        self.add_face(vertices, faces, [Vector((self.pp_FrameWidth, self.pp_Depth,
                                                self.pp_FrameWidth)),
                                        Vector((self.pp_FrameWidth, 0,
                                                self.pp_FrameWidth)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, 0,
                                                self.pp_FrameWidth)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, self.pp_Depth,
                                                self.pp_FrameWidth))])
        self.add_face(vertices, faces, [Vector((self.pp_Width - self.pp_FrameWidth, self.pp_Depth,
                                                self.pp_FrameWidth)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, 0,
                                                self.pp_FrameWidth)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, 0,
                                                self.pp_Height - self.pp_FrameWidth)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, self.pp_Depth,
                                                self.pp_Height - self.pp_FrameWidth))])
        self.add_face(vertices, faces, [Vector((self.pp_FrameWidth, self.pp_Depth,
                                                self.pp_Height - self.pp_FrameWidth)),
                                        Vector((self.pp_FrameWidth, 0,
                                                self.pp_Height - self.pp_FrameWidth)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, 0,
                                                self.pp_Height - self.pp_FrameWidth)),
                                        Vector((self.pp_Width - self.pp_FrameWidth, self.pp_Depth,
                                                self.pp_Height - self.pp_FrameWidth))])

        # print("\nVertices:\n", vertices)
        # print("\nFaces:\n", faces)

        return vertices, [], faces

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, 'pp_Width')
        col.separator()
        col.prop(self, 'pp_Height')
        col.separator()
        col.prop(self, 'pp_Depth')
        col.separator()
        col.prop(self, 'pp_FrameWidth')
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
                    and ('houseWindow' in context.active_object.data.keys()) \
                    and self.change:

                obj = context.active_object

                # This will COPY and preserve smooth choices
                use_auto_smooth = bool(obj.data.use_auto_smooth)
                use_smooth = bool(obj.data.polygons[0].use_smooth)

                mesh = bpy.data.meshes.new(name='House Window')
                vertices, edges, faces = self.generate_window_model()
                mesh.from_pydata(vertices, edges, faces)

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
                mesh = bpy.data.meshes.new(name='House Window')
                vertices, edges, faces = self.generate_window_model()
                mesh.from_pydata(vertices, edges, faces)
                # mesh.validate()
                obj = object_utils.object_data_add(context, mesh, operator=self)

            obj.data["houseWindow"] = True
            obj.data["change"] = False
            for prm in hw_plugin_parameters():
                obj.data[prm] = getattr(self, prm)

        if bpy.context.mode == "EDIT_MESH":
            obj = context.edit_object

            mesh = bpy.data.meshes.new(name='House Window')
            vertices, edges, faces = self.generate_window_model()
            mesh.from_pydata(vertices, edges, faces)

            bm = bmesh.from_edit_mesh(obj.data)  # Access edit mode's mesh data
            bm.from_mesh(mesh)  # Append new mesh data
            bmesh.update_edit_mesh(obj.data)  # Flush changes (update edit mode's view)

            bpy.data.meshes.remove(mesh)  # Remove temporary mesh

        return {'FINISHED'}


# Register section:
def house_window_context_menu(self, context):
    bl_label = 'Edit House Window Object'

    obj = context.object
    layout = self.layout

    if obj.data is not None and 'houseWindow' in obj.data.keys():
        props = layout.operator("mesh.house_window", text="Change House Window Parameters")
        props.change = True
        for prm in hw_plugin_parameters():
            setattr(props, prm, obj.data[prm])
        layout.separator()


def house_window_main_func(self, context):
    layout = self.layout
    layout.separator()
    op = self.layout.operator(AddHouseWindowMesh.bl_idname, text="Add House Window Object", icon="MOD_LATTICE")
    op.change = False


classes = (
    AddHouseWindowMesh,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_mesh_add.append(house_window_main_func)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(house_window_context_menu)


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(house_window_context_menu)
    bpy.types.VIEW3D_MT_mesh_add.remove(house_window_main_func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def hw_plugin_parameters():
    pl_params = [
        "pp_Width",
        "pp_Height",
        "pp_Depth",
        "pp_FrameWidth"
    ]
    return pl_params


if __name__ == "__main__":
    register()
