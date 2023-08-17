export interface Message {
    sender: 'AI' | 'USER';
    text: string;
    timestamp: string;
  }
  
export interface ChatResponse {
    ai_message: Message;
    user_message: Message;
}

export interface ChatOptions {
    model?: string;
    temperature?: number;
    top_p?: number;
    n?: number;
    max_tokens?: number | string;
    presence_penalty?: number;
    frequency_penalty?: number;
}
