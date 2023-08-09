import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Message, ChatResponse } from './message';


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
    this.userMessages.push(userMessage);
    this.allMessages.push(userMessage);

    this.http.post<ChatResponse>(this.buildUrl('/chat'), this.allMessages).subscribe(response => {
      this.aiMessages.push(response.ai_message);
      this.allMessages.push(response.ai_message);
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
