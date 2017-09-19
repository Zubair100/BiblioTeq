import {UserJsonInterface} from "./UserJson";
import {Answer} from "../solution-page/Answer";


export interface NewAnswerJSON {
  readonly question: string;
  readonly user: UserJsonInterface;
  readonly html: string;
}

export class NewAnswerSubmission implements NewAnswerJSON {
  question: string;
  user: UserJsonInterface;
  html: string;

  constructor(question: string, user: UserJsonInterface, html: string) {
    this.question = question;
    this.user = user;
    this.html = html;
  }

  public static makeAnswerFromJson(parsedAnswer: any): Answer {
    return new Answer(
      parsedAnswer.id,
      parsedAnswer.user.id,
      parsedAnswer.user.username,
      parsedAnswer.votes,
      parsedAnswer.timestamp,
      parsedAnswer.html,
      parsedAnswer.question,
      parsedAnswer.can_vote == 1
    );
  }
}




