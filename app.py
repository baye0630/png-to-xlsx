import os
import cv2
import sys
import numpy as np
import pandas as pd
import streamlit as st
from paddleocr import PPStructure, save_structure_res
from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx

# Patch for numpy 2.0 compatibility if needed
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float
if not hasattr(np, 'bool'):
    np.bool = bool

st.set_page_config(page_title="表格识别工具", layout="wide")

st.title("🖼️ 图片表格识别工具 (PaddleOCR)")
st.markdown("""
本工具使用 **PaddleOCR** (PP-Structure) 进行图片中的表格识别。
请上传包含表格的图片 (PNG, JPG, JPEG)，系统将自动提取表格并支持导出为 Excel 或 CSV。
""")

# Sidebar for settings
with st.sidebar:
    st.header("设置")
    use_gpu = st.checkbox("使用 GPU (如果有)", value=False)
    # lang = st.selectbox("语言", ["ch", "en"], index=0)

@st.cache_resource
def load_model(use_gpu):
    # Initialize PPStructure
    # table=True handles table recognition
    # ocr=True handles text recognition inside the table
    try:
        engine = PPStructure(show_log=True, image_orientation=True, use_gpu=use_gpu, lang='ch')
        return engine
    except Exception as e:
        st.error(f"模型加载失败: {e}")
        return None

def process_image(image_path, engine):
    img = cv2.imread(image_path)
    result = engine(img)
    return result

uploaded_file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    # Save temp file for PaddleOCR (it likes paths)
    temp_filename = f"temp_{uploaded_file.name}"
    cv2.imwrite(temp_filename, image)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("原始图片")
        st.image(uploaded_file, use_container_width=True)

    with col2:
        st.subheader("识别结果")
        run_btn = st.button("开始识别")
        
        if run_btn:
            engine = load_model(use_gpu)
            if engine:
                with st.spinner("正在识别中，初次运行会自动下载模型，请稍候..."):
                    try:
                        results = process_image(temp_filename, engine)
                        
                        # Filter for table results
                        tables = []
                        for region in results:
                            if region['type'] == 'table':
                                tables.append(region)
                        
                        if not tables:
                            st.warning("未检测到明显的表格区域。")
                            # Optionally show all text if no table found?
                            # For now, stick to the prompt's request for table recognition.
                        else:
                            st.success(f"检测到 {len(tables)} 个表格！")
                            
                            for i, table in enumerate(tables):
                                st.markdown(f"### 表格 {i+1}")
                                html = table['res']['html']
                                # Convert HTML table to DataFrame
                                try:
                                    dfs = pd.read_html(html)
                                    if dfs:
                                        df = dfs[0]
                                        st.dataframe(df)
                                        
                                        # Export buttons
                                        csv = df.to_csv(index=False).encode('utf-8-sig')
                                        st.download_button(
                                            label=f"下载表格 {i+1} (CSV)",
                                            data=csv,
                                            file_name=f"table_{i+1}.csv",
                                            mime="text/csv",
                                            key=f"csv_{i}"
                                        )
                                        
                                        # Excel buffer
                                        # Use io.BytesIO
                                        import io
                                        output = io.BytesIO()
                                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                            df.to_excel(writer, index=False, sheet_name='Sheet1')
                                        excel_data = output.getvalue()
                                        
                                        st.download_button(
                                            label=f"下载表格 {i+1} (Excel)",
                                            data=excel_data,
                                            file_name=f"table_{i+1}.xlsx",
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            key=f"xlsx_{i}"
                                        )
                                except Exception as e:
                                    st.error(f"解析表格数据出错: {e}")
                                    st.code(html, language='html')

                    except Exception as e:
                        st.error(f"识别过程出错: {e}")
                        import traceback
                        st.text(traceback.format_exc())
                    finally:
                        # Cleanup temp file if needed, or keep for debugging
                        if os.path.exists(temp_filename):
                            os.remove(temp_filename)

