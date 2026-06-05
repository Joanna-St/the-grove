# Ideas & Revisits

Things to consider for later phases. Not current phase scope.

---

## Window & Display

- **Windowed/fullscreen toggle at runtime** — F11 toggle didn't work reliably
  due to SDL2 window repositioning issues on Windows. Currently config-only
  (`"fullscreen": true/false` in config.json, requires restart). Worth
  revisiting in Phase 5 when polishing — may need a pygame._sdl2 approach
  or a launcher settings screen.

- **Custom window icon** — replace the default Pygame icon with something
  grove-themed (a leaf, the Silvanus symbol). Low effort, nice finish.
  Defer to Phase 5 alongside other art tasks.
