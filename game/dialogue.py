"""Dialogue pools for creature interactions and active actions."""

import random

STIRGE = {
    0: [
        "It looks at you with one large eye. Mostly it is looking at your blood.",
        "It skitters sideways when you approach. Still hungry.",
        "Its wings twitch. You're not sure if that means anything.",
        "It has found something dead nearby. You choose not to look closely.",
        "It watches you from a low branch. The proboscis is doing something unsettling.",
    ],
    1: [
        "It settles a little closer than before. Progress.",
        "It watches you work. You get the impression it has opinions.",
        "It didn't flee when you walked past. That felt significant.",
        "It is roosting in the same spot it was yesterday. It has claimed a spot.",
        "It made a sound at you. You're going to interpret that as friendly.",
    ],
    2: [
        "It drops something at your feet. Forage, roughly, if you are charitable.",
        "It arrived before you did this morning. You are not sure how to feel about that.",
        "You found it asleep near the statue. It woke up and looked at you like you were the one out of place.",
        "It is becoming reliable in the way that ugly things sometimes are. Quietly.",
        "It brought back more than it needed to. You're choosing to call that generosity.",
    ],
    3: [
        "It has taken to sitting very still and watching the grove boundary. You're not sure what it sees.",
        "It made a sound you've never heard from it before. The grove felt different after.",
        "It was there when you arrived. It will probably be there when you leave.",
        "You've stopped finding it strange that it's always near. The grove would feel wrong without it.",
        "It looked at the tree line for a long moment. Then back at you. You checked on things.",
    ],
}

BLINK_DOG = {
    0: [
        "It appears three feet to your left, looking extremely pleased with itself.",
        "It teleports mid-run and crashes into a shrub. Both of you pretend this didn't happen.",
        "It has brought you something. It is a sock. Where did it get a sock.",
        "It blinks directly onto the statue and immediately falls off. Twice.",
        "It is trying to sit still. It lasts four seconds before blinking away.",
    ],
    1: [
        "It appeared behind you instead of on top of you. Improvement.",
        "It came back when you called. Eventually. After one extra teleport.",
        "It is sitting still. For almost four seconds. A record.",
        "It blinked away mid-fetch and came back with the wrong thing. But it came back.",
        "It teleported into the clearing and looked very proud of its aim.",
    ],
    2: [
        "It brought back actual forage this time. You didn't ask where it went to get it.",
        "It is attempting to herd the stirge. The stirge is unimpressed. The blink dog is undeterred.",
        "It sat next to you and didn't teleport for almost a minute. You suspect it was trying.",
        "It found something useful and brought it back immediately. On purpose, you think.",
        "It checked on you twice this morning. Neither time did it land correctly, but the intent was there.",
    ],
    3: [
        "It scouted ahead on your last forage trip. You found twice what you expected.",
        "It teleports constantly but always comes back. This feels like loyalty in the only language it has.",
        "It is asleep in a patch of sun, three inches from where it fell asleep. Essentially still.",
        "It has started checking on the stirge. The stirge disapproves. The blink dog doesn't notice.",
        "It blinked back to you from somewhere far away, dropped something at your feet, and left again. You're not sure what to make of that.",
    ],
}

MILESTONES = {
    "stirge": {
        1: "The stirge has stopped targeting you specifically. It has found other things to be hungry near.",
        2: "The stirge has a roost now. The same spot, every night.",
        3: "It brings things back consistently. Not always useful things. Consistently.",
    },
    "blink_dog": {
        1: "The blink dog has stopped teleporting directly onto you. Most of the time.",
        2: "It comes back when called. You've started calling.",
        3: "Its contributions are becoming reliable. Whatever it brings, it brings on purpose now.",
    },
}

STIRGE_FEED = [
    "A small, embarrassingly eager sound. It does not make eye contact after.",
    "It eats quickly. Then looks up. Then back down. Then up again.",
    "It takes the food with surprising gentleness. A pause. Then it nudges your hand.",
    "It watches the food the entire time you're placing it. Does not pretend otherwise.",
    "The stirge is grateful in a way that is slightly mortifying for both of you.",
]

BLINK_DOG_FEED = [
    "It teleports directly onto the food before you've finished setting it down.",
    "There's a small pop. The food is gone. The blink dog is behind you now.",
    "It reappears on the other side of the clearing, looking briefly surprised, as usual.",
    "Gone. The food is gone. You didn't see it happen.",
    "It blinks three times in quick succession and the food simply ceases to exist.",
]

FORAGE = [
    "You return with roots and berries, a little heartwood from fallen branches.",
    "The grove gives what it can. You bring it back.",
    "You foraged along the eastern edge. More than you expected.",
    "The blink dog followed you halfway. Some of this is from places you didn't go.",
    "Quiet work. The kind the grove rewards.",
]

TEND_STATUE = [
    "You rest your hands on the statue. The stone is warm. The grove feels steadier.",
    "You tend the offering at the base. Silvanus doesn't answer, but the grove hums.",
    "You clear the deadfall around the base. The moss on the statue is healthy.",
    "You spend time with the statue. The glamour in the grove settles, reinforced.",
    "The stone is cool this morning. You warm it with your hands.",
]


def pick(pool):
    return random.choice(pool) if pool else ""
