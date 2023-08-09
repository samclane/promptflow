import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

// Interface for a message
interface Message {
  sender: string;
  text: string;
  timestamp: string;
}

// Interface for the response from the server
interface ChatResponse {
  user_message: Message;
  ai_message: Message;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  userMessages: Message[] = [];
  aiMessages: Message[] = [];
  allMessages: Message[] = []; // Combined array of user and AI messages
  messageInput: string = '';

  constructor(private http: HttpClient) {}

  // Method to send a message and receive AI response
  sendMessage(sender: string) {
    const timestamp = new Date().toLocaleTimeString();
    const userMessage: Message = { sender, text: this.messageInput, timestamp };

    this.http.post<ChatResponse>(this.buildUrl('/chat'), userMessage).subscribe(response => {
      this.userMessages.push(response.user_message);
      this.aiMessages.push(response.ai_message);
      this.allMessages.push(response.user_message, response.ai_message); // Interleaving messages
    });

    this.messageInput = '';
  }

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  private buildUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }
}
