import gradio as gr
import requests
import os
import json
import re

# API Server URL
API_URL = "http://127.0.0.1:8000"

# ==========================================
# Helper Functions (الذكاء بتاع الواجهة)
# ==========================================

# 1. دالة بتعرف النص اللي راجع عربي ولا إنجليزي عشان تظبط الاتجاه
def is_arabic(text):
    if not text: return False
    # بتدور على أي حرف من حروف اللغة العربية في النص
    return bool(re.search(r'[\u0600-\u06FF]', str(text)))


# 2. دالة بتنظف الـ JSON بتاع التلخيص وتحوله لنص مقروء
def format_summary_data(data):
    raw_text = json.dumps(data, ensure_ascii=False)
    arab = is_arabic(raw_text)
    
    lines = []
    
    # التعديل هنا: بنشيك الأول لو الداتا فيها مفتاح اسمه chapters أو summary
    if isinstance(data, dict):
        summary_list = data.get("chapters", data.get("summary", data))
    else:
        summary_list = data
    
    if isinstance(summary_list, list):
        for i, item in enumerate(summary_list, 1):
            if isinstance(item, dict):
                c_num = item.get("chapter_number", i)
                # بندور على النص بتاع التلخيص
                content = item.get("summary", item.get("content", str(item)))
                
                # التنسيق: الفصل X: التلخيص...
                title = f"الفصل {c_num}:" if arab else f"Chapter {c_num}:"
                lines.append(title)
                lines.append(f"{content}\n")
            else:
                title = f"الفصل {i}:" if arab else f"Chapter {i}:"
                lines.append(title)
                lines.append(f"{item}\n")
    elif isinstance(summary_list, str):
        lines.append(summary_list)
    else:
        lines.append(str(data))
        
    formatted_text = "\n".join(lines).strip()
    css_class = "rtl-textbox" if arab else "ltr-textbox"
    return gr.Textbox(value=formatted_text, elem_classes=css_class)


# 3. دالة بتنظف الـ JSON بتاع الكويز وتحوله لنص مقروء
def format_quiz_data(data):
    raw_text = json.dumps(data, ensure_ascii=False)
    arab = is_arabic(raw_text)
    
    lines = []
    # بنوصل لمصفوفة الفصول اللي جوه مفتاح quiz
    quiz_list = data.get("quiz", data) if isinstance(data, dict) else data
    
    if not isinstance(quiz_list, list):
        return gr.Textbox(value=str(data), elem_classes="rtl-textbox" if arab else "ltr-textbox")
        
    for chapter in quiz_list:
        if not isinstance(chapter, dict): continue
        
        c_num = chapter.get("chapter_number", 1)
        questions = chapter.get("questions", [])
        
        # عنوان الفصل
        if arab:
            lines.append(f"--- أسئلة الفصل {c_num} ---")
        else:
            lines.append(f"--- Chapter {c_num} Questions ---")
            
        for q_data in questions:
            diff_eng = str(q_data.get("difficulty", "")).lower()
            q_text = q_data.get("question", "")
            a_text = q_data.get("ideal_answer", "")
            
            # تنسيق السؤال والإجابة
            if arab:
                # قاموس ترجمة الصعوبة
                diff_ar_map = {"easy": "السهل", "medium": "المتوسط", "hard": "الصعب"}
                diff_str = diff_ar_map.get(diff_eng, diff_eng)
                
                lines.append(f"السؤال {diff_str}: {q_text}")
                lines.append(f"الإجابة: {a_text}\n")
            else:
                diff_str = diff_eng.capitalize()
                lines.append(f"Question ({diff_str}): {q_text}")
                lines.append(f"Answer: {a_text}\n")
                
    formatted_text = "\n".join(lines).strip()
    css_class = "rtl-textbox" if arab else "ltr-textbox"
    return gr.Textbox(value=formatted_text, elem_classes=css_class)


# ==========================================
# Main API Functions
# ==========================================

def upload_file(file_path):
    if not file_path:
        return "❌ Please upload a file first.", None
        
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        files = {"file": (filename, f)}
        response = requests.post(f"{API_URL}/upload", files=files)
        
    if response.status_code == 200:
        return "✅ File uploaded successfully! Choose an action below.", filename
    return f"❌ Upload failed: {response.text}", None


def get_summary(filename):
    if not filename: return gr.Textbox(value="❌ No file uploaded.", elem_classes="ltr-textbox")
    
    response = requests.post(f"{API_URL}/summarize?filename={filename}")
    if response.status_code == 200:
        return format_summary_data(response.json()["result"])
    return gr.Textbox(value=response.text, elem_classes="ltr-textbox")


def get_translation(filename):
    if not filename: return gr.Textbox(value="❌ No file uploaded.", elem_classes="ltr-textbox")
    
    response = requests.post(f"{API_URL}/translate?filename={filename}")
    if response.status_code == 200:
        result_text = response.json()["result"]
        # فحص لغة الترجمة لضبط الاتجاه
        css = "rtl-textbox" if is_arabic(result_text) else "ltr-textbox"
        return gr.Textbox(value=result_text, elem_classes=css)
    return gr.Textbox(value=response.text, elem_classes="ltr-textbox")


def get_quiz_smart(filename):
    if not filename: return gr.Textbox(value="❌ No file uploaded.", elem_classes="ltr-textbox")
    
    quiz_response = requests.post(f"{API_URL}/quiz?filename={filename}")
    
    if quiz_response.status_code == 404 and "Summary not found" in quiz_response.text:
        print("⚠️ No summary found... Generating summary in the background first...")
        requests.post(f"{API_URL}/summarize?filename={filename}")
        quiz_response = requests.post(f"{API_URL}/quiz?filename={filename}")
        
    if quiz_response.status_code == 200:
        return format_quiz_data(quiz_response.json()["result"])
    return gr.Textbox(value=quiz_response.text, elem_classes="ltr-textbox")

# ==========================================
# UI Layout Construction (تصميم الواجهة)
# ==========================================

# ضفنا الكلاسين عشان نتحكم فيهم براحتنا
custom_css = """
.rtl-textbox textarea {
    direction: rtl !important;
    text-align: right !important;
    overflow-y: auto !important;
}
.ltr-textbox textarea {
    direction: ltr !important;
    text-align: left !important;
    overflow-y: auto !important;
}
"""

with gr.Blocks(title="AI Document Assistant", theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown("# 🤖 AI Document Analyzer")
    gr.Markdown("Upload a text file (.txt) and choose to summarize, translate, or generate a quiz.")
    
    current_filename = gr.State(None)
    
    with gr.Row():
        file_input = gr.File(label="Upload File (.txt)", file_types=[".txt"])
        upload_status = gr.Textbox(label="Upload Status", interactive=False)
    
    with gr.Row():
        btn_summary = gr.Button("📝 Summarize")
        btn_translate = gr.Button("🌐 Translate")
        btn_quiz = gr.Button("🧠 Generate Quiz (Smart)")
        
    # المربع بيبدأ عادي LTR، والدوال هي اللي بتغيره حسب الداتا
    output_display = gr.Textbox(
        label="Output / Result", 
        lines=15, 
        max_lines=15, 
        elem_classes="ltr-textbox"
    )
    
    file_input.upload(fn=upload_file, inputs=file_input, outputs=[upload_status, current_filename])
    
    # هنا بنستقبل التعديل الديناميكي في الـ Textbox
    btn_summary.click(fn=get_summary, inputs=current_filename, outputs=output_display)
    btn_translate.click(fn=get_translation, inputs=current_filename, outputs=output_display)
    btn_quiz.click(fn=get_quiz_smart, inputs=current_filename, outputs=output_display)

if __name__ == "__main__":
    demo.launch()