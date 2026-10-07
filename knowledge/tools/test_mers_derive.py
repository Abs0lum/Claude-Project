"""Unit tests for tools/mers_derive.py formula functions (run: python3 tools/test_mers_derive.py)."""
import sys
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import mers_derive as D


def test_tokens():
    assert D.tokens("leftEar2") == {"left", "ear"}
    assert D.tokens("pw_wing_l") == {"pw", "wing", "l"}
    assert D.tokens("sf_nba:sea_lion") == {"sf", "nba", "sea", "lion"}


def test_material_class():
    assert D.material_class("quadruped", "pw:elephant_african_wa") == "skin"
    assert D.material_class("quadruped", "minecraft:cow") == "fur"
    assert D.material_class("bird", "sf_nba:robin") == "feather"
    assert D.material_class("cetacean", "pw:orca_wwa") == "wet"
    assert D.material_class("object", "minecraft:minecart") == "metal"
    assert D.material_class("quadruped", "pw:boar_ifs") == "fur"          # token-exact: boar != boat
    assert D.material_class("insect_walking", "pw:beetle_elephant_anf") == "chitin"   # plan wins for insects
    assert D.material_class("object", "sf_nba:robin_egg") == "eggshell"


def test_part_values():
    fur = D.MATERIALS["fur"]
    assert D.part_values("leftEye", "quadruped", fur) == (30, 0)
    assert D.part_values("ear_l", "quadruped", fur) == (225, 120)
    assert D.part_values("wing_left", "bat", fur) == (225, 130)
    assert D.part_values("wing_left", "insect_flying", D.MATERIALS["chitin"]) == (60, 60)
    assert D.part_values("wing_left", "bird", D.MATERIALS["feather"]) == (210, 20)
    assert D.part_values("body", "quadruped", fur) == (225, 30)


def test_mers_156():
    spec = np.array([[[200, 240, 100, 255], [0, 10, 64, 40]]], dtype=np.uint8)
    out = D.mers_156(spec)
    assert out[0, 0].tolist() == [255, 0, 55, 48]     # metal; emissive 255 -> 0; rough 255-200; S (100-64)*255/191 = 48
    assert out[0, 1].tolist() == [0, 40, 255, 0]


def test_crevice_sign():
    c = np.full((7, 7, 4), 200, dtype=np.uint8); c[3, 3, :3] = 50
    d = D.crevice(c)
    assert d[3, 3] > 0 and abs(d[0, 0]) < 1e-6


if __name__ == "__main__":
    n = 0
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f(); n += 1
    print(f"{n}/{n} tests passed")
