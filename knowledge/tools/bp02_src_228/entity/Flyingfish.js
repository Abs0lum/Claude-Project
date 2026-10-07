import { system } from "@minecraft/server";

const water = [
  "minecraft:water",
  "minecraft:flowing_water",
];

function getDepth(dimension, location) {
  for (let i = location.y; i < location.y + 15; i++) {
    const block = dimension.getBlock({ x: location.x, y: i, z: location.z });
    if (water.includes(block.typeId) && dimension.getBlock({ x: location.x, y: i + 1, z: location.z })?.isAir) {   // 1.3.227: no Block.above() (leaks)
      return i - location.y + 1;
    }
  }
}

system.afterEvents.scriptEventReceive.subscribe((e) => {
  if (e.id == "sf_nba:flying_fish.leap") {
    const { x: dx, z: dz } = e.sourceEntity.getViewDirection();
    const height = getDepth(e.sourceEntity.dimension, e.sourceEntity.location);

    if (!height) return;
    e.sourceEntity.applyImpulse({ x: dx * 0.1, y: height * 0.25, z: dz * 0.1 });
  }
});
