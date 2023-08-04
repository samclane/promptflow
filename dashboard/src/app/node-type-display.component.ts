import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

interface NodeType {
  nodeType: string;
  options: string[];
  description: string;
}

@Component({
  selector: 'app-node-type-display',
  templateUrl: "./node-type-display.component.html",
  styles: []
})
export class NodeListComponent implements OnInit {
  nodeTypes$?: Observable<NodeType[]>;

  constructor(private http: HttpClient) {}

  get apiUrl() {
    return environment.promptflowApiBaseUrl;
  }

  private buildUrl(endpoint: string): string {
    return `${this.apiUrl}${endpoint}`;
  }

  ngOnInit(): void {
    this.nodeTypes$ = this.http.get<{ node_types: string[], descriptions: {[key: string]: string}, options: {[key: string]: string[]} }>(this.buildUrl('/nodes/types')).pipe(
      map(({ node_types, descriptions, options }) => 
        node_types.map(nodeType => ({ nodeType, options: options[nodeType], description: descriptions[nodeType] }))
      )
    );
  }
}
