import { BiblioFrontendPage } from './app.po';

describe('biblio-frontend App', () => {
  let page: BiblioFrontendPage;

  beforeEach(() => {
    page = new BiblioFrontendPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
