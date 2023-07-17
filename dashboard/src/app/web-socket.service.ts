import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { LogWrapper } from './log';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket$!: WebSocketSubject<LogWrapper>;

  public connect(url: string, jobId: string): void {
    if (!this.socket$ || this.socket$.closed) {
      this.socket$ = webSocket(url);
    }
  }

  public getObservable(): WebSocketSubject<LogWrapper> {
    return this.socket$;
  }

  public close(): void {
    if (this.socket$) {
      this.socket$.complete();
    }
  }
}
