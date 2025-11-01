import streamlit as st

st.set_page_config(layout="wide", page_title="מעצב טבעות")
st.title("💎 מעצב טבעות היהלום האישי שלך")
st.write("בחר את המרכיבים בסרגל הצד כדי לעצב את טבעת החלומות שלך.")

# --- הגדרת אפשרויות ---

# רשימת הצורות (כפי שביקשת)
DIAMOND_SHAPES = [
    "Round (עגול)", "Princess (נסיכה)", "Oval (אובל)", "Emerald (אמרלד)",
    "Cushion (קושן)", "Pear (אגס)", "Marquise (מרקיזה)", 
    "Asscher (אשר)", "Radiant (רדיאנט)"
]

# סוגי מתכות
METALS = {
    "זהב צהוב (14K)": "yellow_gold",
    "זהב לבן (14K)": "white_gold",
    "פלטינה": "platinum",
    "רוז גולד (14K)": "rose_gold"
}

# סוגי שיבוץ (זה עונה על "כמות היהלומים")
SETTINGS = {
    "סוליטר (יהלום בודד)": "solitaire",
    "הילה (Halo - יהלום מרכזי מוקף קטנים)": "halo",
    "שלושה יהלומים (Three-Stone)": "three_stone"
}

# --- יצירת הווידג'טים בסרגל הצד ---
st.sidebar.header("בחר את מרכיבי הטבעת")

# 1. בחירת צורת היהלום
selected_shape = st.sidebar.selectbox("1. בחר צורת יהלום:", DIAMOND_SHAPES)

# 2. בחירת גודל (משקל קראט)
selected_carat = st.sidebar.slider("2. בחר גודל (קראט):", 
                                   min_value=0.5, max_value=3.0, 
                                   value=1.0, step=0.1)

# 3. בחירת סוג השיבוץ
selected_setting = st.sidebar.selectbox("3. בחר סוג שיבוץ:", list(SETTINGS.keys()))

# 4. בחירת סוג המתכת
selected_metal = st.sidebar.selectbox("4. בחר סוג מתכת:", list(METALS.keys()))

# (אופציונלי) נוסיף את "ארבעת ה-C"
st.sidebar.subheader("איכות היהלום (4 C's)")
selected_color = st.sidebar.select_slider("צבע (Color):", 
                                          options=["J", "I", "H", "G", "F", "E", "D"], 
                                          value="G")
selected_clarity = st.sidebar.select_slider("ניקיון (Clarity):", 
                                            options=["SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF", "FL"], 
                                            value="VS1")

# --- מודל חישוב מחיר (דמו) ---

# מחיר בסיס (לדוגמה, ליהלום עגול 1 קראט, צבע G, ניקיון VS1)
BASE_DIAMOND_PRICE_PER_CARAT = 5000  # $

# מכפילים לצורות (עגול הוא הבסיס 1.0)
SHAPE_MULTIPLIERS = {
    "Round (עגול)": 1.0, "Princess (נסיכה)": 0.9, "Oval (אובל)": 0.95,
    "Emerald (אמרלד)": 0.9, "Cushion (קושן)": 0.85, "Pear (אגס)": 0.9,
    "Marquise (מרקיזה)": 0.8, "Asscher (אשר)": 0.85, "Radiant (רדיאנט)": 0.88
}

# מכפילים לצבע
COLOR_MULTIPLIERS = {"J": 0.8, "I": 0.9, "H": 1.0, "G": 1.1, "F": 1.3, "E": 1.5, "D": 2.0}

# מכפילים לניקיון
CLARITY_MULTIPLIERS = {"SI2": 0.8, "SI1": 0.9, "VS2": 1.0, "VS1": 1.1, "VVS2": 1.3, "VVS1": 1.5, "IF": 1.8, "FL": 2.2}

# מחיר בסיס למתכות ולשיבוצים
METAL_BASE_PRICE = {"זהב צהוב (14K)": 500, "זהב לבן (14K)": 550, "פלטינה": 900, "רוז גולד (14K)": 520}
SETTING_BASE_PRICE = {"סוליטר (יהלום בודד)": 200, "הילה (Halo - יהלום מרכזי מוקף קטנים)": 800, "שלושה יהלומים (Three-Stone)": 600}

def calculate_price(shape, carat, color, clarity, metal, setting):
    # 1. חישוב מחיר היהלום
    base_price = BASE_DIAMOND_PRICE_PER_CARAT * carat
    shape_factor = SHAPE_MULTIPLIERS.get(shape, 1.0)
    color_factor = COLOR_MULTIPLIERS.get(color, 1.0)
    clarity_factor = CLARITY_MULTIPLIERS.get(clarity, 1.0)
    
    diamond_price = base_price * shape_factor * color_factor * clarity_factor
    
    # 2. חישוב מחיר השיבוץ והמתכת
    setting_price = METAL_BASE_PRICE.get(metal, 500) + SETTING_BASE_PRICE.get(setting, 200)
    
    # 3. מחיר סופי
    total_price = diamond_price + setting_price
    return total_price, diamond_price, setting_price

# קבלת המחיר הסופי
total_price, diamond_price, setting_price = calculate_price(
    selected_shape, selected_carat, selected_color, 
    selected_clarity, selected_metal, selected_setting
)
