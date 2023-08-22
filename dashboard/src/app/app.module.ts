import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http'; 

import { AppComponent } from './app.component';
import { FlowchartListComponent } from './flowchart-list.component';
import { JobListComponent } from './job-list.component';
import { FlowchartDetailComponent } from './flowchart-detail.component';
import { JobDetailComponent } from './job-detail.component';

import { RouterModule, Routes } from '@angular/router';
import { JobLogsComponent } from './job-logs.component';
import { HeaderComponent } from './header.component';
import { HomeComponent } from './home.component';
import { FlowchartListContainerComponent } from './flowchart-list-container.component';
import { FlowchartDisplayComponent } from './flowchart-display.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FlowchartImportJson } from './flowchart-import-json.component';
import { JobListContainerComponent } from './job-list-container.component';
import { NodeListComponent } from './node-type-display.component';
import { ChatComponent } from './chat.component';
import { ChatButtonComponent } from './chat-button.component';
import { ChatContainerComponent } from './chat-container.component';
import { PopoverComponent } from './popover.component';
import { ChatOptionsComponent } from './chat-options.component';
import { ChatOptionsPopoverComponent } from './chat-options-popover.component';
import { ToggleButtonComponent } from './toggle-button.component';
import { ToggleSliderComponent } from './toggle-slider.component';
import { SliderComponent } from './slider.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'flowcharts', component: FlowchartListContainerComponent },
  { path: 'flowcharts/:id', component: FlowchartDetailComponent },
  { path: 'jobs', component: JobListContainerComponent },
  { path: 'jobs/:id', component: JobDetailComponent },
  { path: 'nodes', component: NodeListComponent },
  { path: 'chat', component: ChatContainerComponent },
  { path: 'chat-options', component: ChatOptionsComponent },
  { path: 'slider', component: SliderComponent },
];



@NgModule({
  declarations: [
    AppComponent,
    FlowchartListComponent,
    JobListComponent,
    FlowchartDetailComponent,
    JobDetailComponent,
    JobLogsComponent,
    HeaderComponent,
    HomeComponent,
    FlowchartListContainerComponent,
    FlowchartDisplayComponent,
    FlowchartImportJson,
    JobListContainerComponent,
    NodeListComponent,
    ChatComponent,
    ChatButtonComponent,
    ChatContainerComponent,
    PopoverComponent,
    ChatOptionsComponent,
    ChatOptionsPopoverComponent,
    ToggleButtonComponent,
    ToggleSliderComponent,
    SliderComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    FormsModule,
    ReactiveFormsModule

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
