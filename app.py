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
selected_setting = st.sidebar.selectbox("3. Select Setting Type:", list(SETTINGS.keys()))

# --- UPDATED: Side stone selection moved and expanded ---
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

selected_metal = st.sidebar.selectbox("4. Select Metal Type:", list(METALS.keys()))
selected_certificate = st.sidebar.selectbox("5. Select Certificate:", CERTIFICATE_TYPES)

st.sidebar.subheader("Diamond Quality")
selected_color = st.sidebar.select_slider("Color:",
                                          options=["J", "I", "H", "G", "F", "E", "D"],
                                          value="G")
selected_clarity = st.sidebar.select_slider("Clarity:",
                                            options=["SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF", "FL"],
                                            value="VS1")

# --- Price Calculation Logic (Demo) ---
BASE_DIAMOND_PRICE_PER_CARAT = 5000
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

# UPDATED: Price function accepts a tuple of side shapes
def calculate_price(shape, carat, color, clarity, metal, setting, certificate, side_shapes_tuple):
    base_price = BASE_DIAMOND_PRICE_PER_CARAT * carat
    shape_factor = SHAPE_MULTIPLIERS.get(shape, 1.0)
    color_factor = COLOR_MULTIPLIERS.get(color, 1.0)
    clarity_factor = CLARITY_MULTIPLIERS.get(clarity, 1.0)
    cert_factor = CERTIFICATE_MULTIPLIERS.get(certificate, 1.0)
    
    diamond_price_usd = base_price * shape_factor * color_factor * clarity_factor * cert_factor
    
    setting_base = SETTING_BASE_PRICE.get(setting, 200)
    
    # Calculate side stone factor based on the tuple
    side_stone_factor = 1.0
    if SETTINGS[setting] in ["three_stone", "seven_stone"]:
        # Get average multiplier for all side stones
        total_multiplier = sum(SIDE_STONE_MULTIPLIER.get(s, 1.0) for s in side_shapes_tuple)
        side_stone_factor = total_multiplier / len(side_shapes_tuple)

    setting_price_usd = METAL_BASE_PRICE.get(metal, 500) + (setting_base * side_stone_factor)
        
    total_price_usd = diamond_price_usd + setting_price_usd
    
    total_price_ils = total_price_usd * USD_TO_ILS_RATE
    diamond_price_ils = diamond_price_usd * USD_TO_ILS_RATE
    setting_price_ils = setting_price_usd * USD_TO_ILS_RATE
    
    return total_price_ils, diamond_price_ils, setting_price_ils

# --- Helper function for drawing side stones ---
def draw_side_stone(draw, shape, center_x, center_y, radius, color, outline, orientation='up'):
    """
    Draws a side stone of a specific shape and orientation.
    Orientation: 'up', 'down', 'left', 'right'
    """
    if radius <= 0: return # Don't draw if radius is zero or negative
    
    if shape == "Round":
        draw.ellipse(
            [(center_x - radius, center_y - radius),
             (center_x + radius, center_y + radius)],
            outline=outline, fill=color, width=2
        )
    elif shape == "Marquise":
        h_radius = radius if orientation in ['left', 'right'] else max(1, radius // 2)
        v_radius = radius if orientation in ['up', 'down'] else max(1, radius // 2)
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
        if orientation == 'up':
            points = [(center_x, center_y - radius), (center_x + radius, center_y + radius), (center_x - radius, center_y + radius)]
        elif orientation == 'down':
            points = [(center_x, center_y + radius), (center_x + radius, center_y - radius), (center_x - radius, center_y - radius)]
        elif orientation == 'left': # Pointing left
            points = [(center_x - radius, center_y), (center_x + radius, center_y - radius), (center_x + radius, center_y + radius)]
        else: # 'right'
            points = [(center_x + radius, center_y), (center_x - radius, center_y - radius), (center_x - radius, center_y + radius)]
        draw.polygon(points, outline=outline, fill=color, width=2)


# --- Image SKETCHING Logic (Top-Down "On-Hand" View) ---
# UPDATED: Function signature accepts side_shapes tuple
def create_ring_sketch(shape, carat, metal_key, setting_key, side_shapes_tuple):
    IMG_SIZE = 500
    CENTER = (IMG_SIZE // 2, IMG_SIZE // 2)
    
    canvas = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    draw = ImageDraw.Draw(canvas)
    
    band_color = METAL_COLORS_RGB.get(metal_key, "grey")
    
    # UPDATED: Reduced base size for better proportion
    base_size_px = int(carat * 35) 
    half_size = max(1, base_size_px // 2)
    
    main_stone_coords = [] 
    total_setting_width = base_size_px 

    # --- 3. Draw Main Diamond (FIRST) ---
    main_stone_coords = [
        (CENTER[0] - half_size, CENTER[1] - half_size),
        (CENTER[0] + half_size, CENTER[1] + half_size)
    ]
    
    if "Round" in shape:
        draw.ellipse(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    
    elif "Princess" in shape:
        draw.rectangle(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
        draw.line([(main_stone_coords[0]), (main_stone_coords[1])], fill=DIAMOND_OUTLINE)
        draw.line([(main_stone_coords[0][0], main_stone_coords[1][1]), (main_stone_coords[1][0], main_stone_coords[0][1])], fill=DIAMOND_OUTLINE)

    elif "Oval" in shape:
        oval_height = int(half_size * 1.4)
        main_stone_coords = [(CENTER[0] - half_size, CENTER[1] - oval_height), (CENTER[0] + half_size, CENTER[1] + oval_height)]
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
        half_height = int(half_size * 1.2); half_width = half_size
        draw.ellipse([(CENTER[0] - half_width, CENTER[1] - half_height // 2), (CENTER[0] + half_width, CENTER[1] + half_height)], outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=1)
        draw.polygon([(CENTER[0], CENTER[1] - half_height), (CENTER[0] + half_width, CENTER[1] - half_height // 2), (CENTER[0] - half_width, CENTER[1] - half_height // 2)], outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=1)
        draw.line([(CENTER[0] - half_width, CENTER[1] - half_height // 2), (CENTER[0] + half_width, CENTER[1] - half_height // 2)], fill=DIAMOND_FILL, width=2)
        main_stone_coords = [(CENTER[0] - half_width, CENTER[1] - half_height), (CENTER[0] + half_width, CENTER[1] + half_height)]

    elif "Marquise" in shape:
        half_height = int(half_size * 1.5); half_width = max(1, half_size // 2)
        points = [(CENTER[0], CENTER[1] - half_height), (CENTER[0] + half_width, CENTER[1]), (CENTER[0], CENTER[1] + half_height), (CENTER[0] - half_width, CENTER[1])]
        draw.polygon(points, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
        main_stone_coords = [(CENTER[0] - half_width, CENTER[1] - half_height), (CENTER[0] + half_width, CENTER[1] + half_height)]
    
    else: # Fallback for Asscher
        draw.rectangle(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)


    # --- 4. Draw the Setting (Prongs, Halo, Side Stones) ---
    
    if "solitaire" in setting_key:
        coords = main_stone_coords
        prong_size = 6; half_prong = prong_size // 2 # Smaller prongs
        draw.ellipse([(coords[0][0]-half_prong, coords[0][1]-half_prong), (coords[0][0]+half_prong, coords[0][1]+half_prong)], fill=band_color)
        draw.ellipse([(coords[1][0]-half_prong, coords[0][1]-half_prong), (coords[1][0]+half_prong, coords[0][1]+half_prong)], fill=band_color)
        draw.ellipse([(coords[0][0]-half_prong, coords[1][1]-half_prong), (coords[0][0]+half_prong, coords[1][1]+half_prong)], fill=band_color)
        draw.ellipse([(coords[1][0]-half_prong, coords[1][1]-half_prong), (coords[1][0]+half_prong, coords[1][1]+half_prong)], fill=band_color)
            
    elif "halo" in setting_key:
        halo_padding = 8 # Smaller halo
        coords = [(main_stone_coords[0][0] - halo_padding, main_stone_coords[0][1] - halo_padding), (main_stone_coords[1][0] + halo_padding, main_stone_coords[1][1] + halo_padding)]
        if "Round" in shape:
            draw.ellipse(coords, outline=band_color, width=6)
        elif "Cushion" in shape or "Princess" in shape:
             draw.rounded_rectangle(coords, radius=halo_padding, outline=band_color, width=6)
        else: 
            draw.ellipse(coords, outline=band_color, width=6)
        total_setting_width += (halo_padding * 2)
            
    elif "three_stone" in setting_key:
        side_stone_shape = side_shapes_tuple[0]
        # UPDATED: Smaller side stone ratio
        side_stone_radius = max(5, int(base_size_px / 3.5)) 
        
        left_center_x = CENTER[0] - half_size - side_stone_radius
        draw_side_stone(draw, side_stone_shape, left_center_x, CENTER[1], side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='right')
        
        right_center_x = CENTER[0] + half_size + side_stone_radius
        draw_side_stone(draw, side_stone_shape, right_center_x, CENTER[1], side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='left')
        
        total_setting_width += (side_stone_radius * 4)

    elif "seven_stone" in setting_key:
        shape_1, shape_2, shape_3 = side_shapes_tuple
        # UPDATED: Smaller side stone ratio
        side_stone_radius = max(4, int(base_size_px / 4.5))
        # UPDATED: Added buffer to prevent overlap
        buffer = 1 
        
        # --- Left Cluster (3 stones) ---
        # 1. Stone 1 (Top)
        left_1_x = CENTER[0] - half_size - side_stone_radius
        left_1_y = CENTER[1] - side_stone_radius - buffer # Move up
        draw_side_stone(draw, shape_1, left_1_x, left_1_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='right')
        
        # 2. Stone 2 (Bottom)
        left_2_x = CENTER[0] - half_size - side_stone_radius
        left_2_y = CENTER[1] + side_stone_radius + buffer # Move down
        draw_side_stone(draw, shape_2, left_2_x, left_2_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='right')

        # 3. Stone 3 (Side)
        left_3_x = left_1_x - (side_stone_radius * 2)
        left_3_y = CENTER[1]
        draw_side_stone(draw, shape_3, left_3_x, left_3_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='right')
        
        # --- Right Cluster (3 stones) ---
        # 1. Stone 1 (Top)
        right_1_x = CENTER[0] + half_size + side_stone_radius
        right_1_y = CENTER[1] - side_stone_radius - buffer # Move up
        draw_side_stone(draw, shape_1, right_1_x, right_1_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='left')
        
        # 2. Stone 2 (Bottom)
        right_2_x = CENTER[0] + half_size + side_stone_radius
        right_2_y = CENTER[1] + side_stone_radius + buffer # Move down
        draw_side_stone(draw, shape_2, right_2_x, right_2_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='left')

        # 3. Stone 3 (Side)
        right_3_x = right_1_x + (side_stone_radius * 2)
        right_3_y = CENTER[1]
        draw_side_stone(draw, shape_3, right_3_x, right_3_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE, orientation='left')

        total_setting_width += (side_stone_radius * 6)
            
    # --- 5. Draw the Ring Band "Shoulders" (LAST) ---
    # UPDATED: Thicker band
    band_thickness = 14
    band_y_start = CENTER[1] - (band_thickness // 2)
    band_y_end = CENTER[1] + (band_thickness // 2)

    setting_half_width = (total_setting_width // 2) + 5 
    
    if shape in ["Oval", "Pear", "Marquise"]:
        # Use the actual drawn coordinates for tall shapes
        setting_half_width = max(main_stone_coords[1][0] - CENTER[0], setting_half_width)
        
    band_end_x_left = CENTER[0] - setting_half_width
    band_end_x_right = CENTER[0] + setting_half_width

    band_end_x_left = max(0, band_end_x_left)
    band_end_x_right = min(IMG_SIZE, band_end_x_right)

    draw.rectangle(
        [(0, band_y_start), (band_end_x_left, band_y_end)],
        fill=band_color
    )
    draw.rectangle(
        [(band_end_x_right, band_y_start), (IMG_SIZE, band_y_end)],
        fill=band_color
    )
    
    return canvas

# --- Main App Logic ---

# 1. Calculate price
total_price, diamond_price, setting_price = calculate_price(
    selected_shape, selected_carat, selected_color,
    selected_clarity, selected_metal, selected_setting,
    selected_certificate, side_stone_shapes # Pass the tuple
)

# 2. Generate the sketch
final_ring_image = create_ring_sketch(
    selected_shape,
    selected_carat,
    METALS[selected_metal],
    SETTINGS[selected_setting],
    side_stone_shapes # Pass the tuple
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
    * **Color:** {selected_color}
    * **Clarity:** {selected_clarity}
    * **Setting:** {selected_setting}
    * **Metal:** {selected_metal}
    * **Certificate:** {selected_certificate} 
    """
    
    # UPDATED: Display logic for side stone shapes
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

