import React, { useState, useEffect } from 'react';
import { Button, TextField, Box, List, ListItem, ListItemText } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ChatInterface = ({ onSendMessage, messages }) => {
    const [inputValue, setInputValue] = useState('');
    const [displayMessages, setDisplayMessages] = useState([]); // to show the streamed responses

    // Use effect to make sure the messages are always kept up to date
    useEffect(() => {
        setDisplayMessages(messages);
    }, [messages]);

    const handleSend = () => {
        if (inputValue.trim() === '') return;
        onSendMessage(inputValue);
        setInputValue('');
    };

    return (
        <Box sx={{ mt: 2, border: '1px solid #373737', borderRadius: 2, p: 2, flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto'}}>
            <List sx={{ mb: 2, flex: 1 , overflowY: 'auto' }}>
                {displayMessages.map((msg, idx) => (
                    <ListItem key={idx} sx={{
                        display: 'flex',
                        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        textAlign: 'left',
                        padding: 0,
                        mb: 1,
                    }}>
                        <ListItemText
                            primary={
                                <ReactMarkdown
                                    children={msg.text}
                                    components={{
                                        code({ node, inline, className, children, ...props }) {
                                            const match = /language-(\w+)/.exec(className || '');
                                            return !inline && match ? (
                                                <SyntaxHighlighter
                                                    children={String(children).replace(/\n$/, '')}
                                                    style={materialDark}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    {...props}
                                                />
                                            ) : (
                                                <code className={className} {...props}>
                                                    {children}
                                                </code>
                                            );
                                        }
                                    }}
                                />
                            }
                            sx={{
                                padding: 1,
                                bgcolor: msg.role === 'user' ? '#373737' : '#212121', // Different backgrounds for user/bot
                                borderRadius: 2,
                                display: 'inline-block',
                            }}
                            primaryTypographyProps={{ variant: 'body2', style: { color: 'white' } }}
                        />
                    </ListItem>
                ))}
            </List>
            <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                    variant="outlined"
                    fullWidth
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask about your document..."
                    sx={{
                        '& .MuiOutlinedInput-root': {
                            '& fieldset': {
                                borderColor: '#555',
                            },
                            '&:hover fieldset': {
                                borderColor: '#777',
                            },
                            '&.Mui-focused fieldset': {
                                borderColor: '#90caf9',
                            },
                        },
                    }}
                />
                <Button variant="contained" color="primary" onClick={handleSend}>
                    Send
                </Button>
            </Box>
        </Box>
    );
};

export default ChatInterface;