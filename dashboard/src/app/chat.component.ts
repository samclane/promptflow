import { Component } from '@angular/core';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  messages: { sender: string, text: string, timestamp: string }[] = [];
  messageInput: string = '';
  private messageSubject = new Subject<{ sender: string, text: string, timestamp: string }>();

  // Observable to listen for new messages
  messages$ = this.messageSubject.asObservable();

  constructor() {
    // Subscribe to the Observable to update the messages array
    this.messages$.subscribe(
      message => this.messages.push(message),
      error => console.error('An error occurred:', error)
    );
  }

  // Method to send a message
  sendMessage(sender: string) {
    const timestamp = new Date().toLocaleTimeString();
    this.messageSubject.next({ sender, text: this.messageInput, timestamp });
    this.messageInput = '';
  }
}
