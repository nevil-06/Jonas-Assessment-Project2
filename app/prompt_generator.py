# prompt_generator.py
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

# Replace 'your-api-key' with your actual OpenAI API key
key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key= key)

def generate_sql_from_nl(nl_query, schema_prompt):
    prompt = schema_prompt.replace("{{user_question}}", nl_query)
    
    response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal:text2sql-v1:BIi3eV8B",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=200
    )
    
    return response.choices[0].message.content.strip()
