import {Component, ElementRef, OnDestroy} from "@angular/core";
import {SafeResourceUrl} from "@angular/platform-browser";
import {ActivatedRoute, Router} from "@angular/router";
import {HttpAPIService} from "../http-api.service";
import {NullSolution, Solution} from "./Solution";
import {Answer} from "./Answer";
import {NewAnswerSubmission} from "../jsonConversion/AnswerSubmissionJson";
import {QuillEditorComponent} from "ngx-quill/src/quill-editor.component";
import {AppSettings} from "../../AppSettings";
import {Observable} from "rxjs/Observable";
import "rxjs/add/observable/timer";
import {Subscription} from "rxjs/Subscription";
import {DownVote, UpVote, Vote} from "./Vote";
import * as LODASH from "lodash";

@Component({
  selector: 'app-solution-page',
  templateUrl: './solution-page.component.html',
  styleUrls: ['./solution-page.component.css'],
  providers: [HttpAPIService]
})


export class SolutionPageComponent implements OnDestroy {
  solutions: Solution[] = [];
  private displayedSolution: Solution = new NullSolution();

  paperName: string;
  paperId: number;
  paperCode: string;
  paperYear: string;
  myId: number;
  myPrivilege: number;

  pdfSrc: SafeResourceUrl;
  private refreshPageSubscription: Subscription;
  private refreshSolutionSubscription: Subscription;

  private editingAnswer: Answer = null;
  answerEditor: QuillEditorComponent = new QuillEditorComponent(new ElementRef('placeholder'));


  constructor(private route: ActivatedRoute,
              private router: Router,
              private apiService: HttpAPIService) {
    this.paperCode = route.snapshot.params['paperCode'];
    this.paperYear = route.snapshot.params['paperYear'];

    this.myId = parseInt(localStorage.getItem(AppSettings.userId));
    this.myPrivilege = parseInt(localStorage.getItem(AppSettings.privilege));

    this.retrievePaper();
    this.retrieveSolutions();
    this.subscribeToUpdates();
  }

  private subscribeToUpdates() {
    this.refreshPageSubscription = Observable.timer(
      SolutionPageComponent.seconds(20), // initial delay
      SolutionPageComponent.seconds(120) // poll rate
    ).subscribe(() => this.refreshPage());

    let solutionRefreshRate = 5;
    this.refreshSolutionSubscription = Observable.timer(
      SolutionPageComponent.seconds(solutionRefreshRate),
      SolutionPageComponent.seconds(solutionRefreshRate)
    ).subscribe(() => this.refreshDisplayedSolution());
  }

  ngOnDestroy(): void {
    this.refreshPageSubscription.unsubscribe();
    this.refreshSolutionSubscription.unsubscribe();
  }

  /*
   Initialisation of page
   */

  private retrievePaper() {
    let jsonPaper: string;
    this.apiService.getPaper(this.paperCode, this.paperYear).subscribe(
      jsonData => jsonPaper = JSON.stringify(jsonData),
      error => {
        console.log(error);
      },
      () => {
        let parsedPaper = JSON.parse(jsonPaper);
        this.paperName = parsedPaper.title;
        this.pdfSrc = this.apiService.makePDF(parsedPaper.pdf);
        this.paperId = parsedPaper.paper_id;
      }
    );
  }

  private retrieveSolutions() {
    let jsonSolutions: string;
    this.apiService.getQuestions(this.paperCode, this.paperYear).subscribe(
      jsonData => jsonSolutions = JSON.stringify(jsonData),
      error => console.log(error),
      () => {
        this.makeSolutionsFromJson(jsonSolutions);
      }
    );
  }

  private makeSolutionsFromJson(jsonSolutions: string) {
    JSON.parse(jsonSolutions).forEach(parsedSolution => {
      this.solutions.push(new Solution(parsedSolution.id, parsedSolution.number));
    });
  }

  private makeAnswersFromJson(solution: Solution, jsonAnswers: string): void {
    solution.answers = JSON.parse(jsonAnswers).map(parsedAnswer => {
      return NewAnswerSubmission.makeAnswerFromJson(parsedAnswer);
    });
    solution.resortAnswers();
  }

  /*
   Real time updates
   */

  private refreshPage(): void {
    this.solutions.forEach(solution => this.refreshSolution(solution));
  }

  private refreshDisplayedSolution(): void {
    if (!this.displayedSolution.isNull() && !this.displayedSolution.hidden) {
      this.refreshSolution(this.displayedSolution);
    }
  }

  private refreshSolution(solution: Solution) {
    let jsonAnswers: string;
    this.apiService.getAnswers(solution.id).subscribe(
      jsonData => jsonAnswers = JSON.stringify(jsonData),
      error => console.log(error),
      () => {
        this.makeAnswersFromJson(solution, jsonAnswers);
      }
    );
  }

  /*
   Interactive display elements
   */

  protected toggleShow(solution: Solution): void {
    if (solution != this.displayedSolution) {
      this.displayedSolution.hide();
      this.displayedSolution = solution;
    }
    solution.toggleShow();
    if (!solution.hidden) {
      this.refreshSolution(solution);
    }
  }

  protected upVoteAnswer(solution: Solution, answer: Answer): void {
    answer.upvote();
    this.voteAnswer(solution, answer, new UpVote());
  }

  protected downVoteAnswer(solution: Solution, answer: Answer): void {
    answer.downvote();
    this.voteAnswer(solution, answer, new DownVote());
  }

  private voteAnswer(solution: Solution, answer: Answer, vote: Vote) {
    let newVotesJson;
    this.apiService.voteAnswer(answer.id, vote).subscribe(
      jsonData => newVotesJson = JSON.stringify(jsonData),
      error => console.log(error),
      () => {
        answer.numVotes = JSON.parse(newVotesJson).votes;
        solution.resortAnswers();
      }
    );
  }

  protected deletePaper(): void {
    this.apiService.deletePaper(this.paperId).subscribe(
      res => {},
      error => console.log(error),
      () => {
        alert('Page successfully deleted');
        this.router.navigate(['/search']);
      }
    );
  }

  /*
   Answer submission
   */

  protected submitAnswer(solution: Solution, editor: QuillEditorComponent): void {
    if (this.checkInvalidSubmission(editor)) {
      return;
    }

    let jsonAnswer: string;
    this.apiService.submitAnswer(
      solution.id,
      parseInt(localStorage.getItem(AppSettings.userId)),
      localStorage.getItem(AppSettings.username),
      editor.editorElem.innerHTML
    )
      .subscribe(
        jsonData => jsonAnswer = JSON.stringify(jsonData),
        error => console.log(error),
        () => {
          solution.addAnswer(NewAnswerSubmission.makeAnswerFromJson(JSON.parse(jsonAnswer)));
          solution.showMore();
        }
      );

  }

  private checkInvalidSubmission(editor: QuillEditorComponent): boolean {
    let invalid = editor.editorElem.innerText.length < 10;
    if (invalid) {
      //TODO show feedback better
      alert('Minimum length of 10 characters');
    }
    return invalid;
  }

  /*
   Answer Editing
   */

  protected setAnswerEditor(editor: QuillEditorComponent) {
    this.answerEditor = editor;
  }

  protected isEditing(answer: Answer): boolean {
    return LODASH.isEqual(this.editingAnswer, answer);
  }

  protected editAnswer(answer: Answer): void {
    this.editingAnswer = answer;
    console.log(this.answerEditor, answer);
    this.answerEditor.editorElem.innerHTML = answer.displayAnswer();
  }

  protected cancelEdit(): void {
    this.editingAnswer = null;
  }

  protected submitUpdatedAnswer(): void {
    if (this.checkInvalidSubmission(this.answerEditor)) {
      return;
    }

    let jsonAnswer: string;
    this.apiService.editAnswer(this.editingAnswer.id, this.answerEditor.editorElem.innerHTML).subscribe(
      jsonData => jsonAnswer = JSON.stringify(jsonData),
      error => console.log(error),
      () => {
        this.displayedSolution.updateAnswer(this.editingAnswer, JSON.parse(jsonAnswer).html);
        console.log('updated answer', this.editingAnswer);
        this.cancelEdit();
      }
    );
  }

  /*
   Answer deletion
   */

  protected deleteAnswer(answer: Answer, solution: Solution) {
    this.apiService.deleteAnswer(answer.id).subscribe(
      res => {
      },
      error => console.log(error),
      () => {
        solution.removeAnswer(answer);
      }
    );
  }


  /*
   Helper methods
   */

  private static seconds(s: number) {
    return s * 1000;
  }


}
