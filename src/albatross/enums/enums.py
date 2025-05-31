import enum

# We declare these enums as as a subclass of str to ensure that they are serializable


class ProductType(str, enum.Enum):
    CAMERA = 1
    LENS = 2


class SensorSize(str, enum.Enum):
    FULL_FRAME = 1
    APSC = 2
    CANON_APSC = 3
    MEDIUM_FORMAT = 4
    FOUR_THIRDS = 5
    ONE_INCH = 6
    UNKNOWN = 7
    TWO_THIRDS = 8
    ONE_OVER_TWO_POINT_THREE = 9


class CameraType(str, enum.Enum):
    DSLR = 1
    MIRRORLESS = 2
    COMPACT = 3
    RANGEFINDER = 4
    ACTION = 5
    DRONE = 6
    PHONE = 7
    UNKNOWN = 8


class MountType(str, enum.Enum):
    F = "f"
    Z = "z"
    NIKON_1 = "Nikon 1"
    EF_S = "ef-s"
    EF = "ef"
    RF_S = "rf-s"
    RF = "rf"
    FOUR_THIRDS = "four thirds"
    M43 = "m43"
    A = "a"
    E = "e"
    FE = "fe"
    XCD = "xcd"
    HCD = "hcd"
    K = "k"
    PENTAX_645 = "pentax 645"
    M = "m"
    TL = "tl"
    X = "x"
    G = "g"
    L = "l"
    NONE = "none"
    UNKNOWN = "unknown"
