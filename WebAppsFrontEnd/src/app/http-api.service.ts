import {Injectable} from "@angular/core";
import {DomSanitizer, SafeResourceUrl} from "@angular/platform-browser";
import "rxjs/add/operator/map";
import {Observable} from "rxjs/Observable";
import {AuthHttp} from "angular2-jwt/angular2-jwt";
import {AppSettings} from "../AppSettings";
import {NewAnswerJSON, NewAnswerSubmission} from "./jsonConversion/AnswerSubmissionJson";
import {UserJson} from "./jsonConversion/UserJson";
import {EditAnswer, EditAnswerJson} from "./jsonConversion/EditAnswerJson";
import {Paper, PaperJson} from "./jsonConversion/PaperJson";
import {EncodedPDF} from "./upload-paper/EncodedPdf";
import {LoginDetails} from "./login/LoginDetails";
import {Headers, RequestOptions} from "@angular/http";
import {Vote} from "./solution-page/Vote";


@Injectable()
export class HttpAPIService {

  private static VOTEINFO = '';
  private static PDFBASE = "data:application/pdf;base64,";

  constructor(private sanitizer: DomSanitizer,
              private http: AuthHttp) {
  }

  /*
   Solution page methods
   */

  public getPaper(paperId: string, paperYear: string): Observable<JSON> {
    return this.http.get(
      HttpAPIService.makeUrl([paperId, paperYear, 'paper'])
    ).map(res => res.json());
  }

  public getQuestions(paperId: string, paperYear: string): Observable<JSON> {
    return this.http.get(
      HttpAPIService.makeUrl([paperId, paperYear, 'questions'])
    ).map(res => res.json());
  }

  public getAnswers(questionId: number): Observable<JSON> {
    return this.http.get(
      HttpAPIService.makeUrl([questionId.toString(), 'answer'])
    ).map(res => res.json());
  }

  public voteAnswer(answerId: number, vote: Vote): Observable<JSON> {
    return this.http.post(
      HttpAPIService.makeUrl([vote.toUri(), answerId.toString()]),
      HttpAPIService.VOTEINFO
    ).map(res => res.json());
  }

  public submitAnswer(questionId: number,
                      userId: number,
                      username: string,
                      answer: string): Observable<JSON> {
    let toSubmit: NewAnswerJSON = new NewAnswerSubmission(
      questionId.toString(),
      new UserJson(userId, username),
      answer
    );
    return this.http.post(
      HttpAPIService.makeUrl(['submit', 'answer']),
      toSubmit
    ).map(res => res.json());
  }

  public editAnswer(answerId: number,
                    answer: string): Observable<JSON> {
    let toUpdate: EditAnswerJson = new EditAnswer(answerId, answer);
    return this.http.post(
      HttpAPIService.makeUrl(['update', 'answer']),
      toUpdate
    ).map(res => res.json());
  }

  public deleteAnswer(answerId: number): Observable<number> {
    return this.http.delete(HttpAPIService.makeUrl(['delete', answerId.toString(), 'answer'])).map(res => res.status);
  }

  public deletePaper(paperId: number): Observable<JSON> {
    return this.http.delete(HttpAPIService.makeUrl(['delete', paperId.toString(), 'paper'])).map(res => res.json());
  }

  public makePDF(encodedPdf: string): SafeResourceUrl {
    return this.sanitizeResource(HttpAPIService.PDFBASE + encodedPdf);
  }

  /*
   Paper uploading methods
   */

  public submitPaper(courseCode: string,
                     paperYear: number,
                     paperTitle: string,
                     encodedPdf: EncodedPDF): Observable<JSON> {
    let toSubmit: PaperJson = new Paper(courseCode, paperYear, paperTitle, encodedPdf.pdfAsString);
    console.log(toSubmit);
    return this.http.post(
      HttpAPIService.makeUrl(['submit', 'paper']),
      toSubmit
    ).map(res => res.json());
  }

  public submitPaperQuestions(paperId: number, questions: string[]): Observable<JSON> {
    // this should not be allowed in any programming language
    // seriously what is this???
    let toSubmit = JSON.stringify(
      questions.map(question => {
        return (q => ({number: q}))(question);
      }));
    console.log(toSubmit);
    let headers = new Headers({'Content-Type': 'application/json'});
    let options = new RequestOptions({'headers': headers});
    return this.http.post(
      HttpAPIService.makeUrl(['submit', paperId.toString(), 'questions']),
      toSubmit,
      options
    ).map(res => res.json());
  }

  /*
    User authentication
   */

  public registerUser(userDetails: LoginDetails): Observable<JSON> {
    return this.http.post(
      HttpAPIService.makeUrl(['register', 'student']),
      userDetails
    ).map(res => res.json());
  }

  /*
    Search page methods
   */

  public retrieveAllPapers(): Observable<JSON> {
    return this.http.get(HttpAPIService.makeUrl(['available-papers/'])).map(res => res.json());
  }

  /*
   Helper methods
   */

  private static makeUrl(params: string[]): string {
    return AppSettings.API_ENDPOINT + params.map(param => '/' + param).join('');
  }

  public sanitizeResource(url: string): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

}



