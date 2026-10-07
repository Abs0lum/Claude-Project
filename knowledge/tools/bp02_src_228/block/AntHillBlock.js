import {
  Block,
  BlockComponentOnPlaceEvent,
  BlockComponentPlayerBreakEvent,
  BlockComponentPlayerInteractEvent,
  BlockComponentPlayerPlaceBeforeEvent,
  BlockComponentRandomTickEvent,
  BlockComponentTickEvent,
  BlockPermutation,
  Dimension,
  EntityEquippableComponent,
  ItemStack,
  world,
} from "@minecraft/server";
import { Vec3 } from "../utils/Vec3";

const ANT_ENTITY_ID = "sf_nba:ant";
const ANT_HILL_BLOCK_ID = "sf_nba:ant_hill";
const ANT_HILL_BASE_BLOCK_ID = "sf_nba:ant_hill_base";
const ANT_HILL_HOLES_NUMBER = [4, 6];

/**
 * @implements {import("@minecraft/server").BlockCustomComponent}
 */
export class AntHillBlock {
  static COMPONENT_ID = "sf_nba:ant_hill";
  static HAS_QUEEN_STATE = "sf_nba:has_queen";
  static WORKERS_STATE = "sf_nba:workers";
  static SOURCE_STATE = "sf_nba:source";
  static MAX_WORKERS = 3;

  constructor() {
    this.onTick = this.onTick.bind(this);
    this.onRandomTick = this.onRandomTick.bind(this);
    this.onPlace = this.onPlace.bind(this);
    this.onPlayerBreak = this.onPlayerBreak.bind(this);
  }

  /**
   * @param {BlockComponentTickEvent} e
   */
  onTick({ block, dimension }) {
    this.#onPlaceOrTick(block, dimension);
  }

  /**
   * @param {BlockComponentOnPlaceEvent} e
   */
  onPlace({ block, dimension }) {
    this.#onPlaceOrTick(block, dimension);
  }

  /**
   * @param {BlockComponentRandomTickEvent} e
   */
  onRandomTick({ block, dimension }) {
    const workers = block.permutation.getState(AntHillBlock.WORKERS_STATE);

    if (workers <= 0) return;
    if (Math.random() >= 0.07) return;

    const { x, y, z } = block.location;
    const neighbors = [
      [1, 0, 0],
      [-1, 0, 0],
      [0, 1, 0],
      [0, -1, 0],
      [0, 0, 1],
      [0, 0, -1],
    ];

    const validPositions = [];

    for (const [dx, dy, dz] of neighbors) {
      const neighbor = dimension.getBlock(new Vec3(x + dx, y + dy, z + dz));
      if (!neighbor) continue;

      if (neighbor.isAir && !dimension.getBlock(new Vec3(x + dx, y + dy - 1, z + dz))?.isAir) {   // 1.3.227: no Block.below() (leaks)
        validPositions.push(neighbor.bottomCenter());
      }
    }

    if (validPositions.length === 0) return;

    const spawnAt =
      validPositions[Math.floor(Math.random() * validPositions.length)];

    block.setPermutation(
      block.permutation.withState(AntHillBlock.WORKERS_STATE, workers - 1),
    );
    dimension.spawnParticle("sf_nba:generic_poof", block.bottomCenter());
    dimension.playSound("sf_nba.ant_hill.enterleave", block.bottomCenter());

    const ant = dimension.spawnEntity(ANT_ENTITY_ID, spawnAt);
    ant.triggerEvent("sf_nba:ant_find_ant_hill_timeout");
  }

  /**
   * @param {BlockComponentPlayerBreakEvent} e
   */
  onPlayerBreak(
    { block, brokenBlockPermutation, player, dimension },
  ) {
    const pos = block.bottomCenter();
    const workers = brokenBlockPermutation.getState(AntHillBlock.WORKERS_STATE);
    const hasQueen = brokenBlockPermutation.getState(
      AntHillBlock.HAS_QUEEN_STATE,
    );

    dimension.playSound("sf_nba.ant_hill.destroy", pos);

    if (workers > 0 || hasQueen) {
      dimension.spawnParticle("sf_nba:generic_poof", pos);
    }

    if (hasQueen) {
      dimension.spawnItem(new ItemStack("sf_nba:queen_ant"), pos);
    }

    //world.sendMessage("Workers on broken Ant Hill: §a" + workers.toString() + "/4§r");
    for (let i = 0; i < workers; i++) {
      const randomX = Math.random() - 0.5;
      const randomZ = Math.random() - 0.5;
      const defPos = { ...pos, x: pos.x + randomX, z: pos.z + randomZ };

      const ant = dimension.spawnEntity(ANT_ENTITY_ID, defPos);
      ant.triggerEvent("sf_nba:ant_find_ant_hill_timeout");
      ant.teleport(defPos, {
        keepVelocity: false,
        facingLocation: player.location,
      });
    }
  }

  /**
   * @param {Block} block
   * @param {Dimension} dimension
   */
  #onPlaceOrTick(block, dimension) {
    if (
      block.permutation.getState(AntHillBlock.HAS_QUEEN_STATE) &&
      block.permutation.getState(AntHillBlock.SOURCE_STATE) === "feature"
    ) {
      this.#buildAntHillHolesAndQueen(dimension, block.location);
    }
  }

  /**
   * @param {Dimension} dimension
   * @param {import("@minecraft/server").Vector3} location
   */
  #buildAntHillHolesAndQueen(dimension, location) {
    let blocks = this.#getAntHillBlocksFrom(dimension, location);
    const antHillHoles = Math.floor(
      Math.random() *
        (ANT_HILL_HOLES_NUMBER[1] - ANT_HILL_HOLES_NUMBER[0] + 1),
    ) + ANT_HILL_HOLES_NUMBER[0];

    /** @type {Block[]} */
    const toUpdateBlocks = [];
    for (let i = 0; i < antHillHoles && blocks.length > 0; i++) {
      const randomIndex = Math.floor(Math.random() * blocks.length);
      toUpdateBlocks.push(blocks[randomIndex]);
      blocks.splice(randomIndex, 1);
    }

    for (const block of toUpdateBlocks) {
      block.setPermutation(
        BlockPermutation.resolve(ANT_HILL_BLOCK_ID, {
          [AntHillBlock.WORKERS_STATE]: this.#getRandomNumberOfWorkers(),
          [AntHillBlock.SOURCE_STATE]: "internal",
        }),
      );
    }

    const queenAntHillBlock =
      toUpdateBlocks[Math.floor(Math.random() * toUpdateBlocks.length)];
    queenAntHillBlock.setPermutation(
      BlockPermutation.resolve(ANT_HILL_BLOCK_ID, {
        [AntHillBlock.HAS_QUEEN_STATE]: true,
        [AntHillBlock.SOURCE_STATE]: "internal",
      }),
    );
  }

  /**
   * @param {Dimension} dimension
   * @param {import("@minecraft/server").Vector3} location
   */
  #getAntHillBlocksFrom(dimension, location) {
    const blocks = [dimension.getBlock(location)]; // Adds the Ant Hill with queen to be randomized again.

    dimension.setBlockType(location, ANT_HILL_BASE_BLOCK_ID);
    const aabb = this.#getAABBFromQueenAntHill(location);

    for (let x = aabb.min.x; x <= aabb.max.x; x++) {
      for (let y = aabb.min.y; y <= aabb.max.y; y++) {
        for (let z = aabb.min.z; z <= aabb.max.z; z++) {
          const block = dimension.getBlock({ x, y, z });

          if (block && block.typeId === ANT_HILL_BASE_BLOCK_ID) {
            blocks.push(block);
          }
        }
      }
    }

    return blocks;
  }

  #getAABBFromQueenAntHill(location) {
    const pos1 = Vec3.add(location, new Vec3(1, 0, 1));
    const pos2 = Vec3.add(location, new Vec3(-1, -4, -1));

    const min = new Vec3(
      Math.min(pos1.x, pos2.x),
      Math.min(pos1.y, pos2.y),
      Math.min(pos1.z, pos2.z),
    );
    const max = new Vec3(
      Math.max(pos1.x, pos2.x),
      Math.max(pos1.y, pos2.y),
      Math.max(pos1.z, pos2.z),
    );

    return { min, max };
  }

  #getRandomNumberOfWorkers() {
    const weights = [25, 55, 20, 0]; // 0, 1, 2, 3 workers
    const sum = weights.reduce((acc, val) => acc + val, 0);
    let random = Math.random() * sum;

    for (let i = 0; i < weights.length; i++) {
      if (random < weights[i]) return i;
      random -= weights[i];
    }

    return random;
  }
}
