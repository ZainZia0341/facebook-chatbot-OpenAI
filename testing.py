from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai
import os
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.retrievers import SelfQueryRetriever
from langchain_openai import OpenAIEmbeddings
from langchain.chains.query_constructor.base import AttributeInfo
from dotenv import load_dotenv
import httpx
import PyPDF2
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

# Load environment variables from .env file
load_dotenv()

# Set OpenAI and Pinecone API keys from environment variables
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')
pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')
page_access_token = os.getenv('PAGE_ACCESS_TOKEN')

# Initialize Pinecone VectorStore
embeddings = OpenAIEmbeddings()
pinecone_store = PineconeVectorStore(embedding=embeddings, pinecone_api_key=os.getenv('PINECONE_API_KEY'), index_name=pinecone_index_name)

# Use existing Pinecone index
docsearch = pinecone_store.from_existing_index(index_name=pinecone_index_name, embedding=embeddings)

# Function to read PDF and create documents
def read_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text())
    return texts

# Import PDF into vector store
pdf_texts = read_pdf('data.pdf')
docs = [Document(page_content=text, metadata={}) for text in pdf_texts]
pinecone_store.add_documents(docs)

# Define attribute info for self-query retriever
attribute_info = [
    AttributeInfo(
        name="content",
        description="The content of the document",
        type="string",
    ),
]

# Set up LangChain components
llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
memory = ConversationBufferMemory()
retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=docsearch,
    document_contents="Details about me and my business",
    metadata_field_info=attribute_info,
    enable_limit=True,
    verbose=True,
)

# Define the ConversationalRetrievalQAChain with RAG
chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True,
    verbose=True
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
    url = 'https://graph.facebook.com/v20.0/me/messages'
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
