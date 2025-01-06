import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { LogWrapper } from './log';
import {environment} from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LogsService {

  constructor(private http: HttpClient) { }

  getLogs(jobId: string): Observable<LogWrapper[]> {
    const baseUrl = environment.promptflowApiBaseUrl;
    const url = `${baseUrl}/jobs/${jobId}/logs`;
    return this.http.get<LogWrapper[]>(url);
  }
}
