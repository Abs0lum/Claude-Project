import { system, world } from "@minecraft/server";

world.afterEvents.entitySpawn.subscribe((event) => {
  const entity = event.entity;

  if (entity.typeId != "sf_nba:sloth") return;

  if (isOnLeaf(entity.dimension, entity.location)) {
    entity.triggerEvent("sf_nba:add_hanging");
  } else if (!isOnLeaf(entity.dimension, entity.location)) {
    entity.triggerEvent("sf_nba:add_ground");
  }
});

system.afterEvents.scriptEventReceive.subscribe((e) => {
  const entity = e.sourceEntity;

  if (!entity) return;
  if (!entity.isValid) return;

  if (e.id == "sf_nba:sloth_state_check") {
    if (entity.typeId != "sf_nba:sloth") {
      console.warn("Error: sf_nba:sloth can only be called from an sloth");

      return;
    }

    if (
      isOnLeaf(entity.dimension, entity.location) &&
      !entity.getProperty("sf_nba:hanging")
    ) {
      entity.triggerEvent("sf_nba:add_hanging");
    } else if (
      !isOnLeaf(entity.dimension, entity.location) &&
      entity.getProperty("sf_nba:hanging")
    ) {
      entity.triggerEvent("sf_nba:add_ground");
    }
  }

  if (e.id == "sf_nba:sloth_spawn_on_tree") {
    for (let i = 0; i < 16; i++) {
      const { location } = entity;
      const block = entity.dimension.getBlock({
        x: location.x,
        y: location.y + i,
        z: location.z,
      });

      if (block.typeId == "minecraft:jungle_leaves") {
        for (let j = 0; j < 7; j++) {
          const blockAbove = entity.dimension.getBlock({ x: location.x, y: location.y + i + j, z: location.z });   // 1.3.227: no Block.above() (leaks)
          if (!blockAbove || !blockAbove.isAir) continue;
          return entity.teleport(blockAbove.location);
        }
      }
    }
  }
});

function isOnLeaf(dimension, pos) {
  try {
    let block1 = dimension.getBlock({ x: pos.x, y: pos.y - 1, z: pos.z });
    let block2 = dimension.getBlock({ x: pos.x, y: pos.y - 2, z: pos.z });
    if (
      (block1.permutation.matches("minecraft:leaves") ||
        block1.permutation.matches("minecraft:leaves2")) &&
      block2.permutation.matches("minecraft:air")
    ) {
      return true;
    }
  } catch (err) {}

  return false;
}
