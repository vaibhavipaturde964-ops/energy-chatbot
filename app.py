import streamlit as st
import base64
import os

# Import query engine with a clear error message if dependencies are missing
try:
    import query_engine
    import importlib
    importlib.reload(query_engine)
    _engine_loaded = True
except RuntimeError as _engine_err:
    _engine_loaded = False
    _engine_error_msg = str(_engine_err)
except Exception as _engine_err:
    _engine_loaded = False
    _engine_error_msg = f"Failed to load query engine: {_engine_err}"

# Function to convert local image files to base64 for CSS rendering
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return None

# Convert background image (Using bg.png from your folder)
bg_b64 = get_base64_image("bg.png")

if bg_b64:
    bg_css = f"""
        .stApp {{
            background: linear-gradient(rgba(14, 17, 23, 0.82), rgba(14, 17, 23, 0.82)), 
                        url("data:image/png;base64,{bg_b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
    """
else:
    bg_css = """
        .stApp {
            background-color: #0e1117;
        }
    """

# 1. Page Configuration
st.set_page_config(
    page_title="EcoBot — Smart Energy Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom CSS
st.markdown(f"""
    <style>
    {bg_css}
    
    .stApp {{
        color: #ffffff;
    }}
    
    /* Header & Logo Alignment */
    .header-container {{
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 5px;
    }}
    
    .main-title {{
        font-size: 2.2rem;
        font-weight: 800;
        color: #2ecc71;
        margin: 0;
    }}
    
    .sub-title {{
        font-size: 1.0rem;
        color: #9ca3af;
        margin-bottom: 25px;
    }}

    /* Semi-transparent Glass Cards */
    .metric-card {{
        background: rgba(31, 41, 55, 0.8);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(46, 204, 113, 0.4);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 1.3rem;
        font-weight: bold;
        color: #2ecc71;
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        color: #9ca3af;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: rgba(14, 17, 23, 0.92) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("🌱 EcoBot Hub")
    st.caption("AI Energy & Sustainability Assistant")
    st.divider()
    
    st.markdown("### ⚡ System Status")
    st.markdown("🟢 **Model:** `Llama 3.3 (70B)`")
    st.markdown("🟢 **Vector DB:** `ChromaDB`")
    st.markdown("🟢 **Engine:** `Groq RAG`")
    st.divider()
    
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. Top Logo + Header Layout
logo_b64 = get_base64_image("logo.png")

if logo_b64:
    st.markdown(f"""
        <div class="header-container">
            <img src="data:image/png;base64,{logo_b64}" width="50" style="object-fit: contain;">
            <div class="main-title">EcoBot Assistant</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="main-title">EcoBot Assistant</div>', unsafe_allow_html=True)

st.markdown('<div class="sub-title">Your intelligent consultant for smart energy usage, weather impacts, and clean tech.</div>', unsafe_allow_html=True)

# 5. Metric Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><div class="metric-value">⚡ Smart Grid</div><div class="metric-label">Energy Management</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><div class="metric-value">🍃 Zero Carbon</div><div class="metric-label">Sustainability</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><div class="metric-value">🧠 Groq + RAG</div><div class="metric-label">Fast Engine</div></div>', unsafe_allow_html=True)

st.write("")

# 6. Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🌱"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 7. User Input Processing
if not _engine_loaded:
    st.error(f"⚠️ EcoBot cannot start: {_engine_error_msg}\n\nPlease check that `GROQ_API_KEY` is set in your environment or Streamlit Cloud Secrets.")
    st.stop()

if prompt := st.chat_input("Ask about energy efficiency, sustainability, or weather..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🌱"):
        status_placeholder = st.empty()
        status_placeholder.markdown("🤖 *EcoBot is thinking...* `🌱⚡✨` ")
        
        answer = query_engine.query_rag(prompt)
        
        status_placeholder.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})