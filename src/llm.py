import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.rate_limiters import InMemoryRateLimiter
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from matching import find_products_in_review
from prompt import system, system_tags
from utils import is_empty_or_nan
from preprocessing import clean_text


load_dotenv()
rpm = 15
rate_limiter = InMemoryRateLimiter(
    requests_per_second=rpm/60,
    check_every_n_seconds=1,
)
# LLM = ChatGoogleGenerativeAI(
#     api_key=os.getenv("GEMINI_KEY"),
#     model=os.getenv("GEMINI_MODEL"),
#     temperature=0,
#     verbose=True,
#     rate_limiter=rate_limiter
# )
LLM = AzureChatOpenAI(
    azure_endpoint = os.getenv("OPENAI_GPT_BASE"),
    azure_deployment = os.getenv("OPENAI_GPT_DEPLOYMENT_NAME"),
    api_key = os.getenv("OPENAI_GPT_KEY"),
    api_version = os.getenv("OPENAI_API_VERSION")
)

class Output(BaseModel):
    tagy: str = Field(..., description="Comma separated string of tags relevant to the review")
    nadpis: str = Field(..., description="Title summarizing the review")

async def agent(row):
    review = clean_text(row['zkusenost'])
    lng = row['lng']

    system_prompt = system if is_empty_or_nan(row['nadpis']) else system_tags

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            ('user', '**Review:**\n{review}')
        ]
    )
    structured_llm = LLM.with_structured_output(Output, method="function_calling")
    chain = prompt | structured_llm
    response = await chain.ainvoke({'lng': lng, 'review': review})

    response = dict(response)
    response['zkusenost'] = review
    return response

async def product_agent(data, df):
    data['prodID'] = find_products_in_review(data['zkusenost'], df)['ID'].astype(str).str.cat(sep=",")

    return data

    