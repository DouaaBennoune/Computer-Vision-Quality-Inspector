"""
Computer Vision Quality Inspector - Frontend (Streamlit-HTML-CSS)
connects to FastAPI Backend
"""
import streamlit as st
import pandas as pd
import requests
import os
import zipfile
import io
from typing import List

#API_URL=os.getenv("API_URL")
API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1/predict")

st.set_page_config(
    page_title="Computer Vision Quality Inspector",
    page_icon="🔩",
    layout="wide",
    initial_sidebar_state="collapsed")

st.markdown("""
    <style>
            
            /*background and general styling*/
            .main{
            background-color:#F2EAE0;
            color:#4A4466;}
            .stApp{
            background-color:#F2EAE0;}  
            .cards{
            padding:40px;
            border-radius: 10px;
            border-left: 4px solid #e9e9e9;
            color:#ffffff;
            transition:transform 0.2s;
            }     
            .cards:hover{
            background-color:#BDA6CE;
            transform:translateY(-5px);
            }  
            .stButton > button {
            font-size: 20px!important;
            font-weight: bold !important;
            background:#F2EAE0;
            color:#6b6470;
            font_weight:bold;
            border:none;
            border_radius:8px;
            padding:12px 24px;
            width:100%;
            transition: all 0.3s;
            

            }
            .stButton > button:hover{
            font-size: 20px;
            font-weight: bold;
            background: #BDA6CE !important;
            color:#1d1b22 !important;
            box-shadow: 0 4px 12px #FFDBFD!important;
            }
            .stButton > button:hover p {
            font-size: 20px;
            font-weight: bold;
            color: #1d1b22 !important;
            }
            .stButton > button:hover span {
            font-size: 20px;
            font-weight: bold;
            color: #1d1b22 !important;
            }
            [data-testid="stDataFrame"] {
            background-color: #9B8EC7;
            }
            .nav-bar {
            min-width: 600px;
            overflow-x: auto;
            }
    </style>        
""",unsafe_allow_html=True)
import streamlit as st

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --font-display: 'Space Grotesk', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-display);
    }

    /* Apply JetBrains Mono to code blocks and small system text */
    code, pre, .stMarkdown code {
        font-family: var(--font-mono);
    }

    /* Optional: footer/system labels */
    .footer, .system-label {
        font-family: var(--font-mono);
        font-size: 0.85rem;
        color: #aaa;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'selected_status' not in st.session_state:
    st.session_state.selected_status = None


def Upload_images(uploaded_files: List):
    try:
        response = requests.post(API_URL, files=uploaded_files, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except Exception:
                error_detail = response.text or f"HTTP {response.status_code}"
            st.error(f"API Error {response.status_code}: {error_detail}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend!")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out — the model may still be loading, try again.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None
def create_zip_of_images(api_data):
    """Fetches predicted images from the API links and packages them into a ZIP file in memory."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for item in api_data['dashboard']:
            img_name = item['id']
            img_url = item['image_link']
            
            try:
                
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    
                    zip_file.writestr(img_name, img_response.content)
            except Exception as e:
                pass 
                
    return zip_buffer.getvalue()  
zip_data = None  
#navigation bar
st.markdown('<div class= "nav-bar">',unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([8, 1, 1, 1, 1])
with col1:
    
    st.markdown("""
                <h3 style="font-family: var(--font-display);color:#6b6470">
               Computer Vision Quality Inspector
                </h3>
                """,unsafe_allow_html=True)
with col2:
    if st.button("Home", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()
with col3:
    if st.button("Upload", use_container_width=True):
        st.session_state.current_page = 'upload'
        st.rerun()
with col4:
    if st.button("Dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()
with col5:
    if st.button("Docs", use_container_width=True):
        st.session_state.current_page = 'docs'
        st.rerun()

st.divider()

# Home page
if (st.session_state.current_page== 'home'):
     st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <h1 style="font-size: 90px; color: #9b8ec7; font-family: var(--font-display); margin-bottom: 10px;">
                Detect every defect.
            </h1>
            <h1 style="font-size: 40px; color:#6b6470; font-family: var(--font-display); margin-bottom: 10px;">
                An AI-powered computer vision inspector for steel surfaces.<br>
                Upload a batch, get a full defect report — classified, counted and <br>
                annotated — in seconds.
            </h1>
        

        </div>
    """, unsafe_allow_html=True)
     
     col1,col2,col3,col4=st.columns([1,1.1,1.1,1])
     with col2:
         if st.button("Start Inspection",use_container_width=True):
             st.session_state.current_page= "upload"
             st.rerun()
     with col3:
         if st.button("Read Documentation",use_container_width=True):
             st.session_state.current_page= "docs"
             st.rerun()
     st.markdown("<br><br>", unsafe_allow_html=True)

#features grid
     
     c1, c2, c3 = st.columns(3)
     with c1:
         st.markdown("""
             <div class="cards" style="background-color:#ffffff;">
                     <h3 style="color:#1d1b22;font-size: 30px;font-weight:bold;margin-bottom: 10px;font-family: var(--font-display);">Batch Detection</h3>
                     <h4 style="color:#6b6470;font-size:25px;font-family: var(--font-display);">Upload single images or a ZIP — every frame is analyzed in parallel</h4>
            </div>
                    """, unsafe_allow_html=True)
     with c2:
         st.markdown("""
             <div class="cards" style="background-color:#ffffff;">
                     <h3 style="color:#1d1b22;font-size: 30px;font-weight:bold;margin-bottom: 10px;font-family: var(--font-display);">YOLOv8n Inference</h3>
                     <h4 style="color:#6b6470;font-size:25px;font-family: var(--font-display);">State-of-the-art object detection fine-tuned on NEU steel defect data.</h4>
            </div>
                    """, unsafe_allow_html=True)
     with c3:
         st.markdown("""
             <div class="cards" style="background-color:#ffffff;">
                     <h3 style="color:#1d1b22;font-size: 30px;font-weight:bold;margin-bottom: 10px;font-family: var(--font-display);">Dashboard</h3>
                     <h4 style="color:#6b6470;font-size:25px;font-family: var(--font-display);">Aggregate KPIs and per-image breakdowns with bounding-box overlays.</h4>
            </div>
                    """, unsafe_allow_html=True)
#UPLOAD PAGE
elif(st.session_state.current_page=='upload'):
    st.markdown("""
<h5 style="color:#886e82;font-size:15px;margin-bottom: 1px;margin-left: 350px;font-family: var(--font-mono);">Step 01 ● Acquisition</h5>
<h1 style="color:#1d1b22;font-size:50px;margin-bottom: 1px;margin-left: 350px;font-family: var(--font-display);">Upload for Inspection</h1>
<h4 style="color:#886e82;font-size:18px;margin-bottom: 1px;margin-left: 350px;font-family: var(--font-display);">Drop steel surface images or a ZIP archive. Supported: .jpg  .png  .jpeg  .bmp   .tiff   .webp .</h4> 


""",unsafe_allow_html=True)
    c1,c2,c3=st.columns([1.99,7,1.99])
    with c1:
        st.markdown("")
    with c2:
        uploaded_files=st.file_uploader("Drag & drop steel surface images or ZIP files",type=["zip","jpg", "jpeg", "png", "bmp", "tiff", "webp"],label_visibility="collapsed",accept_multiple_files=True)
        files = []
        if uploaded_files:
            for f in uploaded_files:
                files.append(("file", (f.name, f.getbuffer(), f.type)))
                st.info(f"Selected:{f.name}")
        if st.button("Run Inspection",use_container_width=True):
            result=Upload_images(files)
            if result:
                st.session_state.predictions=result
                st.session_state.selected_status=None
                st.session_state.current_page='dashboard'
                st.rerun()
    with c3:
        st.markdown("")
#page dashboard

elif (st.session_state.current_page=='dashboard'):
    
    if not st.session_state.predictions:
        
        st.markdown("""
<h1 style="color:#1d1b22;font-size:60px;text-align: center;font-family:var(--font-display);margin-top: 100px;">No inspection yet</h1>
<h4 style="color:#886e82;font-size:25px;margin-bottom: 20px;text-align: center;font-family: var(--font-display);">Run an inspection from the Upload page to populate this dashboard.</h4> 

""",unsafe_allow_html=True)

        if st.button("back to Upload",use_container_width=True):
            
            c1,c2,c3=st.columns([2,1,2])
            with c2:
                st.session_state.current_page='upload'
    else:
        api_data=st.session_state.predictions
        
        df_pred=pd.DataFrame(api_data['dashboard'])
        st.markdown("""
<h1 style="color:#1d1b22;font-size:50px;margin-bottom: 1px;margin-left: 35px;font-family: var(--font-display);">Detailed Data Registry</h1>

""",unsafe_allow_html=True)
        
        if not df_pred.empty:
            c1,c2=st.columns([1,1])
            

            with c1:
                st.markdown(f"""
                <div class="cards" style="background-color:#ffffff;padding:15px;">
                        <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Crazing</h3>
                        <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-mono);">{api_data['crazing']}</h4>
                </div>
                <br></br>           
                <div class="cards" style="background-color:#ffffff;padding:15px;">
                        <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Patches</h3>
                        <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-mono);">{api_data['patches']}</h4>
                </div>
                <br></br>   
                <div class="cards" style="background-color:#ffffff;padding:15px;">
                        <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Rolled-in Scale</h3>
                        <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-mono);">{api_data['rolled_in_scale']}</h4>
                </div>
            
    """,unsafe_allow_html=True)
                
                with c2:
                    
                    st.markdown(f"""
                                
                <div class="cards" style="background-color:#ffffff;padding:15px;">
                        <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Inclusion</h3>
                        <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-mono);">{api_data['inclusion']}</h4>
                </div>
                        <br></br>       
                <div class="cards" style="background-color:#ffffff;padding:15px;">
                        <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Pitted Surface</h3>
                        <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-mono);">{api_data['pitted_surface']}</h4>
                </div>
                <br></br>   
                <div class="cards" style="background-color:#ffffff;padding:15px;">
                        <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Scratches</h3>
                        <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-mono);">{api_data['scratches']}</h4>
                </div>
            <br></br>
            <br></br>
            <br></br>
    """,unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True) 
                    api_data=st.session_state.predictions    
                    zip_data = create_zip_of_images(api_data)
                        
               


            table_df = df_pred[['id', 'defects', 'image_link']].copy()
            table_df['defects'] = table_df['defects'].apply(
                lambda x: ", ".join([f"{d['defect_class']} ({d['count']})" for d in x]) if isinstance(x, list) else x
            )
            st.dataframe(
                    table_df,
                    use_container_width=True,
                    column_config={
                        "id": "Image id",
                        "defects": "defect class",
                        "image_link": st.column_config.LinkColumn("View detected Image")
                    },
                    hide_index=True
                )
        else:
            st.info("No equipment found in this category.")
elif st.session_state.current_page=='docs':
    c1,c2,c3=st.columns([1.99,7,1.99])

    with c2:

        st.markdown("""
        <h1 style="color:#1d1b22;font-size:60px;font-family:var(--font-display);margin-top: 20px;margin-left: 0px;">Documentation</h1>
        <h4 style="color:#886e82;font-size:25px;margin-bottom: 20px;font-family: var(--font-display);margin-left: 0px;">The AI Quality Inspector is a computer-vision dashboard that classifies six common steel surface defects: crazing, inclusion, patches, pitted surface, rolled-in scale,and scratches. The frontend uploads images to a local FastAPI backend running a YOLOv8 object-detection model by Ultralytics and renders the results — both aggregate KPIs and per-image annotated previews.</h4> 
        <h1 style="color:#1d1b22;font-size:60px;font-family:var(--font-display);margin-top: 20px;margin-left: 0px;">Defect Classes</h1>
        
        """,unsafe_allow_html=True)
        c1,c2=st.columns([1,1])
        with c1:
            st.markdown("""
            <div class="cards" style="background-color:#ffffff;padding:15px;">
                    <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Crazing</h3>
                    <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-display);">Network of fine surface cracks</h4>
            </div>
            <br></br>           
            <div class="cards" style="background-color:#ffffff;padding:15px;">
                    <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Patches</h3>
                    <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-display);">Discolored regions / irregular texture</h4>
            </div>
            <br></br>   
            <div class="cards" style="background-color:#ffffff;padding:15px;">
                    <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Rolled-in Scale</h3>
                    <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-display);">Oxide scale pressed into surface during rolling</h4>
            </div>
        
""",unsafe_allow_html=True)
        with c2:
                st.markdown("""
                            
            <div class="cards" style="background-color:#ffffff;padding:15px;">
                    <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Inclusion</h3>
                    <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-display);">Foreign material embedded in surface</h4>
            </div>
                    <br></br>       
            <div class="cards" style="background-color:#ffffff;padding:15px;">
                    <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Pitted Surface</h3>
                    <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-display);">Small cavities or pits in the metal</h4>
            </div>
            <br></br>   
            <div class="cards" style="background-color:#ffffff;padding:15px;">
                    <h3 style="color:#1d1b22;font-size: 25px;font-weight:bold;font-family: var(--font-display);">Scratches</h3>
                    <h4 style="color:#6b6470;font-size:18px;font-family: var(--font-display);">Linear grooves on the surface</h4>
            </div>
        
""",unsafe_allow_html=True)
header_col, button_col = st.columns([7, 3])
        
if zip_data is not None:
    st.download_button(
        label="📥 Download Annotated Images (.ZIP)",
        data=zip_data,
        file_name="AI_Inspected_Images.zip",
        mime="application/zip",
        use_container_width=True
    )






                