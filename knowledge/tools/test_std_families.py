#!/usr/bin/env python3
"""tests for std_families.family_of — the names a substring match got wrong (10-01) + one per family style."""
import sys

sys.path.insert(0, "/home/claude/tools")
import std_families as F  # noqa: E402

CASES = {
    "pw:gecko_leopard_anf": "lizard", "pw:jerboa_wwa": None, "pw:lemur_mouse_brown_anf": "lemur", "pw:lantern_fish_wa": "fish",
    "pw:newt_eastern_anf": "salamander", "pw:hedgehog_euro_anf": "hedgehog", "pw:fly_horse_anf": "fly_insect",
    "sf_nba:peafowl": "galliform", "pw:sealion_anf": "pinniped", "pw:beetle_elephant_anf": "beetle",
    "pw:shark_hammerhead_anf": "shark", "pw:hammerhead_shark_wa": "shark", "pw:snake_coral_wa": "snake",
    "pw:red_panda_wa": "procyonid", "pw:prairie_dog_wwa": "sciurid", "pw:komodo_dragon_wa": "lizard",
    "pw:gila_monster_ws": "lizard", "pw:bird_of_paradise_wwa": "songbird", "pw:african_wild_dog_ysav": "canid",
    "pw:fisher_eagle_ysav": "raptor", "pw:eagle_blackhawk_anf": "raptor", "pw:slug_leopard_anf": "gastropod",
    "pw:crab_spider_anf": "crab", "minecraft:cave_spider": "spider", "minecraft:polar_bear": "ursid", "minecraft:panda": "ursid",
    "sf_nba:female_lion": "felid", "pw:white_lioness_ysav": "felid", "pw:gazelle_female_ysav": "cervid_antelope",
    "pw:dik_dik_ytri": "cervid_antelope", "pw:toadfish_wwa": "fish", "sf_nba:tree_frog": "anuran", "minecraft:xp_bottle": None,
    "minecraft:phantom": None, "pw:snapping_turtle_wwa": "turtle", "minecraft:trader_llama": "pacer", "pw:honey_badger_ysav": "mustelid",
    "minecraft:horse": "equid", "pw:zebra_wa": "equid", "minecraft:mooshroom": "bovine", "pw:flamingo_american_anf": "wader",
    "pw:shoebill_wwa": "wader", "pw:duck_indianrunner_anf": "waterfowl", "sf_nba:emperor_penguin": None,
}


def test_cases():
    bad = {k: (F.family_of(k)[0], v) for k, v in CASES.items() if F.family_of(k)[0] != v}
    assert not bad, bad


def test_kinds_are_real():
    for f, nouns, kinds, why in F.FAMILIES:
        assert kinds and set(kinds) <= set(F.ALL), f
        assert why, f
    assert "sit" not in F.FAMILY_TABLE["equid"][1]          # horses do not sit like dogs
    assert "swim" not in F.FAMILY_TABLE["wader"][1]         # a heron does not swim like a duck
    assert "fly" not in F.FAMILY_TABLE["ratite"][1]


if __name__ == "__main__":
    test_cases()
    test_kinds_are_real()
    print(f"family tests passed ({len(CASES)} names)")
