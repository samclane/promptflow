import { ChangeDetectionStrategy, Component } from '@angular/core';
import { trigger, transition, style, animate } from '@angular/animations';
import { combineLatest, BehaviorSubject } from 'rxjs';
import { FormBuilder } from '@angular/forms';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [
    trigger('messageState', [
      transition(':enter', [
        style({ opacity: 0 }),
        animate('300ms ease-out', style({ opacity: 1 }))
      ])
    ])
  ]
})
export class ChatComponent {
  constructor(
    private readonly chatService: ChatService,
    private readonly form: FormBuilder
  ) {}

  public readonly messageControl = this.form.nonNullable.control('');
  public showOptions$ = new BehaviorSubject<boolean>(false);

  public readonly vm$ = combineLatest({
    messages: this.chatService.messages$,
    sendMessage: this.chatService.sendMessage$,
    loading: this.chatService.loadingSource.asObservable(),
    showOptions: this.showOptions$.asObservable()
  });

  // Method to send a message and receive AI response
  sendMessage() {
    if (!this.messageControl.value) return;

    this.chatService.sendMessage({
      sender: 'USER',
      text: this.messageControl.value,
      timestamp: (new Date()).toISOString()
    });

    this.messageControl.reset();
  }

  clearMessages() {
    this.chatService.clearMessages();
  }

  toggleOptions() {
    this.showOptions$.next(!this.showOptions$.value);
  }
}
