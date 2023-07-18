import { Component, OnInit } from '@angular/core';
import { NodeService } from './node.service';
import { take } from 'rxjs/operators';

@Component({
  selector: 'app-node-type-list',
  templateUrl: './node-type-list.component.html',
  styleUrls: ['./node-type-list.component.css']
})
export class NodeTypeListComponent implements OnInit {
  nodeTypes: string[] = [];

  constructor(private nodeService: NodeService) { }

  ngOnInit(): void {
    this.getNodeTypes();
  }

  getNodeTypes(): void {
    this.nodeService.getNodeTypes().pipe(take(1)).subscribe(nodeTypes => this.nodeTypes = nodeTypes["node_types"]);
  }

}
