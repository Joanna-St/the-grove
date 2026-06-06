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
    "owlbear": {
        1: "The owlbear has stopped startling when you approach. It has decided you are not a threat. Probably.",
        2: "It has a roost in the thicket now. It expects you to know which one.",
        3: "The thicket is better tended than you left it. The owlbear has noticed things you missed.",
    },
    "pseudodragon": {
        1: "The pseudodragon has descended to a lower branch. It has not said this is for you. It is for you.",
        2: "It chirruped at you by name, or close enough. You've started answering.",
        3: "The canopy sings at dusk now. The glamour rises when it does.",
    },
    "flumph": {
        1: "The flumph has a colour it uses specifically for you. You're learning what it means.",
        2: "It is communicating now. You understand more than you expected.",
        3: "The boundary is quieter on its side. Whatever it does there, it does it for the grove.",
    },
    "moss_wisp": {
        1: "The moss wisp comes to the clearing sometimes. This is not nothing.",
        2: "The oldwood is more generous than it was. You're not the only reason.",
        3: "You don't need to speak. The grove translates. The wisp has been speaking all along.",
    },
    "pixie": {
        1: "The pixie has started learning which things are yours. It still touches them. More carefully now.",
        2: "It is helping in ways you can predict. Occasionally.",
        3: "The grove is brighter with it here. Not a metaphor. Measurably brighter.",
    },
    "displacer_beast": {
        1: "The displacer beast has been seen closer to the heartstone. Not close. Closer.",
        2: "You have an understanding now. Neither of you has said so.",
        3: "It chose the grove. You're not sure what it left behind to do that.",
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
    "There's a small pop. The food is on the other side of the clearing. So is the blink dog.",
    "The food is gone. The blink dog is gone. You're not sure either of them were ever here.",
    "It ate with the focused intensity of something that has been thinking about this specific moment all day.",
    "It reappeared next to you a moment later, licked your hand, and was gone again before you could react.",
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


OWLBEAR = {
    0: [
        "It is enormous. It is also, somehow, trying very hard not to break anything.",
        "It looks at you. You look at it. It looks away first. You're not sure what that means.",
        "It moved a fallen log to get a better view of the grove. The log is not where you left it.",
        "It has a sound somewhere between a hoot and a growl. It seems to use this for everything.",
        "It is sitting very still near the tree line, which is more frightening than if it were moving.",
    ],
    1: [
        "It chose a spot closer to the clearing today. Not close. Closer.",
        "It watched you forage and didn't follow, which might be restraint.",
        "It left something at the edge of the clearing. Bark, mostly. You thanked it anyway.",
        "It hoots when it sees you arrive. You're choosing to call that a greeting.",
        "It is moving more carefully around the grove now. Like it knows it's large.",
    ],
    2: [
        "It has started nudging fallen branches toward the statue. You're not sure it knows why.",
        "You found it asleep in the thicket, one ear twitching. It woke up and looked embarrassed.",
        "It brought back more heartwood than it could carry comfortably. It managed anyway.",
        "It hoots twice when you leave. Once when you return. You've started counting.",
        "It sat beside you for a while without doing anything in particular. The grove felt steadier.",
    ],
    3: [
        "It positions itself at the grove's edge each morning. Something about its presence keeps things quiet.",
        "You found it sitting with the stirge. Neither of them looked comfortable about it.",
        "It has started clearing deadfall without being asked. The thicket is tidier than you left it.",
        "It hoots at the tree line sometimes and nothing comes out of it. You're grateful.",
        "The grove is bigger with it in it. Not just in size.",
    ],
}

PSEUDODRAGON = {
    0: [
        "It is watching you from extremely high up, with an expression you can only describe as judging.",
        "It flew off when you looked directly at it. This will require patience.",
        "It has opinions about where you stand. It expresses these by moving to a higher branch.",
        "A small, dismissive sound from somewhere in the canopy. You don't know what you did wrong.",
        "It is very small and very certain about everything. You're not sure how to feel about that.",
    ],
    1: [
        "It allowed you to see it today, which felt like an achievement.",
        "It didn't leave when you sat beneath its branch. Progress.",
        "It made a sound that wasn't quite a growl. You're interpreting that as interest.",
        "It watched you tend the statue from close enough to count. You counted.",
        "It descended to a lower branch this morning. Still out of reach. But lower.",
    ],
    2: [
        "It landed on the statue briefly and looked at you. Then went back up. The moment felt deliberate.",
        "You offered your arm and it considered this for a long time before deciding against it.",
        "It brought something small and shiny to the canopy. You didn't ask what it was.",
        "It is less dismissive now. More like it has evaluated you and found you adequate.",
        "You arrived this morning and suddenly knew it had noticed. You're calling that a greeting.",
    ],
    3: [
        "It landed on your shoulder. Just for a moment. Both of you pretended to be calm about it.",
        "It has started singing at dusk. The glamour in the grove rises noticeably when it does.",
        "It keeps watch from the canopy and has started making a sound when anything approaches the boundary.",
        "It still has opinions about everything. Now it shares them with you directly.",
        "The grove feels different with something keeping watch above it. More complete.",
    ],
}

FLUMPH = {
    0: [
        "It floats at the grove boundary, glowing faintly. You're not sure if it's cautious or curious. Possibly both.",
        "It changes colour when you approach. You don't know what the colours mean.",
        "It made a soft, wet sound and drifted away. You do not know if you did something wrong.",
        "Its tentacles trail gently below it. It moves like it's thinking about something.",
        "It has been floating in the same place for an hour. Its glow shifts slowly, in a rhythm you can't quite place.",
    ],
    1: [
        "It is glowing a little warmer now. You're choosing to call that welcome.",
        "It drifted closer when you were tending the statue. It watched the whole thing.",
        "It made a sound you hadn't heard from it before. You felt briefly calm, which surprised you.",
        "It has found a spot it prefers and returns to it. You've stopped startling when you see it there.",
        "It changed colour when the stirge flew past. You're not sure what it was communicating.",
    ],
    2: [
        "It glows a specific colour when you arrive each morning. You think you know what it means.",
        "It drifted very close today and stayed for a while. You felt it was paying attention.",
        "It made a sound you've come to understand as contentment. At least, that's your interpretation.",
        "You found it near the boundary again, but facing inward this time. Watching over things.",
        "It brightened when you looked at it. You brightened back. This felt like something.",
    ],
    3: [
        "It has started touching the boundary with its tentacles at dusk. The light on that side dims. You're grateful.",
        "You understand most of its colours now. It has a great deal to say.",
        "It is always a little warmer near the flumph. You've stopped questioning it.",
        "It communicates something complicated and kind whenever you're tired. You feel it before you understand it.",
        "The boundary is quieter with it there. Whatever it does at the edge, it works.",
    ],
}

MOSS_WISP = {
    0: [
        "It drifts slowly through the oldwood. Ancient and quiet.",
        "It is old. You can't explain how you know that. You just know.",
        "It doesn't approach. It doesn't flee. It simply continues.",
        "The moss near it is thicker than it should be. You notice this.",
        "You stood near it for a while. It didn't acknowledge you. The grove did.",
    ],
    1: [
        "It drifted a little toward the clearing today. A little.",
        "It paused near the statue for a long moment before continuing.",
        "The forage you found near it was older growth than usual. Better.",
        "It made no sound, but something in the grove settled when it passed.",
        "It is aware of you now. That's different from before.",
    ],
    2: [
        "You walked near it and the grove smelled different. Older. Familiar in a way you can't name.",
        "It moved toward you once. Only a few steps. Then it stopped and waited.",
        "You found it near the heartstone at dawn. It left before you could say anything. Some things are enough.",
        "The oldwood is more generous since it arrived. You're not sure if that's cause or consequence.",
        "It doesn't speak, exactly. But you're starting to hear it anyway.",
    ],
    3: [
        "It has started coming to the heartstone at dusk. You don't speak. You don't need to.",
        "The grove grows differently near it. You've stopped trying to explain it.",
        "You feel it when it's there, even before you see it. The roots know.",
        "It has lived through things you will never see. It shares none of it. You understand all of it.",
        "The oldwood has been here longer than memory. The moss wisp may have been here longer than that.",
    ],
}

PIXIE = {
    0: [
        "You heard it before you saw it. You still haven't seen it clearly.",
        "Something small and fast rearranged the forage pile while you weren't looking.",
        "A brief, bright light. Then nothing. Then your boot is in a tree.",
        "It left dust on the statue. You're not sure if this was reverence or vandalism.",
        "It is extremely interested in everything and has the attention span to match.",
    ],
    1: [
        "It slowed down enough for you to see it. Then immediately did something inexplicable.",
        "It brought you something. You're not sure what it is. It seems pleased with itself.",
        "It stayed in one place for almost thirty seconds. You felt this was significant.",
        "It has opinions about the arrangement of the grove. It is acting on them.",
        "It spoke to you in a language you don't know. It seemed to think you understood.",
    ],
    2: [
        "It is helping, probably. The results are chaotic. The intention is kind.",
        "You found the clearing rearranged this morning. Somehow it's better.",
        "It sat on your shoulder for a moment. Both of you were surprised.",
        "It is becoming more predictable. You're using that term loosely.",
        "It left something useful by the statue. You're taking this as deliberate.",
    ],
    3: [
        "It went ahead on your last forage trip and came back three times mid-route for no reason. You still found more than usual.",
        "It has decided it is in charge of the other creatures in an emergency. They have not agreed to this. It works anyway.",
        "You can't always see it. You can always tell. The grove is brighter when it's there, and it knows you know.",
        "It has settled into a pattern. For a pixie, this is extraordinary.",
        "It leaves gifts. They are always slightly wrong and completely right.",
    ],
}

DISPLACER_BEAST = {
    0: [
        "It is further away than it appears. You are learning not to close the distance.",
        "You caught movement at the edge of the oldwood. When you looked, nothing was there. Or something was.",
        "It watches from a position that is wrong in a way you can't quite articulate.",
        "It made no sound. You knew it was there anyway.",
        "It hasn't left. That feels like the most you can say right now.",
    ],
    1: [
        "It appeared where you expected it not to be. This is, apparently, normal.",
        "It walked through the clearing without vanishing. You're not sure that was for your benefit.",
        "It sat near the boundary for a long time and then was somewhere else entirely.",
        "You caught movement at the grove edge. It didn't disappear when you looked. A first.",
        "It was there when you arrived. It had been there a while, you think.",
    ],
    2: [
        "It passed close enough that you felt the displacement. Neither of you acknowledged it.",
        "It brought something back from outside the boundary. You don't know what it is. You kept it.",
        "You found it near the heartstone in the early hours. It looked at you. Both of you went back to what you were doing.",
        "Its presence at the boundary has a particular quality. Things that were testing the edge have stopped.",
        "It is easier to find now. It still isn't where it appears to be.",
    ],
    3: [
        "It patrols the boundary at night. You've started sleeping more soundly without meaning to.",
        "You can read it now. The displacement is a language, once you know the grammar.",
        "It has chosen the grove. Whatever it left behind to do that, you're grateful.",
        "The boundary is harder to cross with it there. This is exactly what you needed.",
        "It never quite appears where you look. You've learned to look where you feel it instead.",
    ],
}

OWLBEAR_FEED = [
    "It takes the food with extreme care for something that large.",
    "It looks at the food. Then you. Then the food. Then it eats.",
    "A small, pleased sound. It didn't expect that, and neither did you.",
    "It ate quickly and then looked embarrassed about it.",
    "It accepted the food with more dignity than you were expecting.",
]

PSEUDODRAGON_FEED = [
    "It descended to take the food and immediately returned to its branch.",
    "It accepted the food with the air of someone doing you a favour.",
    "A brief acknowledgment. You're counting it.",
    "It chirruped. You're fairly sure that's good.",
    "It took the food and looked at you assessingly. Then flew up. Progress.",
]

FLUMPH_FEED = [
    "It glows warmer. You think that means thank you.",
    "It drifted closer to take the food and stayed a little longer after.",
    "A soft sound. The colour it turns is one you're starting to understand.",
    "It accepted and then changed colour slowly, like a sigh.",
    "It took the food gently and pulsed once. You felt it as well as saw it.",
]

MOSS_WISP_FEED = [
    "It drifted closer. That's all. That's enough.",
    "It accepted and the grove smelled different for a moment.",
    "No sound. But it stayed near you longer than usual.",
    "The forage around it grew a little thicker after. You noticed.",
    "It absorbed the food slowly. Then continued. You felt seen.",
]

PIXIE_FEED = [
    "Gone. The food is gone. Something small and bright is laughing somewhere.",
    "It ate it and immediately did something completely unrelated.",
    "It accepted the food and looked at you like you'd finally done something right.",
    "A tiny, enthusiastic sound. Then it vanished. Then it was back.",
    "It ate it faster than you could track and then did an extremely complicated gesture.",
]

DISPLACER_BEAST_FEED = [
    "It accepted from a position slightly other than where it appeared to be.",
    "It ate without looking at you, which still felt like attention.",
    "A low sound, felt more than heard. You're choosing to call that gratitude.",
    "The displacement rippled when it accepted. You think that's a good sign.",
    "It took the food from a direction you weren't looking and then was still.",
]

AREA_RESTORED = {
    "thicket":          "The Thicket opens. Old growth answers.",
    "canopy":           "The Canopy is whole again. Something perches.",
    "feywild_boundary": "The Boundary steadies. The Feywild recedes to its proper distance.",
    "oldwood":          "The Oldwood wakes. Slowly, as it always has.",
}


def pick(pool):
    return random.choice(pool) if pool else ""