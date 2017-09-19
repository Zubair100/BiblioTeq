export class Answer {

  constructor(
    private _id: number,
    private _userId: number,
    private _username: string,
    private _numVotes: number,
    private _timestamp: Date,
    private _answer: string,
    private _questionId: number,
    private _canVote: boolean
  ) {}


  public canEdit(myId: number): boolean {
    return myId == this.userId;
  }

  public displayAnswer(): string {
    return this._answer;
  }

  public setAnswer(newAnswer: string): void {
    this._answer = newAnswer;
  }

  public upvote(): void {
    this._numVotes++;
    this._canVote = false;
  }

  public downvote(): void {
    this._numVotes--;
    this._canVote = true;
  }

  get id(): number {
    return this._id;
  }

  get username(): string {
    return this._username;
  }

  get numVotes(): number {
    return this._numVotes;
  }

  set numVotes(value: number) {
    this._numVotes = value;
  }

  get timestamp(): Date {
    return this._timestamp;
  }

  get questionId(): number {
    return this._questionId;
  }

  get userId(): number {
    return this._userId;
  }

  get canVote(): boolean {
    return this._canVote;
  }

}
