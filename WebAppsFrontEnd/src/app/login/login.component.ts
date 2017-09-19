import {Component} from "@angular/core";
import {login} from "../auth/auth.module";
import {Http} from "@angular/http";
import {Router} from "@angular/router";
import {UserDetails} from "../jsonConversion/RegisterJson";
import {AppSettings} from "../../AppSettings";
import {HttpAPIService} from "../http-api.service";
import {SafeResourceUrl} from "@angular/platform-browser";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['../../assets/forms.css']
})
export class LoginComponent {
  failed: boolean = false;
  logoSrc: SafeResourceUrl;

  _username: string;
  _password: string;

  constructor(private http: Http,
              private apiService: HttpAPIService,
              private router: Router)
  {
    this.logoSrc = this.apiService.sanitizeResource(AppSettings.logoSrc);
  }


  onSubmit() {
    login(new UserDetails(this._username, this._password), this.http, this.router,
      // success
      () => {},
      // failure
      () => {
        this.failed = true;
      }
    );
  }

  register() {
    this.router.navigate(['/register']);
  }
}


