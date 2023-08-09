// Interface for a message
export interface Message {
    sender: string;
    text: string;
    timestamp: string;
  }
  
  // Interface for the response from the server
export interface ChatResponse {
    user_message: Message;
    ai_message: Message;
  }