import { Injectable } from '@angular/core';
import { WebSocketService } from './web-socket.service';
import { Observable } from 'rxjs';
import { LogWrapper } from './log';
import {environment} from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LogsService {
  private logs$!: Observable<LogWrapper>;

  constructor(private webSocketService: WebSocketService) { }

  startLogging(jobId: string): void {
    const baseUrl = environment.promptflowWsBaseUrl;
    const url = `${baseUrl}/jobs/${jobId}/ws`;
    this.webSocketService.connect(url, jobId);
    this.logs$ = this.webSocketService.getObservable();
  }

  getLogs(): Observable<LogWrapper> {
    return this.logs$;
  }
}
