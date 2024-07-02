# import json
# from dotenv import load_dotenv
# import requests
# from langchain_pinecone import PineconeVectorStore
# from langchain.memory import ConversationBufferWindowMemory
# from langchain.chains import ConversationalRetrievalChain
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from dotenv import load_dotenv
# import os


# # Load environment variables from .env file
# load_dotenv()

# VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
# PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

# def verify_token(event, context):
#     params = event.get('queryStringParameters', {})
#     hub_mode = params.get('hub.mode')
#     hub_verify_token = params.get('hub.verify_token')
#     hub_challenge = params.get('hub.challenge')

#     if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
#         return {
#             'statusCode': 200,
#             'body': hub_challenge
#         }
#     return {
#         'statusCode': 403,
#         'body': 'Invalid verification token'
#     }

# def webhook_event(event, context):
#     body = json.loads(event['body'])
#     if 'object' in body and body['object'] == 'page':
#         entries = body['entry']
#         for entry in entries:
#             webhook_event = entry['messaging'][0]
#             sender_psid = webhook_event['sender']['id']
#             if 'message' in webhook_event:
#                 handle_message(sender_psid, webhook_event['message'])
#         return {
#             'statusCode': 200,
#             'body': json.dumps({"status": "EVENT_RECEIVED"})
#         }
#     else:
#         return {
#             'statusCode': 404,
#             'body': json.dumps({"status": "ERROR"})
#         }


# import openai
# def handle_message(sender_psid, received_message):

#     # Set your OpenAI API key here
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     index_name = os.getenv("PINECONE_INDEX_NAME")

#     llm = ChatOpenAI(
#         model_name="gpt-4o",  # Correct model name for chat
#         openai_api_key=openai_api_key,
#         max_tokens=512,
#         temperature=0,
#         top_p=1,
#     )

#     memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True)
#     embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
#     pinecone_store = PineconeVectorStore(embedding=embeddings, pinecone_api_key=os.getenv('PINECONE_API_KEY'), index_name=index_name)
#     docsearch = pinecone_store.from_existing_index(index_name=index_name, embedding=embeddings)

#     conversation_with_retrieval = ConversationalRetrievalChain.from_llm(
#         llm, 
#         retriever=docsearch.as_retriever(), 
#         memory=memory, 
#         verbose=True
#     )
#     chat_response = conversation_with_retrieval({"question": received_message})
    

#     call_send_api(sender_psid, chat_response["answer"])

# def call_send_api(sender_psid, response):
#     url = f'https://graph.facebook.com/v20.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
#     payload = {
#         'recipient': {'id': sender_psid},
#         'message': response,
#         'messaging_type': 'RESPONSE'
#     }
#     headers = {'Content-Type': 'application/json'}
#     response = requests.post(url, json=payload, headers=headers)
#     print(response.text)

#     return {
#         'statusCode': 200,
#         'body': json.dumps('Message sent!')
#     }



# import json
# import os
# import requests
# from dotenv import load_dotenv
# from langchain_pinecone import PineconeVectorStore
# from langchain.memory import ConversationBufferWindowMemory
# from langchain.chains import ConversationalRetrievalChain
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# load_dotenv()

# VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
# PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# # def verify_token(event, context):
# #     try:
# #         print("Event ", event)
# #         return print("Hello")
# #     except Exception as e:
# #         return print("Error")


# def verify_token(event, context):
#     try:
#         print("Event ", event)
#         params = event.get('queryStringParameters', {})
#         hub_mode = params.get('hub.mode')
#         hub_verify_token = params.get('hub.verify_token')
#         hub_challenge = params.get('hub.challenge')

#         if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
#             webhook_event(event, context)
#             return {
#                 'statusCode': 200,
#                 'body': hub_challenge
#             }
#         return {
#             'statusCode': 403,
#             'body': 'Invalid verification token'
#         }
#     except Exception as e:
#         print(f"Error in verify_token: {e}")
#         return {
#             'statusCode': 500,
#             'body': 'Internal Server Error'
#         }

# def webhook_event(event, context):
#     # print("event ", event)
#     # return {
#     #      'statusCode': 200,
#     #         'body': json.dumps({"status": "OK POST request recieved"})
#     # }
#     try:
#         print("checking ", event['body'])
#         body = json.loads(event['body'])
#         if 'object' in body and body['object'] == 'page':
#             entries = body['entry']
#             for entry in entries:
#                 webhook_event = entry['messaging'][0]
#                 sender_psid = webhook_event['sender']['id']
#                 if 'message' in webhook_event:
#                     handle_message(sender_psid, webhook_event['message'])
#             return {
#                 'statusCode': 200,
#                 'body': json.dumps({"status": "EVENT_RECEIVED"})
#             }
#         else:
#             return {
#                 'statusCode': 404,
#                 'body': json.dumps({"status": "ERROR"})
#             }
#     except Exception as e:
#         print(f"Error in webhook_event: {e}")
#         return {
#             'statusCode': 500,
#             'body': 'Internal Server Error'
#         }

# def handle_message(sender_psid, received_message):
#     print("checking post requuest ")
#     try:
#         print("checking received_message", received_message)
#         llm = ChatOpenAI(
#             model_name="gpt-4o",  # Ensure correct model name
#             openai_api_key=OPENAI_API_KEY,
#             max_tokens=512,
#             temperature=0,
#             top_p=1,
#         )

#         memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True)
#         embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
#         pinecone_store = PineconeVectorStore(embedding=embeddings, pinecone_api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME)
#         docsearch = pinecone_store.from_existing_index(index_name=PINECONE_INDEX_NAME, embedding=embeddings)

#         conversation_with_retrieval = ConversationalRetrievalChain.from_llm(
#             llm, 
#             retriever=docsearch.as_retriever(), 
#             memory=memory, 
#             verbose=True
#         )

#         chat_response = conversation_with_retrieval({"question": received_message})

#         call_send_api(sender_psid, chat_response["answer"])
#     except Exception as e:
#         print(f"Error in handle_message: {e}")
#         call_send_api(sender_psid, "Sorry, there was an error processing your message.")

# def call_send_api(sender_psid, response):
#     try:
#         print("checking response sender_psid ", response, sender_psid)
#         url = f'https://graph.facebook.com/v20.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
#         payload = {
#             'recipient': {'id': sender_psid},
#             'message': {'text': response},
#             'messaging_type': 'RESPONSE'
#         }
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(url, json=payload, headers=headers)
#         print(response.text)
#         return {
#             'statusCode': 200,
#             'body': json.dumps('Message sent!')
#         }
#     except Exception as e:
#         print(f"Error in call_send_api: {e}")
#         return {
#             'statusCode': 500,
#             'body': 'Internal Server Error'
#         }




import json
import os
import requests
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

def webhook_handler(event, context):
    http_method = event.get('httpMethod')
    if http_method == 'GET':
        return verify_token(event)
    elif http_method == 'POST':
        return webhook_event(event)
    else:
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }

def verify_token(event):
    try:
        print("Event ", event)
        params = event.get('queryStringParameters', {})
        hub_mode = params.get('hub.mode')
        hub_verify_token = params.get('hub.verify_token')
        hub_challenge = params.get('hub.challenge')

        if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
            return {
                'statusCode': 200,
                'body': hub_challenge
            }
        return {
            'statusCode': 403,
            'body': 'Invalid verification token'
        }
    except Exception as e:
        print(f"Error in verify_token: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }

def webhook_event(event):
    try:
        print("Received event: ", event)
        if event['body']:
            body = json.loads(event['body'])
            print("Parsed body: ", body)
            
            if 'object' in body and body['object'] == 'page':
                entries = body['entry']
                for entry in entries:
                    webhook_event = entry['messaging'][0]
                    sender_psid = webhook_event['sender']['id']
                    if 'message' in webhook_event:
                        handle_message(sender_psid, webhook_event['message'])
                return {
                    'statusCode': 200,
                    'body': json.dumps({"status": "EVENT_RECEIVED"})
                }
            else:
                print("Error: Invalid object in body")
                return {
                    'statusCode': 404,
                    'body': json.dumps({"status": "ERROR"})
                }
        else:
            print("Error: No body in event")
            return {
                'statusCode': 400,
                'body': json.dumps({"status": "ERROR: No body in request"})
            }
    except Exception as e:
        print(f"Error in webhook_event: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }

def handle_message(sender_psid, received_message):
    try:
        print("Received message: ", received_message)
        llm = ChatOpenAI(
            model_name="gpt-4o",  # Ensure correct model name
            openai_api_key=OPENAI_API_KEY,
            max_tokens=512,
            temperature=0
        )

        memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True)
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        pinecone_store = PineconeVectorStore(embedding=embeddings, pinecone_api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME)
        docsearch = pinecone_store.from_existing_index(index_name=PINECONE_INDEX_NAME, embedding=embeddings)

        conversation_with_retrieval = ConversationalRetrievalChain.from_llm(
            llm, 
            retriever=docsearch.as_retriever(), 
            memory=memory, 
            verbose=True
        )

        chat_response = conversation_with_retrieval({"question": received_message["text"]})

        call_send_api(sender_psid, chat_response["answer"])
    except Exception as e:
        print(f"Error in handle_message: {e}")
        call_send_api(sender_psid, "Sorry, there was an error processing your message.")

def call_send_api(sender_psid, response):
    try:
        print("Sending response to sender_psid: ", response, sender_psid)
        url = f'https://graph.facebook.com/v20.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
        payload = {
            'recipient': {'id': sender_psid},
            'message': {'text': response},
            'messaging_type': 'RESPONSE'
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent!')
        }
    except Exception as e:
        print(f"Error in call_send_api: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }
