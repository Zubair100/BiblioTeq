import {NgModule} from "@angular/core";
import {Headers, Http, RequestOptions} from "@angular/http";
import {AuthConfig, AuthHttp, JwtHelper} from "angular2-jwt";
import {Router} from "@angular/router";
import {AppSettings} from "../../AppSettings";
import {LoginDetails} from "../login/LoginDetails";

export function authHttpServiceFactory(http: Http, options: RequestOptions): AuthHttp {
  return new AuthHttp(new AuthConfig({noJwtError: true, headerPrefix: "JWT"}), http, options);
}

export function login(
  loginDetails: LoginDetails,
  http: Http,
  router: Router,
  success: () => void,
  fail: () => void
): void {
  let headers : Headers = new Headers();
  headers.append('Content-Type', 'application/json');

  http.post(AppSettings.API_ENDPOINT + '/auth/', JSON.stringify(loginDetails), {
    headers: headers
  })
    .map(res => res.json())
    .subscribe(
      data => {
        localStorage.setItem(AppSettings.userId, data.user.id);
        localStorage.setItem(AppSettings.username, loginDetails.username);
        localStorage.setItem(AppSettings.tokenName, data.token);
        localStorage.setItem(AppSettings.privilege, data.privilege);
        console.log('logged in.');
        router.navigate(['/search']);
        success();
      },
      err => fail()
    );
}

export function isAuthenticated(): boolean {
  let token: string = localStorage.getItem(AppSettings.tokenName);
  if (token != null) {
    //has token, check if it's valid and redirect to login if it's not
    let jwtHelper: JwtHelper = new JwtHelper();
    return !jwtHelper.isTokenExpired(token);
  }

  //no token
  return false;
}

export function logout(router: Router): void {
  localStorage.clear();
  console.log('Logged out.');
  router.navigate(['/login']);
}

@NgModule({
  providers: [
    {
      provide: AuthHttp,
      useFactory: authHttpServiceFactory,
      deps: [Http, RequestOptions]
    }
  ]
})
export class AuthModule {}
