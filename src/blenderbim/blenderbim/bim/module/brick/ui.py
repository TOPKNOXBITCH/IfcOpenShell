# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import blenderbim.tool as tool
from bpy.types import Panel, UIList
from blenderbim.bim.helper import prop_with_search
from blenderbim.bim.module.brick.data import BrickschemaData, BrickschemaReferencesData
from blenderbim.tool.brick import BrickStore


class BIM_PT_brickschema(Panel):
    bl_label = "Brickschema Project"
    bl_idname = "BIM_PT_brickschema"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_operations"

    def draw(self, context):
        if not BrickschemaData.is_loaded:
            BrickschemaData.load()
        self.props = context.scene.BIMBrickProperties

        if not BrickschemaData.data["is_loaded"]:
            row = self.layout.row(align=True)
            row.operator("bim.new_brick_file", text="Create Project")
            row.operator("bim.load_brick_project", text="Load Project")
            return

        row = self.layout.row(align=True)
        if BrickStore.path:
            row.label(text=BrickStore.path, icon="FILEBROWSER")
        else:
            row.label(text="No file", icon="FILEBROWSER")
        
        row = self.layout.row(align=True)
        if BrickStore.last_saved:
            row.label(text=BrickStore.last_saved, icon="TIME")
        else:
            row.label(text="Not saved", icon="TIME")

        row = self.layout.row(align=True)
        op = row.operator("bim.serialize_brick", icon="EXPORT", text="Save")
        op.should_save_as = False
        op = row.operator("bim.serialize_brick", icon="FILE_TICK", text="Save As")
        op.should_save_as = True
        row.operator("bim.close_brick_project", text="", icon="CANCEL")

        row = self.layout.row(align=True)
        row.prop(data=self.props, property="brick_settings_toggled", text="", icon="PREFERENCES")

        if self.props.brick_settings_toggled:
            box = self.layout.box()
            row = box.row(align=True)
            row.label(text="Active Namespace:")

            row = box.row(align=True)
            prop_with_search(row, self.props, "namespace", text="")

            row = box.row(align=True)
            row.label(text="Bind New Namespace:")

            row = box.row(align=True)
            row.prop(data=self.props, property="new_brick_namespace_alias", text="")
            col = row.column()
            col.alignment = "CENTER"
            col.scale_x = 1.1
            col.label(text=":")
            row.prop(data=self.props, property="new_brick_namespace_uri", text="")
            row.operator("bim.add_brick_namespace", text="", icon="ADD")

        row = self.layout.row(align=True)
        row.label(text="Create Entity:")

        row = self.layout.row(align=True)
        row.prop(data=self.props, property="brick_entity_create_type", text="")

        # hide this if selected entity already has a reference
        row = self.layout.row(align=True)
        active = tool.Ifc.get_entity(context.active_object)
        if active and context.selected_objects:
            row.label(text=active.Name if active.Name else "Unnamed")
        else:
            row.prop(data=self.props, property="new_brick_label", text="")
        prop_with_search(row, self.props, "brick_entity_class", text="")
        row.operator("bim.add_brick", text="", icon="ADD")

        row = self.layout.row(align=True)
        col = row.column()
        col.alignment = "RIGHT"
        row.prop(data=self.props, property="set_list_root_toggled", text="", icon="OUTLINER")
        row.prop(data=self.props, property="split_screen_toggled", text="", icon="WINDOW")
        row.operator("bim.refresh_brick_viewer", text="", icon="FILE_REFRESH")

        grid = self.layout.grid_flow(even_columns=True)
        grid_left = grid.column(align=True)
        row = grid_left.row(align=True)
        if len(self.props.brick_breadcrumbs):
            op = row.operator("bim.rewind_brick_class", text="", icon="FRAME_PREV")
            op.split_screen = False
        row.label(text=self.props.active_brick_class)

        if self.props.set_list_root_toggled:
            row = grid_left.row(align=True)
            row.prop(data=self.props, property="brick_list_root", text="")

        row = grid_left.row()
        BIM_UL_bricks.split_screen = False
        row.template_list("BIM_UL_bricks", "", self.props, "bricks", self.props, "active_brick_index")

        if self.props.split_screen_toggled:
            grid_right = grid.column(align=True)
            row = grid_right.row(align=True)
            if len(self.props.split_screen_brick_breadcrumbs):
                op = row.operator("bim.rewind_brick_class", text="", icon="FRAME_PREV")
                op.split_screen = True
            row.label(text=self.props.split_screen_active_brick_class)

            if self.props.set_list_root_toggled:
                row = grid_right.row(align=True)
                row.prop(data=self.props, property="split_screen_brick_list_root", text="")

            row = grid_right.row()
            BIM_UL_bricks.split_screen = True
            row.template_list("BIM_UL_bricks", "", self.props, "split_screen_bricks", self.props, "split_screen_active_brick_index")

        if BrickschemaData.data["active_relations"]:
            row = self.layout.row(align=True)
            col = row.column()
            col.alignment = "RIGHT"
            row.prop(data=self.props, property="brick_create_relations_toggled", text="", icon="PLUGIN")
            row.prop(data=self.props, property="brick_edit_relations_toggled", text="", icon="TOOL_SETTINGS")
            row.operator("bim.remove_brick", text="", icon="X")

            if self.props.brick_create_relations_toggled:
                row = self.layout.row(align=True)
                row.label(text="Create Relation:")

            if self.props.brick_create_relations_toggled and self.props.new_brick_relation_type == "http://www.w3.org/2000/01/rdf-schema#label":
                row = self.layout.row(align=True)
                prop_with_search(row, self.props, "new_brick_relation_type", text="")
                row.prop(data=self.props, property="new_brick_relation_object", text="")
                row.operator("bim.add_brick_relation", text="", icon="ADD")

            elif self.props.brick_create_relations_toggled and self.props.split_screen_toggled:
                row = self.layout.row(align=True)
                split_screen_selection = self.props.split_screen_bricks[self.props.split_screen_active_brick_index]
                if split_screen_selection.total_items:
                    row.label(text="No selection", icon="INFO")
                else:
                    prop_with_search(row, self.props, "new_brick_relation_type", text="")
                    row.label(text=split_screen_selection.label if split_screen_selection.label else split_screen_selection.name)
                    row.operator("bim.add_brick_relation", text="", icon="ADD")

            elif self.props.brick_create_relations_toggled: 
                row = self.layout.row(align=True)
                prop_with_search(row, self.props, "new_brick_relation_namespace", text="")

                row = self.layout.row(align=True)
                prop_with_search(row, self.props, "new_brick_relation_type", text="")
                row.prop(data=self.props, property="new_brick_relation_object", text="")
                row.operator("bim.add_brick_relation", text="", icon="ADD")

            if self.props.brick_create_relations_toggled and self.props.add_relation_failed:
                row = self.layout.row(align=True)
                row.label(text="Failed to find this entity!", icon="ERROR")

        for relation in BrickschemaData.data["active_relations"]:
            row = self.layout.row(align=True)
            row.label(text=relation["predicate_name"])
            row.label(text=relation["object_name"])
            if self.props.brick_edit_relations_toggled and relation["predicate_name"] != "type":
                op = row.operator("bim.remove_brick_relation", text="", icon="UNLINKED")
                op.predicate = relation["predicate"]
                op.object = relation["object"]
            if relation["is_uri"] and relation["object_name"] != self.props.active_brick_class:
                op = row.operator("bim.view_brick_item", text="", icon="DISCLOSURE_TRI_RIGHT")
                op.item = relation["object_uri"]
            if relation["is_globalid"]:
                op = row.operator("bim.select_global_id", icon="RESTRICT_SELECT_OFF", text="")
                op.global_id = relation["object_name"]


class BIM_PT_ifc_brickschema_references(Panel):
    bl_label = "Brickschema References"
    bl_idname = "BIM_PT_ifc_brickschema_references"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_brickschema"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not BrickschemaReferencesData.is_loaded:
            BrickschemaReferencesData.load()
        self.props = context.scene.BIMBrickProperties

        if not BrickschemaReferencesData.data["is_loaded"]:
            row = self.layout.row()
            row.label(text="No Brickschema Project Loaded")
            return

        if not BrickschemaReferencesData.data["libraries"]:
            row = self.layout.row(align=True)
            if BrickStore.path:
                row.label(text="No IFC Libraries")
                row.operator("bim.convert_brick_project", text="", icon="ADD")
            else:
                row.label(text="No IFC Libraries. Save the Brick project to create a new library.", icon="ERROR")
            return

        row = self.layout.row(align=True)
        prop_with_search(row, self.props, "libraries")
        row.operator("bim.convert_brick_project", text="", icon="ADD")

        row = self.layout.row(align=True)
        row.operator("bim.assign_brick_reference", icon="ADD")
        row.operator("bim.convert_ifc_to_brick", icon="IMPORT")

        if not BrickschemaReferencesData.data["references"]:
            row = self.layout.row()
            row.label(text="No References")

        for reference in BrickschemaReferencesData.data["references"]:
            row = self.layout.row(align=True)
            row.label(text=reference["identification"], icon="ASSET_MANAGER")
            row.label(text=reference["name"])
            row.operator("bim.unassign_library_reference", text="", icon="X").reference = reference["id"]
            row.operator("bim.view_brick_item", text="", icon="DISCLOSURE_TRI_RIGHT").item = reference["identification"]


class BIM_UL_bricks(UIList):
    split_screen = False

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            label = item.label if item.label else item.name
            if item.total_items:
                op = row.operator("bim.view_brick_class", text="", icon="DISCLOSURE_TRI_RIGHT", emboss=False)
                op.brick_class = item.name
                op.split_screen = self.split_screen
                label = label + " (" + str(item.total_items) + ")" 
            row.label(text=label)
