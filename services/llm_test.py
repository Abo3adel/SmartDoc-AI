from openai import OpenAI

client = OpenAI(
    api_key="api_gAAAAABqjZYNWw9hwSBT7V_ZxIudBvmFELkKzn91rmPeTFJQv-RHDUUtK_Zdnnz38_O0kSgmQYyFL7Edq4rytVpJnvYfPwgQmZ5x4TSZVeLpTpB4NdSe8fsJbCFATaw5m5_JXPA4wp_8",     
    base_url="https://api-pilot-sandbox.aurai.solutions/v1"    
)

def chat_with_ai(user_message):
    print("waitt\n")

    response = client.chat.completions.create(
        model="Aurai-3.0",  
        messages=[
           {"role": "system", "content": "You are a helpful and smart assistant."},
                
            {"role": "user", "content": user_message}
        ]
    )
        
    ai_reply = response.choices[0].message.content
    return ai_reply

if __name__ == "__main__":
    my_question = "how are you?.. i want your help in some tasks, can you help me?"
    
    answer = chat_with_ai(my_question)

    print("let ai answer your question\n")
    print("-" * 30)
    print(answer)
    print("-" * 30)