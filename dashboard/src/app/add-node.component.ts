import { Component, Input, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Subject, debounceTime, take } from 'rxjs';
import { NodeService } from './node.service';

@Component({
  selector: 'app-add-node',
  templateUrl: './add-node.component.html',
  styleUrls: ['./add-node.component.css']
})
export class AddNodeComponent implements OnInit {
  @Input() flowchartId!: string;
  nodeType: string = '';
  nodeLabel = new FormControl('');
  addNode = new Subject<string>();
  labelSub: any;
  constructor(
    private nodeService: NodeService
  ) { }

  ngOnInit(): void {
    this.labelSub = this.nodeLabel.valueChanges.pipe(debounceTime(300)).subscribe(label => {
        if (label) {
            console.log(label);
            this.addNode.next(label);
        }
    });
  }

  onSubmit(): void {
    console.log("Adding node...");
    // Reset the form
    this.nodeLabel.reset();
    // Add the node
    this.nodeService.addNode(this.flowchartId, this.nodeType).pipe(take(1)).subscribe(() => {
        console.log('Node added!');
    });
  }

  ngOnDestroy(): void {
    this.labelSub.unsubscribe();
  }

  onNodeTypeSelected(nodeType: string) {
    console.log('Selected node type: ', nodeType);
    this.nodeType = nodeType;
  }
  
}
