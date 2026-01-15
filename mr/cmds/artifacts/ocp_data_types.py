from typing import Any

from pydantic import BaseModel


class Buffer(BaseModel):
    shape: list[int]
    dtype: str
    buffer: str
    codec: str


class Instance(BaseModel):
    vertices: Buffer
    triangles: Buffer
    normals: Buffer
    edges: Buffer
    obj_vertices: Buffer
    face_types: Buffer
    edge_types: Buffer
    triangles_per_face: Buffer
    segments_per_edge: Buffer


class BoundingBox(BaseModel):
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float


class ShapeRef(BaseModel):
    ref: int


class Part(BaseModel):
    id: str
    type: str
    subtype: str
    name: str
    shape: ShapeRef
    state: list[int]
    color: str
    alpha: float
    texture: Any | None = None
    loc: list[list[float]]
    renderback: bool
    accuracy: Any | None = None
    bb: BoundingBox | None = None


class Shapes(BaseModel):
    version: int
    parts: list[Part]
    loc: list[list[float]]
    name: str
    id: str
    normal_len: int
    bb: BoundingBox


class OcpData(BaseModel):
    instances: list[Instance]
    shapes: Shapes


class OcpPayload(BaseModel):
    data: OcpData
    type: str
    count: int
