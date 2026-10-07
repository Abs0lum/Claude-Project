import { system, world } from "@minecraft/server";

const DEER_TYPE = "sf_nba:deer";
const GRAZING_PROP = "sf_nba:is_grazing";
const EAT_DURATION_TICKS = 36;
// AbsolutRealism 1.3.227 (profiled at city II: every tick, 1.4 ms): the check runs every DEER_EVERY ticks with the
// chances scaled by it, so a deer grazes as often as before
const DEER_EVERY = 4;
const SUCCESS_CHANCE_ADULT = 0.001 * DEER_EVERY;
const SUCCESS_CHANCE_BABY = 0.02 * DEER_EVERY;

/** @type {Map<string, { endTick: number, x: number, y: number, z: number, dimensionId: string }>} */
const grazingDeer = new Map();

const DIMENSION_IDS = ["overworld", "nether", "the_end"];

function isGrazeableBlock(block) {
  if (!block?.isValid) return false;
  const id = block.typeId;
  return (
    id === "minecraft:grass_block" ||
    id === "minecraft:tall_grass" ||
    id === "minecraft:short_grass" ||
    id === "minecraft:short_dry_grass" ||
    id === "minecraft:tall_dry_grass"
  );
}

function replaceBlockWithEaten(dimension, x, y, z) {
  try {
    const block = dimension.getBlock({ x, y, z });
    if (!block?.isValid) return;
    const id = block.typeId;
    const pos = { x: x + 0.5, y: y + 0.5, z: z + 0.5 };

    if (id === "minecraft:grass_block") {
      dimension.playSound("dig.grass", pos, { volume: 0.6, pitch: 0.8 });
      block.setType("minecraft:dirt");
    } else if (
      id === "minecraft:tall_grass" ||
      id === "minecraft:short_grass" ||
      id === "minecraft:short_dry_grass" ||
      id === "minecraft:tall_dry_grass"
    ) {
      dimension.playSound("dig.grass", pos, { volume: 0.5, pitch: 0.9 });
      dimension.spawnParticle("sf_nba:generic_poof", pos);
      block.setType("minecraft:air");
    }
  } catch (_) {}
}

system.runInterval(() => {
  const currentTick = system.currentTick;

  for (const dimensionId of DIMENSION_IDS) {
    const dimension = world.getDimension(dimensionId);
    for (const entity of dimension.getEntities({ type: DEER_TYPE })) {
      if (!entity?.isValid) continue;

      const key = entity.id;

      // Finish grazing: replace block and clear property
      const pending = grazingDeer.get(key);
      if (pending && currentTick >= pending.endTick) {
        replaceBlockWithEaten(
          dimension,
          pending.x,
          pending.y,
          pending.z,
        );
        try {
          entity.setProperty(GRAZING_PROP, false);
          entity.triggerEvent("sf_nba:stop_grazing");
        } catch (_) {}
        grazingDeer.delete(key);
        continue;
      }

      if (pending) continue;

      const loc = entity.location;
      const blockX = Math.floor(loc.x);
      const blockY = Math.floor(loc.y) - 1;
      const blockZ = Math.floor(loc.z);

      const blockBelow = dimension.getBlock({
        x: blockX,
        y: blockY,
        z: blockZ,
      });

      if (!isGrazeableBlock(blockBelow)) continue;

      const isBaby = entity.getComponent("is_baby") ?? false;
      const chance = isBaby ? SUCCESS_CHANCE_BABY : SUCCESS_CHANCE_ADULT;
      if (Math.random() >= chance) continue;

      grazingDeer.set(key, {
        endTick: currentTick + EAT_DURATION_TICKS,
        x: blockX,
        y: blockY,
        z: blockZ,
        dimensionId,
      });
      try {
        entity.setProperty(GRAZING_PROP, true);
        entity.triggerEvent("sf_nba:start_grazing");
      } catch (_) {}
    }
  }
}, DEER_EVERY);

// Clear grazing state when a deer is removed
world.afterEvents.entityRemove.subscribe((e) => {
  if (e.removedEntity?.typeId === DEER_TYPE) {
    grazingDeer.delete(e.removedEntity.id);
  }
});
