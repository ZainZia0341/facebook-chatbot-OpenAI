from fastapi import FastAPI, Request, HTTPException, Query
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
llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), model="gpt-4o")
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
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

@app.get('/webhook')
async def verify_token(
    hub_mode: str = Query(..., alias='hub.mode'),
    hub_verify_token: str = Query(..., alias='hub.verify_token'),
    hub_challenge: str = Query(..., alias='hub.challenge')
):
    if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Invalid verification token")

@app.post('/webhook')
async def webhook_event(request: Request):
    data = await request.json()
    if 'object' in data and data['object'] == 'page':
        entries = data['entry']
        for entry in entries:
            webhook_event = entry['messaging'][0]
            sender_psid = webhook_event['sender']['id']
            if 'message' in webhook_event:
                await handle_message(sender_psid, webhook_event['message'])
        return JSONResponse(content={"status": "EVENT_RECEIVED"}, status_code=200)
    else:
        return JSONResponse(content={"status": "ERROR"}, status_code=404)

async def handle_message(sender_psid, received_message):
    if 'text' in received_message:
        response = {"text": f"You just sent: {received_message['text']}"}
    else:
        response = {"text": "This chatbot only accepts text messages"}

    await call_send_api(sender_psid, response)

async def call_send_api(sender_psid, response):
    url = f'https://graph.facebook.com/v20.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
    payload = {
        'recipient': {'id': sender_psid},
        'message': response,
        'messaging_type': 'RESPONSE'
    }
    headers = {'Content-Type': 'application/json'}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        print(r.text)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
