import { Component, OnInit } from '@angular/core';
import { FlowchartService } from './flowchart.service';
import { JobsService } from './jobs.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  flowchartCount: number = 0;
  jobCount: number = 0;

  constructor(
    private flowchartService: FlowchartService,
    private jobService: JobsService
  ) { }

  ngOnInit(): void {
    this.flowchartService.getFlowchartCount().subscribe(count => {
      this.flowchartCount = count;
    });

    this.jobService.getJobCount().subscribe(count => {
      this.jobCount = count;
    });
  }
}
