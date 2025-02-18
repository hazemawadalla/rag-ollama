import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, CssBaseline, Box, createTheme, ThemeProvider, FormControlLabel, Switch, Button, CircularProgress } from '@mui/material';
import FileUploader from './components/FileUploader';
import ChatInterface from './components/ChatInterface';

const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#90caf9', // A light blue for primary actions
        },
        background: {
            default: '#121212',
             paper: '#1e1e1e', // Slightly lighter for containers
        },
        text: {
            primary: '#ffffff',
            secondary: '#bdbdbd', // A soft gray for less important text
        },
    },
    typography: {
        fontFamily: 'Roboto, sans-serif',
    }
});


function App() {
    const [filename, setFilename] = useState(null);
    const [messages, setMessages] = useState([]);
    const [models, setModels] = useState([]);
    const [webSearchEnabled, setWebSearchEnabled] = useState(false); // New state for web search toggle
    const [fileUploaded, setFileUploaded] = useState(false); // New state for if a file is uploaded
    const [selectedModel, setSelectedModel] = useState("llama2"); // New state for selected model
    const [loading, setLoading] = useState(false); // Loading state

    useEffect(() => {
        const fetchModels = async () => {
            try {
                const response = await axios.get('http://localhost:8000/list-models');
                setModels(response.data.models || []);
            } catch (error) {
                console.error('Error fetching models:', error);
                setModels([]);
            }
        };
        fetchModels();
    }, []);

     const handleWebSearchToggleChange = (event) => {
        setWebSearchEnabled(event.target.checked);
    };

    const handleModelChange = (e) => {
        setSelectedModel(e.target.value);
    };

    const handleFileProcessed = (uploadedFilename) => {
        setFilename(uploadedFilename);
        setFileUploaded(true) // Set the file uploaded state
    };


      const handleClearContext = async () => {
      try{
          await axios.post('http://localhost:8000/clear-context');
          setMessages([]);
          setFilename(null);
           setFileUploaded(false) // set file uploaded state to false

      }
      catch(err){
           console.error('Error clearing context:', err);
           alert('Error clearing context');

      }
    };



    const handleSendMessage = async (message) => {
        setMessages((prev) => [...prev, { role: 'user', text: message }]);
         setLoading(true); // set loading to true
         try {
            const formData = new FormData();
            formData.append('prompt', message);
             formData.append('filename', filename);
            formData.append('web_search_enabled', webSearchEnabled); // Send toggle state to backend
            formData.append('message_history', JSON.stringify(messages));  // Send history
             formData.append('file_uploaded', fileUploaded);
             formData.append('model', selectedModel); // Send model to backend


             const response = await axios.post('http://localhost:8000/generate-response', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
             });


            const botReply = response.data.response;
            setMessages((prev) => [...prev, { role: 'bot', text: botReply }]);
         }
         catch (err) {
              console.error('Error generating response:', err);
              setMessages((prev) => [...prev, { role: 'bot', text: `Error: ${err.message}` }]);
        }
        finally{
           setLoading(false) // set loading to false when the request finishes
        }


    };


    return (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
                <Container maxWidth="xl" sx={{ mt: 4, display: 'flex', flexDirection: 'column', height: '90vh' }}>
                    <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, p: 3, boxShadow: 3, flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'hidden' }}>
                         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb:2}}>
                            <Typography variant="h4"  sx={{ color: 'text.primary' }}>
                                RAG OLLAMA: Advanced RAG with Ollama + Chromadb
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Typography variant="body2" sx={{ color: 'text.secondary', mr: 2 }}>
                                    Hazem Awadallah v1.0 {'<'}February, 17, 2025{'>'}
                                </Typography>
                                <Button variant="contained" color="secondary" onClick={handleClearContext}>
                                    Clear Context
                                </Button>
                            </Box>
                         </Box>

                        <Typography variant="body1" gutterBottom sx={{ color: 'text.secondary', mb: 2 }}>
                            1) Upload a doc (PDF/PPTX/Image). 2) Pick a generation model. 3) Chat with context from vector embeddings.
                        </Typography>


                         <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                              <FormControlLabel
                                control={<Switch checked={webSearchEnabled} onChange={handleWebSearchToggleChange} />}
                                label="Enable Web Search"
                                sx={{ color: 'text.secondary' }}
                             />
                        </Box>
                        <FileUploader onFileProcessed={handleFileProcessed} models={models} handleModelChange={handleModelChange} selectedModel={selectedModel}/>
                       <Box sx={{flex: 1,  display: 'flex', flexDirection: 'column',  overflowY: 'hidden', }}>
                         <ChatInterface onSendMessage={handleSendMessage} messages={messages} />
                          {loading && (
                            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                              <CircularProgress />
                            </Box>
                          )}
                        </Box>
                  </Box>
            </Container>
        </ThemeProvider>
    );
}

export default App;