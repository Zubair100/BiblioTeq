import {BrowserModule} from "@angular/platform-browser";
import {NgModule} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {HttpModule} from "@angular/http";
import {MomentModule} from "angular2-moment";
import {QuillModule} from "ngx-quill";
import {NgbModule} from '@ng-bootstrap/ng-bootstrap';

import {AppComponent} from "./app.component";
import {SearchComponent} from "./search/search.component";
import {SolutionPageComponent} from "./solution-page/solution-page.component";
import {AuthModule} from "./auth/auth.module";
import {LoginComponent} from "./login/login.component";
import {AuthGuard} from "./auth/auth-guard.service";
import {UploadPaperComponent} from "./upload-paper/upload-paper.component";
import {AppRoutingModule} from "./app-routing.module";
import {LoginGuard} from "./auth/login-guard-service";
import { RegisterUserComponent } from './register-user/register-user.component';
import {StudentGuard} from "./auth/studentGuard";


@NgModule({
  declarations: [
    AppComponent,
    SearchComponent,
    SolutionPageComponent,
    LoginComponent,
    UploadPaperComponent,
    RegisterUserComponent,
  ],
  imports: [
    AppRoutingModule,
    BrowserModule,
    FormsModule,
    HttpModule,
    AuthModule,
    MomentModule,
    QuillModule,
    NgbModule.forRoot()
  ],
  providers: [AuthGuard, LoginGuard, StudentGuard],
  bootstrap: [AppComponent]
})
export class AppModule {
}

