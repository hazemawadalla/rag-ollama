**A Full Stack, Local Retrieval Augmented Generation Pipeline**

##### Author: Hazem Awadallah <hazem.awadalla@gmail.com>, Independent


**Abstract**

The RAG Ollama Project presents a novel retrieval-augmented generation (RAG) pipeline to create an efficient and powerful framework for accurate response generation using  smaller, computationally efficient ollama models. The pipeline integrates FastAPI, Ollama, Chromadb, and React to provide an end-to-end user experience. 

**Introduction**

Retrieval-augmented generation (RAG) is a method in natural language processing that allows for generating more accurate and informative answers from pretrained models by leveraging external knowledge sTheces. The RAG Ollama Project, has set its mission to improve the usability of small local ollama models  by creating an end-to-end pipeline with an indexed chromadb database. 

**System Architecture**
 
The RAG-ollama pipeline consists of the following components:

1. **Backend**: Built using FastAPI, The  backend handles API requests, processes files, and interacts with a vector database.
2. **Ollama**: The system utilizes Ollama for embeddings and model generation, enabling the creation of high-quality responses.
3. **Chromadb**: The system uses Chromadb as a vector database to efficiently store and retrieve documents.
4. **Frontend**: The React-based frontend provides an intuitive interface for users to interact with the system.

**Unique Features**

1. **Google Search Integration**: The pipeline incorporates Google Custom Search API to fetch relevant Ib search results, enhancing the quality of The responses.
2. **File Processing**: I support processing of various file types using libraries like PyPDF2, python-pptx, opencv-python, and pytesseract.
3. **Modular Design**: The system is designed with modularity in mind, allowing for easy extension and customization.

**Technical Details**
###### Backend

requirements.txt

- `fastapi and uvicorn: For building and running the FastAPI server.`
- `python-multipart: For handling form data.`
- `ollama: For embeddings and model generation.`
- `PyPDF2, python-pptx, opencv-python, pytesseract: For processing different file types.`
- `chromadb: As a vector database for storing and retrieving documents.`
- `python-dotenv: For loading environment variables from a .env file.`
- `markdown: For handling markdown content.`
- `google-api-python-client: For interacting with the Google Custom Search API.`

The backend is built using FastAPI and consists of the following components:

 `main.py`
- **Purpose**: Acts as the entry point for the FastAPI application. It defines the API routes and handles incoming HTTP requests.
- **Functionality**:
  - Defines endpoints for different operations (e.g., file uploads, chat interactions).
  - Routes requests to the appropriate handler functions in other modules like `file_processor.py` and `google_search.py`.
  - Manages request parameters and responses.

 `file_processor.py`
- **Purpose**: Handles the processing of uploaded files.
- **Functionality**:
  - Receives file data from API requests.
  - Parses and extracts relevant information from the files (e.g., text, metadata).
  - Converts extracted data into a format suitable for further processing or storage in Chromadb.
  - Interacts with Chromadb to store processed data as embeddings.

`google_search.py`
- **Purpose**: Performs Google searches using the Custom Search API.
- **Functionality**:
  - Accepts search queries and the number of results desired.
  - Utilizes the Google Custom Search JSON API to fetch search results.
  - Formats the search results into a list of dictionaries containing titles, links, and snippets.
  - Handles errors during the search process and returns appropriate error messages.


###### Frontend

The frontend is built using React and provides an intuitive interface for users to interact with the system. 

###### `App.jsx`
The main component of the React application. It manages the overall state, renders other components like `FileUploader.jsx` and `ChatInterface.jsx`, and handles API interactions with the backend.

###### `FileUploader.jsx`
A component that allows users to upload files (e.g., PDFs, PowerPoint slides, images). It provides a file selection interface, validates file types and sizes, sends uploaded files to the backend using `axios`, and displays feedback to the user about the upload status.

###### `ChatInterface.jsx`
A component for displaying and managing chat interactions with the RAG pipeline. It renders a list of chat messages, handles user input, sends user messages to the backend using `axios`, and updates the chat interface in real-time as new messages are sent and received.


**Setup and Usage**

To get started with the RAG Ollama Project, follow these steps:

Prerequisites: 
i. Install ollama, ollama models (eg llama3:latest), ollama embedding model (default is mxbai-embed-large) & node.js
ii. Create a .env environment with your GOOGLE_API_KEY & GOOGLE_CSE_ID with access to the Google Custom Search API.

1. Clone the repository: [`git clone https://github.com/hazemawadalla/rag-ollama.git`]
2. Navigate to the backend directory: `cd backend`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the FastAPI server: `uvicorn main:app --reload`
5. Navigate to the frontend directory: `cd ../frontend`
6. Install packages: `npm install`
7. Start the React dev server: `npm start`

**Conclusion**
  
The RAG Ollama Project presents a novel retrieval-augmented generation pipeline that leverages cutting-edge technologies to create a robust and efficient system for generating human-like responses. The pipeline is designed with modularity in mind, allowing for easy extension and customization. I believe that The project has the potential to make a significant impact in the field of natural language processing and look forward to continuing its development.

**Future Work**

I plan to continue improving and expanding the RAG Ollama Project by:

- Integrating additional file processing libraries
- Integrating code analysis feature
- Implementing deep search with Deepseek-R1 ollama models and Google search integration

I invite researchers, developers, and industry professionals to join us in this effort and contribute to the advancement of retrieval-augmented generation technology.


<video src="[URL_TO_YOUR_VIDEO](https://github.com/user-attachments/assets/2e21ccda-a710-49bd-a432-1ecdc67fa334)" controls="controls" style="max-width: 100%;"></video>


https://github.com/user-attachments/assets/2e21ccda-a710-49bd-a432-1ecdc67fa334




###### GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Copyright (C) 2025 [Hazem Awadallah]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

[Hazem Awadallah]
[hazem.awadalla@gmail.com]
