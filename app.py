import streamlit as st
from PIL import Image, ImageDraw

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Ring Sketch Designer", page_icon="💍")

# --- Main Title ---
st.title("Ring Sketch Designer")
st.write("Select the components in the sidebar to sketch your dream ring.")

# --- Constants & Options ---
DIAMOND_SHAPES = [
    "Round", "Princess", "Oval", "Emerald",
    "Cushion", "Pear", "Marquise",
    "Asscher", "Radiant"
]
DIAMOND_TYPES = ["Natural", "Lab-Grown"]
METALS = {
    "Yellow Gold (14K)": "yellow_gold",
    "White Gold (14K)": "white_gold",
    "Rose Gold (14K)": "rose_gold"
}
SETTINGS = {
    "Solitaire (Single Diamond)": "solitaire",
    "Halo": "halo",
    "Three-Stone": "three_stone",
    "Seven-Stone (Cluster Sides)": "seven_stone"
}
SIDE_STONE_SHAPES = ["Round", "Marquise", "Pear"]
CERTIFICATE_TYPES = ["GIA", "CGL"]
USD_TO_ILS_RATE = 3.7

# --- Color definitions for drawing ---
METAL_COLORS_RGB = {
    "yellow_gold": (212, 175, 55),
    "white_gold": (220, 220, 220),
    "rose_gold": (230, 180, 170)
}
DIAMOND_OUTLINE = (50, 50, 50)
DIAMOND_FILL = (245, 245, 245)

# --- Sidebar Widgets (User Input) ---
st.sidebar.header("Select Your Ring Components")
selected_shape = st.sidebar.selectbox("1. Select Diamond Shape:", DIAMOND_SHAPES)
selected_carat = st.sidebar.slider("2. Select Size (Carat):",
                                   min_value=0.5, max_value=3.0,
                                   value=1.0, step=0.1)
selected_diamond_type = st.sidebar.selectbox("3. Select Diamond Type:", DIAMOND_TYPES)

st.sidebar.subheader("4. Diamond Quality")
selected_color = st.sidebar.select_slider("Color:",
                                          options=["J", "I", "H", "G", "F", "E", "D"],
                                          value="G")
selected_clarity = st.sidebar.select_slider("Clarity:",
                                            options=["SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF", "FL"],
                                            value="VS1")

selected_metal = st.sidebar.selectbox("5. Select Metal Type:", list(METALS.keys()))
selected_certificate = st.sidebar.selectbox("6. Select Certificate:", CERTIFICATE_TYPES)

selected_setting = st.sidebar.selectbox("7. Select Setting Type:", list(SETTINGS.keys()))

# --- Side stone selection (now follows Setting) ---
setting_key = SETTINGS[selected_setting]
side_stone_shapes = ("Round",) # Default tuple

if setting_key == "three_stone":
    st.sidebar.subheader("Side Stone")
    shape = st.sidebar.selectbox(
        "Select Side Stone Shape:",
        SIDE_STONE_SHAPES,
        key="three_stone_shape"
    )
    side_stone_shapes = (shape,) # Tuple with one element

elif setting_key == "seven_stone":
    st.sidebar.subheader("Side Stones (Symmetrical)")
    shape_1 = st.sidebar.selectbox(
        "Stone 1 (Top):",
        SIDE_STONE_SHAPES,
        key="seven_stone_1"
    )
    shape_2 = st.sidebar.selectbox(
        "Stone 2 (Bottom):",
        SIDE_STONE_SHAPES,
        key="seven_stone_2"
    )
    shape_3 = st.sidebar.selectbox(
        "Stone 3 (Side):",
        SIDE_STONE_SHAPES,
        key="seven_stone_3"
    )
    side_stone_shapes = (shape_1, shape_2, shape_3) # Tuple with three elements


# --- Price Calculation Logic (Demo) ---
BASE_DIAMOND_PRICE_PER_CARAT = 5000
DIAMOND_TYPE_MULTIPLIERS = {"Natural": 1.0, "Lab-Grown": 0.5} 
SHAPE_MULTIPLIERS = {
    "Round": 1.0, "Princess": 0.9, "Oval": 0.95,
    "Emerald": 0.9, "Cushion": 0.85, "Pear": 0.9,
    "Marquise": 0.8, "Asscher": 0.85, "Radiant": 0.88
}
COLOR_MULTIPLIERS = {"J": 0.8, "I": 0.9, "H": 1.0, "G": 1.1, "F": 1.3, "E": 1.5, "D": 2.0}
CLARITY_MULTIPLIERS = {"SI2": 0.8, "SI1": 0.9, "VS2": 1.0, "VS1": 1.1, "VVS2": 1.3, "VVS1": 1.5, "IF": 1.8, "FL": 2.2}
METAL_BASE_PRICE = {"Yellow Gold (14K)": 500, "White Gold (14K)": 550, "Rose Gold (14K)": 520}
SETTING_BASE_PRICE = {
    "Solitaire (Single Diamond)": 200,
    "Halo": 800,
    "Three-Stone": 600,
    "Seven-Stone (Cluster Sides)": 1400
}
CERTIFICATE_MULTIPLIERS = {"GIA": 1.15, "CGL": 1.0}
SIDE_STONE_MULTIPLIER = {"Round": 1.0, "Marquise": 1.2, "Pear": 1.25}

def calculate_price(shape, carat, color, clarity, metal, setting, certificate, side_shapes_tuple, diamond_type):
    base_price = BASE_DIAMOND_PRICE_PER_CARAT * carat
    
    type_factor = DIAMOND_TYPE_MULTIPLIERS.get(diamond_type, 1.0)
    shape_factor = SHAPE_MULTIPLIERS.get(shape, 1.0)
    color_factor = COLOR_MULTIPLIERS.get(color, 1.0)
    clarity_factor = CLARITY_MULTIPLIERS.get(clarity, 1.0)
    cert_factor = CERTIFICATE_MULTIPLIERS.get(certificate, 1.0)
    
    diamond_price_usd = base_price * type_factor * shape_factor * color_factor * clarity_factor * cert_factor
    
    setting_base = SETTING_BASE_PRICE.get(setting, 200)
    
    side_stone_factor = 1.0
    if SETTINGS[setting] in ["three_stone", "seven_stone"]:
        total_multiplier = sum(SIDE_STONE_MULTIPLIER.get(s, 1.0) for s in side_shapes_tuple)
        side_stone_factor = total_multiplier / len(side_shapes_tuple)

    setting_price_usd = METAL_BASE_PRICE.get(metal, 500) + (setting_base * side_stone_factor)
        
    total_price_usd = diamond_price_usd + setting_price_usd
    
    total_price_ils = total_price_usd * USD_TO_ILS_RATE
    diamond_price_ils = diamond_price_usd * USD_TO_ILS_RATE
    setting_price_ils = setting_price_usd * USD_TO_ILS_RATE
    
    return total_price_ils, diamond_price_ils, setting_price_ils

# --- Helper function for drawing prongs ---
def draw_prongs(draw, center_x, center_y, radius_x, radius_y, color, base_size_px):
    """Draws 4 small prongs outside a stone, respecting x and y radius."""
    prong_size = max(2, int(base_size_px * 0.05)) 
    half_prong = max(1, prong_size // 2)
    
    offset_x = radius_x + half_prong 
    offset_y = radius_y + half_prong
    
    draw.ellipse([(center_x - offset_x - half_prong, center_y - half_prong), 
                  (center_x - offset_x + half_prong, center_y + half_prong)], fill=color) # Left
    draw.ellipse([(center_x + offset_x - half_prong, center_y - half_prong), 
                  (center_x + offset_x + half_prong, center_y + half_prong)], fill=color) # Right
    draw.ellipse([(center_x - half_prong, center_y - offset_y - half_prong), 
                  (center_x + half_prong, center_y - offset_y + half_prong)], fill=color) # Top
    draw.ellipse([(center_x - half_prong, center_y + offset_y - half_prong), 
                  (center_x + half_prong, center_y + offset_y + half_prong)], fill=color) # Bottom

# --- Helper function for drawing side stones ---
def draw_side_stone(draw, shape, center_x, center_y, radius, color, outline, orientation='up'):
    if radius <= 0: return
    
    h_radius_out = radius
    v_radius_out = radius

    if shape == "Round":
        draw.ellipse(
            [(center_x - radius, center_y - radius),
             (center_x + radius, center_y + radius)],
            outline=outline, fill=color, width=2
        )
    elif shape == "Marquise":
        # Default vertical orientation (for main stone)
        h_radius = max(1, int(radius * 0.8)) # UPDATED: "Fatter" marquise (was 0.5)
        v_radius = int(radius * 1.5)
        
        if orientation == 'left' or orientation == 'right':
            # Horizontal orientation (for side stones)
            h_radius = int(radius * 1.5)
            v_radius = max(1, int(radius * 0.8)) # UPDATED: "Fatter" marquise (was 0.5)
        
        h_radius_out = h_radius
        v_radius_out = v_radius
        
        draw.polygon(
            [
                (center_x, center_y - v_radius), # Top
                (center_x + h_radius, center_y), # Right
                (center_x, center_y + v_radius), # Bottom
                (center_x - h_radius, center_y)  # Left
            ],
            outline=outline, fill=color, width=2
        )
    elif shape == "Pear":
        h_radius = radius
        v_radius = int(radius * 1.3)
        h_radius_out, v_radius_out = h_radius, v_radius # Default for up/down
        
        if orientation == 'up':
            points = [(center_x, center_y - v_radius), (center_x + h_radius, center_y), (center_x + h_radius * 0.5, center_y + v_radius), (center_x - h_radius * 0.5, center_y + v_radius), (center_x - h_radius, center_y)]
        elif orientation == 'down':
             points = [(center_x, center_y + v_radius), (center_x + h_radius, center_y), (center_x + h_radius * 0.5, center_y - v_radius), (center_x - h_radius * 0.5, center_y - v_radius), (center_x - h_radius, center_y)]
        elif orientation == 'left':
            h_radius, v_radius = v_radius, h_radius
            h_radius_out, v_radius_out = h_radius, v_radius
            points = [(center_x - h_radius, center_y), (center_x, center_y - v_radius), (center_x + h_radius * 0.8, center_y - v_radius * 0.5), (center_x + h_radius * 0.8, center_y + v_radius * 0.5), (center_x, center_y + v_radius)]
        else: # 'right'
            h_radius, v_radius = v_radius, h_radius
            h_radius_out, v_radius_out = h_radius, v_radius
            points = [(center_x + h_radius, center_y), (center_x, center_y - v_radius), (center_x - h_radius * 0.8, center_y - v_radius * 0.5), (center_x - h_radius * 0.8, center_y + v_radius * 0.5), (center_x, center_y + v_radius)]
        draw.polygon(points, outline=outline, fill=color, width=2)
    
    return h_radius_out, v_radius_out


# --- Image SKETCHING Logic (Top-Down "On-Hand" View) ---
def create_ring_sketch(shape, carat, metal_key, setting_key, side_shapes_tuple):
    IMG_SIZE = 500
    CENTER = (IMG_SIZE // 2, IMG_SIZE // 2)
    
    canvas = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    draw = ImageDraw.Draw(canvas)
    
    band_color = METAL_COLORS_RGB.get(metal_key, "grey")
    
    base_size_px = int(carat * 35) 
    half_size = max(1, base_size_px // 2)
    
    # --- Step A: Calculate Dimensions (No Drawing) ---
    total_setting_width = base_size_px
    main_stone_coords = [
        (CENTER[0] - half_size, CENTER[1] - half_size),
        (CENTER[0] + half_size, CENTER[1] + half_size)
    ]
    main_stone_extents = {'half_width': half_size, 'half_height': half_size}

    if "Oval" in shape:
        main_stone_extents['half_height'] = int(half_size * 1.4)
        main_stone_extents['half_width'] = half_size
        main_stone_coords = [(CENTER[0] - half_size, CENTER[1] - main_stone_extents['half_height']), (CENTER[0] + half_size, CENTER[1] + main_stone_extents['half_height'])]
    elif "Pear" in shape:
        main_stone_extents['half_height'] = int(half_size * 1.3)
        main_stone_extents['half_width'] = half_size
        main_stone_coords = [(CENTER[0] - main_stone_extents['half_width'], CENTER[1] - main_stone_extents['half_height']), (CENTER[0] + main_stone_extents['half_width'], CENTER[1] + main_stone_extents['half_height'])]
    elif "Marquise" in shape:
        main_stone_extents['half_height'] = int(half_size * 1.5)
        main_stone_extents['half_width'] = max(1, int(half_size * 0.8)) # UPDATED: "Fatter" marquise (was 0.5)
        main_stone_coords = [(CENTER[0] - main_stone_extents['half_width'], CENTER[1] - main_stone_extents['half_height']), (CENTER[0] + main_stone_extents['half_width'], CENTER[1] + main_stone_extents['half_height'])]

    side_stone_radius = 0 # Initialize
    if "halo" in setting_key:
        halo_padding = 8
        total_setting_width += (halo_padding * 2)
    elif "three_stone" in setting_key:
        side_stone_radius = max(4, int(base_size_px / 4.0)) 
        total_setting_width += (side_stone_radius * 4)
    elif "seven_stone" in setting_key:
        side_stone_radius = max(3, int(base_size_px / 6.0))
        total_setting_width += (side_stone_radius * 6)
            
# --- Step B: Draw the Ring Band "Shoulders" (FIRST) ---
    band_thickness = 14
    band_y_start = CENTER[1] - (band_thickness // 2)
    band_y_end = CENTER[1] + (band_thickness // 2)

    setting_half_width = (total_setting_width // 2) 

    # Determine the actual connection point for the band, considering the stone's shape
    # For settings like halo, three-stone, seven-stone, the setting_half_width will be larger
    # For solitaire, it's just the main stone's width
    connection_x_left = CENTER[0] - setting_half_width
    connection_x_right = CENTER[0] + setting_half_width

    # Adjust connection_x based on main stone's actual half_width if solitaire
    if "solitaire" in setting_key:
        connection_x_left = CENTER[0] - main_stone_extents['half_width']
        connection_x_right = CENTER[0] + main_stone_extents['half_width']
    
    # Ensure band doesn't go off canvas
    band_start_x_left = max(0, connection_x_left - band_thickness) # extend a bit for curve
    band_start_x_right = min(IMG_SIZE, connection_x_right + band_thickness) # extend a bit for curve

    # Draw the main band rectangles (away from the stone)
    draw.rectangle(
        [(0, band_y_start), (connection_x_left - band_thickness, band_y_end)],
        fill=band_color
    )
    draw.rectangle(
        [(connection_x_right + band_thickness, band_y_start), (IMG_SIZE, band_y_end)],
        fill=band_color
    )

    # Now, draw the connecting "shoulders" with curves if necessary
    # These connect the main band to the setting/stone
    if "Round" in shape or "Oval" in shape or "Cushion" in shape:
        # Use rounded rectangles or ellipses for a smooth connection
        draw.rounded_rectangle(
            [(connection_x_left - band_thickness, band_y_start), (connection_x_right + band_thickness, band_y_end)],
            radius=band_thickness // 2, # Adjust radius for smoother curve
            fill=band_color
        )
    elif "Princess" in shape or "Emerald" in shape or "Radiant" in shape or "Asscher" in shape:
        # For square/rectangular shapes, a straight connection is appropriate
        draw.rectangle(
            [(connection_x_left - band_thickness, band_y_start), (connection_x_right + band_thickness, band_y_end)],
            fill=band_color
        )
    elif "Pear" in shape:
        # For pear shape, connect to the wider part
        points_left = [
            (CENTER[0] - main_stone_extents['half_width'], CENTER[1] + main_stone_extents['half_height']), # Bottom-left of stone
            (CENTER[0] - main_stone_extents['half_width'], CENTER[1] - main_stone_extents['half_height']), # Top-left of stone
            (connection_x_left - band_thickness, band_y_start),
            (connection_x_left - band_thickness, band_y_end),
        ]
        points_right = [
            (CENTER[0] + main_stone_extents['half_width'], CENTER[1] + main_stone_extents['half_height']), # Bottom-right of stone
            (CENTER[0] + main_stone_extents['half_width'], CENTER[1] - main_stone_extents['half_height']), # Top-right of stone
            (connection_x_right + band_thickness, band_y_start),
            (connection_x_right + band_thickness, band_y_end),
        ]
        # This is a simplification; for a perfect fit, you'd need to calculate precise tangent points.
        # For now, we'll draw a rectangle that covers the area and blends.
        draw.rectangle(
            [(connection_x_left - band_thickness, band_y_start), (connection_x_right + band_thickness, band_y_end)],
            fill=band_color
        )
    elif "Marquise" in shape:
        # For marquise shape, connect to the widest part (sides)
        points_left = [
            (CENTER[0] - main_stone_extents['half_width'], CENTER[1]), # Left point of stone
            (connection_x_left - band_thickness, band_y_start),
            (connection_x_left - band_thickness, band_y_end),
        ]
        points_right = [
            (CENTER[0] + main_stone_extents['half_width'], CENTER[1]), # Right point of stone
            (connection_x_right + band_thickness, band_y_start),
            (connection_x_right + band_thickness, band_y_end),
        ]
        draw.rectangle(
            [(connection_x_left - band_thickness, band_y_start), (connection_x_right + band_thickness, band_y_end)],
            fill=band_color
        )
    # The default for settings other than solitaire (halo, three-stone, seven-stone)
    # will be covered by the main band drawing, as they are generally more symmetrical.
    if not ("solitaire" in setting_key):
        draw.rectangle(
            [(connection_x_left, band_y_start), (connection_x_right, band_y_end)],
            fill=band_color
        )
    
    # --- Step C: Draw Main Diamond (SECOND) ---
    main_radius_x = main_stone_extents['half_width']
    main_radius_y = main_stone_extents['half_height']
    
    if "Round" in shape:
        draw.ellipse(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    elif "Princess" in shape:
        draw.rectangle(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
        draw.line([(main_stone_coords[0]), (main_stone_coords[1])], fill=DIAMOND_OUTLINE)
        draw.line([(main_stone_coords[0][0], main_stone_coords[1][1]), (main_stone_coords[1][0], main_stone_coords[0][1])], fill=DIAMOND_OUTLINE)
    elif "Oval" in shape:
        draw.ellipse(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    elif "Emerald" in shape or "Radiant" in shape:
        cut_size = max(1, half_size // 4)
        points = [
            (CENTER[0] - half_size + cut_size, CENTER[1] - half_size), (CENTER[0] + half_size - cut_size, CENTER[1] - half_size),
            (CENTER[0] + half_size, CENTER[1] - half_size + cut_size), (CENTER[0] + half_size, CENTER[1] + half_size - cut_size),
            (CENTER[0] + half_size - cut_size, CENTER[1] + half_size), (CENTER[0] - half_size + cut_size, CENTER[1] + half_size),
            (CENTER[0] - half_size, CENTER[1] + half_size - cut_size), (CENTER[0] - half_size, CENTER[1] - half_size + cut_size),
        ]
        draw.polygon(points, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    elif "Cushion" in shape:
        draw.rounded_rectangle(main_stone_coords, radius=max(1, half_size // 3), outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    elif "Pear" in shape:
        points = [
            (CENTER[0], CENTER[1] - main_radius_y), # Top point
            (CENTER[0] + main_radius_x, CENTER[1]), # Right shoulder
            (CENTER[0] + main_radius_x * 0.5, CENTER[1] + main_radius_y), # Bottom-right
            (CENTER[0] - main_radius_x * 0.5, CENTER[1] + main_radius_y), # Bottom-left
            (CENTER[0] - main_radius_x, CENTER[1])  # Left shoulder
        ]
        draw.polygon(points, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    elif "Marquise" in shape:
        points = [(CENTER[0], CENTER[1] - main_radius_y), (CENTER[0] + main_radius_x, CENTER[1]), (CENTER[0], CENTER[1] + main_radius_y), (CENTER[0] - main_radius_x, CENTER[1])]
        draw.polygon(points, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    else: # Fallback for Asscher
        draw.rectangle(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)

    # --- Step D: Draw the Setting (Prongs, Halo, Side Stones) (LAST) ---
    if "solitaire" in setting_key:
        draw_prongs(draw, CENTER[0], CENTER[1], main_radius_x, main_radius_y, band_color, base_size_px=base_size_px)
            
    elif "halo" in setting_key:
        halo_padding = 8
        coords = [(main_stone_coords[0][0] - halo_padding, main_stone_coords[0][1] - halo_padding), (main_stone_coords[1][0] + halo_padding, main_stone_coords[1][1] + halo_padding)]
        if "Round" in shape:
            draw.ellipse(coords, outline=band_color, width=6)
        elif "Cushion" in shape or "Princess" in shape:
             draw.rounded_rectangle(coords, radius=halo_padding, outline=band_color, width=6)
        else: 
            draw.ellipse(coords, outline=band_color, width=6)
            
    elif "three_stone" in setting_key:
        side_stone_shape = side_shapes_tuple[0]
        side_stone_radius = max(4, int(base_size_px / 4.0))
        
        left_center_x = CENTER[0] - main_radius_x - side_stone_radius
        rx1, ry1 = draw_side_stone(draw, side_stone_shape, left_center_x, CENTER[1], side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='right')
        draw_prongs(draw, left_center_x, CENTER[1], rx1, ry1, band_color, base_size_px=base_size_px)
        
        right_center_x = CENTER[0] + main_radius_x + side_stone_radius
        rx2, ry2 = draw_side_stone(draw, side_stone_shape, right_center_x, CENTER[1], side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='left')
        draw_prongs(draw, right_center_x, CENTER[1], rx2, ry2, band_color, base_size_px=base_size_px)
        
        draw_prongs(draw, CENTER[0], CENTER[1], main_radius_x, main_radius_y, band_color, base_size_px=base_size_px)
        
    elif "seven_stone" in setting_key:
        shape_1, shape_2, shape_3 = side_shapes_tuple
        side_stone_radius = max(3, int(base_size_px / 6.0))
        buffer = 1 
        
        # --- Left Cluster (3 stones) ---
        left_1_x = CENTER[0] - main_radius_x - side_stone_radius
        left_1_y = CENTER[1] - side_stone_radius - buffer 
        rx1, ry1 = draw_side_stone(draw, shape_1, left_1_x, left_1_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='right')
        draw_prongs(draw, left_1_x, left_1_y, rx1, ry1, band_color, base_size_px=base_size_px)
        
        left_2_x = CENTER[0] - main_radius_x - side_stone_radius
        left_2_y = CENTER[1] + side_stone_radius + buffer
        rx2, ry2 = draw_side_stone(draw, shape_2, left_2_x, left_2_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='right')
        draw_prongs(draw, left_2_x, left_2_y, rx2, ry2, band_color, base_size_px=base_size_px)
        
        left_3_x = left_1_x - (side_stone_radius * 2)
        left_3_y = CENTER[1]
        rx3, ry3 = draw_side_stone(draw, shape_3, left_3_x, left_3_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='left')
        draw_prongs(draw, left_3_x, left_3_y, rx3, ry3, band_color, base_size_px=base_size_px)
        
        # --- Right Cluster (3 stones) ---
        right_1_x = CENTER[0] + main_radius_x + side_stone_radius
        right_1_y = CENTER[1] - side_stone_radius - buffer
        rx4, ry4 = draw_side_stone(draw, shape_1, right_1_x, right_1_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='left')
        draw_prongs(draw, right_1_x, right_1_y, rx4, ry4, band_color, base_size_px=base_size_px)
        
        right_2_x = CENTER[0] + main_radius_x + side_stone_radius
        right_2_y = CENTER[1] + side_stone_radius + buffer
        rx5, ry5 = draw_side_stone(draw, shape_2, right_2_x, right_2_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='left')
        draw_prongs(draw, right_2_x, right_2_y, rx5, ry5, band_color, base_size_px=base_size_px)

        right_3_x = right_1_x + (side_stone_radius * 2)
        right_3_y = CENTER[1]
        rx6, ry6 = draw_side_stone(draw, shape_3, right_3_x, right_3_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='right')
        draw_prongs(draw, right_3_x, right_3_y, rx6, ry6, band_color, base_size_px=base_size_px)
        
        # Prongs for main stone
        draw_prongs(draw, CENTER[0], CENTER[1], main_radius_x, main_radius_y, band_color, base_size_px=base_size_px)

    return canvas

# --- Main App Logic ---

# 1. Calculate price
total_price, diamond_price, setting_price = calculate_price(
    selected_shape, selected_carat, selected_color,
    selected_clarity, selected_metal, selected_setting,
    selected_certificate, side_stone_shapes, selected_diamond_type
)

# 2. Generate the sketch
final_ring_image = create_ring_sketch(
    selected_shape,
    selected_carat,
    METALS[selected_metal],
    SETTINGS[selected_setting],
    side_stone_shapes
)

# 3. Display the results
st.sidebar.success("Your sketch is ready!")

# --- Display Area (Main Page) ---
col1, col2 = st.columns(2)

with col1:
    st.header("Your Sketch:")
    st.image(final_ring_image, use_column_width=True)

with col2:
    st.header(f"Estimated Price: ₪{total_price:,.0f}")
    st.subheader("Your Selections:")
    
    selections_markdown = f"""
    * **Diamond Shape:** {selected_shape}
    * **Carat Weight:** {selected_carat}
    * **Diamond Type:** {selected_diamond_type}
    * **Color:** {selected_color}
    * **Clarity:** {selected_clarity}
    * **Metal:** {selected_metal}
    * **Certificate:** {selected_certificate} 
    * **Setting:** {selected_setting}
    """
    
    if setting_key == "three_stone":
        selections_markdown += f"\n    * **Side Stone Shape:** {side_stone_shapes[0]}"
    elif setting_key == "seven_stone":
        selections_markdown += f"\n    * **Side Stone 1 (Top):** {side_stone_shapes[0]}"
        selections_markdown += f"\n    * **Side Stone 2 (Bottom):** {side_stone_shapes[1]}"
        selections_markdown += f"\n    * **Side Stone 3 (Side):** {side_stone_shapes[2]}"
        
    st.markdown(selections_markdown)
    
    st.subheader("Cost Breakdown (Demo):")
    st.markdown(f"""
    * **Diamond Cost:** ₪{diamond_price:,.0f}
    * **Setting & Metal Cost:** ₪{setting_price:,.0f}
    """)

