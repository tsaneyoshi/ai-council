import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import Stage1 from './Stage1';
import Stage2 from './Stage2';
import Stage3 from './Stage3';
import './ChatInterface.css';



export default function ChatInterface({
  conversation,
  onSendMessage,
  isLoading,
}) {
  const [input, setInput] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleFileSelect = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      setIsUploading(true);

      try {
        const uploadedFiles = await Promise.all(files.map(async (file) => {
          const formData = new FormData();
          formData.append('file', file);

          const response = await fetch('http://localhost:8001/api/upload', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
          }

          return await response.json();
        }));

        setSelectedFiles(prev => [...prev, ...uploadedFiles]);
      } catch (error) {
        console.error('File upload error:', error);
        alert('Failed to upload file');
      } finally {
        setIsUploading(false);
        // Reset input so same file can be selected again if needed
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    }
  };

  const removeFile = (fileId) => {
    setSelectedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if ((input.trim() || selectedFiles.length > 0) && !isLoading && !isUploading) {
      onSendMessage(input, selectedFiles);
      setInput('');
      setSelectedFiles([]);
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift) and ensure not in IME composition
    if (e.key === 'Enter' && !e.shiftKey && !isComposing && !e.nativeEvent.isComposing) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  if (!conversation) {
    return (
      <div className="chat-interface">
        <div className="empty-state">
          <h2>Welcome to LLM Council</h2>
          <p>Create a new conversation to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {conversation.messages.length === 0 ? (
          <div className="empty-state">
            <h2>Start a conversation</h2>
            <p>Ask a question to consult the LLM Council</p>
          </div>
        ) : (
          conversation.messages.map((msg, index) => (
            <div key={index} className="message-group">
              {msg.role === 'user' ? (
                <div className="user-message">
                  <div className="message-label">You</div>
                  <div className="message-content">
                    <div className="markdown-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                    {msg.files && msg.files.length > 0 && (
                      <div className="message-files">
                        {msg.files.map((file, i) => (
                          <a
                            key={i}
                            href={`http://localhost:8001/api/files/${file.id}/download`}
                            className="file-attachment-link"
                            target="_blank"
                            rel="noopener noreferrer"
                            download
                          >
                            <span className="file-icon">📎</span>
                            <span className="file-name">{file.name}</span>
                            <span className="download-icon">⬇️</span>
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="assistant-message">
                  <div className="message-label">LLM Council</div>

                  {/* Stage 1 */}
                  {msg.loading?.stage1 && (
                    <div className="stage-loading">
                      <div className="spinner"></div>
                      <span>Running Stage 1: Collecting individual responses...</span>
                    </div>
                  )}
                  {msg.stage1 && <Stage1 responses={msg.stage1} />}

                  {/* Stage 2 */}
                  {msg.loading?.stage2 && (
                    <div className="stage-loading">
                      <div className="spinner"></div>
                      <span>Running Stage 2: Peer rankings...</span>
                    </div>
                  )}
                  {msg.stage2 && (
                    <Stage2
                      rankings={msg.stage2}
                      labelToModel={msg.metadata?.label_to_model}
                      aggregateRankings={msg.metadata?.aggregate_rankings}
                    />
                  )}

                  {/* Stage 3 */}
                  {msg.loading?.stage3 && (
                    <div className="stage-loading">
                      <div className="spinner"></div>
                      <span>Running Stage 3: Final synthesis...</span>
                    </div>
                  )}
                  {msg.stage3 && <Stage3 finalResponse={msg.stage3} />}
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <span>Consulting the council...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {conversation.messages.length === 0 && (
        <form className="input-form" onSubmit={handleSubmit}>
          {selectedFiles.length > 0 && (
            <div className="file-previews">
              {selectedFiles.map(file => (
                <div key={file.id} className="file-preview">
                  <span className="file-name">{file.filename}</span>
                  <button
                    type="button"
                    className="remove-file"
                    onClick={() => removeFile(file.id)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="input-row">
            <input
              type="file"
              multiple
              ref={fileInputRef}
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept=".txt,.csv,.png,.jpg,.jpeg,.py,.pdf,.docx,.xml,.pptx,.xlsx,.xls"
            />
            <button
              type="button"
              className="attach-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading || isUploading}
              title="Attach files"
            >
              📎
            </button>
            <textarea
              className="message-input"
              placeholder="Ask your question... (Shift+Enter for new line, Enter to send)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              onCompositionStart={() => setIsComposing(true)}
              onCompositionEnd={() => setIsComposing(false)}
              disabled={isLoading || isUploading}
              rows={3}
            />
            <button
              type="submit"
              className="send-button"
              disabled={(!input.trim() && selectedFiles.length === 0) || isLoading || isUploading}
            >
              {isUploading ? 'Uploading...' : 'Send'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
