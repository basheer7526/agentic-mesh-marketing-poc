import streamlit as st
import requests

# Define the backend API URL
API_URL = "http://127.0.0.1:8000/api/v1/workflows/run"

# Page Configuration
st.set_page_config(
    page_title="Agentic Mesh | News Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to exactly match the image's dark, high-tech theme
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dark Theme & Background Grid */
    .stApp {
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
        background-size: 60px 60px;
        color: white;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Breaking Badge */
    .breaking-badge {
        display: inline-flex;
        align-items: center;
        border: 1px solid #FF0000;
        color: #FF0000;
        padding: 4px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    .dot {
        height: 8px;
        width: 8px;
        background-color: #FF0000;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 8px #FF0000;
    }

    /* Typography */
    .sub-header {
        color: #B0B0B0;
        font-size: 1.3rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 10px;
    }
    .hero-title {
        font-size: 5.5rem !important;
        font-weight: 800 !important;
        line-height: 1.05 !important;
        margin-bottom: 20px;
        color: #FFFFFF;
        letter-spacing: -1px;
    }
    
    /* Orange Underline */
    .orange-line {
        width: 150px;
        height: 4px;
        background-color: #FF4500;
        margin-bottom: 30px;
    }

    /* Tags */
    .tags-container {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        margin-bottom: 40px;
    }
    .tag {
        border: 1px solid #555;
        color: #DDD;
        padding: 8px 20px;
        border-radius: 25px;
        font-size: 0.95rem;
        background: rgba(255, 255, 255, 0.03);
    }

    /* Custom Run Button */
    .stButton>button {
        background-color: transparent !important;
        color: #FF4500 !important;
        border: 2px solid #FF4500 !important;
        border-radius: 30px !important;
        padding: 15px 30px !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: 0.3s !important;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #FF4500 !important;
        color: black !important;
        box-shadow: 0 0 20px rgba(255, 69, 0, 0.4) !important;
    }

    /* Style the output cards to be dark */
    div[data-testid="stExpander"] {
        background-color: rgba(20, 20, 20, 0.8);
        border: 1px solid #333;
    }
    
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HTML Hero Section (Matches the Image perfectly)
# ---------------------------------------------------------
st.markdown("""
<div style="padding: 20px 0px;">
    <div class="breaking-badge"><span class="dot"></span> BREAKING</div>
    <div class="sub-header">TECHNICAL DEEP DIVE</div>
    <h1 class="hero-title">Building an<br>Agentic Mesh<br>for News Intelligence</h1>
    <div class="orange-line"></div>
    
    <div class="tags-container">
        <div class="tag">LangGraph Orchestrator</div>
        <div class="tag">Groq Workflows</div>
        <div class="tag">AI Agents SDK</div>
        <div class="tag">RDGCC + RAG</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Application Logic
# ---------------------------------------------------------

col1, col2, col3 = st.columns([1.5, 1, 1.5])

with col1:
    st.markdown("<h4 style='color: #06B6D4;'>AGENTIC PARAMETERS</h4>", unsafe_allow_html=True)
    max_evaluations = st.number_input("Max Articles to Read (Relevance Agent)", min_value=1, max_value=200, value=40, help="How many raw RSS articles should the first agent read?")
    max_articles = st.number_input("Max Output Items (Final Digest)", min_value=1, max_value=10, value=3, help="How many relevant articles make it to the final dashboard?")

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    run_button = st.button("INITIALIZE MESH")

if run_button:
    with st.spinner("ORCHESTRATOR ONLINE: Ingesting feeds, summarizing entities, publishing digest..."):
        payload = {
            "task": "Monitor marketing news and identify important developments in AI marketing, demand generation, customer experience, Martech, and competitor activity.",
            "max_articles": max_articles,
            "max_evaluations": max_evaluations
        }
        
        try:
            response = requests.post(API_URL, json=payload, timeout=600)
            
            if response.status_code == 200:
                data = response.json()
                digest = data.get("digest")
                
                if digest and digest.get("items"):
                    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
                    st.markdown("<h2 style='color: #FF4500;'>AGENTIC DIGEST PUBLISHED</h2>", unsafe_allow_html=True)
                    
                    # Metric Cards
                    m1, m2, m3 = st.columns(3)
                    m1.metric("High Priority Entities", digest.get("high_priority", 0))
                    m2.metric("Medium Priority", digest.get("medium_priority", 0))
                    m3.metric("Low Priority", digest.get("low_priority", 0))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Render each article
                    for idx, item in enumerate(digest.get("items", [])):
                        priority = item.get("priority", "Low")
                        p_color = "#FF0000" if priority == "High" else "#FF8C00" if priority == "Medium" else "#00FF00"
                        
                        with st.container(border=True):
                            st.markdown(f"<h3 style='color: white;'>{item.get('headline')}</h3>", unsafe_allow_html=True)
                            st.markdown(f"**SOURCE:** [{item.get('source')}]({item.get('url')}) &nbsp;|&nbsp; **PRIORITY:** <span style='color: {p_color}; border: 1px solid {p_color}; padding: 2px 8px; border-radius: 10px;'>{priority}</span>", unsafe_allow_html=True)
                            
                            c_left, c_right = st.columns(2)
                            with c_left:
                                st.markdown(f"<div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 5px; border-left: 3px solid #06B6D4;'><b>SUMMARISER</b><br>{item.get('summary')}</div>", unsafe_allow_html=True)
                            with c_right:
                                st.markdown(f"<div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 5px; border-left: 3px solid #FF4500;'><b>ORCHESTRATOR INSIGHT</b><br>{item.get('why_it_matters')}</div>", unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.success(f"**ACTION ITEM:** {item.get('recommended_action')}")
                            
                    # Show Raw API Output Section
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    with st.expander("⚙️ RAW MESH TELEMETRY (JSON OUTPUT)", expanded=False):
                        st.json(data)
                        
                else:
                    st.warning("Mesh execution completed, but no relevant entities matched the criteria.")
                    with st.expander("⚙️ RAW MESH TELEMETRY (JSON OUTPUT)", expanded=False):
                        st.json(data)
                    
            else:
                st.error(f"Mesh Offline: {response.status_code}")
                
        except Exception as e:
            st.error(f"Execution failed: {e}")
