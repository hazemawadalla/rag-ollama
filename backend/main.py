import os
import uvicorn
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from chromadb.config import Settings
from file_processor import extract_text_from_file
from typing import List
from pydantic import BaseModel, Field
import json
from google_search import google_search  # Import the web search tool
import markdown
#from dotenv import load_dotenv
import warnings
import urllib3

# Load environment variables from .env file
#load_dotenv()
#warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)  # Suppress InsecureRequestWarning

app = FastAPI()

# Allow CORS for cross-origin requests, this is needed for the frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 1. Initialize global Chromadb client and collection (persistent)
# -------------------------------------------------------------------
CHROMA_DB_PATH = "chroma_db"  # Path to the Chroma DB
client = chromadb.PersistentClient(path=CHROMA_DB_PATH, settings=Settings())
collection = client.get_or_create_collection(name="docs")


filename_to_model = {}

# -------------------------------------------------------------------
# 2. Ollama API Configuration
# -------------------------------------------------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#OLLAMA_USERNAME = os.getenv("OLLAMA_USERNAME")
#OLLAMA_PASSWORD = os.getenv("OLLAMA_PASSWORD")


@app.get("/list-models")
async def list_models():
    """
    Endpoint to fetch models from remote ollama API.
    """
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        print(f"Fetching models from: {url}")
        response = requests.get(url, verify=False, timeout=180)
        response.raise_for_status()  
        print(f"Ollama API response status code: {response.status_code}")
        data = response.json()
        print(f"Ollama API response data: {data}") # Comment out after debugging
        models = [model["name"] for model in data["models"]]
        return {"models": models}
    except requests.exceptions.RequestException as e:
        print(f"Request Exception listing Ollama models: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing Ollama models: {e}")
    except Exception as e:
        print(f"General Exception listing Ollama models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------
# Utility: a naive text splitter to chunk the doc text
# -----------------------------------------------------------
def chunk_text(text, chunk_size=500, overlap=50):
    """
    Splits 'text' into overlapping chunks of length 'chunk_size'.
    Overlap is optional.
    Returns a list of text chunks.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        start += (chunk_size - overlap)  # move by chunk_size - overlap

    return chunks

# -----------------------------------------------------------
# 3. File Upload -> Extract -> Embed -> Store
# -----------------------------------------------------------
@app.post("/process-files")
async def process_files(
    files: List[UploadFile] = File(...),
    model: str = Form(...),  
):
    """
    - Extract text from the file
    - Chunk it
    - Generate embeddings for each chunk using Ollama's embed model
    - Store them in the Chromadb collection
    - Also store the generation model for later
    """
    print(f"process_files called with files: {[file.filename for file in files]} and model: {model}") # ADDED
    filenames = []
    try:
      for file in files:
       
        embedding_model = "mxbai-embed-large"  # any embed model you've pulled with ollama

        # 1. Extract text
        print(f"Extracting text from {file.filename}") # ADDED
        doc_text = extract_text_from_file(file)
        if not doc_text:
            raise HTTPException(status_code=400, detail="No text extracted from file.")

        # 2. Chunk text to smaller pieces for better retrieval
        chunks = chunk_text(doc_text, chunk_size=200, overlap=20)
        print(f"Created {len(chunks)} chunks") # ADDED

        # 3. For each chunk, get embeddings from Ollama
        #    We'll remove old embeddings for this filename first, in case user re-uploads
        #    We store each chunk with an ID like "<filename>_<index>"
        # -------------------------------------------------------------------------
        # Remove any existing vectors for this file
        existing_ids = [f"{file.filename}_{i}" for i in range(len(chunks))]
        print(f"Existing ids to delete: {existing_ids}") # ADDED
        try:
            if existing_ids:
                collection.delete(ids=existing_ids)
                print(f"Deleted existing ids") # ADDED
        except Exception as e:
            print(f"Error deleting ids: {e}") #ADDED
            pass

        # 4. Add new embeddings to the collection
        for i, chunk in enumerate(chunks):
            url = f"{OLLAMA_BASE_URL}/api/embeddings"
            payload = {"model": embedding_model, "prompt": chunk}
            response = requests.post(url, json=payload, verify=False, timeout=1800)
            response.raise_for_status()
            emb_response = response.json()
            embedding = emb_response["embedding"]
            doc_id = f"{file.filename}_{i}"

            # Insert into collection
            collection.add(
                embeddings=[embedding],
                documents=[chunk],
                ids=[doc_id],
                metadatas=[{"filename": file.filename}]
            )

        # 5. Save the user-chosen generation model
        filename_to_model[file.filename] = model
        print(f"filename_to_model: {filename_to_model}") #ADDED
        filenames.append(file.filename)


      return {"message": "Files processed successfully.", "filenames": filenames}

    except requests.exceptions.RequestException as e:
        print(f"Error in process_files: {e}") # ADDED
        raise HTTPException(status_code=500, detail=f"Error processing files: {e}")
    except Exception as e:
        print(f"Error in process_files: {e}") # ADDED
        raise HTTPException(status_code=500, detail=str(e))

class ChatResponse(BaseModel):
    response: str = Field(..., description="The response to the user's query")

# -----------------------------------------------------------
# 4. Generate a response using retrieved text from Chromadb
# -----------------------------------------------------------
def get_ollama_response(prompt, api_url="http://localhost:11434/api/generate", model="deepseek-r1:70b"):
    """
    Sends a prompt to the Ollama API and returns the response.
    """
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "model": model,
            "stream": False
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False, timeout=1800)
        response.raise_for_status()
        try:
            json_response = response.json()
            return json_response["response"]
        except json.JSONDecodeError:
            return f"Error: Could not decode JSON response: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the Ollama API: {e}"


#-------------------------------------------------------------------------------
#Generate a response using retrieved text from Chromadb (with web search enabled)
#-------------------------------------------------------------------------------

@app.post("/generate-response")
async def generate_response(
    prompt: str = Form(...),
    filename: str = Form(...),
    web_search_enabled: bool = Form(False),  #websearch is disabled by default
    message_history: str = Form("[]"), 
    file_uploaded: bool = Form(False), # check if a file was uploaded
    model: str = Form("llama2") #  receive the model from the form data
):
    """
    - Embed the user's prompt
    - Retrieve top-k relevant chunks from Chromadb
    - Pass them as context to the chosen generation model
    - Return the LLM's response
    """
    print(f"generate_response called with prompt: '{prompt}', filename: '{filename}', web_search_enabled: {web_search_enabled}, file_uploaded: {file_uploaded}, model: {model}")  # ADDED
    try:
        generation_model = model # Use the model provided by the frontend

        if filename and filename in filename_to_model:
            generation_model = filename_to_model[filename] # override default if filename exists

        embedding_model = "mxbai-embed-large"

        # 1. Embed user prompt
        url = f"{OLLAMA_BASE_URL}/api/embeddings"
        payload = {"model": embedding_model, "prompt": prompt}
        print(f"Requesting embeddings from ollama with payload: {payload}")  # ADDED
        response = requests.post(url, json=payload, verify=False, timeout=300)
        response.raise_for_status()
        prompt_embedding = response.json()
        query_emb = prompt_embedding["embedding"]
        print(f"Received prompt embedding successfully")  # ADDED

        # 2. Perform web search if necessary. Only if web_search_enabled is True
        web_search_results = ""
        if web_search_enabled: # CHECK IF WEBSEARCH IS ENABLED
            web_search_query = prompt.strip()
            print(f"Performing web search with query: {web_search_query}") # ADDED
            try:
               search_results = google_search(web_search_query, num_results=10) # Select the top 10 results
               web_search_results = "\n\n".join([f"Source: {res['link']}\n{res['snippet']}" for res in search_results]) # Format search results with links
               print(f"Web search results: {web_search_results}") #ADDED
            except Exception as e:
                print(f"Error during web search: {e}")
                web_search_results = f"Error during web search: {e}"

        # 3. Query Chromadb for top 2 chunks
        context_text = "" # if there are no uploaded files, then the context_text should be empty
        if file_uploaded and filename: # Only query chromadb if file was uploaded, and there is a filename
           print(f"Querying chromadb for top 2 chunks with filename: {filename}")  # ADDED
           results = collection.query(
               query_embeddings=[query_emb],
                where={"filename": filename}, # ADDED A WHERE CLAUSE TO THE QUERY
               n_results=2
           )
           print(f"ChromaDB Query Results: {results}")  # ADDED

           # results['documents'] is a list of lists
           # e.g. [['chunk1 text', 'chunk2 text']]
           if "documents" not in results or not results["documents"]:
               # fallback if no results
               context_text = "No relevant chunks found."
           else:
               top_docs = results["documents"][0]  # the top matched docs for this single query
               context_text = "\n".join(top_docs)

        # Concatenate the context from chromadb, and the web search results
        final_context = f"Document context:\n{context_text}\n\nWeb search results:\n{web_search_results}\n\n"

        # 4. Construct final prompt for generation, and include the message history
        try:
            history = json.loads(message_history)
            history_text = "\n".join([f"**{msg['role'].upper()}:** {msg['text']}" for msg in history]) # Format history
        except Exception as e:
            print(f"Error parsing message history: {e}")
            history_text = "Error parsing message history"

        final_prompt = (
                f"You are a helpful AI assistant. Use the context provided to answer the user's question. "
                f"Please provide a detailed and verbose response, explaining your reasoning step by step. If you are referencing multiple concepts in a list, please only provide the top 5.\n\n"
                f"Make sure to format the response with paragraphs (using double newlines), and use code blocks (using triple backticks) when appropriate. **Make sure to include citations and source links at the end of the response, after all other text**. "
                f"Specifically, if any of the web search results were used, please cite the source links in the response. If the question is to find the current date, you MUST use web search to answer it. You must also take into account the following conversation history to answer the user's question:\n{history_text}\n\n"
                f"Here is the context for the current question:\n{final_context}\n\n"
                f"You are using the {generation_model} model. When you answer the question, make sure to be very detailed, verbose and comprehensive.\n\n"
                f"You must answer in a human-like scientific writing style, all the answers must be undetectable by online AI checkers. \n\n"
                f"Question: {prompt}\nAnswer:\n"  # Add a newline character after "Answer:"
            )

        # 5. Generate response using get_ollama_response
        print(f"Requesting Ollama chat with Pydantic schema")  # ADDED
        response = get_ollama_response(final_prompt, api_url=f"{OLLAMA_BASE_URL}/api/generate", model=generation_model)
        print(f"Ollama response: {response}")  # ADDED
        return {"response": response}

    except requests.exceptions.RequestException as e:
        print(f"Error in generate_response: {e}")  # ADDED
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")
    except Exception as e:
        print(f"Error in generate_response: {e}")  # ADDED
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 5. Clear context, This endpoint is used to clear the context of the conversation. It deletes all embeddings from the Chromadb collection and clears the filename_to_model mapping.
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.post("/clear-context")
async def clear_context():
    """
    - Clear the filename_to_model mapping
    - Delete all embeddings from the Chromadb collection
    """
    print(f"clear_context called")
    try:
        # 1. Clear the filename_to_model mapping
        filename_to_model.clear()

        # 2. Delete all embeddings from the Chromadb collection
        collection.delete(where={"filename": {"$ne": "null"}})
        print(f"Cleared filename_to_model and all chromadb entries")
        return {"message": "Context cleared successfully."}
    except Exception as e:
        print(f"Error clearing context: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing context: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)