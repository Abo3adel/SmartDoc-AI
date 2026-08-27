from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import json
import PyPDF2
import docx
from pydantic import ValidationError
from schemas.models import StandardResponse, LLMQuizOutput
from services.llm_service import summarize_text, translate_document ,generate_quiz

router = APIRouter()

STORE_FOLDER = "document_store"

def extract_text_from_file(file_path: str, ext: str) -> str:
    text = ""
    if ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    elif ext == ".docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    return text

@router.post("/upload", response_model=StandardResponse)
async def upload_document(file: UploadFile = File(...)):

    ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = [".txt", ".pdf", ".docx"]
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only .txt, .pdf, and .docx files are allowed!")
    
    temp_file_path = f"{STORE_FOLDER}/temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        extracted_text = extract_text_from_file(temp_file_path, ext)
        
        clean_name = file.filename.replace(ext, "")
        final_txt_filename = f"{clean_name}.txt"
        final_txt_path = f"{STORE_FOLDER}/{final_txt_filename}"
        
        with open(final_txt_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
            
        os.remove(temp_file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
        
    return {
        "message": "File uploaded, text extracted and saved successfully!",
        "saved_file": final_txt_filename
    }



@router.post("/summarize", response_model=StandardResponse)
async def summarize_document(filename: str):
    file_path = f"{STORE_FOLDER}/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found! Please upload it first.")
    
    with open(file_path, "r", encoding="utf-8") as file:
        document_text = file.read()
        
    try:
        validated_summary = summarize_text(document_text) 
        if isinstance(validated_summary, str):
            raise HTTPException(status_code=500, detail=validated_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    clean_name = filename.replace(".txt", "")
    summary_file_path = f"{STORE_FOLDER}/{clean_name}_summary.json"

    with open(summary_file_path, "w", encoding="utf-8") as summary_file:
        json.dump(validated_summary.model_dump(), summary_file, ensure_ascii=False, indent=4)
        
    return {
        "message": "Document summarized, validated, and saved successfully!",
        "saved_file": f"{clean_name}_summary.json",
        "result": validated_summary.model_dump()
    }




@router.post("/translate", response_model=StandardResponse)
async def translate_full_document(filename: str):
    file_path = f"{STORE_FOLDER}/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Original file not found! Please upload it first.")
    
    with open(file_path, "r", encoding="utf-8") as file:
        document_text = file.read()

    try:   
        translated_result = translate_document(document_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    translated_file_path = f"{STORE_FOLDER}/translated_{filename}"
    with open(translated_file_path, "w", encoding="utf-8") as translated_file:
        translated_file.write(translated_result)
        
    return {
        "message": "Original document translated and saved successfully!",
        "saved_translated_file": f"translated_{filename}",
        "result": translated_result
    }





@router.post("/quiz", response_model=StandardResponse)
async def create_quiz(filename: str):

    clean_name = filename.replace(".txt", "")
    summary_file_path = f"{STORE_FOLDER}/{clean_name}_summary.json"
    
    if not os.path.exists(summary_file_path):
        raise HTTPException(status_code=404, detail="Summary not found! Please summarize the file first.")
    
    with open(summary_file_path, "r", encoding="utf-8") as file:
        summary_data = file.read()
        
    try:
        validated_quiz = generate_quiz(summary_data) 
        if isinstance(validated_quiz, str):
            raise HTTPException(status_code=500, detail=validated_quiz)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    quiz_file_path = f"{STORE_FOLDER}/{clean_name}_quiz.json"
    with open(quiz_file_path, "w", encoding="utf-8") as quiz_file:
        json.dump(validated_quiz.model_dump(), quiz_file, ensure_ascii=False, indent=4)
        
    return {
        "message": "Quiz generated, auto-corrected, and saved successfully!",
        "saved_file": f"{clean_name}_quiz.json",
        "result": validated_quiz.model_dump()
    }