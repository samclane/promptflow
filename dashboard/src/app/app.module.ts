import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';  // Import HttpClientModule

import { AppComponent } from './app.component';
import { FlowchartListComponent } from './flowchart-list.component';

@NgModule({
  declarations: [
    AppComponent,
    FlowchartListComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule  // Add HttpClientModule to imports
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
