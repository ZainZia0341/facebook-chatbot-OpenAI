from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai
import os
from langchain.chains import ConversationChain
from langchain_community.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.retrievers import SelfQueryRetriever
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import httpx
from pinecone import exceptions as pinecone_exceptions, ServerlessSpec
import PyPDF2
from langchain_pinecone import PineconeVectorStore

# Load environment variables from .env file
load_dotenv()

# Set OpenAI and Pinecone API keys from environment variables
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')
pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')
page_access_token = os.getenv('PAGE_ACCESS_TOKEN')

# Initialize Pinecone
pinecone = PineconeVectorStore(api_key=os.getenv('PINECONE_API_KEY'))
index_name = pinecone_index_name

# Create the Pinecone index if it doesn't exist
try:
    if index_name not in [index.name for index in PineconeVectorStore.list_indexes()]:
        PineconeVectorStore.create_index(
            name=index_name,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
except pinecone_exceptions.PineconeApiException as e:
    if e.status != 409:
        raise

index = pinecone.Index(index_name)

# Set up embeddings and Pinecone vector store
embeddings = OpenAIEmbeddings()
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

# Function to read PDF and create documents
def read_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text())
    return texts

# Import PDF into vector store
pdf_texts = read_pdf('your_pdf_file.pdf')
docs = [{"content": text, "metadata": {}} for text in pdf_texts]
vectorstore.add_documents(docs)

# Define attribute info for self-query retriever
attribute_info = [
    {"name": "content", "description": "The content of the document", "type": "string"},
]

# Set up LangChain components
llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
memory = ConversationBufferMemory()
retriever = SelfQueryRetriever(
    llm=llm,
    vector_store=vectorstore,
    document_contents="Summary of the document",
    attribute_info=attribute_info,
    # structured_query_translator=Pinecone()
)

# Define the ConversationalChain with RAG
chain = ConversationChain(
    llm=llm,
    retriever=retriever,
    memory=memory
)

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

class WebhookEvent(BaseModel):
    object: str
    entry: list

@app.get('/webhook')
async def verify_token(hub_mode: str, hub_verify_token: str, hub_challenge: str):
    if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Invalid verification token")

@app.post('/webhook')
async def webhook_event(request: Request):
    data = await request.json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if 'message' in messaging_event:
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text')
                    if message_text:
                        response_text = await handle_message(message_text)
                        await send_message(sender_id, response_text)
    return JSONResponse(content={"status": "success"})

async def handle_message(message_text: str) -> str:
    response = chain.run(message_text)
    return response

async def send_message(recipient_id: str, text: str):
    url = 'https://graph.facebook.com/v11.0/me/messages'
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': text}
    }
    params = {
        'access_token': page_access_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
