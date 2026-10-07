import { BlockVolume, system, world } from "@minecraft/server";

const Entities = new Set();

const ENTITY = "sf_nba:kakapo";
const EFFECTS = [
  { name: "night_vision", duration: 1200, amplifier: 0 },
  { name: "speed", duration: 1200, amplifier: 1 },
];

world.afterEvents.playerInteractWithEntity.subscribe((e) => {
  const { beforeItemStack, player, target } = e;

  if (
    target.typeId != ENTITY ||
    beforeItemStack?.typeId != "minecraft:spore_blossom"
  ) return;

  for (const effect of EFFECTS) {
    player.addEffect(effect.name, effect.duration, {
      amplifier: effect.amplifier,
      showParticles: false,
    });
  }
});

// AbsolutRealism 1.3.227 (gate 226-2: a 3.2 s watchdog hang was interrupted in this loop): only kakapos are kept — the
// add-on's set held EVERY loaded and spawned entity and walked it each tick; the music check now runs twice a second.
world.afterEvents.entityLoad.subscribe((e) => {
  try { if (e.entity.typeId === ENTITY) Entities.add(e.entity); } catch (err) {}
});

world.afterEvents.entitySpawn.subscribe((e) => {
  try { if (e.entity.typeId === ENTITY) Entities.add(e.entity); } catch (err) {}
});

system.runInterval(() => {
  for (const entity of Entities) {
    if (!entity.isValid) {
      Entities.delete(entity);
      continue;
    }
    if (entity.typeId != ENTITY) continue;

    const { dimension, location } = entity;
    const soundRange = 3;
    const volume = new BlockVolume(
      {
        x: location.x - soundRange,
        y: location.y - soundRange,
        z: location.z - soundRange,
      },
      {
        x: location.x + soundRange,
        y: location.y + soundRange,
        z: location.z + soundRange,
      },
    );

    try {
      const jukeboxLocations = dimension.getBlocks(volume, {
        includeTypes: ["minecraft:jukebox"],
        allowUnloadedChunks: true,
      });
      let hasNearbyPlayingJukebox = false;

      for (const location of jukeboxLocations.getBlockLocationIterator()) {
        const block = dimension.getBlock(location);
        const record = block.getComponent("minecraft:record_player");

        if (record?.isPlaying()) {
          hasNearbyPlayingJukebox = true;
          break;
        }
      }

      entity.setProperty("sf_nba:has_music_nearby", hasNearbyPlayingJukebox);
    } catch (e) {}
  }
}, 10);
