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
    max_tokens?: number | null;
    presence_penalty?: number;
    frequency_penalty?: number;
}

export const DEFAULT_OPTIONS: ChatOptions = {
    model: 'gpt-4',
    temperature: 1,
    top_p: 1,
    n: 1,
    max_tokens: null,
    presence_penalty: 0,
    frequency_penalty: 0
};
  