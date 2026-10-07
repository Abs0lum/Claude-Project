// pw_testrunner_p18.js — lineup "p18" THE NEW ANIMALS PARADE (PW-TestRunner BP v0.5.5, D-C351; menagerie wave P1, his 20:10 / 22:11 CT 09-30).
// /scriptevent pw:test start p18 — RP-07 v1.4.32 + PW-StripMine BP v1.3.7: the 147 new animals ported from his add-on collection
// (ids pw:<animal>_<pack>), five to a roofed pen (water ones three to a pool), each with its name tag, held still so they can be looked at.
// The rig (pw_testrunner_rig.js) spawns them; a creature the packs do not have is logged ('RIG ... FAILED'), never thrown.
function lines(text) {
  const out = [];
  for (const para of String(text).split("\n")) {
    let cur = "";
    for (const piece of para.split(/(?<=[.!?:]) +| (?=- )/)) {
      if (cur && (cur + " " + piece).length > 190) { out.push(cur); cur = piece; } else cur = cur ? cur + " " + piece : piece;
    }
    if (cur) out.push(cur);
  }
  return out.join("\n");
}
const CLEAR = ["fill ~-12 ~ ~-14 ~12 ~7 ~-2 air"];
const LOOK = "Look for: each animal drawn whole (no missing parts, no purple-black checker texture, no floating), its name tag, a sensible size next to you; " +
  "tap one to hear it. They are held still (idle animation only).";
const PASSN = "PASS = all right. FAIL + note = which one and what (use all 3 note boxes if needed).";
export const P18_DATA = [
 {
  "id": "a01",
  "group": "P18 NEW ANIMALS",
  "title": "AFRICAN WILD DOG \u00b7 ALPACA \u00b7 ANACONDA \u00b7 BIRD OF PARADISE \u00b7 BISON",
  "look": "LEFT to RIGHT: AFRICAN WILD DOG (YSAV), ALPACA (YTRI), ANACONDA (WS), BIRD OF PARADISE (WWA), BISON (YTRI).",
  "rig": {
   "mob": "pw:anaconda_ws",
   "label": "anaconda",
   "name": "Anaconda",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:african_wild_dog_ysav",
     "dx": -8,
     "label": "african wild dog",
     "name": "African Wild Dog"
    },
    {
     "mob": "pw:alpaca_ytri",
     "dx": -4,
     "label": "alpaca",
     "name": "Alpaca"
    },
    {
     "mob": "pw:bird_of_paradise_wwa",
     "dx": 4,
     "label": "bird of paradise",
     "name": "Bird Of Paradise"
    },
    {
     "mob": "pw:bison_ytri",
     "dx": 8,
     "label": "bison",
     "name": "Bison"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a02",
  "group": "P18 NEW ANIMALS",
  "title": "BONGO \u00b7 CARACAL \u00b7 CENTIPEDE BROWN \u00b7 CENTIPEDE COMMON \u00b7 CENTIPEDE DESERT",
  "look": "LEFT to RIGHT: BONGO (YTRI), CARACAL (WA), CENTIPEDE BROWN (ANF), CENTIPEDE COMMON (ANF), CENTIPEDE DESERT (ANF).",
  "rig": {
   "mob": "pw:centipede_brown_anf",
   "label": "centipede brown",
   "name": "Centipede Brown",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:bongo_ytri",
     "dx": -8,
     "label": "bongo",
     "name": "Bongo"
    },
    {
     "mob": "pw:caracal_wa",
     "dx": -4,
     "label": "caracal",
     "name": "Caracal"
    },
    {
     "mob": "pw:centipede_common_anf",
     "dx": 4,
     "label": "centipede common",
     "name": "Centipede Common"
    },
    {
     "mob": "pw:centipede_desert_anf",
     "dx": 8,
     "label": "centipede desert",
     "name": "Centipede Desert"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a03",
  "group": "P18 NEW ANIMALS",
  "title": "CENTIPEDE PACIFICGIANT \u00b7 CHAMELEON \u00b7 CHEETAH \u00b7 COBRA \u00b7 COUGAR",
  "look": "LEFT to RIGHT: CENTIPEDE PACIFICGIANT (ANF), CHAMELEON (ANF), CHEETAH (YSAV), COBRA (YSAV), COUGAR (WA).",
  "rig": {
   "mob": "pw:cheetah_ysav",
   "label": "cheetah",
   "name": "Cheetah",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:centipede_pacificgiant_anf",
     "dx": -8,
     "label": "centipede pacificgiant",
     "name": "Centipede Pacificgiant"
    },
    {
     "mob": "pw:chameleon_anf",
     "dx": -4,
     "label": "chameleon",
     "name": "Chameleon"
    },
    {
     "mob": "pw:cobra_ysav",
     "dx": 4,
     "label": "cobra",
     "name": "Cobra"
    },
    {
     "mob": "pw:cougar_wa",
     "dx": 8,
     "label": "cougar",
     "name": "Cougar"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a04",
  "group": "P18 NEW ANIMALS",
  "title": "CRANE COMMON \u00b7 CRANE HOODEN \u00b7 CRANE SIBERIAN \u00b7 CRANE WHOPPING \u00b7 DIK DIK",
  "look": "LEFT to RIGHT: CRANE COMMON (ANF), CRANE HOODEN (ANF), CRANE SIBERIAN (ANF), CRANE WHOPPING (ANF), DIK DIK (YTRI).",
  "rig": {
   "mob": "pw:crane_siberian_anf",
   "label": "crane siberian",
   "name": "Crane Siberian",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:crane_common_anf",
     "dx": -8,
     "label": "crane common",
     "name": "Crane Common"
    },
    {
     "mob": "pw:crane_hooden_anf",
     "dx": -4,
     "label": "crane hooden",
     "name": "Crane Hooden"
    },
    {
     "mob": "pw:crane_whopping_anf",
     "dx": 4,
     "label": "crane whopping",
     "name": "Crane Whopping"
    },
    {
     "mob": "pw:dik_dik_ytri",
     "dx": 8,
     "label": "dik dik",
     "name": "Dik Dik"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a05",
  "group": "P18 NEW ANIMALS",
  "title": "DOG ALSATIAN \u00b7 DOG LAB BLACK \u00b7 DOG LAB CHOCOLATE \u00b7 DOG LAB GOLDEN \u00b7 DOG RETRIEVER GOLDEN",
  "look": "LEFT to RIGHT: DOG ALSATIAN (ANF), DOG LAB BLACK (ANF), DOG LAB CHOCOLATE (ANF), DOG LAB GOLDEN (ANF), DOG RETRIEVER GOLDEN (ANF).",
  "rig": {
   "mob": "pw:dog_lab_chocolate_anf",
   "label": "dog lab chocolate",
   "name": "Dog Lab Chocolate",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:dog_alsatian_anf",
     "dx": -8,
     "label": "dog alsatian",
     "name": "Dog Alsatian"
    },
    {
     "mob": "pw:dog_lab_black_anf",
     "dx": -4,
     "label": "dog lab black",
     "name": "Dog Lab Black"
    },
    {
     "mob": "pw:dog_lab_golden_anf",
     "dx": 4,
     "label": "dog lab golden",
     "name": "Dog Lab Golden"
    },
    {
     "mob": "pw:dog_retriever_golden_anf",
     "dx": 8,
     "label": "dog retriever golden",
     "name": "Dog Retriever Golden"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a06",
  "group": "P18 NEW ANIMALS",
  "title": "DOG RETRIEVER WHITE \u00b7 EARTHWORM COMMON \u00b7 EARTHWORM GIPPSLAND \u00b7 EARTHWORM NIGHTCRAWLER \u00b7 EGRET GREAT",
  "look": "LEFT to RIGHT: DOG RETRIEVER WHITE (ANF), EARTHWORM COMMON (ANF), EARTHWORM GIPPSLAND (ANF), EARTHWORM NIGHTCRAWLER (ANF), EGRET GREAT (ANF).",
  "rig": {
   "mob": "pw:earthworm_gippsland_anf",
   "label": "earthworm gippsland",
   "name": "Earthworm Gippsland",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:dog_retriever_white_anf",
     "dx": -8,
     "label": "dog retriever white",
     "name": "Dog Retriever White"
    },
    {
     "mob": "pw:earthworm_common_anf",
     "dx": -4,
     "label": "earthworm common",
     "name": "Earthworm Common"
    },
    {
     "mob": "pw:earthworm_nightcrawler_anf",
     "dx": 4,
     "label": "earthworm nightcrawler",
     "name": "Earthworm Nightcrawler"
    },
    {
     "mob": "pw:egret_great_anf",
     "dx": 8,
     "label": "egret great",
     "name": "Egret Great"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a07",
  "group": "P18 NEW ANIMALS",
  "title": "EGRET LITTLE \u00b7 EGRET REDDISH \u00b7 FLY BLUEBOTTLE \u00b7 FLY DUNG \u00b7 FLY FRUIT",
  "look": "LEFT to RIGHT: EGRET LITTLE (ANF), EGRET REDDISH (ANF), FLY BLUEBOTTLE (ANF), FLY DUNG (ANF), FLY FRUIT (ANF).",
  "rig": {
   "mob": "pw:fly_bluebottle_anf",
   "label": "fly bluebottle",
   "name": "Fly Bluebottle",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:egret_little_anf",
     "dx": -8,
     "label": "egret little",
     "name": "Egret Little"
    },
    {
     "mob": "pw:egret_reddish_anf",
     "dx": -4,
     "label": "egret reddish",
     "name": "Egret Reddish"
    },
    {
     "mob": "pw:fly_dung_anf",
     "dx": 4,
     "label": "fly dung",
     "name": "Fly Dung"
    },
    {
     "mob": "pw:fly_fruit_anf",
     "dx": 8,
     "label": "fly fruit",
     "name": "Fly Fruit"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a08",
  "group": "P18 NEW ANIMALS",
  "title": "FLY HORSE \u00b7 FLY HOVER \u00b7 GAVIAL \u00b7 GECKO BLACK \u00b7 GECKO BLUE",
  "look": "LEFT to RIGHT: FLY HORSE (ANF), FLY HOVER (ANF), GAVIAL (YTRI), GECKO BLACK (ANF), GECKO BLUE (ANF).",
  "rig": {
   "mob": "pw:gavial_ytri",
   "label": "gavial",
   "name": "Gavial",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:fly_horse_anf",
     "dx": -8,
     "label": "fly horse",
     "name": "Fly Horse"
    },
    {
     "mob": "pw:fly_hover_anf",
     "dx": -4,
     "label": "fly hover",
     "name": "Fly Hover"
    },
    {
     "mob": "pw:gecko_black_anf",
     "dx": 4,
     "label": "gecko black",
     "name": "Gecko Black"
    },
    {
     "mob": "pw:gecko_blue_anf",
     "dx": 8,
     "label": "gecko blue",
     "name": "Gecko Blue"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a09",
  "group": "P18 NEW ANIMALS",
  "title": "GECKO LEOPARD \u00b7 GECKO YELLOW \u00b7 GERBIL \u00b7 GRASSHOPPER \u00b7 HARE ARCTIC",
  "look": "LEFT to RIGHT: GECKO LEOPARD (ANF), GECKO YELLOW (ANF), GERBIL (ANF), GRASSHOPPER (ANF), HARE ARCTIC (ANF).",
  "rig": {
   "mob": "pw:gerbil_anf",
   "label": "gerbil",
   "name": "Gerbil",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:gecko_leopard_anf",
     "dx": -8,
     "label": "gecko leopard",
     "name": "Gecko Leopard"
    },
    {
     "mob": "pw:gecko_yellow_anf",
     "dx": -4,
     "label": "gecko yellow",
     "name": "Gecko Yellow"
    },
    {
     "mob": "pw:grasshopper_anf",
     "dx": 4,
     "label": "grasshopper",
     "name": "Grasshopper"
    },
    {
     "mob": "pw:hare_arctic_anf",
     "dx": 8,
     "label": "hare arctic",
     "name": "Hare Arctic"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a10",
  "group": "P18 NEW ANIMALS",
  "title": "HARE BLACKTAILED \u00b7 HARE EUROPEAN \u00b7 HARE MOUNTAIN \u00b7 HAWK GREY \u00b7 HAWK HARRIER",
  "look": "LEFT to RIGHT: HARE BLACKTAILED (ANF), HARE EUROPEAN (ANF), HARE MOUNTAIN (ANF), HAWK GREY (ANF), HAWK HARRIER (ANF).",
  "rig": {
   "mob": "pw:hare_mountain_anf",
   "label": "hare mountain",
   "name": "Hare Mountain",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:hare_blacktailed_anf",
     "dx": -8,
     "label": "hare blacktailed",
     "name": "Hare Blacktailed"
    },
    {
     "mob": "pw:hare_european_anf",
     "dx": -4,
     "label": "hare european",
     "name": "Hare European"
    },
    {
     "mob": "pw:hawk_grey_anf",
     "dx": 4,
     "label": "hawk grey",
     "name": "Hawk Grey"
    },
    {
     "mob": "pw:hawk_harrier_anf",
     "dx": 8,
     "label": "hawk harrier",
     "name": "Hawk Harrier"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a11",
  "group": "P18 NEW ANIMALS",
  "title": "HAWK HARRIS \u00b7 HAWK SPARROW \u00b7 HERON AGAMI \u00b7 HERON BLACK \u00b7 HERON BLACKCROWNED",
  "look": "LEFT to RIGHT: HAWK HARRIS (ANF), HAWK SPARROW (ANF), HERON AGAMI (ANF), HERON BLACK (ANF), HERON BLACKCROWNED (ANF).",
  "rig": {
   "mob": "pw:heron_agami_anf",
   "label": "heron agami",
   "name": "Heron Agami",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:hawk_harris_anf",
     "dx": -8,
     "label": "hawk harris",
     "name": "Hawk Harris"
    },
    {
     "mob": "pw:hawk_sparrow_anf",
     "dx": -4,
     "label": "hawk sparrow",
     "name": "Hawk Sparrow"
    },
    {
     "mob": "pw:heron_black_anf",
     "dx": 4,
     "label": "heron black",
     "name": "Heron Black"
    },
    {
     "mob": "pw:heron_blackcrowned_anf",
     "dx": 8,
     "label": "heron blackcrowned",
     "name": "Heron Blackcrowned"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a12",
  "group": "P18 NEW ANIMALS",
  "title": "HERON GREATBLUE \u00b7 HERON GREEN \u00b7 HERON GREY \u00b7 HONEY BADGER \u00b7 HORNET ASIAN",
  "look": "LEFT to RIGHT: HERON GREATBLUE (ANF), HERON GREEN (ANF), HERON GREY (ANF), HONEY BADGER (YSAV), HORNET ASIAN (ANF).",
  "rig": {
   "mob": "pw:heron_grey_anf",
   "label": "heron grey",
   "name": "Heron Grey",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:heron_greatblue_anf",
     "dx": -8,
     "label": "heron greatblue",
     "name": "Heron Greatblue"
    },
    {
     "mob": "pw:heron_green_anf",
     "dx": -4,
     "label": "heron green",
     "name": "Heron Green"
    },
    {
     "mob": "pw:honey_badger_ysav",
     "dx": 4,
     "label": "honey badger",
     "name": "Honey Badger"
    },
    {
     "mob": "pw:hornet_asian_anf",
     "dx": 8,
     "label": "hornet asian",
     "name": "Hornet Asian"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a13",
  "group": "P18 NEW ANIMALS",
  "title": "HORNET EUROPEAN \u00b7 IMPALA \u00b7 IMPALA FEMALE \u00b7 JAY BROWN \u00b7 JERBOA",
  "look": "LEFT to RIGHT: HORNET EUROPEAN (ANF), IMPALA (YSAV), IMPALA FEMALE (YSAV), JAY BROWN (ANF), JERBOA (WWA).",
  "rig": {
   "mob": "pw:impala_female_ysav",
   "label": "impala female",
   "name": "Impala Female",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:hornet_european_anf",
     "dx": -8,
     "label": "hornet european",
     "name": "Hornet European"
    },
    {
     "mob": "pw:impala_ysav",
     "dx": -4,
     "label": "impala",
     "name": "Impala"
    },
    {
     "mob": "pw:jay_brown_anf",
     "dx": 4,
     "label": "jay brown",
     "name": "Jay Brown"
    },
    {
     "mob": "pw:jerboa_wwa",
     "dx": 8,
     "label": "jerboa",
     "name": "Jerboa"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a14",
  "group": "P18 NEW ANIMALS",
  "title": "KOALA \u00b7 KOB \u00b7 KOB FEMALE \u00b7 LEMMING ARCTIC \u00b7 LEMMING BOG",
  "look": "LEFT to RIGHT: KOALA (YTRI), KOB (YSAV), KOB FEMALE (YSAV), LEMMING ARCTIC (ANF), LEMMING BOG (ANF).",
  "rig": {
   "mob": "pw:kob_female_ysav",
   "label": "kob female",
   "name": "Kob Female",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:koala_ytri",
     "dx": -8,
     "label": "koala",
     "name": "Koala"
    },
    {
     "mob": "pw:kob_ysav",
     "dx": -4,
     "label": "kob",
     "name": "Kob"
    },
    {
     "mob": "pw:lemming_arctic_anf",
     "dx": 4,
     "label": "lemming arctic",
     "name": "Lemming Arctic"
    },
    {
     "mob": "pw:lemming_bog_anf",
     "dx": 8,
     "label": "lemming bog",
     "name": "Lemming Bog"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a15",
  "group": "P18 NEW ANIMALS",
  "title": "LEMMING NORWAY \u00b7 LEMMING YELLOWSTEPPE \u00b7 MAGPIE \u00b7 MANDRILL \u00b7 MONITOR LIZARD",
  "look": "LEFT to RIGHT: LEMMING NORWAY (ANF), LEMMING YELLOWSTEPPE (ANF), MAGPIE (ANF), MANDRILL (ANF), MONITOR LIZARD (YSAV).",
  "rig": {
   "mob": "pw:magpie_anf",
   "label": "magpie",
   "name": "Magpie",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:lemming_norway_anf",
     "dx": -8,
     "label": "lemming norway",
     "name": "Lemming Norway"
    },
    {
     "mob": "pw:lemming_yellowsteppe_anf",
     "dx": -4,
     "label": "lemming yellowsteppe",
     "name": "Lemming Yellowsteppe"
    },
    {
     "mob": "pw:mandrill_anf",
     "dx": 4,
     "label": "mandrill",
     "name": "Mandrill"
    },
    {
     "mob": "pw:monitor_lizard_ysav",
     "dx": 8,
     "label": "monitor lizard",
     "name": "Monitor Lizard"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a16",
  "group": "P18 NEW ANIMALS",
  "title": "MOTH ATLAS \u00b7 MOTH COMET \u00b7 MOTH EMPEROR \u00b7 MOTH GARDENTIGER \u00b7 MOTH GIANTLEOPARD",
  "look": "LEFT to RIGHT: MOTH ATLAS (ANF), MOTH COMET (ANF), MOTH EMPEROR (ANF), MOTH GARDENTIGER (ANF), MOTH GIANTLEOPARD (ANF).",
  "rig": {
   "mob": "pw:moth_emperor_anf",
   "label": "moth emperor",
   "name": "Moth Emperor",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:moth_atlas_anf",
     "dx": -8,
     "label": "moth atlas",
     "name": "Moth Atlas"
    },
    {
     "mob": "pw:moth_comet_anf",
     "dx": -4,
     "label": "moth comet",
     "name": "Moth Comet"
    },
    {
     "mob": "pw:moth_gardentiger_anf",
     "dx": 4,
     "label": "moth gardentiger",
     "name": "Moth Gardentiger"
    },
    {
     "mob": "pw:moth_giantleopard_anf",
     "dx": 8,
     "label": "moth giantleopard",
     "name": "Moth Giantleopard"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a17",
  "group": "P18 NEW ANIMALS",
  "title": "MOTH GYPSY \u00b7 MOTH LUNA \u00b7 MOTH ROSYMAPLE \u00b7 MOUSE HARVEST \u00b7 MOUSE HOUSE",
  "look": "LEFT to RIGHT: MOTH GYPSY (ANF), MOTH LUNA (ANF), MOTH ROSYMAPLE (ANF), MOUSE HARVEST (ANF), MOUSE HOUSE (ANF).",
  "rig": {
   "mob": "pw:moth_rosymaple_anf",
   "label": "moth rosymaple",
   "name": "Moth Rosymaple",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:moth_gypsy_anf",
     "dx": -8,
     "label": "moth gypsy",
     "name": "Moth Gypsy"
    },
    {
     "mob": "pw:moth_luna_anf",
     "dx": -4,
     "label": "moth luna",
     "name": "Moth Luna"
    },
    {
     "mob": "pw:mouse_harvest_anf",
     "dx": 4,
     "label": "mouse harvest",
     "name": "Mouse Harvest"
    },
    {
     "mob": "pw:mouse_house_anf",
     "dx": 8,
     "label": "mouse house",
     "name": "Mouse House"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a18",
  "group": "P18 NEW ANIMALS",
  "title": "MOUSE JUMPING \u00b7 MOUSE WOOD \u00b7 NEWT CRESTED \u00b7 NEWT EASTERN \u00b7 NEWT EMPEROR",
  "look": "LEFT to RIGHT: MOUSE JUMPING (ANF), MOUSE WOOD (ANF), NEWT CRESTED (ANF), NEWT EASTERN (ANF), NEWT EMPEROR (ANF).",
  "rig": {
   "mob": "pw:newt_crested_anf",
   "label": "newt crested",
   "name": "Newt Crested",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:mouse_jumping_anf",
     "dx": -8,
     "label": "mouse jumping",
     "name": "Mouse Jumping"
    },
    {
     "mob": "pw:mouse_wood_anf",
     "dx": -4,
     "label": "mouse wood",
     "name": "Mouse Wood"
    },
    {
     "mob": "pw:newt_eastern_anf",
     "dx": 4,
     "label": "newt eastern",
     "name": "Newt Eastern"
    },
    {
     "mob": "pw:newt_emperor_anf",
     "dx": 8,
     "label": "newt emperor",
     "name": "Newt Emperor"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a19",
  "group": "P18 NEW ANIMALS",
  "title": "NEWT FIREBELLY \u00b7 KUDU \u00b7 KUDU FEMALE \u00b7 ORYX \u00b7 PANGOLIN",
  "look": "LEFT to RIGHT: NEWT FIREBELLY (ANF), KUDU (YSAV), KUDU FEMALE (YSAV), ORYX (YSAV), PANGOLIN (YSAV).",
  "rig": {
   "mob": "pw:kudu_female_ysav",
   "label": "kudu female",
   "name": "Kudu Female",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:newt_firebelly_anf",
     "dx": -8,
     "label": "newt firebelly",
     "name": "Newt Firebelly"
    },
    {
     "mob": "pw:kudu_ysav",
     "dx": -4,
     "label": "kudu",
     "name": "Kudu"
    },
    {
     "mob": "pw:oryx_ysav",
     "dx": 4,
     "label": "oryx",
     "name": "Oryx"
    },
    {
     "mob": "pw:pangolin_ysav",
     "dx": 8,
     "label": "pangolin",
     "name": "Pangolin"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a20",
  "group": "P18 NEW ANIMALS",
  "title": "PIGEON AFRICANOLIVE \u00b7 PIGEON PASSENGER \u00b7 PIGEON ROCK \u00b7 PIGEON WOOD \u00b7 PRAIRIE DOG",
  "look": "LEFT to RIGHT: PIGEON AFRICANOLIVE (ANF), PIGEON PASSENGER (ANF), PIGEON ROCK (ANF), PIGEON WOOD (ANF), PRAIRIE DOG (WWA).",
  "rig": {
   "mob": "pw:pigeon_rock_anf",
   "label": "pigeon rock",
   "name": "Pigeon Rock",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:pigeon_africanolive_anf",
     "dx": -8,
     "label": "pigeon africanolive",
     "name": "Pigeon Africanolive"
    },
    {
     "mob": "pw:pigeon_passenger_anf",
     "dx": -4,
     "label": "pigeon passenger",
     "name": "Pigeon Passenger"
    },
    {
     "mob": "pw:pigeon_wood_anf",
     "dx": 4,
     "label": "pigeon wood",
     "name": "Pigeon Wood"
    },
    {
     "mob": "pw:prairie_dog_wwa",
     "dx": 8,
     "label": "prairie dog",
     "name": "Prairie Dog"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a21",
  "group": "P18 NEW ANIMALS",
  "title": "PUFFIN \u00b7 ROADRUNNER \u00b7 SABLE ANTELOPE \u00b7 SAIGA \u00b7 SEALION",
  "look": "LEFT to RIGHT: PUFFIN (ANF), ROADRUNNER (WWA), SABLE ANTELOPE (YSAV), SAIGA (WWA), SEALION (ANF).",
  "rig": {
   "mob": "pw:sable_antelope_ysav",
   "label": "sable antelope",
   "name": "Sable Antelope",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:puffin_anf",
     "dx": -8,
     "label": "puffin",
     "name": "Puffin"
    },
    {
     "mob": "pw:roadrunner_wwa",
     "dx": -4,
     "label": "roadrunner",
     "name": "Roadrunner"
    },
    {
     "mob": "pw:saiga_wwa",
     "dx": 4,
     "label": "saiga",
     "name": "Saiga"
    },
    {
     "mob": "pw:sealion_anf",
     "dx": 8,
     "label": "sealion",
     "name": "Sealion"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a22",
  "group": "P18 NEW ANIMALS",
  "title": "SERVAL \u00b7 SHOEBILL \u00b7 SNOW LEOPARD \u00b7 STICKINSECT GOLIATH \u00b7 STOAT BRITISH",
  "look": "LEFT to RIGHT: SERVAL (YSAV), SHOEBILL (WWA), SNOW LEOPARD (WA), STICKINSECT GOLIATH (ANF), STOAT BRITISH (ANF).",
  "rig": {
   "mob": "pw:snow_leopard_wa",
   "label": "snow leopard",
   "name": "Snow Leopard",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:serval_ysav",
     "dx": -8,
     "label": "serval",
     "name": "Serval"
    },
    {
     "mob": "pw:shoebill_wwa",
     "dx": -4,
     "label": "shoebill",
     "name": "Shoebill"
    },
    {
     "mob": "pw:stickinsect_goliath_anf",
     "dx": 4,
     "label": "stickinsect goliath",
     "name": "Stickinsect Goliath"
    },
    {
     "mob": "pw:stoat_british_anf",
     "dx": 8,
     "label": "stoat british",
     "name": "Stoat British"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a23",
  "group": "P18 NEW ANIMALS",
  "title": "STOAT IRISH \u00b7 STOAT JAPANESE \u00b7 STOAT RUSSIAN \u00b7 TERN BLACK \u00b7 TERN CASPIAN",
  "look": "LEFT to RIGHT: STOAT IRISH (ANF), STOAT JAPANESE (ANF), STOAT RUSSIAN (ANF), TERN BLACK (ANF), TERN CASPIAN (ANF).",
  "rig": {
   "mob": "pw:stoat_russian_anf",
   "label": "stoat russian",
   "name": "Stoat Russian",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:stoat_irish_anf",
     "dx": -8,
     "label": "stoat irish",
     "name": "Stoat Irish"
    },
    {
     "mob": "pw:stoat_japanese_anf",
     "dx": -4,
     "label": "stoat japanese",
     "name": "Stoat Japanese"
    },
    {
     "mob": "pw:tern_black_anf",
     "dx": 4,
     "label": "tern black",
     "name": "Tern Black"
    },
    {
     "mob": "pw:tern_caspian_anf",
     "dx": 8,
     "label": "tern caspian",
     "name": "Tern Caspian"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a24",
  "group": "P18 NEW ANIMALS",
  "title": "TERN COMMON \u00b7 TERN CRESTED \u00b7 TERN FAIRY \u00b7 TERN LARGEBILLED \u00b7 TERN SOOTY",
  "look": "LEFT to RIGHT: TERN COMMON (ANF), TERN CRESTED (ANF), TERN FAIRY (ANF), TERN LARGEBILLED (ANF), TERN SOOTY (ANF).",
  "rig": {
   "mob": "pw:tern_fairy_anf",
   "label": "tern fairy",
   "name": "Tern Fairy",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:tern_common_anf",
     "dx": -8,
     "label": "tern common",
     "name": "Tern Common"
    },
    {
     "mob": "pw:tern_crested_anf",
     "dx": -4,
     "label": "tern crested",
     "name": "Tern Crested"
    },
    {
     "mob": "pw:tern_largebilled_anf",
     "dx": 4,
     "label": "tern largebilled",
     "name": "Tern Largebilled"
    },
    {
     "mob": "pw:tern_sooty_anf",
     "dx": 8,
     "label": "tern sooty",
     "name": "Tern Sooty"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a25",
  "group": "P18 NEW ANIMALS",
  "title": "TIT BEARDED \u00b7 TIT BLUE \u00b7 TIT COAL \u00b7 TIT CRESTED \u00b7 TIT GREAT",
  "look": "LEFT to RIGHT: TIT BEARDED (ANF), TIT BLUE (ANF), TIT COAL (ANF), TIT CRESTED (ANF), TIT GREAT (ANF).",
  "rig": {
   "mob": "pw:tit_coal_anf",
   "label": "tit coal",
   "name": "Tit Coal",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:tit_bearded_anf",
     "dx": -8,
     "label": "tit bearded",
     "name": "Tit Bearded"
    },
    {
     "mob": "pw:tit_blue_anf",
     "dx": -4,
     "label": "tit blue",
     "name": "Tit Blue"
    },
    {
     "mob": "pw:tit_crested_anf",
     "dx": 4,
     "label": "tit crested",
     "name": "Tit Crested"
    },
    {
     "mob": "pw:tit_great_anf",
     "dx": 8,
     "label": "tit great",
     "name": "Tit Great"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a26",
  "group": "P18 NEW ANIMALS",
  "title": "TIT LONGTAILED \u00b7 TIT MARSH \u00b7 TIT WILLOW \u00b7 TOAD AFRICANGIANT \u00b7 TOAD CANADIAN",
  "look": "LEFT to RIGHT: TIT LONGTAILED (ANF), TIT MARSH (ANF), TIT WILLOW (ANF), TOAD AFRICANGIANT (ANF), TOAD CANADIAN (ANF).",
  "rig": {
   "mob": "pw:tit_willow_anf",
   "label": "tit willow",
   "name": "Tit Willow",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:tit_longtailed_anf",
     "dx": -8,
     "label": "tit longtailed",
     "name": "Tit Longtailed"
    },
    {
     "mob": "pw:tit_marsh_anf",
     "dx": -4,
     "label": "tit marsh",
     "name": "Tit Marsh"
    },
    {
     "mob": "pw:toad_africangiant_anf",
     "dx": 4,
     "label": "toad africangiant",
     "name": "Toad Africangiant"
    },
    {
     "mob": "pw:toad_canadian_anf",
     "dx": 8,
     "label": "toad canadian",
     "name": "Toad Canadian"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a27",
  "group": "P18 NEW ANIMALS",
  "title": "TOAD EUROPEAN \u00b7 TOAD INDIAN \u00b7 TOAD YOSEMITE \u00b7 VIPER \u00b7 WASP PAPER",
  "look": "LEFT to RIGHT: TOAD EUROPEAN (ANF), TOAD INDIAN (ANF), TOAD YOSEMITE (ANF), VIPER (YSAV), WASP PAPER (ANF).",
  "rig": {
   "mob": "pw:toad_yosemite_anf",
   "label": "toad yosemite",
   "name": "Toad Yosemite",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:toad_european_anf",
     "dx": -8,
     "label": "toad european",
     "name": "Toad European"
    },
    {
     "mob": "pw:toad_indian_anf",
     "dx": -4,
     "label": "toad indian",
     "name": "Toad Indian"
    },
    {
     "mob": "pw:viper_ysav",
     "dx": 4,
     "label": "viper",
     "name": "Viper"
    },
    {
     "mob": "pw:wasp_paper_anf",
     "dx": 8,
     "label": "wasp paper",
     "name": "Wasp Paper"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a28",
  "group": "P18 NEW ANIMALS",
  "title": "WASP YELLOWJACKET \u00b7 TSESSEBE",
  "look": "LEFT to RIGHT: TSESSEBE (YSAV), WASP YELLOWJACKET (ANF).",
  "rig": {
   "mob": "pw:wasp_yellowjacket_anf",
   "label": "wasp yellowjacket",
   "name": "Wasp Yellowjacket",
   "half": 10,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:tsessebe_ysav",
     "dx": -4,
     "label": "tsessebe",
     "name": "Tsessebe"
    }
   ],
   "roof": true
  }
 },
 {
  "id": "a29",
  "group": "P18 WATER",
  "title": "BELUGA \u00b7 SHELLFISH CLAM \u00b7 GIANT SQUID",
  "look": "LEFT to RIGHT: BELUGA (YTRI), SHELLFISH CLAM (ANF), GIANT SQUID (WWA).",
  "rig": {
   "mob": "pw:shellfish_clam_anf",
   "label": "shellfish clam",
   "name": "Shellfish Clam",
   "half": 5,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:beluga_ytri",
     "dx": -3,
     "label": "beluga",
     "name": "Beluga"
    },
    {
     "mob": "pw:giant_squid_wwa",
     "dx": 3,
     "label": "giant squid",
     "name": "Giant Squid"
    }
   ],
   "water": true,
   "depth": 3
  }
 },
 {
  "id": "a30",
  "group": "P18 WATER",
  "title": "LANTERN FISH \u00b7 LOBSTER \u00b7 MANATEE",
  "look": "LEFT to RIGHT: LANTERN FISH (WA), LOBSTER (ANF), MANATEE (YTRI).",
  "rig": {
   "mob": "pw:lobster_anf",
   "label": "lobster",
   "name": "Lobster",
   "half": 5,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:lantern_fish_wa",
     "dx": -3,
     "label": "lantern fish",
     "name": "Lantern Fish"
    },
    {
     "mob": "pw:manatee_ytri",
     "dx": 3,
     "label": "manatee",
     "name": "Manatee"
    }
   ],
   "water": true,
   "depth": 3
  }
 },
 {
  "id": "a31",
  "group": "P18 WATER",
  "title": "SHELLFISH SCALLOP \u00b7 SHELLFISH SEAURCHIN \u00b7 SWORDFISH",
  "look": "LEFT to RIGHT: SHELLFISH SCALLOP (ANF), SHELLFISH SEAURCHIN (ANF), SWORDFISH (WA).",
  "rig": {
   "mob": "pw:shellfish_seaurchin_anf",
   "label": "shellfish seaurchin",
   "name": "Shellfish Seaurchin",
   "half": 5,
   "halfz": 3,
   "height": 5,
   "row": [
    {
     "mob": "pw:shellfish_scallop_anf",
     "dx": -3,
     "label": "shellfish scallop",
     "name": "Shellfish Scallop"
    },
    {
     "mob": "pw:swordfish_wa",
     "dx": 3,
     "label": "swordfish",
     "name": "Swordfish"
    }
   ],
   "water": true,
   "depth": 3
  }
 },
 {
  "id": "a32",
  "group": "P18 WATER",
  "title": "TOADFISH",
  "look": "LEFT to RIGHT: TOADFISH (WWA).",
  "rig": {
   "mob": "pw:toadfish_wwa",
   "label": "toadfish",
   "name": "Toadfish",
   "half": 5,
   "halfz": 3,
   "height": 5,
   "row": [],
   "water": true,
   "depth": 3
  }
 }
];
const Q0 = { id: "q0", group: "P18 SETUP", title: "P18 NEW ANIMALS: PHONE HOSTS, PS5 JOINS (VIBRANT VISUALS), FLAT GROUND, FACE NORTH",
  body: lines("Packs (on the phone): RP-07 v1.4.34 + PW-StripMine BP v1.3.9 (they hold everything of v1.4.32 / v1.3.7) - always together; PW-TestRunner BP v0.5.7 at the bottom. " +
    "Use a COPY of the test world; host on the phone, join on the PS5 with Vibrant Visuals ON. Creative.\n" +
    "Content log after load: 'PW Test Runner BP v0.5.7'.\nStand on big FLAT open ground (15 blocks clear each side, 15 NORTH) and FACE NORTH.\nPASS = ready."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const STEPS18 = P18_DATA.map((d) => ({ id: d.id, group: d.group, title: d.title,
  body: lines(`${d.look}\n${LOOK}\nSHOT of the pen from the front (south).\n${PASSN}`), setup: [{ cmd: CLEAR }, { rig: d.rig }] }));
const Q9 = { id: "q9", group: "P18 DONE", title: "P18: ALL CLEAR - UPLOAD",
  body: lines("The last pen is removed when you pass this step. Upload any shots and copy the content log (or /scriptevent pw:test report p18).\nPASS = uploaded (or about to)."),
  setup: [{ cmd: CLEAR }, { daytime: "noon" }] };
export const P18_STEPS = [Q0, ...STEPS18, Q9];
export const P18_INDEX = Object.fromEntries(P18_STEPS.map((s, i) => [s.id, i]));
