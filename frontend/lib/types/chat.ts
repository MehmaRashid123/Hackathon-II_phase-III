/**
 * Chat Types
 * TypeScript interfaces for chat functionality
 */

export interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>;
  result?: Record<string, any> | string;
}

export type MessageRole = "user" | "assistant" | "system";
export type MessageStatus = "sending" | "sent" | "failed";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status: MessageStatus;
  toolCalls?: ToolCall[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  lastMessageAt: Date;
  isActive: boolean;
}

export interface ChatState {
  // Data
  currentConversationId: string | null;
  conversations: Record<string, Conversation>;
  
  // UI State
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  
  // Actions
  sendMessage: (content: string) => Promise<void>;
  loadConversation: (id: string) => Promise<void>;
  createNewConversation: () => void;
  retryFailedMessage: (messageId: string) => Promise<void>;
  clearError: () => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
}
