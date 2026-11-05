-- Desenează panoul de fundal și inelele (CPU, RAM, Disk) cu Cairo.
require 'cairo'
local ok, cairo_xlib = pcall(require, 'cairo_xlib')  -- conky >= 1.10 poate încărca separat

-- Fiecare inel: expresia conky de citit, valoarea maximă, poziția și aspectul
local rings = {
    { expr = 'cpu cpu0',        max = 100, x = 60,  y = 120, r = 38, w = 8, color = {0.31, 0.76, 0.97} },
    { expr = 'memperc',         max = 100, x = 60,  y = 120, r = 28, w = 6, color = {0.55, 0.87, 0.55} },
    { expr = 'fs_used_perc /',  max = 100, x = 60,  y = 120, r = 19, w = 5, color = {1.00, 0.76, 0.28} },
}

local bg_alpha = 0.55   -- opacitatea panoului de fundal (0..1)

local function rounded_rect(cr, x, y, w, h, r)
    cairo_new_sub_path(cr)
    cairo_arc(cr, x + w - r, y + r,     r, -math.pi/2, 0)
    cairo_arc(cr, x + w - r, y + h - r, r, 0,           math.pi/2)
    cairo_arc(cr, x + r,     y + h - r, r, math.pi/2,   math.pi)
    cairo_arc(cr, x + r,     y + r,     r, math.pi,     3*math.pi/2)
    cairo_close_path(cr)
end

local function draw_ring(cr, t, value)
    local start = math.rad(-90)
    local full  = math.rad(360)
    local frac  = math.min(math.max(value / t.max, 0), 1)

    cairo_set_line_width(cr, t.w)
    cairo_set_line_cap(cr, CAIRO_LINE_CAP_ROUND)

    -- pista (fundal inel)
    cairo_set_source_rgba(cr, 1, 1, 1, 0.12)
    cairo_arc(cr, t.x, t.y, t.r, 0, full)
    cairo_stroke(cr)

    -- valoarea
    if frac > 0 then
        cairo_set_source_rgba(cr, t.color[1], t.color[2], t.color[3], 1)
        cairo_arc(cr, t.x, t.y, t.r, start, start + full * frac)
        cairo_stroke(cr)
    end
end

function conky_draw_rings()
    if conky_window == nil then return end

    local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable,
                                         conky_window.visual, conky_window.width, conky_window.height)
    local cr = cairo_create(cs)

    -- panou de fundal cu colțuri rotunjite
    rounded_rect(cr, 0, 0, conky_window.width, conky_window.height, 14)
    cairo_set_source_rgba(cr, 0.07, 0.08, 0.10, bg_alpha)
    cairo_fill(cr)

    for _, t in ipairs(rings) do
        local v = tonumber(conky_parse('${' .. t.expr .. '}')) or 0
        draw_ring(cr, t, v)
    end

    cairo_destroy(cr)
    cairo_surface_destroy(cs)
end
