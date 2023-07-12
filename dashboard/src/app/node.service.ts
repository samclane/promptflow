import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class NodeService {
  private apiUrl = 'http://localhost:8000';  // Your API URL

  constructor(private http: HttpClient) { }

  getNodeTypes(): Observable<any> {
    return this.http.get(`${this.apiUrl}/nodes/types`);
  }

}
