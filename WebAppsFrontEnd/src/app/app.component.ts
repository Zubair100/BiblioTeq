import {Component} from "@angular/core";
import {HttpAPIService} from "./http-api.service";
import {SafeResourceUrl} from "@angular/platform-browser";
import {AppSettings} from "../AppSettings";
import {isAuthenticated, logout} from "./auth/auth.module";
import {Router} from "@angular/router";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [HttpAPIService]
})
export class AppComponent {

  constructor(
    private apiService: HttpAPIService,
    private router: Router
  ) {}

  doLogout(): void {
    logout(this.router);
  }

  get checkPrivilege(): boolean {
    let privString : string = localStorage.getItem(AppSettings.privilege);

    return privString && parseInt(privString) > 0;
  }

  get greeting(): string {
    return "Signed in as " + localStorage.getItem(AppSettings.username);
  }

  // get wrapper so that we can conditionally display navbar items
  get isAuthenticated(): boolean {
    return isAuthenticated();
  }
}


