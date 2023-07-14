import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { JobsService } from './jobs.service';

@Component({
  selector: 'app-job-detail',
  templateUrl: './job-detail.component.html',
  styleUrls: ['./job-detail.component.css']
})
export class JobDetailComponent implements OnInit {
  jobId!: string;
  job: any;

  constructor(
    private route: ActivatedRoute,
    private jobsService: JobsService
  ) { }

  ngOnInit(): void {
    this.jobId = this.route.snapshot.paramMap.get('id') as string;
    if (this.jobId){ 
        this.getJob();

    }
  }

  getJob(): void {
    if (this.jobId) {
        this.jobsService.getJob(this.jobId).subscribe(job => this.job = job);
    }
  }

}
