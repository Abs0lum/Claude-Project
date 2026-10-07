// Identification Diagnostics BP — v1.3.34
//
// Purpose: When you break any block, chat prints the full block identifier,
// coordinates, and some useful diagnostics. Designed for PlayStation / console
// use where F3 isn't available — you can break a block, take a phone photo of
// the chat, and know exactly what block identifier to send for investigation.
//
// Load this pack LAST in the world's behavior pack list (highest priority).
// It does not modify any blocks — it only observes break events.
//
// Commands (type in chat, cheats on — the same way as /scriptevent civ:markers):
//   /scriptevent pw:diag on        Enable announcements (brief)
//   /scriptevent pw:diag off       Disable announcements
//   /scriptevent pw:diag verbose   Include permutation states + dimension + texture hint
//   /scriptevent pw:diag brief     Back to default brief mode
//   /scriptevent pw:diag status    Show the current mode
//   /scriptevent pw:diag help      Show help
// Shortcut ids also work: /scriptevent diag:off, diag:on, diag:verbose, diag:brief, diag:status, diag:help
//
// v1.3.34 (2026-09-22): the old "!diag" chat commands used world.beforeEvents.chatSend, which is NOT in
// the stable @minecraft/server this pack pins (beta only), so they never worked. /scriptevent is stable.
//
// Setting is per-player (uses dynamic properties) so multiplayer works cleanly.

import { world, system } from "@minecraft/server";

const MODE_KEY      = "pw_diag_mode";       // "off" | "brief" | "verbose"
const DEFAULT_MODE  = "brief";

// Cosmetic formatting for chat
const C = {
    white:  "§f",
    gray:   "§7",
    dgray:  "§8",
    aqua:   "§b",
    yellow: "§e",
    gold:   "§6",
    green:  "§a",
    red:    "§c",
    reset:  "§r",
    bold:   "§l",
    italic: "§o",
};

function getMode(player) {
    try {
        const v = player.getDynamicProperty(MODE_KEY);
        if (typeof v === "string" && (v === "off" || v === "brief" || v === "verbose")) {
            return v;
        }
    } catch (_) {}
    return DEFAULT_MODE;
}

function setMode(player, mode) {
    try {
        player.setDynamicProperty(MODE_KEY, mode);
    } catch (_) {}
}

function formatCoords(block) {
    // Coord triplet
    return `${block.x}, ${block.y}, ${block.z}`;
}

function shortId(fullId) {
    // Strip "minecraft:" prefix for brevity when that's the namespace
    if (fullId.startsWith("minecraft:")) return fullId.slice(10);
    return fullId;
}

// Announce a broken block to the player who broke it
function announceBreak(event) {
    const player = event.player;
    if (!player) return;

    const mode = getMode(player);
    if (mode === "off") return;

    const permutation = event.brokenBlockPermutation;
    const block = event.block;
    if (!permutation || !block) return;

    const type = permutation.type;
    const fullId = type.id;                    // e.g. "minecraft:brain_coral_wall_fan"
    const shortName = shortId(fullId);         // e.g. "brain_coral_wall_fan"

    // Brief: highlighted id + coords
    // Verbose: + dimension + permutation states + a compact "possible texture paths" hint
    let msg = "";
    msg += `${C.dgray}[${C.gold}BLOCK${C.dgray}]${C.reset} `;
    msg += `${C.aqua}${C.bold}${shortName}${C.reset}`;
    if (fullId !== `minecraft:${shortName}`) {
        // Not the default namespace; show full id
        msg += ` ${C.gray}(${fullId})${C.reset}`;
    }
    msg += ` ${C.gray}@ ${formatCoords(block)}${C.reset}`;

    if (mode === "verbose") {
        // Dimension
        const dimId = block.dimension?.id ?? "?";
        msg += `\n${C.gray}  dim: ${shortId(dimId)}${C.reset}`;

        // Permutation states
        try {
            const allStates = permutation.getAllStates();
            if (allStates) {
                const keys = Object.keys(allStates);
                if (keys.length > 0) {
                    const statePairs = keys.slice(0, 6).map(k => `${k}=${allStates[k]}`).join(", ");
                    msg += `\n${C.gray}  states: ${statePairs}${C.reset}`;
                    if (keys.length > 6) {
                        msg += `${C.gray} (+${keys.length - 6} more)${C.reset}`;
                    }
                }
            }
        } catch (_) {}

        // Texture-path hint (most useful for diagnostics — suggests where the texture
        // SHOULD live for our pack to replace this block)
        const texName = shortName.replace(/_wall_fan$/, "_wall_fan").replace(/_fan$/, "_fan");
        msg += `\n${C.gray}  likely texture: ${C.dgray}textures/blocks/${texName}.png${C.reset}`;
    }

    player.sendMessage(msg);
}

// The diag verbs — one place for every way of asking (was handleChat's switch)
function runDiag(player, arg) {
    switch (arg) {
        case "":
        case "help":
            player.sendMessage([
                `${C.gold}${C.bold}== Identification Diagnostics ==${C.reset}`,
                `${C.aqua}/scriptevent pw:diag on${C.reset}       ${C.gray}enable brief announcements${C.reset}`,
                `${C.aqua}/scriptevent pw:diag off${C.reset}      ${C.gray}disable announcements${C.reset}`,
                `${C.aqua}/scriptevent pw:diag brief${C.reset}    ${C.gray}short: id + coords${C.reset}`,
                `${C.aqua}/scriptevent pw:diag verbose${C.reset}  ${C.gray}long: + states + texture hint${C.reset}`,
                `${C.aqua}/scriptevent pw:diag status${C.reset}   ${C.gray}show current mode${C.reset}`,
            ].join("\n"));
            break;
        case "on":
            setMode(player, "brief");
            player.sendMessage(`${C.green}✓ Diagnostics ON (brief)${C.reset}`);
            break;
        case "off":
            setMode(player, "off");
            player.sendMessage(`${C.red}✗ Diagnostics OFF${C.reset}`);
            break;
        case "brief":
            setMode(player, "brief");
            player.sendMessage(`${C.green}✓ Mode: brief${C.reset}`);
            break;
        case "verbose":
            setMode(player, "verbose");
            player.sendMessage(`${C.green}✓ Mode: verbose${C.reset}`);
            break;
        case "status":
            player.sendMessage(`${C.gold}Current mode: ${C.aqua}${getMode(player)}${C.reset}`);
            break;
        default:
            player.sendMessage(`${C.red}Unknown diag command. Try ${C.aqua}/scriptevent pw:diag help${C.reset}`);
    }
}

// Who typed the command: the player who ran /scriptevent; from a command block or the
// server console there is no player, so fall back to the first player (single-player worlds)
function commandPlayer(ev) {
    if (ev.sourceEntity && ev.sourceEntity.typeId === "minecraft:player") return ev.sourceEntity;
    try { return world.getAllPlayers()[0]; } catch (_) { return undefined; }
}

// "/scriptevent pw:diag off" -> "off" ; "/scriptevent diag:off" -> "off" ; anything else -> null
function diagVerb(id, message) {
    const first = String(message ?? "").trim().split(/\s+/)[0].toLowerCase();
    if (id === "pw:diag") return first;
    if (typeof id === "string" && id.startsWith("diag:")) return id.slice(5).toLowerCase();
    return null;
}

// Greet player on join so they know the pack is active
function greetPlayer(player) {
    const mode = getMode(player);
    player.sendMessage([
        `${C.gold}${C.bold}[Identification Diagnostics]${C.reset} ${C.gray}loaded, mode: ${C.aqua}${mode}${C.reset}`,
        `${C.gray}Break any block to see its id. Type ${C.aqua}/scriptevent pw:diag help${C.gray} for options.${C.reset}`,
    ].join("\n"));
}

// -----------------------------------------------------------------------------
// Subscriptions (root context — required by @minecraft/server 2.x)
// -----------------------------------------------------------------------------

world.afterEvents.playerBreakBlock.subscribe((event) => {
    try { announceBreak(event); } catch (e) { /* swallow */ }
});

system.afterEvents.scriptEventReceive.subscribe((ev) => {
    try {
        const verb = diagVerb(ev.id, ev.message);
        if (verb === null) return;
        const player = commandPlayer(ev);
        if (player) runDiag(player, verb);
    } catch (e) { /* swallow */ }
}, { namespaces: ["pw", "diag"] });

world.afterEvents.playerSpawn.subscribe((event) => {
    if (!event.initialSpawn) return;
    try { greetPlayer(event.player); } catch (e) { /* swallow */ }
});

try { console.warn("[PW-VERSION] BP-03 Identification Diagnostics v1.3.34 — version-flag law"); } catch {}
