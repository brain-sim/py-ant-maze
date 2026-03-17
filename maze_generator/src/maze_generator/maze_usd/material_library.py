"""Material creation for USD output."""

from __future__ import annotations

from dataclasses import dataclass

from ..maze_materials.color import ColorResolver, MaterialMap
from ..maze_materials.source import FaceSide, MaterialSource, texture_name_requests_stretch
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

    def create(
        self,
        stage,
        material_requests: tuple[tuple[str, FaceSide | None], ...],
    ) -> dict[tuple[str, FaceSide | None], object]:
        materials: dict[tuple[str, FaceSide | None], object] = {}
        color_resolver = ColorResolver(material_map=self.material_map)

        for element_name, face in material_requests:
            mat_path = f"/Maze/Materials/{_material_request_name(element_name, face)}"
            if self.material_source is not None:
                usd_material, texture_path = self.material_source.resolve_for_usd(
                    element_name,
                    face=face,
                )
                if usd_material is not None:
                    materials[(element_name, face)] = reference_usd_material(
                        stage,
                        mat_path,
                        usd_material.file,
                        usd_material.path,
                    )
                    continue

                if texture_path is not None:
                    materials[(element_name, face)] = create_texture_material(
                        stage,
                        mat_path,
                        element_name,
                        texture_path,
                        repeat=not texture_name_requests_stretch(texture_path),
                    )
                    continue

            materials[(element_name, face)] = create_preview_material(
                stage,
                mat_path,
                element_name,
                color_resolver.resolve(element_name),
            )
        return materials


def _material_request_name(element_name: str, face: FaceSide | None) -> str:
    if face is None:
        return sanitize_prim_name(element_name)
    return sanitize_prim_name(f"{element_name}_{face}")
