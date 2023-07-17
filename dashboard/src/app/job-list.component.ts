import { Component, OnInit } from '@angular/core';
import { JobsService } from './jobs.service';

@Component({
  selector: 'app-job-list',
  templateUrl: './job-list.component.html',
  styleUrls: ['./job-list.component.css']
})
export class JobListComponent implements OnInit {
  jobs: any[] = [];
  sortDirection = 1; // 1 for ascending, -1 for descending

  constructor(private jobsService: JobsService) { }

  ngOnInit(): void {
    this.getJobs();
  }

  getJobs(): void {
    this.jobsService.getJobs().subscribe(jobs => this.jobs = jobs);
  }

  sortJobs(property_name: string) {
    this.jobs.sort((a, b) => (a[property_name] > b[property_name] ? 1 : -1) * this.sortDirection);
    // Flip the direction for the next sort
    this.sortDirection *= -1;
  }
}
