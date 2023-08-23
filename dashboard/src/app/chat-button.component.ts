import { Component } from '@angular/core';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'app-chat-button',
  templateUrl: './chat-button.component.html',
  styleUrls: ['./chat-button.component.css'],
  animations: [
    trigger('chatState', [
      state('hidden', style({
        height: '0',
        overflow: 'hidden',
        opacity: 0
      })),
      state('visible', style({
        height: '*', // Will expand to content height
        overflow: 'hidden',
        opacity: 1
      })),
      transition('hidden <=> visible', animate('200ms'))
    ])
  ]
})
export class ChatButtonComponent {
  private showChatSubject = new BehaviorSubject<boolean>(false);
  showChat$ = this.showChatSubject.asObservable();

  toggleChat() {
    this.showChatSubject.next(!this.showChatSubject.getValue());
  }

  get chatState() {
    return this.showChatSubject.getValue() ? 'visible' : 'hidden';
  }
}
