"""Material creation for USD output."""

from __future__ import annotations

from dataclasses import dataclass

from ..maze_materials.color import ColorResolver, MaterialMap
from ..maze_materials.source import MaterialSource
from ..maze_materials.usd_nodes import (
    create_preview_material,
    create_texture_material,
    reference_usd_material,
)
from .mesh_primitives import sanitize_prim_name


@dataclass(frozen=True, slots=True)
class MaterialLibrary:
    material_map: MaterialMap | None
    material_source: MaterialSource | None

    def create(self, stage, element_names: tuple[str, ...]) -> dict[str, object]:
        materials: dict[str, object] = {}
        color_resolver = ColorResolver(material_map=self.material_map)

        for element_name in element_names:
            mat_path = f"/Maze/Materials/{sanitize_prim_name(element_name)}"
            if self.material_source is not None:
                usd_material = self.material_source.get_usd_material(element_name)
                if usd_material is not None:
                    materials[element_name] = reference_usd_material(
                        stage,
                        mat_path,
                        usd_material.file,
                        usd_material.path,
                    )
                    continue

                texture_path = self.material_source.get_texture(element_name)
                if texture_path is not None:
                    materials[element_name] = create_texture_material(
                        stage,
                        mat_path,
                        element_name,
                        texture_path,
                    )
                    continue

            materials[element_name] = create_preview_material(
                stage,
                mat_path,
                element_name,
                color_resolver.resolve(element_name),
            )
        return materials
