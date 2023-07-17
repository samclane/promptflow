import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Job, JobLog } from './job';

@Injectable({
  providedIn: 'root'
})
export class JobsService {
  private apiUrl = 'http://localhost:8000';  // Your API URL

  constructor(private http: HttpClient) { }

  getJobs(): Observable<Job[]> {
    return this.http.get(`${this.apiUrl}/jobs`) as Observable<Job[]>;
  }

  getJob(jobId: string): Observable<Job> {
    return this.http.get(`${this.apiUrl}/jobs/${jobId}`) as Observable<Job>;
  }

  getJobLogs(jobId: string): Observable<JobLog> {
    return this.http.get(`${this.apiUrl}/jobs/${jobId}/logs`) as Observable<JobLog>;
  }

  createJob(jobData: Object): Observable<Job> {
    return this.http.post(`${this.apiUrl}/jobs`, jobData) as Observable<Job>;
  }

  getJobCount(): Observable<number> {
    return this.getJobs().pipe(
      map(jobs => jobs.length)
    );
  }
}
