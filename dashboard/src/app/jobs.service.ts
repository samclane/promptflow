import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class JobsService {
  private apiUrl = 'http://localhost:8000';  // Your API URL

  constructor(private http: HttpClient) { }

  getJobs(): Observable<any> {
    return this.http.get(`${this.apiUrl}/jobs`);
  }

  getJob(jobId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/jobs/${jobId}`);
  }

  getJobLogs(jobId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/jobs/${jobId}/logs`);
  }

  createJob(jobData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/jobs`, jobData);
  }
}
