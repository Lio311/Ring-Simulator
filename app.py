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
    # Platinum removed
    "Rose Gold (14K)": "rose_gold"
}
SETTINGS = {
    "Solitaire (Single Diamond)": "solitaire",
    "Halo (Center diamond surrounded by small ones)": "halo",
    "Three-Stone": "three_stone"
}
# NEW: Certificate Types
CERTIFICATE_TYPES = ["GIA", "CGL"]

# NEW: Currency Conversion
USD_TO_ILS_RATE = 3.7 # Example exchange rate

# --- Color definitions for drawing ---
METAL_COLORS_RGB = {
    "yellow_gold": (212, 175, 55),
    "white_gold": (220, 220, 220),
    # platinum removed
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
# NEW: Certificate selection
selected_certificate = st.sidebar.selectbox("5. Select Certificate:", CERTIFICATE_TYPES)

st.sidebar.subheader("Diamond Quality")
selected_color = st.sidebar.select_slider("Color:",
                                          options=["J", "I", "H", "G", "F", "E", "D"],
                                          value="G")
selected_clarity = st.sidebar.select_slider("Clarity:",
                                            options=["SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF", "FL"],
                                            value="VS1")

# --- Price Calculation Logic (Demo) ---
BASE_DIAMOND_PRICE_PER_CARAT = 5000 # Base price in USD
# IMPORTANT: Keys must match the new English strings in DIAMOND_SHAPES
SHAPE_MULTIPLIERS = {
    "Round": 1.0, "Princess": 0.9, "Oval": 0.95,
    "Emerald": 0.9, "Cushion": 0.85, "Pear": 0.9,
    "Marquise": 0.8, "Asscher": 0.85, "Radiant": 0.88
}
COLOR_MULTIPLIERS = {"J": 0.8, "I": 0.9, "H": 1.0, "G": 1.1, "F": 1.3, "E": 1.5, "D": 2.0}
CLARITY_MULTIPLIERS = {"SI2": 0.8, "SI1": 0.9, "VS2": 1.0, "VS1": 1.1, "VVS2": 1.3, "VVS1": 1.5, "IF": 1.8, "FL": 2.2}
# IMPORTANT: Keys must match the new English strings in METALS
METAL_BASE_PRICE = {"Yellow Gold (14K)": 500, "White Gold (14K)": 550, "Rose Gold (14K)": 520} # In USD
# IMPORTANT: Keys must match the new English strings in SETTINGS
SETTING_BASE_PRICE = {"Solitaire (Single Diamond)": 200, "Halo (Center diamond surrounded by small ones)": 800, "Three-Stone": 600} # In USD
# NEW: Certificate price factor
CERTIFICATE_MULTIPLIERS = {"GIA": 1.15, "CGL": 1.0} # GIA costs 15% more

def calculate_price(shape, carat, color, clarity, metal, setting, certificate):
    # 1. Calculate Diamond Price in USD
    base_price = BASE_DIAMOND_PRICE_PER_CARAT * carat
    shape_factor = SHAPE_MULTIPLIERS.get(shape, 1.0)
    color_factor = COLOR_MULTIPLIERS.get(color, 1.0)
    clarity_factor = CLARITY_MULTIPLIERS.get(clarity, 1.0)
    cert_factor = CERTIFICATE_MULTIPLIERS.get(certificate, 1.0)
    
    diamond_price_usd = base_price * shape_factor * color_factor * clarity_factor * cert_factor
    
    # 2. Calculate Setting Price in USD
    setting_price_usd = METAL_BASE_PRICE.get(metal, 500) + SETTING_BASE_PRICE.get(setting, 200)
    
    # 3. Calculate Total Price in USD
    total_price_usd = diamond_price_usd + setting_price_usd
    
    # 4. Convert all prices to ILS
    total_price_ils = total_price_usd * USD_TO_ILS_RATE
    diamond_price_ils = diamond_price_usd * USD_TO_ILS_RATE
    setting_price_ils = setting_price_usd * USD_TO_ILS_RATE
    
    return total_price_ils, diamond_price_ils, setting_price_ils

# --- Image SKETCHING Logic (Top-Down View) ---

def create_ring_sketch(shape, carat, metal_key, setting_key):
    """
    Procedurally draws a 2D sketch of the ring from a top-down view.
    """
    IMG_SIZE = 500
    CENTER = (IMG_SIZE // 2, IMG_SIZE // 2)
    
    # 1. Create a blank white canvas
    canvas = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    draw = ImageDraw.Draw(canvas)
    
    # 2. Get colors and dynamic sizes
    band_color = METAL_COLORS_RGB.get(metal_key, "grey")
    
    # This is the main logic: convert carat to pixel size
    base_size_px = int(carat * 80)
    half_size = base_size_px // 2

    # 3. Draw the Ring Band (as a simple thick circle)
    # This is the top-down view
    band_radius = half_size + 15 
    band_thickness = 10
    draw.ellipse(
        [(CENTER[0] - band_radius, CENTER[1] - band_radius),
         (CENTER[0] + band_radius, CENTER[1] + band_radius)],
        outline=band_color,
        width=band_thickness
    )
    
    # 4. Draw the Diamond Shape
    shape_coords = []
    
    if "Round" in shape:
        shape_coords = [
            (CENTER[0] - half_size, CENTER[1] - half_size),
            (CENTER[0] + half_size, CENTER[1] + half_size)
        ]
        draw.ellipse(shape_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
    
    elif "Princess" in shape:
        shape_coords = [
            (CENTER[0] - half_size, CENTER[1] - half_size),
            (CENTER[0] + half_size, CENTER[1] + half_size)
        ]
        draw.rectangle(shape_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)
        # Add simple facets
        draw.line([(shape_coords[0]), (shape_coords[1])], fill=DIAMOND_OUTLINE)
        draw.line([(shape_coords[0][0], shape_coords[1][1]), (shape_coords[1][0], shape_coords[0][1])], fill=DIAMOND_OUTLINE)

    elif "Oval" in shape:
        # Make it taller than it is wide (e.g., 1.4 ratio)
        oval_height = int(half_size * 1.4)
        shape_coords = [
            (CENTER[0] - half_size, CENTER[1] - oval_height),
            (CENTER[0] + half_size, CENTER[1] + oval_height)
        ]
        draw.ellipse(shape_coords, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)

    elif "Emerald" in shape:
        # A rectangle with cut corners (an octagon)
        cut_size = half_size // 4 # How much to cut off the corners
        points = [
            (CENTER[0] - half_size + cut_size, CENTER[1] - half_size), # Top-left
            (CENTER[0] + half_size - cut_size, CENTER[1] - half_size), # Top-right
            (CENTER[0] + half_size, CENTER[1] - half_size + cut_size), # Right-top
            (CENTER[0] + half_size, CENTER[1] + half_size - cut_size), # Right-bottom
            (CENTER[0] + half_size - cut_size, CENTER[1] + half_size), # Bottom-right
            (CENTER[0] - half_size + cut_size, CENTER[1] + half_size), # Bottom-left
            (CENTER[0] - half_size, CENTER[1] + half_size - cut_size), # Left-bottom
            (CENTER[0] - half_size, CENTER[1] - half_size + cut_size), # Left-top
        ]
        draw.polygon(points, outline=DIAMOND_OUTLINE, fill=DIAMOND_FILL, width=2)

    else:
        # Fallback for unimplemented shapes
        draw.rectangle(
            [(CENTER[0] - half_size, CENTER[1] - half_size),
             (CENTER[0] + half_size, CENTER[1] + half_size)],
            outline="red", width=2
        )
        draw.text((10, 10), f"Sketch for '{shape}' not yet implemented.", fill="red")

    # 5. Draw the Setting (Prongs)
    prong_size = 8
    half_prong = prong_size // 2

    if "solitaire" in setting_key and shape_coords:
        if "Round" in shape or "Princess" in shape:
            # Simple 4 prongs at the corners
            coords = shape_coords
            # Top-left prong
            draw.ellipse([(coords[0][0]-half_prong, coords[0][1]-half_prong), (coords[0][0]+half_prong, coords[0][1]+half_prong)], fill=band_color)
            # Top-right prong
            draw.ellipse([(coords[1][0]-half_prong, coords[0][1]-half_prong), (coords[1][0]+half_prong, coords[0][1]+half_prong)], fill=band_color)
            # Bottom-left prong
            draw.ellipse([(coords[0][0]-half_prong, coords[1][1]-half_prong), (coords[0][0]+half_prong, coords[1][1]+half_prong)], fill=band_color)
            # Bottom-right prong
            draw.ellipse([(coords[1][0]-half_prong, coords[1][1]-half_prong), (coords[1][0]+half_prong, coords[1][1]+half_prong)], fill=band_color)
            
    elif "halo" in setting_key and shape_coords:
        # Draw a "halo" (another border) around the main stone
        halo_padding = 10
        if "Round" in shape:
            draw.ellipse(
                [(shape_coords[0][0] - halo_padding, shape_coords[0][1] - halo_padding),
                 (shape_coords[1][0] + halo_padding, shape_coords[1][1] + halo_padding)],
                outline=band_color, width=8
            )
        # (You would add 'elif' for other halo shapes here)
            
    return canvas

# --- Main App Logic ---

# 1. Calculate price
total_price, diamond_price, setting_price = calculate_price(
    selected_shape, selected_carat, selected_color,
    selected_clarity, selected_metal, selected_setting,
    selected_certificate # Pass the new variable
)

# 2. Generate the sketch
final_ring_image = create_ring_sketch(
    selected_shape,
    selected_carat,
    METALS[selected_metal],       # Pass the key (e.g., "yellow_gold")
    SETTINGS[selected_setting]    # Pass the key (e.g., "solitaire")
)

# 3. Display the results
st.sidebar.success("Your sketch is ready!")

# --- Display Area (Main Page) ---
col1, col2 = st.columns(2)

with col1:
    st.header("Your Sketch:")
    st.image(final_ring_image, use_column_width=True)

with col2:
    # Updated to show ILS (₪)
    st.header(f"Estimated Price: ₪{total_price:,.0f}")
    st.subheader("Your Selections:")
    
    st.markdown(f"""
    * **Diamond Shape:** {selected_shape}
    * **Carat Weight:** {selected_carat}
    * **Color:** {selected_color}
    * **Clarity:** {selected_clarity}
    * **Setting:** {selected_setting}
    * **Metal:** {selected_metal}
    * **Certificate:** {selected_certificate} 
    """)
    
    st.subheader("Cost Breakdown (Demo):")
    # Updated to show ILS (₪)
    st.markdown(f"""
    * **Diamond Cost:** ₪{diamond_price:,.0f}
    * **Setting & Metal Cost:** ₪{setting_price:,.0f}
    """)

