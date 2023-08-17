import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Subject, scan, startWith, switchMap, tap, withLatestFrom } from 'rxjs';
import { Message, ChatResponse, ChatOptions } from './chat';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  public readonly loadingSource = new BehaviorSubject<boolean>(false);
  private readonly messagesSource = new Subject<Message | null>();
  private readonly sendMessageSource = new Subject<Message>();

  messages$ = this.messagesSource.pipe(
    scan((a, b) => {
      const newMessages = b === null ? [] : [...a, b];
      localStorage.setItem('chat_messages', JSON.stringify(newMessages));
      return newMessages;
    }, JSON.parse(localStorage.getItem('chat_messages') || '[]') as Message[]),
    startWith(JSON.parse(localStorage.getItem('chat_messages') || '[]') as Message[])
  );

  sendMessage$ = this.sendMessageSource.pipe(
    tap((x) => {
      this.messagesSource.next(x);
      this.loadingSource.next(true);
    }),
    withLatestFrom(this.messages$),
    switchMap(([_, messages]) => this.http.post<ChatResponse>(this.buildUrl('/chat'), {messages, options: <ChatOptions>{}})),
    tap((m) => {
      this.messagesSource.next({
        sender: 'AI',
        text: m.ai_message.text,
        timestamp: new Date().toISOString()
      });
      this.loadingSource.next(false);
    }),
    startWith(<Message>{ sender: 'USER', text: '', timestamp: '' }),
  );

  constructor(private readonly http: HttpClient) {}

  private buildUrl(endpoint: string): string {
    return `${environment.promptflowApiBaseUrl}${endpoint}`;
  }

  public sendMessage(message: Message) {
    this.sendMessageSource.next(message);
  }

  public clearMessages() {
    localStorage.removeItem('chat_messages');
    this.messagesSource.next(null);
  }
}
