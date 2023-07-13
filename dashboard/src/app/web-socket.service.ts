// web-socket.service.ts
import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket$!: WebSocketSubject<any>;

  public connect(url: string, jobId: string): void {
    if (!this.socket$ || this.socket$.closed) {
      this.socket$ = webSocket(url);
    }
  }

  public getObservable(): WebSocketSubject<any> {
    return this.socket$;
  }

  public close(): void {
    if (this.socket$) {
      this.socket$.complete();
    }
  }
}
