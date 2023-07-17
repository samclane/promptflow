import { Injectable } from '@angular/core';
import { WebSocketService } from './web-socket.service';
import { Observable } from 'rxjs';
import { LogWrapper } from './log';

@Injectable({
  providedIn: 'root'
})
export class LogsService {
  private logs$!: Observable<LogWrapper>;

  constructor(private webSocketService: WebSocketService) { }

  startLogging(jobId: string): void {
    const url = `ws://localhost:8000/jobs/${jobId}/ws`;
    this.webSocketService.connect(url, jobId);
    this.logs$ = this.webSocketService.getObservable();
  }

  getLogs(): Observable<LogWrapper> {
    return this.logs$;
  }
}
