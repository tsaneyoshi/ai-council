import { useState, useEffect } from 'react';
import './Sidebar.css';

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onRenameConversation,
  onOpenSettings,
  settings,
}) {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const startEditing = (e, conv) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title || 'New Conversation');
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditTitle('');
  };

  const saveTitle = (e) => {
    e.stopPropagation();
    if (editingId && editTitle.trim()) {
      onRenameConversation(editingId, editTitle.trim());
      setEditingId(null);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      saveTitle(e);
    } else if (e.key === 'Escape') {
      cancelEditing();
    }
  };

  const organizationName = settings?.organization_name || '';

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>{organizationName}AI審議会</h1>
        <button className="new-conversation-btn" onClick={onNewConversation}>
          <strong>+ New</strong>
        </button>
      </div>

      <div className="conversation-list">
        {conversations.length === 0 ? (
          <div className="no-conversations">No conversations yet</div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''
                }`}
              onClick={() => onSelectConversation(conv.id)}
            >
              {editingId === conv.id ? (
                <div className="conversation-edit">
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onClick={(e) => e.stopPropagation()}
                    autoFocus
                    onBlur={cancelEditing}
                  />
                </div>
              ) : (
                <>
                  <div className="conversation-content">
                    <div className="conversation-title">
                      {conv.title || 'New Conversation'}
                    </div>
                    <div className="conversation-meta">
                      {conv.message_count} messages
                    </div>
                  </div>
                  <div className="conversation-actions">
                    <button
                      className="action-btn edit-btn"
                      onClick={(e) => startEditing(e, conv)}
                      title="Rename"
                    >
                      ✎
                    </button>
                    <button
                      className="action-btn delete-btn"
                      onClick={(e) => onDeleteConversation(conv.id, e)}
                      title="Delete"
                    >
                      ×
                    </button>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
      <div className="sidebar-footer">
        <button className="settings-btn" onClick={onOpenSettings} title="Settings">
          ⚙️ Settings
        </button>
      </div>
    </div>
  );
}
