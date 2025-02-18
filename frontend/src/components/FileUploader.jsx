import React, { useState } from 'react';
import axios from 'axios';
import { MenuItem, Select, InputLabel, FormControl, Button, Box } from '@mui/material';

const FileUploader = ({ onFileProcessed, models, handleModelChange, selectedModel }) => {
    const [selectedFiles, setSelectedFiles] = useState([]);


    const handleFileChange = (e) => {
        setSelectedFiles(Array.from(e.target.files)); // Convert FileList to Array
    };


    const handleUpload = async () => {
       if (!selectedFiles || selectedFiles.length === 0) {
            alert('No files selected!');
            return;
        }
        if (!selectedModel) {
            alert('No model selected!');
            return;
        }

        const formData = new FormData();
        selectedFiles.forEach((file) => formData.append('files', file)); // Append all files
        formData.append('model', selectedModel);

       try {
            const response = await axios.post('http://localhost:8000/process-files', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            alert('Files processed successfully!');
           // Call the callback for each processed file
           for(const filename of response.data.filenames) {
               onFileProcessed(filename)
           }


        } catch (error) {
            console.error('Error uploading files:', error);
            alert('Error uploading files.');
        }
    };

    return (
        <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
            <Box sx={{ flex: 1 }}>
                <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.pptx,.png,.jpg,.jpeg"
                    multiple  // Allow multiple file selection
                    style={{ marginBottom: 10, color: 'white'  }}
                />
            </Box>
            <FormControl variant="outlined" sx={{ minWidth: 200,  }}>
                <InputLabel id="model-select-label"  sx={{ color: 'white'  }}>Model</InputLabel>
                <Select
                    labelId="model-select-label"
                    id="model-select"
                    value={selectedModel}
                    onChange={handleModelChange}
                    label="Model"
                    sx={{ color: 'white',
                        '& .MuiOutlinedInput-notchedOutline': {
                            borderColor: '#555',
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                            borderColor: '#777',
                        },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                            borderColor: '#90caf9',
                        },
                      }}
                    >
                    {models.map((m) => (
                        <MenuItem key={m} value={m}  sx={{color: 'black' }}>
                            {m}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Button variant="contained" color="primary" onClick={handleUpload} >
                Upload & Process
            </Button>
        </Box>
    );
};

export default FileUploader;