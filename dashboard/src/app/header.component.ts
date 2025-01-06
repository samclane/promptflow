import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Flowchart } from './flowchart';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  flowcharts: Flowchart[] = [];

  constructor(private http: HttpClient) {}

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  private buildUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }

  ngOnInit(): void {
    this.http.get<Flowchart[]>(this.buildUrl('/flowcharts')).subscribe(data => {
      this.flowcharts = data.slice(0, 5);
    });
  }
}
