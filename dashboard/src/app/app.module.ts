import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';  // Import HttpClientModule

import { AppComponent } from './app.component';
import { FlowchartListComponent } from './flowchart-list.component';
import { JobListComponent } from './job-list.component';
import { NodeTypeListComponent } from './node-type-list.component';
import { FlowchartDetailComponent } from './flowchart-detail.component';
import { JobDetailComponent } from './job-detail.component';

import { RouterModule, Routes } from '@angular/router';
import { JobLogsComponent } from './job-logs.component';
import { HeaderComponent } from './header.component';
import { HomeComponent } from './home.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'flowcharts', component: FlowchartListComponent },
  { path: 'flowcharts/:id', component: FlowchartDetailComponent },
  { path: 'jobs', component: JobListComponent },
  { path: 'jobs/:id', component: JobDetailComponent }
];



@NgModule({
  declarations: [
    AppComponent,
    FlowchartListComponent,
    JobListComponent,
    NodeTypeListComponent,
    FlowchartDetailComponent,
    JobDetailComponent,
    JobLogsComponent,
    HeaderComponent,
    HomeComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,  // Add HttpClientModule to imports
    RouterModule.forRoot(routes)  // Add RouterModule to imports
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
