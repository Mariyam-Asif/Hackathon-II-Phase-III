'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../auth-provider';
import { useRouter } from 'next/navigation';

interface Message {
  message_id: string;
  sender_type: 'user' | 'agent';
  content: string;
  timestamp: string;
  status: string;
}

interface Conversation {
  conversation_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export default function ChatPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [newConversationTitle, setNewConversationTitle] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations when user logs in
  useEffect(() => {
    if (user && token) {
      loadConversations();
    }
  }, [user, token]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    if (!user || !token) return;

    try {
      const response = await fetch(`/api/${user.id}/conversations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      } else {
        console.error('Failed to load conversations:', response.statusText);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const loadConversationHistory = async (conversationId: string) => {
    if (!user || !token) return;

    try {
      const response = await fetch(`/api/${user.id}/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data);
        setSelectedConversationId(conversationId);
      } else {
        console.error('Failed to load conversation:', response.statusText);
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const createNewConversation = async () => {
    setMessages([]);
    setSelectedConversationId(null);
    setNewConversationTitle('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading || !user || !token) return;

    const userMessage: Message = {
      message_id: Date.now().toString(),
      sender_type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
      status: 'sent',
    };

    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const requestBody = {
        message: inputMessage,
        conversation_id: selectedConversationId || undefined,
      };

      const response = await fetch(`/api/${user.id}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const data = await response.json();

        // Update conversation ID if it's a new conversation
        if (!selectedConversationId && data.conversation_id) {
          setSelectedConversationId(data.conversation_id);

          // Add to conversations list if it's not already there
          if (!conversations.some(conv => conv.conversation_id === data.conversation_id)) {
            const newConversation: Conversation = {
              conversation_id: data.conversation_id,
              title: `Conversation ${new Date().toLocaleString()}`,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            };
            setConversations(prev => [newConversation, ...prev]);
          }
        }

        // Add agent response to messages
        const agentMessage: Message = {
          message_id: `agent-${Date.now()}`,
          sender_type: 'agent',
          content: data.response,
          timestamp: new Date().toISOString(),
          status: 'sent',
        };

        setMessages(prev => [...prev, agentMessage]);
      } else {
        console.error('Failed to send message:', response.statusText);
        // Add error message to UI
        const errorMessage: Message = {
          message_id: `error-${Date.now()}`,
          sender_type: 'agent',
          content: `Error: ${response.statusText}`,
          timestamp: new Date().toISOString(),
          status: 'error',
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message to UI
      const errorMessage: Message = {
        message_id: `error-${Date.now()}`,
        sender_type: 'agent',
        content: 'Error: Failed to connect to the AI service',
        timestamp: new Date().toISOString(),
        status: 'error',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    router.push('/auth/login');
    return null;
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={createNewConversation}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition duration-200"
          >
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <h3 className="px-4 py-2 text-sm font-semibold text-gray-700">Recent Chats</h3>
          <div className="space-y-1 p-2">
            {conversations.map((conv) => (
              <button
                key={conv.conversation_id}
                onClick={() => loadConversationHistory(conv.conversation_id)}
                className={`w-full text-left p-2 rounded-md text-sm ${
                  selectedConversationId === conv.conversation_id
                    ? 'bg-blue-100 text-blue-800'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                <div className="font-medium truncate">{conv.title}</div>
                <div className="text-xs text-gray-500">
                  {new Date(conv.updated_at).toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500">
                <p className="text-lg mb-2">Welcome to the AI Chat Assistant!</p>
                <p>Start a conversation by typing a message below.</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.message_id}
                className={`flex ${
                  message.sender_type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-3xl rounded-lg p-4 ${
                    message.sender_type === 'user'
                      ? 'bg-blue-500 text-white'
                      : message.status === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className="text-xs mt-1 opacity-70">
                    {new Date(message.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-3xl rounded-lg p-4 bg-gray-200 text-gray-800">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-white">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}