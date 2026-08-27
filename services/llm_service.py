from openai import OpenAI
from schemas.models import LLMQuizOutput, LLMSummaryOutput
from pydantic import ValidationError
from core.config import OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api-pilot-sandbox.aurai.solutions/v1"
)
MODEL_NAME = "Aurai-3.0"


def summarize_text(document_text: str):    
    system_prompt = """
    You are an expert AI assistant. Your task is to analyze the provided text, 
    divide it into logical chapters based on topic transitions or natural breaks, 
    and provide a summary for each chapter and the summery should be in the same language as the original text.
    
    You MUST return the result EXACTLY as a valid JSON object in this format:
    {
        "chapters": [
            {
                "chapter_number": 1,
                "summary": "Summary of the first logical section..."
            },
            {
                "chapter_number": 2,
                "summary": "Summary of the second logical section..."
            }
        ]
    }
    Do not include any other text, markdown formatting, or explanations outside the JSON object.
    Return ONLY a valid JSON object. Do NOT wrap the response in markdown code blocks (like ```json). Do NOT add any conversational text before or after the JSON.
    """

    messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please divide and summarize the following text:\n\n{document_text}"}
            ]
    

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            summary_result = response.choices[0].message.content
            
            summary_result = summary_result.replace("```json", "").replace("```", "").strip()
            
            validated_summary = LLMSummaryOutput.model_validate_json(summary_result)
            
            print("Successfully validated summary data on attempt", attempt + 1)
            return validated_summary
            
        except ValidationError as e:
            print(f"Attempt {attempt + 1}: LLM Validation Error:", e)
            if attempt == 2:
                raise Exception("The AI failed to return the correct format after 3 attempts.")
                
            error_message = f"Your previous response was invalid JSON or did not match the schema. Here is the error:\n{e}\n\nPlease fix the JSON and return ONLY the valid JSON object."
            messages.append({"role": "user", "content": error_message})


        except Exception as e:
            return f"something was wrong :{e}"
    



def translate_document(document_text: str):
    
    system_prompt = """
    You are an expert professional translator. 
    Analyze the language of the provided text.
    - If the text is in Arabic, translate it completely into English.
    - If the text is in English, translate it completely into Arabic.
    
    Maintain the original formatting, paragraphs, and tone.
    ONLY return the translated text. Do not add any introductory words, explanations, or mention the detected language.
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please translate this text accordingly:\n\n{document_text}"}
            ]
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"something was wrong :{e}"
    


def generate_quiz(summary_data: str):
    system_prompt = """
    You are an expert educator. You will receive a JSON string containing chapters and their summaries.
    For each chapter, generate EXACTLY 3 open-ended questions based on its summary.
    and the questions should be in the same language as the text provided.
    The questions MUST be strictly categorized by difficulty:
    1. One 'Easy' question (basic factual recall).
    2. One 'Medium' question (comprehension and explanation).
    3. One 'Hard' question (analysis, synthesis, or critical thinking).
    
    You MUST return the result EXACTLY as a valid JSON object in this format:
    {
        "quiz": [
            {
                "chapter_number": 1,
                "questions": [
                    {
                        "difficulty": "Easy",
                        "question": "What is...?",
                        "ideal_answer": "Brief model answer here..."
                    },
                    {
                        "difficulty": "Medium",
                        "question": "How does...?",
                        "ideal_answer": "Brief model answer here..."
                    },
                    {
                        "difficulty": "Hard",
                        "question": "Why might...?",
                        "ideal_answer": "Brief model answer here..."
                    }
                ]
            }
        ]
    }
    Do not include any other text, markdown formatting, or explanations outside the JSON object.
    Return ONLY a valid JSON object. Do NOT wrap the response in markdown code blocks (like ```json). Do NOT add any conversational text before or after the JSON.
    """

    messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please generate a structured open-ended quiz for this summary:\n\n{summary_data}"}
            ]
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            quiz_result = response.choices[0].message.content
            
            quiz_result = quiz_result.replace("```json", "").replace("```", "").strip()
            
            validated_quiz = LLMQuizOutput.model_validate_json(quiz_result)
            
            print("Successfully validated quiz data on attempt", attempt + 1)
            return validated_quiz
            
        except ValidationError as e:
            print(f"Attempt {attempt + 1}: LLM Validation Error:", e)
            if attempt == 2:
                raise Exception("The AI failed to return the correct format after 3 attempts.")
                
            error_message = f"Your previous response was invalid JSON or did not match the schema. Here is the error:\n{e}\n\nPlease fix the JSON and return ONLY the valid JSON object."
            messages.append({"role": "user", "content": error_message})


        except Exception as e:
            return f"something was wrong :{e}"