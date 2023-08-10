import { ChangeDetectionStrategy, Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import {BehaviorSubject, combineLatest, scan, startWith, Subject, switchMap, tap, withLatestFrom} from 'rxjs';
import {FormBuilder} from '@angular/forms';

interface Message {
  sender: 'AI' | 'USER';
  text: string;
  timestamp: string;
}

interface ChatResponse {
  ai_message: Message;
  user_message: Message;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatComponent {
  constructor(
    private readonly http: HttpClient,
    private readonly form: FormBuilder
  ) {}

  public readonly messageControl = this.form.nonNullable.control('');

  private readonly loadingSource = new BehaviorSubject<boolean>(false);

  private readonly messagesSource = new Subject<Message>();
  private readonly messages$ = this.messagesSource.pipe(
    scan((a, b) => {
      return [...a, b];
    }, <Message[]>[]),
    startWith(<Message[]>[]),
  )

  private readonly sendMessageSource = new Subject<Message>();
  private readonly sendMessage$ = this.sendMessageSource.pipe(
    tap((x) => {
      this.messagesSource.next(x);
      this.loadingSource.next(true);
    }),
    withLatestFrom(this.messages$),
    switchMap(([_, messages]) => this.http.post<ChatResponse>(this.buildUrl('/chat'), messages)),
    tap((m) => {
      this.messagesSource.next({
        sender: 'AI',
        text: m.ai_message.text,
        timestamp: new Date().toISOString()
      });
      this.loadingSource.next(false)
    }),
    startWith(<Message>{ sender: 'USER', text: '', timestamp: '' }),
  )

  public readonly vm$ = combineLatest({
    messages: this.messages$,
    sendMessage: this.sendMessage$,
    loading: this.loadingSource.asObservable()
  });

  // Method to send a message and receive AI response
  sendMessage() {
    if (!this.messageControl.value) return;

    this.sendMessageSource.next({
      sender: 'USER',
      text: this.messageControl.value,
      timestamp: (new Date()).toISOString()
    })

    this.messageControl.reset();
  }

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  private buildUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }
}
