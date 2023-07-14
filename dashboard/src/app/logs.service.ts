import { Injectable } from '@angular/core';
import { WebSocketService } from './web-socket.service';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LogsService {
  private logs$!: Observable<any>;

  constructor(private webSocketService: WebSocketService) { }

  startLogging(jobId: string): void {
    const url = `ws://localhost:8000/jobs/${jobId}/ws`;
    this.webSocketService.connect(url, jobId);
    this.logs$ = this.webSocketService.getObservable();
  }

  getLogs(): Observable<any> {
    return this.logs$;
  }
}
