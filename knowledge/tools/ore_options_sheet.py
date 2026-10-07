#!/usr/bin/env python3
"""ore_options_sheet.py — side-by-side ore art options (his 15:12 CT 10-02 request): for each ore, the image from every
pack on hand (Patrix 256 = ours now, Stratum 256, GameplayFriendly 128, his April Drive pack 64) + our plain base block.
Writes /mnt/user-data/outputs/ORE-ART-OPTIONS-<group>-2026-10-02.png (stone / deepslate / nether)."""
import io
import os
import zipfile

from PIL import Image, ImageDraw

ROOT = "/home/claude/"
PATRIX = zipfile.ZipFile(ROOT + "_intake/patrix262_256/Patrix_26.2_256x_basic.zip")
STRATUM = zipfile.ZipFile(ROOT + "_intake/newpacks-1001/Stratum 256x.zip")
GFT = zipfile.ZipFile(ROOT + "_intake/newpacks-1001/GameplayFriendlyTextures_128x_v12.zip")
BLOCK_DIR = "/textures/block/"
OUR_BASE = {"stone": "stone.png", "deepslate": "deepslate_0.png", "nether": "netherrack_v0.png"}
TILE = 240
STONE_ORES = ["coal_ore", "iron_ore", "copper_ore", "gold_ore", "redstone_ore", "lapis_ore", "emerald_ore", "diamond_ore"]
GROUPS = {"stone": STONE_ORES, "deepslate": ["deepslate_" + o for o in STONE_ORES],
          "nether": ["nether_gold_ore", "nether_quartz_ore"]}


def stem_index(z):
    return {n.split("/")[-1][:-4]: n for n in z.namelist() if n.endswith(".png") and BLOCK_DIR in n}


def zip_image(z, index, stem):
    return Image.open(io.BytesIO(z.read(index[stem]))).convert("RGBA") if stem in index else None


def sources(stem, indexes):
    old = ROOT + "_intake/drive-blocks-0423/" + stem + ".png"
    return [("Patrix 256 (ours now)", zip_image(PATRIX, indexes["p"], stem)),
            ("Stratum 256", zip_image(STRATUM, indexes["s"], stem)),
            ("GameplayFriendly 128", zip_image(GFT, indexes["g"], stem)),
            ("Your old pack 64 (Drive)", Image.open(old).convert("RGBA") if os.path.exists(old) else None)]


def main():
    indexes = {"p": stem_index(PATRIX), "s": stem_index(STRATUM), "g": stem_index(GFT)}
    for group, ores in GROUPS.items():
        base = Image.open(ROOT + "_build/rp04-154/textures/blocks/" + OUR_BASE[group]).convert("RGBA")
        sheet = Image.new("RGBA", (150 + 5 * (TILE + 10), 6 + len(ores) * (TILE + 26)), (26, 26, 26, 255))
        draw = ImageDraw.Draw(sheet)
        for row, stem in enumerate(ores):
            y = 6 + row * (TILE + 26)
            draw.text((6, y + TILE // 2), stem, fill=(255, 220, 120))
            for col, (label, image) in enumerate(sources(stem, indexes) + [("our plain " + group, base)]):
                x = 150 + col * (TILE + 10)
                if image is None:
                    draw.text((x, y), label, fill="white")
                    draw.rectangle((x, y + 14, x + TILE, y + 14 + TILE), outline=(90, 90, 90))
                    draw.text((x + TILE // 2 - 14, y + TILE // 2), "none", fill=(150, 150, 150))
                    continue
                draw.text((x, y), f"{label}  {image.size[0]}px", fill="white")
                resample = Image.LANCZOS if image.size[0] >= TILE else Image.NEAREST
                sheet.paste(image.resize((TILE, TILE), resample), (x, y + 14))
        out = f"/mnt/user-data/outputs/ORE-ART-OPTIONS-{group}-2026-10-02.png"
        sheet.save(out)
        print(out, sheet.size)


if __name__ == "__main__":
    main()
