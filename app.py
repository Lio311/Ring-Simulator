import streamlit as st
from PIL import Image
import os

# --- Page Configuration ---
# Set the layout to wide and define the page title
st.set_page_config(layout="wide", page_title="מעצב טבעות")

# --- Main Title ---
st.title("💎 מעצב טבעות היהלום האישי שלך")
st.write("בחר את המרכיבים בסרגל הצד כדי לעצב את טבעת החלומות שלך.")

# --- Constants & Options ---

# List of available diamond shapes
DIAMOND_SHAPES = [
    "Round (עגול)", "Princess (נסיכה)", "Oval (אובל)", "Emerald (אמרלד)",
    "Cushion (קושן)", "Pear (אגס)", "Marquise (מרקיזה)",
    "Asscher (אשר)", "Radiant (רדיאנט)"
]

# Dictionary for metal types (Display Name -> file_key)
METALS = {
    "זהב צהוב (14K)": "yellow_gold",
    "זהב לבן (14K)": "white_gold",
    "פלטינה": "platinum",
    "רוז גולד (14K)": "rose_gold"
}

# Dictionary for setting types (Display Name -> file_key)
SETTINGS = {
    "סוליטר (יהלום בודד)": "solitaire",
    "הילה (Halo - יהלום מרכזי מוקף קטנים)": "halo",
    "שלושה יהלומים (Three-Stone)": "three_stone"
}

# --- Sidebar Widgets (User Input) ---
st.sidebar.header("בחר את מרכיבי הטבעת")

# 1. Diamond Shape Selection
selected_shape = st.sidebar.selectbox("1. בחר צורת יהלום:", DIAMOND_SHAPES)

# 2. Carat Size Selection
selected_carat = st.sidebar.slider("2. בחר גודל (קראט):",
                                   min_value=0.5, max_value=3.0,
                                   value=1.0, step=0.1)

# 3. Setting Selection
selected_setting = st.sidebar.selectbox("3. בחר סוג שיבוץ:", list(SETTINGS.keys()))

# 4. Metal Selection
selected_metal = st.sidebar.selectbox("4. בחר סוג מתכת:", list(METALS.keys()))

# 5. Optional "4 C's" for pricing
st.sidebar.subheader("איכות היהלום (4 C's)")
selected_color = st.sidebar.select_slider("צבע (Color):",
                                          options=["J", "I", "H", "G", "F", "E", "D"],
                                          value="G")
selected_clarity = st.sidebar.select_slider("ניקיון (Clarity):",
                                            options=["SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF", "FL"],
                                            value="VS1")

# --- Price Calculation Logic (Demo) ---

# Base price for a 1-carat, G-color, VS1-clarity round diamond
BASE_DIAMOND_PRICE_PER_CARAT = 5000  # $

# Price multipliers for different shapes
SHAPE_MULTIPLIERS = {
    "Round (עגול)": 1.0, "Princess (נסיכה)": 0.9, "Oval (אובל)": 0.95,
    "Emerald (אמרלד)": 0.9, "Cushion (קושן)": 0.85, "Pear (אגס)": 0.9,
    "Marquise (מרקיזה)": 0.8, "Asscher (אשר)": 0.85, "Radiant (רדיאנט)": 0.88
}

# Price multipliers for color grades
COLOR_MULTIPLIERS = {"J": 0.8, "I": 0.9, "H": 1.0, "G": 1.1, "F": 1.3, "E": 1.5, "D": 2.0}

# Price multipliers for clarity grades
CLARITY_MULTIPLIERS = {"SI2": 0.8, "SI1": 0.9, "VS2": 1.0, "VS1": 1.1, "VVS2": 1.3, "VVS1": 1.5, "IF": 1.8, "FL": 2.2}

# Base prices for metals and settings
METAL_BASE_PRICE = {"זהב צהוב (14K)": 500, "זהב לבן (14K)": 550, "פלטינה": 900, "רוז גולד (14K)": 520}
SETTING_BASE_PRICE = {"סוליטר (יהלום בודד)": 200, "הילה (Halo - יהלום מרכזי מוקף קטנים)": 800, "שלושה יהלומים (Three-Stone)": 600}

def calculate_price(shape, carat, color, clarity, metal, setting):
    """
    Calculates the estimated price of the ring based on user selections.
    This is a simplified demo model.
    """
    # 1. Calculate diamond price
    base_price = BASE_DIAMOND_PRICE_PER_CARAT * carat
    shape_factor = SHAPE_MULTIPLIERS.get(shape, 1.0)
    color_factor = COLOR_MULTIPLIERS.get(color, 1.0)
    clarity_factor = CLARITY_MULTIPLIERS.get(clarity, 1.0)
    
    diamond_price = base_price * shape_factor * color_factor * clarity_factor
    
    # 2. Calculate setting and metal price
    setting_price = METAL_BASE_PRICE.get(metal, 500) + SETTING_BASE_PRICE.get(setting, 200)
    
    # 3. Calculate total price
    total_price = diamond_price + setting_price
    return total_price, diamond_price, setting_price

# --- Image Composition Logic ---

def create_ring_image(metal_key, setting_key, shape_key, carat):
    """
    Composites the ring image from transparent PNG layers.
    """
    try:
        # 1. Load base image (setting + metal)
        # This assumes you have images like "solitaire_yellow_gold.png"
        metal_file = METALS[metal_key]
        setting_file = SETTINGS[setting_key]
        base_image_path = os.path.join("assets", "settings", f"{setting_file}_{metal_file}.png")
        
        # Fallback image if the specific combination doesn't exist
        if not os.path.exists(base_image_path):
            base_image_path = os.path.join("assets", "settings", "solitaire_yellow_gold.png") 
            
        base_image = Image.open(base_image_path).convert("RGBA")
        
        # 2. Load diamond image
        # Converts "Round (עגול)" to "round"
        shape_file = shape_key.split(" ")[0].lower() 
        diamond_image_path = os.path.join("assets", "shapes", f"{shape_file}.png")
        
        # Fallback diamond image
        if not os.path.exists(diamond_image_path):
            diamond_image_path = os.path.join("assets", "shapes", "round.png") 
            
        diamond_image = Image.open(diamond_image_path).convert("RGBA")

        # 3. Resize diamond based on carat size (simplified scaling)
        base_width, base_height = diamond_image.size
        # Simple scaling factor - you may need to adjust this formula
        scale_factor = (carat / 1.0) * 0.5 + 0.5  
        new_size = (int(base_width * scale_factor), int(base_height * scale_factor))
        diamond_image = diamond_image.resize(new_size, Image.LANCZOS)
        
        # 4. Composite the images
        # These coordinates are estimates. You MUST calibrate (x, y)
        # for each setting type for accurate placement.
        paste_x = (base_image.width - diamond_image.width) // 2
        paste_y = (base_image.height - diamond_image.height) // 2 - 50 # Adjust as needed
        
        # Paste the diamond onto the base image using its alpha channel as a mask
        base_image.paste(diamond_image, (paste_x, paste_y), diamond_image)
        
        return base_image

    except FileNotFoundError as e:
        st.error(f"Image file not found: {e}. Please check your 'assets' folder.")
        return Image.new("RGBA", (500, 500), (255, 255, 255, 0)) # Return a blank image on error
    except Exception as e:
        st.error(f"Error creating image: {e}")
        return Image.new("RGBA", (500, 500), (255, 255, 255, 0))

# --- Main App Logic ---

# 1. Calculate the price based on sidebar selections
total_price, diamond_price, setting_price = calculate_price(
    selected_shape, selected_carat, selected_color,
    selected_clarity, selected_metal, selected_setting
)

# 2. Create the final composite image
#    This line MUST come AFTER the sidebar selections and BEFORE st.image
final_ring_image = create_ring_image(
    selected_metal, 
    selected_setting, 
    selected_shape, 
    selected_carat
)

# 3. Display the results
st.sidebar.success("הטבעת שלך מוכנה!")

# --- Display Area (Main Page) ---

# Split the main area into two columns
col1, col2 = st.columns(2)

# Column 1: The Ring Image
with col1:
    st.header("הטבעת שלך:")
    # This is the line that caused the NameError, it should now work
    st.image(final_ring_image, use_column_width=True)

# Column 2: The Price and Details
with col2:
    st.header(f"הערכת מחיר: ${total_price:,.0f}")
    st.subheader("פירוט הבחירות שלך:")
    
    st.markdown(f"""
    * **צורת יהלום:** {selected_shape}
    * **משקל (קראט):** {selected_carat}
    * **צבע:** {selected_color}
    * **ניקיון:** {selected_clarity}
    * **שיבוץ:** {selected_setting}
    * **מתכת:** {selected_metal}
    """)
    
    st.subheader("פירוט עלות (דמו):")
    st.markdown(f"""
    * **עלות יהלום:** ${diamond_price:,.0f}
    * **עלות שיבוץ ומתכת:** ${setting_price:,.0f}
    """)
