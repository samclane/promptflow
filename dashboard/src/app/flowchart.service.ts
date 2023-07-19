import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Flowchart, FlowchartConfirmation } from './flowchart';

@Injectable({
  providedIn: 'root'
})
export class FlowchartService {
  private apiUrl = 'http://localhost:8000';  // Your API URL

  constructor(private http: HttpClient) { }

  getFlowcharts(): Observable<Flowchart[]> {
    return this.http.get(`${this.apiUrl}/flowcharts`) as Observable<Flowchart[]>;
  }

  getFlowchart(flowchartId: string): Observable<Flowchart> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}`) as Observable<Flowchart>;
  }

  upsertFlowchart(flowchartJson: Flowchart): Observable<Flowchart> {
    return this.http.post(`${this.apiUrl}/flowcharts`, flowchartJson) as Observable<Flowchart>;
  }

  runFlowchart(flowchartId: string): Observable<FlowchartConfirmation> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/run`) as Observable<FlowchartConfirmation>;
  }

  stopFlowchart(flowchartId: string): Observable<FlowchartConfirmation> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/stop`) as Observable<FlowchartConfirmation>;
  }

  getFlowchartCount(): Observable<number> {
    return this.getFlowcharts().pipe(
      map(flowcharts => flowcharts.length)
    );
  }

  deleteFlowchart(flowchartId: string): Observable<FlowchartConfirmation> {
    return this.http.delete(`${this.apiUrl}/flowcharts/${flowchartId}`) as Observable<FlowchartConfirmation>;
  }

  getFlowchartSvg(flowchartId: string): Observable<string> {
    return this.http.get(`${this.apiUrl}/flowcharts/${flowchartId}/svg`, { responseType: 'text' }) as Observable<string>;
  }
}
