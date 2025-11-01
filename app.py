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
