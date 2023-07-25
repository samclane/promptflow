import { Component, OnInit, Input, AfterViewInit } from '@angular/core';
import { Flowchart } from './flowchart';
import { FlowchartService } from './flowchart.service';
import { ActivatedRoute } from '@angular/router';
import { take } from 'rxjs/operators';

@Component({
  selector: 'app-flowchart-display',
  templateUrl: './flowchart-display.component.html',
  styleUrls: ['./flowchart-display.component.css']
})
export class FlowchartDisplayComponent implements OnInit {

  id!: string;

  constructor(private route: ActivatedRoute, private flowchartService: FlowchartService) {
    this.id = this.route.snapshot.paramMap.get('id')!;
  }

  ngOnInit(): void {
    this.flowchartService.getFlowchartPng(this.id).pipe(take(1)).subscribe(base64String => {
      // Remove the base64 image prefix if present
      const base64Image = base64String.replace(/^data:image\/(png|jpg);base64,/, "");
    
      // Decode the base64 string
      const byteCharacters = atob(base64Image);
    
      // Convert the bytes to a Blob
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "image/png" });
    
      // Create an object URL for the Blob
      const url = URL.createObjectURL(blob);
    
      // Create an img element and set the src attribute to the Blob URL
      const img = document.createElement('img');
      img.src = url;
    
      // Append the img element to the container
      const container = document.getElementById('flowchart-display');
      if (container) {
        container.appendChild(img);
      } else {
        console.error('Could not find element with id flowchart-display');
      }
    });
    
  }
  
  
  
  
}
