import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Subject, debounceTime, take } from 'rxjs';

@Component({
  selector: 'app-add-node',
  templateUrl: './add-node.component.html',
  styleUrls: ['./add-node.component.css']
})
export class AddNodeComponent implements OnInit {
  nodeLabel = new FormControl('');
  addNode = new Subject<string>();
    labelSub: any;
  constructor() { }

  ngOnInit(): void {
    this.labelSub = this.nodeLabel.valueChanges.pipe(debounceTime(300)).subscribe(label => {
        if (label) {
            console.log(label);
            this.addNode.next(label);
        }
    });
  }

  onSubmit(): void {
    // Reset the form
    this.nodeLabel.reset();
  }

  ngOnDestroy(): void {
    this.labelSub.unsubscribe();
  }

}
