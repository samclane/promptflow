// web-socket.service.ts
import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket$!: WebSocketSubject<any>;

  public connect(jobId: string): void {
    const url = `ws://localhost:8000/jobs/${jobId}/ws`;  // replace with your WebSocket server URL
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
