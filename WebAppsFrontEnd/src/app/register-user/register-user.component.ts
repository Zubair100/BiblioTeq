import {Component} from "@angular/core";
import {HttpAPIService} from "../http-api.service";
import {UserDetails} from "../jsonConversion/RegisterJson";
import {login} from "../auth/auth.module";
import {Http} from "@angular/http";
import {Router} from "@angular/router";

@Component({
  selector: 'app-register-user',
  templateUrl: './register-user.component.html',
  styleUrls: ['../../assets/forms.css']
})
export class RegisterUserComponent {

  _username: string;
  _password: string;

  constructor(private apiService: HttpAPIService,
              private http: Http,
              private router: Router
  ) { }

  submit() {
    let userDetails = new UserDetails(this._username, this._password);
    let userInfo: string;
    this.apiService.registerUser(userDetails).subscribe(
      jsonData => userInfo = JSON.stringify(jsonData),
      error => console.log(error),
      () => {
        login(userDetails, this.http, this.router, () => {}, () => {});
      }
    );
  }

}
