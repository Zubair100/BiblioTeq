import {Answer} from "app/solution-page/Answer";
import * as LODASH from 'lodash';

export class Solution {
  private _hidden: boolean = true;
  private _answers: Answer[] = [];
  private _showMore: boolean = false;

  constructor(private _id: number, private _question: string) {
  }

  public toggleShow() {
    this._hidden = !this._hidden;
    this._showMore = false;
  }

  public showMore() {
    this._showMore = true;
  }

  public displayAnswers(): Answer[] {
    if (this.getShowMore()) {
      return [this.answers[0]];
    }
    return this.answers;
  }

  public getShowMore() {
    return !this._showMore && this._answers.length > 1;
  }

  public hide(): void {
    this._hidden = true;
  }

  public addAnswer(answer: Answer) {
    this._answers.push(answer);
    this.resortAnswers();
  }

  public removeAnswer(answer: Answer) {
    this._answers = this.answers.filter(ans => ans.id !== answer.id);
    this.resortAnswers();
  }

  public updateAnswer(answer: Answer, newValue: string): void {
    this.answers.find(ans => LODASH.isEqual(ans, answer)).setAnswer(newValue);
    this.resortAnswers();
  }

  public resortAnswers() {
    this.answers.sort((a1, a2) => a2.numVotes - a1.numVotes);
  }

  public canSubmitNewAnswer(myId: number): boolean {
    return this.answers.map(answer => answer.userId !== myId).reduce((b1, b2) => b1 && b2, true);
  }

  public getSolutionHeader() {
    return this.answers.length > 0 ?
      "Answers for " + this.question + ':' :
      "There are no answers for " + this.question + '. Why not submit yours?';
  }

  public isNull(): boolean {
    return false;
  }


  /*
  Getters and setters
   */

  get question(): string {
    return this._question;
  }

  get answers(): Answer[] {
    return this._answers;
  }

  set answers(value: Answer[]) {
    this._answers = value;
  }

  get hidden(): boolean {
    return this._hidden;
  }

  get id(): number {
    return this._id;
  }

}

export class NullSolution extends Solution {

  constructor() {
    super(NaN, "null");
  }

  public hide(): void {}


  public isNull(): boolean {
    return true;
  }
}
