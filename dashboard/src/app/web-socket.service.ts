import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService<T> {
  private socket$!: WebSocketSubject<T>;

  public connect(url: string, jobId: string): void {
    if (!this.socket$ || this.socket$.closed) {
      this.socket$ = webSocket(url);
    }
  }

  public getObservable(): WebSocketSubject<T> {
    return this.socket$;
  }

  public close(): void {
    if (this.socket$) {
      this.socket$.complete();
    }
  }
}
