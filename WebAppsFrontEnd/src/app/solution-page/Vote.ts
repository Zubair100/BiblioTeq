
export interface Vote {
  toUri(): string;
}

export class UpVote implements Vote {
  toUri(): string {
    return 'upvote';
  }
}

export class DownVote implements Vote {
  toUri(): string {
    return 'downvote';
  }
}
