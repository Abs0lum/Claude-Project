import {
  EntityComponentTypes,
  ItemStack,
  ItemTypes,
  system,
  world,
} from "@minecraft/server";

let farmingAddonCompatabilityEnabled = false;

const farmingAddonItemCompatability = {
  "sf_nba:venison": "pod_farm:venison_raw",
  "sf_nba:goose": "pod_farm:goose_raw",
  "sf_nba:duck": "pod_farm:duck_raw",
  "sf_nba:cooked_venison": "pod_farm:venison_cooked",
  "sf_nba:cooked_goose": "pod_farm:goose_cooked",
  "sf_nba:cooked_egg": "pod_farm:cooked_egg",
  "sf_nba:cooked_duck": "pod_farm:duck_cooked",
};

world.afterEvents.entitySpawn.subscribe(async (event) => {
  try {
    if (!farmingAddonCompatabilityEnabled) return;

    const entity = event.entity;
    if (entity.typeId !== "minecraft:item") return;

    const itemComponent = entity.getComponent(EntityComponentTypes.Item);
    if (!itemComponent) return;

    const newItemType =
      farmingAddonItemCompatability[itemComponent.itemStack.typeId];
    if (!newItemType) return;

    const itemStack = new ItemStack(
      newItemType,
      itemComponent.itemStack.amount,
    );
    const item = entity.dimension.spawnItem(itemStack, entity.location);
    item.applyImpulse(entity.getVelocity());

    entity.remove();
  } catch (error) {}
});

world.afterEvents.worldLoad.subscribe((event) => {
  try {
    farmingAddonCompatabilityEnabled =
      ItemTypes.get("pod_farm:venison_raw") !== undefined;
  } catch (error) {}
});

world.afterEvents.playerSpawn.subscribe((e) => {
  if (!farmingAddonCompatabilityEnabled) return;
  const player = e.player;
  if (!player) return;
  if (!e.initialSpawn) return;
  // Check full inventory on first spawn only - subsequent replacements are handled by playerInventoryItemChange
  checkPlayerInventory(player);
});

world.afterEvents.playerInventoryItemChange.subscribe((e) => {
  if (!farmingAddonCompatabilityEnabled) return;
  const player = e.player;
  const itemStack = e.itemStack;
  const slot = e.slot;
  if (!player) return;
  if (!itemStack) return;
  if (!slot) return;

  // Verify whether there is a corresponding compatibility item
  const newItemType = farmingAddonItemCompatability[itemStack.typeId];
  if (!newItemType) return;

  // If so, replace the item
  try {
    const newItemStack = new ItemStack(newItemType, itemStack.amount);
    slot.setItem(newItemStack);
  } catch (_) {}
});

function checkPlayerInventory(player) {
  try {
    const inventory = player.getComponent(EntityComponentTypes.Inventory);
    if (!inventory) return;
    const container = inventory.container;
    if (!container) return;

    const size = container.size;

    for (let slotIndex = 0; slotIndex < size; slotIndex++) {
      try {
        const slot = container.getSlot(slotIndex);
        if (!slot || !slot.isValid) return;

        const slotItemStack = slot.getItem();
        if (!slotItemStack) return;

        const newItemType = farmingAddonItemCompatability[slotItemStack.typeId];
        if (!newItemType) return;

        const itemStack = new ItemStack(newItemType, slotItemStack.amount);
        slot.setItem(itemStack);
      } catch (slotError) {}
    }
  } catch (error) {
    console.error("Error initializing world compatibility job:", error);
  }
}
// system.afterEvents.scriptEventReceive.subscribe(async (event) => {
//     const id = event.id

//     if (id !== 'sf_nba:compatability_loot_update') return

//     const entity = event.sourceEntity

//     if(!farmingAddonCompatabilityEnabled) return

//     entity.triggerEvent('sf_nba:enable_farming_addon_loot')
// })
