import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class PointcloudField:
    name: str
    dtype: np.dtype

X = PointcloudField('X', np.float32)
Y = PointcloudField('Y', np.float32)
Z = PointcloudField('Z', np.float32)
R = PointcloudField('red', np.uint8)
G = PointcloudField('green', np.uint8)
B = PointcloudField('blue', np.uint8)
INTENSITY = PointcloudField('intensity', np.uint32)
CHANGE = PointcloudField('change', np.uint8)
SEMANTIC = PointcloudField('semantic', np.uint8)
INSTANCE = PointcloudField('instance', np.uint16)

@dataclass
class PointcloudFormat:
    fields: list
    txt_output_dtypes: str | None = None
    txt_output_header: str | None = None
    ply_output_dtypes: np.dtype | None = None

    def __post_init__(self):
        field_dtypes = [f.dtype for f in self.fields]
        field_names = [f.name for f in self.fields]

        self.txt_output_header = ','.join(field_names)
        txt_dtypes = ['%1.6f' if dtype is np.float32 else '%u' for dtype in field_dtypes]
        self.txt_output_dtypes = ','.join(txt_dtypes)

        ply_dtypes = [(name, dtype) for name, dtype in zip(field_names, field_dtypes)]
        self.ply_output_dtypes = np.dtype(ply_dtypes)


FORMAT_XYZ = PointcloudFormat([X, Y, Z])
FORMAT_XYZI = PointcloudFormat([X, Y, Z, INTENSITY])
FORMAT_XYZC = PointcloudFormat([X, Y, Z, CHANGE])
FORMAT_XYZRGB = PointcloudFormat([X, Y, Z, R, G, B])
FORMAT_XYZRGBC = PointcloudFormat([X, Y, Z, R, G, B, CHANGE])
FORMAT_XYZRGBS = PointcloudFormat([X, Y, Z, R, G, B, SEMANTIC])
FORMAT_XYZRGBSC = PointcloudFormat([X, Y, Z, R, G, B, SEMANTIC, CHANGE])
FORMAT_XYZRGBSIC = PointcloudFormat([X, Y, Z, R, G, B, SEMANTIC, INSTANCE, CHANGE])