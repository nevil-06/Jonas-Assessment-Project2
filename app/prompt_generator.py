# prompt_generator.py
import os
from openai import OpenAI

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv

load_dotenv()
# Replace 'your-api-key' with your actual OpenAI API key
client = OpenAI(api_key= key)


# def generate_sql_from_nl(nl_query, schema_prompt):
#     prompt = f"{schema_prompt}\n\nUser Question: {nl_query}\nSQL:"
#     response = client.chat.completions.create(model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": prompt}],
#     temperature=0.3,
#     max_tokens=150)
#     return response.choices[0].message.content.strip()


def generate_sql_from_nl(nl_query, schema_prompt):
    prompt = schema_prompt.replace("{{user_question}}", nl_query)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=200
    )
    
    return response.choices[0].message.content.strip()
