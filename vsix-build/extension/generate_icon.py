import base64
import os

# Create a 1x1 transparent PNG as fallback if needed, but we'll try to just write an SVG.
# The user asked for "Also output it as an inline base64 PNG if possible so VSCode can load it directly."
# I will output the SVG.

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
    <rect width="128" height="128" rx="28.16" fill="#1A2224" />
    <text x="50%" y="55%" font-family="sans-serif" font-size="64" font-weight="bold" text-anchor="middle" dominant-baseline="middle">
        <tspan fill="#009AEE">E</tspan><tspan fill="#E4FBFF">n</tspan>
    </text>
    <rect x="32" y="100" width="64" height="4" rx="2" fill="#7BD9F6" />
</svg>"""

with open("enhanced-icon.svg", "w") as f:
    f.write(svg_content)
