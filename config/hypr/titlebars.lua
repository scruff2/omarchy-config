-- Traditional title bars, provided by the official Hyprbars plugin.
local plugin_path = os.getenv("HOME") .. "/.local/lib/hyprland/hyprbars.so"
local file = io.open(plugin_path, "r")
if file then
  file:close()
  hl.plugin.load(plugin_path)
  hl.config({ plugin = { hyprbars = {
    bar_height = 32,
    bar_color = "rgb(252a34)",
    ["col.text"] = "rgb(eeeeee)",
    bar_text_size = 12,
    bar_text_font = "sans-serif",
    bar_text_align = "left",
    bar_buttons_alignment = "right",
    bar_button_padding = 7,
    bar_padding = 8,
    on_double_click = [[hyprctl dispatch 'hl.dsp.window.fullscreen({mode="maximized", action="toggle", layout_aware=false})']],
  } } })
  -- Buttons are placed from right to left.
  hl.plugin.hyprbars.add_button({
    bg_color = "rgb(c94f5d)", fg_color = "rgb(ffffff)",
    size = 22, icon = "×",
    action = [[hyprctl dispatch 'hl.dsp.window.close()']],
  })
  hl.plugin.hyprbars.add_button({
    bg_color = "rgb(434c5e)", fg_color = "rgb(ffffff)",
    size = 22, icon = "▢",
    action = [[hyprctl dispatch 'hl.dsp.window.fullscreen({mode="maximized", action="toggle", layout_aware=false})']],
  })
  hl.plugin.hyprbars.add_button({
    bg_color = "rgb(434c5e)", fg_color = "rgb(ffffff)",
    size = 22, icon = "−",
    action = os.getenv("HOME") .. "/.config/omarchy/scripts/window-control minimize",
  })
end

-- Maximized windows fill the working area, including their title bars.
hl.workspace_rule({
  workspace = "f[1]",
  gaps_out = 0,
  border_size = 0,
  no_rounding = true,
})
