import streamlit as st
from PIL import Image, ImageDraw

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Ring Sketch Designer")

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
# UPDATED: Simplified keys
SETTINGS = {
    "Solitaire (Single Diamond)": "solitaire",
    "Halo": "halo",
    "Three-Stone": "three_stone",
    "Seven-Stone (Cluster Sides)": "seven_stone" # Updated name
}
# NEW: Side stone shapes
SIDE_STONE_SHAPES = ["Round", "Marquise", "Pear"]
CERTIFICATE_TYPES = ["GIA", "CGL"]
USD_TO_ILS_RATE = 3.7 # Example exchange rate

# --- Color definitions for drawing ---
METAL_COLORS_RGB = {
    "yellow_gold": (212, 175, 55),
    "white_gold": (220, 220, 220),
    "rose_gold": (230, 180, 170)
}
DIAMOND_OUTLINE = (50, 50, 50) # Dark grey outline
DIAMOND_FILL = (245, 245, 245)  # Very light grey fill

# --- Sidebar Widgets (User Input) ---
st.sidebar.header("Select Your Ring Components")
selected_shape = st.sidebar.selectbox("1. Select Diamond Shape:", DIAMOND_SHAPES)
selected_carat = st.sidebar.slider("2. Select Size (Carat):",
                                   min_value=0.5, max_value=3.0,
                                   value=1.0, step=0.1)
selected_setting = st.sidebar.selectbox("3. Select Setting Type:", list(SETTINGS.keys()))
selected_metal = st.sidebar.selectbox("4. Select Metal Type:", list(METALS.keys()))
selected_certificate = st.sidebar.selectbox("5. Select Certificate:", CERTIFICATE_TYPES)

# NEW: Conditional selection for side stones
selected_side_stone_shape = "Round" # Default
setting_key = SETTINGS[selected_setting]
if setting_key in ["three_stone", "seven_stone"]:
    selected_side_stone_shape = st.sidebar.selectbox(
        "6. Select Side Stone Shape:", 
        SIDE_STONE_SHAPES
    )

st.sidebar.subheader("Diamond Quality")
selected_color = st.sidebar.select_slider("Color:",
                                          options=["J", "I", "H", "G", "F", "E", "D"],
                                          value="G")
selected_clarity = st.sidebar.select_slider("Clarity:",
                                            options=["SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF", "FL"],
                                            value="VS1")

# --- Price Calculation Logic (Demo) ---
BASE_DIAMOND_PRICE_PER_CARAT = 5000 # Base price in USD
SHAPE_MULTIPLIERS = {
    "Round": 1.0, "Princess": 0.9, "Oval": 0.95,
    "Emerald": 0.9, "Cushion": 0.85, "Pear": 0.9,
    "Marquise": 0.8, "Asscher": 0.85, "Radiant": 0.88
}
COLOR_MULTIPLIERS = {"J": 0.8, "I": 0.9, "H": 1.0, "G": 1.1, "F": 1.3, "E": 1.5, "D": 2.0}
CLARITY_MULTIPLIERS = {"SI2": 0.8, "SI1": 0.9, "VS2": 1.0, "VS1": 1.1, "VVS2": 1.3, "VVS1": 1.5, "IF": 1.8, "FL": 2.2}
METAL_BASE_PRICE = {"Yellow Gold (14K)": 500, "White Gold (14K)": 550, "Rose Gold (14K)": 520} # In USD
SETTING_BASE_PRICE = { # Base price for setting (labor + small round side stones)
    "Solitaire (Single Diamond)": 200,
    "Halo": 800,
    "Three-Stone": 600,
    "Seven-Stone (Cluster Sides)": 1400 # Updated price for 7 stones cluster
} # In USD
CERTIFICATE_MULTIPLIERS = {"GIA": 1.15, "CGL": 1.0}
# NEW: Price multiplier for fancy side stones
SIDE_STONE_MULTIPLIER = {"Round": 1.0, "Marquise": 1.2, "Pear": 1.25}


def calculate_price(shape, carat, color, clarity, metal, setting, certificate, side_shape):
    base_price = BASE_DIAMOND_PRICE_PER_CARAT * carat
    shape_factor = SHAPE_MULTIPLIERS.get(shape, 1.0)
    color_factor = COLOR_MULTIPLIERS.get(color, 1.0)
    clarity_factor = CLARITY_MULTIPLIERS.get(clarity, 1.0)
    cert_factor = CERTIFICATE_MULTIPLIERS.get(certificate, 1.0)
    
    diamond_price_usd = base_price * shape_factor * color_factor * clarity_factor * cert_factor
    
    # Setting price now depends on side stone shape
    setting_base = SETTING_BASE_PRICE.get(setting, 200)
    side_stone_factor = SIDE_STONE_MULTIPLIER.get(side_shape, 1.0)
    
    # Apply side stone multiplier only if it's a multi-stone setting
    if SETTINGS[setting] in ["three_stone", "seven_stone"]:
        setting_price_usd = METAL_BASE_PRICE.get(metal, 500) + (setting_base * side_stone_factor)
    else:
        setting_price_usd = METAL_BASE_PRICE.get(metal, 500) + setting_base
        
    total_price_usd = diamond_price_usd + setting_price_usd
    
    total_price_ils = total_price_usd * USD_TO_ILS_RATE
    diamond_price_ils = diamond_price_usd * USD_TO_ILS_RATE
    setting_price_ils = setting_price_usd * USD_TO_ILS_RATE
    
    return total_price_ils, diamond_price_ils, setting_price_ils

# --- Helper function for drawing side stones ---
def draw_side_stone(draw, shape, center_x, center_y, radius, color, outline):
    """Draws a side stone of a specific shape at a location."""
    if shape == "Round":
        draw.ellipse(
            [(center_x - radius, center_y - radius),
             (center_x + radius, center_y + radius)],
            outline=outline, fill=color, width=2
        )
    elif shape == "Marquise":
        # Draw a polygon for Marquise (thin, pointed ellipse)
        draw.polygon(
            [
                (center_x, center_y - radius), # Top point
                (center_x + radius // 2, center_y), # Right point
                (center_x, center_y + radius), # Bottom point
                (center_x - radius // 2, center_y)  # Left point
            ],
            outline=outline, fill=color, width=2
        )
    elif shape == "Pear":
        # Draw a polygon for Pear (teardrop)
        draw.polygon(
            [
                (center_x, center_y - radius), # Top point
                (center_x + radius, center_y + radius // 2), # Bottom-right
                (center_x - radius, center_y + radius // 2)  # Bottom-left
            ],
            outline=outline, fill=color, width=2
        )

# --- Image SKETCHING Logic (Top-Down "On-Hand" View) ---

def create_ring_sketch(shape, carat, metal_key, setting_key, side_stone_shape):
    """
    Procedurally draws a 2D sketch of the ring from a top-down view,
    showing the band shoulders, not the full circle.
    """
    IMG_SIZE = 500
    CENTER = (IMG_SIZE // 2, IMG_SIZE // 2)
    
    canvas = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    draw = ImageDraw.Draw(canvas)
    
    band_color = METAL_COLORS_RGB.get(metal_key, "grey")
    
    base_size_px = int(carat * 50) 
    half_size = base_size_px // 2
    
    main_stone_coords = [] 
    total_setting_width = base_size_px 

    # --- 3. Draw Main Diamond (FIRST) ---
    # (Coordinates are [top_left_xy, bottom_right_xy])
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
        main_stone_coords = [
            (CENTER[0] - half_size, CENTER[1] - oval_height),
            (CENTER[0] + half_size, CENTER[1] + oval_height)
        ]
        draw.ellipse(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)

    elif "Emerald" in shape or "Radiant" in shape: # Radiant is similar
        cut_size = half_size // 4
        points = [
            (CENTER[0] - half_size + cut_size, CENTER[1] - half_size), (CENTER[0] + half_size - cut_size, CENTER[1] - half_size),
            (CENTER[0] + half_size, CENTER[1] - half_size + cut_size), (CENTER[0] + half_size, CENTER[1] + half_size - cut_size),
            (CENTER[0] + half_size - cut_size, CENTER[1] + half_size), (CENTER[0] - half_size + cut_size, CENTER[1] + half_size),
            (CENTER[0] - half_size, CENTER[1] + half_size - cut_size), (CENTER[0] - half_size, CENTER[1] - half_size + cut_size),
        ]
        draw.polygon(points, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)

    elif "Cushion" in shape:
        # Draw a rectangle with rounded corners
        draw.rounded_rectangle(main_stone_coords, radius=half_size // 3, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)

    elif "Pear" in shape:
        points = [
            (CENTER[0], CENTER[1] - half_size), # Top point
            (CENTER[0] + half_size, CENTER[1] + half_size), # Bottom-right
            (CENTER[0] - half_size, CENTER[1] + half_size)  # Bottom-left
        ]
        draw.polygon(points, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)

    elif "Marquise" in shape:
        points = [
            (CENTER[0], CENTER[1] - half_size), # Top point
            (CENTER[0] + half_size, CENTER[1]), # Right point
            (CENTER[0], CENTER[1] + half_size), # Bottom point
            (CENTER[0] - half_size, CENTER[1])  # Left point
        ]
        draw.polygon(points, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    
    else: # Fallback for Asscher or others
        draw.rectangle(main_stone_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)


    # --- 4. Draw the Setting (Prongs, Halo, Side Stones) ---
    
    if "solitaire" in setting_key:
        coords = main_stone_coords
        prong_size = 8
        half_prong = prong_size // 2
        draw.ellipse([(coords[0][0]-half_prong, coords[0][1]-half_prong), (coords[0][0]+half_prong, coords[0][1]+half_prong)], fill=band_color)
        draw.ellipse([(coords[1][0]-half_prong, coords[0][1]-half_prong), (coords[1][0]+half_prong, coords[0][1]+half_prong)], fill=band_color)
        draw.ellipse([(coords[0][0]-half_prong, coords[1][1]-half_prong), (coords[0][0]+half_prong, coords[1][1]+half_prong)], fill=band_color)
        draw.ellipse([(coords[1][0]-half_prong, coords[1][1]-half_prong), (coords[1][0]+half_prong, coords[1][1]+half_prong)], fill=band_color)
            
    elif "halo" in setting_key:
        halo_padding = 10
        coords = main_stone_coords
        draw.ellipse(
            [(coords[0][0] - halo_padding, coords[0][1] - halo_padding),
             (coords[1][0] + halo_padding, coords[1][1] + halo_padding)],
            outline=band_color, width=8
        )
        total_setting_width += (halo_padding * 2)
            
    elif "three_stone" in setting_key:
        side_stone_radius = base_size_px // 3
        # gap = base_size_px // 8 # REMOVED

        # Left stone
        left_center_x = CENTER[0] - half_size - side_stone_radius # No gap
        draw_side_stone(draw, side_stone_shape, left_center_x, CENTER[1], side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE)
        
        # Right stone
        right_center_x = CENTER[0] + half_size + side_stone_radius # No gap
        draw_side_stone(draw, side_stone_shape, right_center_x, CENTER[1], side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE)
        
        total_setting_width += (side_stone_radius * 4) # No gap

    elif "seven_stone" in setting_key: # UPDATED: Cluster logic
        side_stone_radius = base_size_px // 4
        # gap = base_size_px // 12 # REMOVED
        
        # --- Left Cluster (3 stones) ---
        # 1. Stone next to center
        left_1_x = CENTER[0] - half_size - side_stone_radius # No gap
        left_1_y = CENTER[1]
        draw_side_stone(draw, side_stone_shape, left_1_x, left_1_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE)
        
        # 2. Stone above-left
        left_2_x = left_1_x - side_stone_radius # No gap
        left_2_y = CENTER[1] - side_stone_radius # No gap
        draw_side_stone(draw, side_stone_shape, left_2_x, left_2_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE)
        
        # 3. Stone below-left
        left_3_x = left_1_x - side_stone_radius # No gap
        left_3_y = CENTER[1] + side_stone_radius # No gap
        draw_side_stone(draw, side_stone_shape, left_3_x, left_3_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE)
        
        # --- Right Cluster (3 stones) ---
        # 1. Stone next to center
        right_1_x = CENTER[0] + half_size + side_stone_radius # No gap
        right_1_y = CENTER[1]
        draw_side_stone(draw, side_stone_shape, right_1_x, right_1_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE)
        
        # 2. Stone above-right
        right_2_x = right_1_x + side_stone_radius # No gap
        right_2_y = CENTER[1] - side_stone_radius # No gap
        draw_side_stone(draw, side_stone_shape, right_2_x, right_2_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE)
        
        # 3. Stone below-right
        right_3_x = right_1_x + side_stone_radius # No gap
        right_3_y = CENTER[1] + side_stone_radius # No gap
        draw_side_stone(draw, side_stone_shape, right_3_x, right_3_y, side_stone_radius, DIAMOND_FILL, DIAMOND_OUTLINE)

        # Update total width based on the cluster's outermost point
        # Total width added on one side is approx side_stone_radius * 2 (for stone 1) + side_stone_radius * 2 (for stone 2/3)
        total_setting_width += (side_stone_radius * 8) # (4 on left, 4 on right)
            
    # --- 5. Draw the Ring Band "Shoulders" (LAST) ---
    band_thickness = 12
    band_y_start = CENTER[1] - (band_thickness // 2)
    band_y_end = CENTER[1] + (band_thickness // 2)

    setting_half_width = total_setting_width // 2
    band_end_x_left = CENTER[0] - setting_half_width
    band_end_x_right = CENTER[0] + setting_half_width

    band_end_x_left = max(0, band_end_x_left)
    band_end_x_right = min(IMG_SIZE, band_end_x_right)

    # Left shoulder
    draw.rectangle(
        [(0, band_y_start), (band_end_x_left, band_y_end)],
        fill=band_color
    )
    # Right shoulder
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
    selected_certificate, selected_side_stone_shape # Pass new var
)

# 2. Generate the sketch
final_ring_image = create_ring_sketch(
    selected_shape,
    selected_carat,
    METALS[selected_metal],
    SETTINGS[selected_setting],
    selected_side_stone_shape # Pass new var
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
    
    # Only add side stone shape to list if relevant
    if SETTINGS[selected_setting] in ["three_stone", "seven_stone"]:
        selections_markdown += f"\n    * **Side Stone Shape:** {selected_side_stone_shape}"
        
    st.markdown(selections_markdown)
    
    st.subheader("Cost Breakdown (Demo):")
    st.markdown(f"""
    * **Diamond Cost:** ₪{diamond_price:,.0f}
    * **Setting & Metal Cost:** ₪{setting_price:,.0f}
    """)


