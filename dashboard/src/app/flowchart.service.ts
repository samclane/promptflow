import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FlowchartService {
  private apiUrl = 'http://localhost:8000';  // Your API URL

  constructor(private http: HttpClient) { }

  getFlowcharts(): Observable<any> {
    return this.http.get(`${this.apiUrl}/flowcharts`);
  }

  getFlowchart(flowchartId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}`);
  }

  upsertFlowchart(flowchartJson: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/flowcharts`, flowchartJson);
  }

  runFlowchart(flowchartId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/run`);
  }

  stopFlowchart(flowchartId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/stop`);
  }
}
