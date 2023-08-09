import { Component } from '@angular/core';

@Component({
  selector: 'app-chat-button',
  templateUrl: './chat-button.component.html',
  styleUrls: ['./chat-button.component.css']
})
export class ChatButtonComponent {
  showChat: boolean = false;

  toggleChat() {
    this.showChat = !this.showChat;
  }
}
