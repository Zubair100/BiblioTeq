from collections import OrderedDict
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import Paper, Question, Answer, Comment, PaperTitle
from api.serializers import QuestionSerializer, AnswerSerializer, CommentSerializer

# This User info is reserved during testing
_TEST_USER_ID       = 200000
_TEST_USER_USERNAME = '__test_username_'
_TEST_USER_PASSWORD = '__test_password_'

# The test user, initialised in setUpModule()
_test_user = None


# Add _test_user to db.
def setUpModule():
    global _test_user
    _test_user = User.objects.create_user(
        id=_TEST_USER_ID,
        username=_TEST_USER_USERNAME,
        password=_TEST_USER_PASSWORD
    )


# Remove _test_user from db.
def tearDownModule():
    _test_user.delete()


# Forces authentication for the client using the _test_user
class AuthAPITestCase(APITestCase):
    def setUp(self):
        self.client.force_login(user=_test_user)

    def tearDown(self):
        self.client.logout()


class RetrievePdfFromDBTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(RetrievePdfFromDBTestCase, cls).setUpTestData()
        t = PaperTitle.objects.create(title="__TEST__")
        Paper.objects.create(course="C212", year=2016, title=t)

    def test_c212_2016_exists(self):
        try:
            Paper.objects.get(course="C212", year=2016)
        except Paper.DoesNotExist:
            self.fail("Calling get() on Paper.objects with course=C212 and year=2016 raised DoesNotExist exception")


class CorrectlySerializesQuestions(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(CorrectlySerializesQuestions, cls).setUpTestData()

        t = PaperTitle.objects.create(title="__TEST__")

        p = Paper.objects.create(course="C212", year=2016, title=t)
        for x in range(1, 5):
            Question.objects.create(number=str(x), paper=p)

        p2 = Paper.objects.create(course="C212", year=2015, title=t)
        for x in range(1, 5):
            Question.objects.create(number=str(x) + "ai", paper=p2)

    def test_serializer1(self):
        paper = Paper.objects.get(course="C212", year=2016)
        questions = Question.objects.filter(paper=paper)

        # Serialise into (question id, question number)
        serializer = QuestionSerializer(questions, many=True)
        self.assertEqual(serializer.data, [
                OrderedDict([('id', 1), ('number', '1')]),
                OrderedDict([('id', 2), ('number', '2')]),
                OrderedDict([('id', 3), ('number', '3')]),
                OrderedDict([('id', 4), ('number', '4')])
        ])

    def test_serializer2(self):
        paper = Paper.objects.get(course="C212", year=2015)
        questions = Question.objects.filter(paper=paper)

        # Serialise into (question id, question number)
        serializer = QuestionSerializer(questions, many=True)
        self.assertEqual(serializer.data, [
                OrderedDict([('id', 5), ('number', '1ai')]),
                OrderedDict([('id', 6), ('number', '2ai')]),
                OrderedDict([('id', 7), ('number', '3ai')]),
                OrderedDict([('id', 8), ('number', '4ai')])
        ])


class ValidateGetRequests(AuthAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super(ValidateGetRequests, cls).setUpTestData()

        # Create dummy PaperTitle
        t = PaperTitle.objects.create(title="__TEST__")

        # Create dummy paper
        p = Paper.objects.create(course="C141", year=2015, title=t)

        # Create dummy questions
        qs = []
        for i in range(0, 4):
            q = Question.objects.create(id=i, number=str(i), paper=p)
            qs.insert(i, q)

        # Create dummy users
        us = []
        for i in range(0, 4):
            u = User.objects.create_user(
                    id=i,
                    username="user_" + str(i),
                    password="password_" + str(i)
            )
            us.insert(i, u)

        # Create dummy answers
        k = 0
        ans = []
        for i in range(0, 4):
            for j in range(0, 4):
                user_voted = []
                if j % 2 == 0:
                    user_voted.append(j)
                a = Answer.objects.create(
                        id=k,
                        question=qs[i],
                        user=us[j],
                        user_voted=str(user_voted),
                        html="<p> This is a dummy answer <\p>"
                )
                k += 1
                ans.insert(k, a)

        # Create dummy comments
        k = 0
        cs = []
        for i in range(0, 4):
            for j in range(0, 4):
                parent = None
                if j > 1:
                    parent = cs[j - 1]

                c = Comment.objects.create(
                        id=k,
                        answer=ans[i],
                        user=us[j],
                        parent=parent,
                        html="<p> This is a dummy comment <\p>"
                )

                k += 1
                cs.insert(k, c)

    def test_get_questions_correctly(self):
        P_COURSE = 'C141'
        P_YEAR = '2015'

        response = self.client.get('/api/' + P_COURSE + '/' + P_YEAR + '/questions')

        # Test GET response OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Test response data can be serialized
        serializer = QuestionSerializer(data=data, many=True)
        self.assertTrue(serializer.is_valid(), msg=str(serializer.errors))

        # Test response data correct
        for i in range(0, 4):
            self.assertEquals(data[i]['id'], i)
            self.assertEquals(data[i]['number'], str(i))

    def test_get_answers_correctly(self):
        Q_ID = 3
        response = self.client.get('/api/' + str(Q_ID) + '/answer')

        # Test response says GET request succeeded.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test response data can be serialized.
        serializer = AnswerSerializer(data=response.data, many=True)
        self.assertTrue(serializer.is_valid(), msg=str(serializer.errors))

        # Test response data is correct.
        for i in range(0, 4):
            data = response.data[i]
            r_user_id = data['user']['id']
            self.assertEqual(data['id'], Q_ID * 4 + i)
            self.assertEqual(data['question'], Q_ID)
            self.assertEqual(data['user']['id'], i)
            self.assertEqual(data['user']['username'], "user_" + str(i))
            self.assertEqual(data['votes'], 0)
            self.assertEqual(data['html'], "<p> This is a dummy answer <\p>")

    def test_correct_user_can_vote(self):
        Q_ID = 3

        client = APIClient()
        url = '/api/' + str(Q_ID) + '/answer/'

        for i in range(0, 4):
            # Login to client and make request
            u = User.objects.get(username="user_" + str(i))
            assert u.id == i
            client.force_login(user=u)
            response = client.get(url)

            self.assertEqual(response.data[i]['can_vote'], int(not (u.id % 2 == 0)))

    def test_get_comments_correctly(self):
        A_ID = 2

        response = self.client.get('/api/' + str(A_ID) + '/comment')

        # Test response says GET request succeeded.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test response data can be serialized.
        serializer = CommentSerializer(data=response.data, many=True)
        self.assertTrue(serializer.is_valid(), msg=str(serializer.errors))

        # Test response data is correct.
        for i in range(0, 4):
            data = response.data[i]

            parent_id = None
            if i > 1:
                parent_id = i - 1

            self.assertEqual(data['id'], A_ID * 4 + i)
            self.assertEqual(data['answer'], A_ID)
            self.assertEqual(data['user']['id'], i)
            self.assertEqual(data['user']['username'], "user_" + str(i))
            self.assertEqual(data['parent'], parent_id)
            self.assertEqual(data['html'], "<p> This is a dummy comment <\p>")


class RetrievingQuestionsOfNonExistentPaperReturns404(AuthAPITestCase):
    def test_bad_paper_returns_404(self):
        response = self.client.get('/api/C212/2015')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class ValidURLsAreRecognised(TestCase):
    def test_comment_url(self):
        resolver = resolve('/api/25/comment')
        self.assertEqual(resolver.view_name, 'api.views.Comments')

    def test_answer_url(self):
        resolver = resolve('/api/25/answer')
        self.assertEqual(resolver.view_name, 'api.views.Answers')

    def test_comment_resource_url(self):
        resolver = resolve('/api/23/img1.jpg/comments')
        self.assertEqual(resolver.view_name, 'api.views.CommentResource')

    def test_answer_resource_url(self):
        resolver = resolve('/api/23/img1.jpg/answers')
        self.assertEqual(resolver.view_name, 'api.views.AnswerResource')

    def test_put_answer_url(self):
        resolver = resolve("/api/submit/answer/")
        self.assertEqual(resolver.view_name, 'api.views.Answers')

    def test_put_comment_url(self):
        resolver = resolve("/api/submit/comment")
        self.assertEqual(resolver.view_name, 'api.views.Comments')

    def test_register_users_student(self):
        resolver = resolve("/api/register/student")
        self.assertEqual(resolver.view_name, 'api.views.RegStudent')

    def test_register_users_staff(self):
        resolver = resolve("/api/register/staff")
        self.assertEqual(resolver.view_name, 'api.views.RegStaff')


class RetrievesAnswersFromDatabase(TestCase):
    q = None

    @classmethod
    def setUpTestData(cls):
        super(RetrievesAnswersFromDatabase, cls).setUpTestData()

        # Create dummy PaperTitle
        t = PaperTitle.objects.create(title="__TEST__")

        u = User.objects.create_user(username="shiraz", password="butt")
        p = Paper.objects.create(course="C212", year="2016", title=t)
        q = Question.objects.create(paper=p, number="1ai")
        for i in range(0, 5):
            Answer.objects.create(id=i, question=q, user=u, votes=12, timestamp=datetime.now(), html="<p> Hi </p>")

    def test_gets_all_answers_from_database(self):
        answers = Answer.objects.filter(question=self.q)

        for i, answer in enumerate(answers):
            self.assertEqual(i, answer.id)


class RetrievesCommentsFromDatabase(TestCase):
    a = None

    @classmethod
    def setUpTestData(cls):
        super(RetrievesCommentsFromDatabase, cls).setUpTestData()

        t = PaperTitle.objects.create(title="__TEST__")
        u = User.objects.create_user(username="shiraz", password="butt")
        p = Paper.objects.create(course="C212", year="2016", title=t)
        q = Question.objects.create(paper=p, number="1ai")
        RetrievesCommentsFromDatabase.a = Answer.objects.create(
                id=1,
                question=q,
                user=u,
                votes=12,
                timestamp=datetime.now(),
                html="<p> Hi </p>"
        )

        for i in range(0, 5):
            Comment.objects.create(
                    id=i,
                    user=u, answer=RetrievesCommentsFromDatabase.a,
                    timestamp=datetime.now(),
                    html="<p> This is comment " + str(i) + " </p>"
            )

    def test_gets_all_comments_from_database(self):
        comments = Comment.objects.filter(answer=RetrievesCommentsFromDatabase.a)

        for i, comment in enumerate(comments):
            self.assertEqual(i, comment.id)


class SubmitToDatabase(AuthAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super(SubmitToDatabase, cls).setUpTestData()

        # Create dummy PaperTitle
        t = PaperTitle.objects.create(title="__TEST__")

        # Create dummy papers
        p = Paper.objects.create(course="C141", year=2015, title=t)
        p2 = Paper.objects.create(course="C141", year=2010, title=t)

        # Create dummy questions
        qs = []
        for i in range(1, 4):
            q = Question.objects.create(id=i, number=str(i), paper=p)
            qs.insert(i, q)

        # Create dummy users
        us = []
        for i in range(1, 4):
            u = User.objects.create_user(
                    id=i,
                    username="user_" + str(i),
                    password="password_" + str(i)
            )
            us.insert(i, u)

        # Create dummy answers
        for i in range(1, 5):
            a = Answer.objects.create(
                    id=i,
                    question=qs[1],
                    user=us[1],
                    html="<p> This is a dummy answer <\p>"
            )

    def test_new_answer_inserted_correctly(self):
        Q_ID = 1
        U_ID = 3
        U_NAME = "user_" + str(U_ID)
        A_HTML = '<p> Hello! This is a test. </p>'

        url = '/api/submit/answer/'
        data = {
                'question': str(Q_ID),
                'user': {'id': U_ID, 'username': U_NAME},
                'html': A_HTML
        }
        response = self.client.post(url, data, format='json')

        # Test response says answer created successfully.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test response data can be serialized.
        serializer = AnswerSerializer(data=response.data)
        self.assertTrue(serializer.is_valid(), msg=str(serializer.errors))

        # Test response data is correct.
        self.assertEqual(response.data['id'], 5)
        self.assertEqual(response.data['question'], Q_ID)
        self.assertEqual(response.data['user']['id'], U_ID)
        self.assertEqual(response.data['user']['username'], U_NAME)
        self.assertEqual(response.data['votes'], 0)
        self.assertEqual(response.data['html'], A_HTML)

    def test_new_comment_inserted_correctly(self):
        U_ID = 3
        U_NAME = "user_" + str(U_ID)
        A_ID = 4
        C_HTML = "<p> Test insert comment. </p>"

        url = '/api/submit/comment/'
        data = {
                'user': {'id': U_ID, 'username': U_NAME},
                'answer': str(A_ID),
                'html': C_HTML
        }
        response = self.client.post(url, data, format='json')

        # Test response says comment created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test response data can be serialized.
        serializer = CommentSerializer(data=response.data)
        self.assertTrue(serializer.is_valid(), msg=str(serializer.errors))

        # Test response data is correct.
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['user']['id'], U_ID)
        self.assertEqual(response.data['user']['username'], U_NAME)
        self.assertEqual(response.data['answer'], A_ID)
        self.assertEqual(response.data['html'], C_HTML)

    def test_new_questions(self):
        P_ID = 1
        url = '/api/submit/' + str(P_ID) + '/questions'
        data = [
            {"number": "1a"},
            {"number": "1b"},
            {"number": "2ai"},
            {"number": "2aii"},
            {"number": "2b"}
        ]

        response = self.client.post(url, data, format='json')

        # Test status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test response data valid
        serializer = QuestionSerializer(data=response.data, many=True,
                                        context={'paper_id': P_ID})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)

        # Test response data correct
        self.assertEqual(response.data[0]['number'], "1a")
        self.assertEqual(response.data[1]['number'], "1b")
        self.assertEqual(response.data[2]['number'], "2ai")
        self.assertEqual(response.data[3]['number'], "2aii")
        self.assertEqual(response.data[4]['number'], "2b")

    def test_cannot_insert_duplicate_questions(self):
        P_ID = 2
        url = '/api/submit/' + str(P_ID) + '/questions/'
        data = [
            {"number": "2b"},
            {"number": "2c"}
        ]

        response = self.client.post(url, data, format='json')

        # Test status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Send same post again
        response = self.client.post(url, data, format='json')

        # Test failed this time
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateDatabase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(UpdateDatabase, cls).setUpTestData()

        # Create dummy PaperTitle
        t = PaperTitle.objects.create(title="__TEST__")

        # Create dummy paper
        p = Paper.objects.create(course="C141", year=2015, title=t)

        # Create dummy questions
        qs = []
        for i in range(1, 5):
            q = Question.objects.create(id=i, number=str(i), paper=p)
            qs.insert(i, q)

        # Create dummy users
        us = []
        for i in range(1, 5):
            u = User.objects.create_user(
                    id=i,
                    username="user_" + str(i),
                    password="password_" + str(i)
            )
            us.insert(i, u)

        # Create dummy answers
        ans = []
        k = 0
        for i in range(0, 4):
            for j in range(0, 4):
                a = Answer.objects.create(
                        question=qs[i],
                        user=us[j],
                        html="<p> This is a dummy answer <\p>"
                )
                ans.insert(k, a)
                k += 1

        # Create dummy comments
        k = 0
        cs = []
        for i in range(0, 4):
            for j in range(0, 4):
                parent = None
                if j > 0:
                    parent = cs[j - 1]

                c = Comment.objects.create(
                        id=k,
                        answer=ans[i],
                        user=us[j],
                        parent=parent,
                        html="<p> This is a dummy comment <\p>"
                )

                k += 1
                cs.insert(k, c)

    def test_partial_update_answer(self):
        A_ID = 8
        Q_ID = 2
        U_ID = 4
        U_NAME = "user_" + str(U_ID)
        U_PASS = "password_" + str(U_ID)
        A_VOTES = 10
        A_HTML = '<p> Updated answer. </p>'

        url = '/api/update/answer'
        data = {
                'id': A_ID,
                'votes': A_VOTES,
                'html': A_HTML
        }

        # Test login
        success = self.client.login(username=U_NAME, password=U_PASS)
        self.assertTrue(success)

        # Perform update
        response = self.client.post(url, data, format='json')

        # Test status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test can be serialized.
        serializer = AnswerSerializer(data=response.data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)

        # Test response data
        self.assertEqual(response.data['id'], A_ID)
        self.assertEqual(response.data['question'], Q_ID)
        self.assertEqual(response.data['user']['id'], U_ID)
        self.assertEqual(response.data['user']['username'], U_NAME)
        self.assertEqual(response.data['votes'], A_VOTES)
        self.assertEqual(response.data['html'], A_HTML)

    def test_partial_update_comment(self):
        C_ID = 10
        C_HTML = "<p> Updated comment. </p>"
        U_ID = 3
        U_NAME = "user_" + str(U_ID)
        U_PASS = "password_" + str(U_ID)
        A_ID = 3
        C_PAR = 1

        url = '/api/update/comment/'
        data = {
            'id': C_ID,
            'html': C_HTML
        }

        # Test login.
        success = self.client.login(username=U_NAME, password=U_PASS)
        self.assertTrue(success)

        # Perform update.
        response = self.client.post(url, data, format='json')

        # Test status code.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test response data can be serialized.
        serializer = CommentSerializer(data=response.data)
        self.assertTrue(serializer.is_valid(), msg=str(serializer.errors))

        # Test response data is correct.
        self.assertEqual(response.data['id'], C_ID)
        self.assertEqual(response.data['user']['id'], U_ID)
        self.assertEqual(response.data['user']['username'], U_NAME)
        self.assertEqual(response.data['answer'], A_ID)
        self.assertEqual(response.data['parent'], C_PAR)
        self.assertEqual(response.data['html'], C_HTML)


class Voting(AuthAPITestCase):
    u = None

    @classmethod
    def setUpTestData(cls):
        super(Voting, cls).setUpTestData()

        # Create dummy PaperTitle
        t = PaperTitle.objects.create(title="__TEST__")

        # Create dummy paper
        p = Paper.objects.create(course="C141", year=2015, title=t)

        # Create dummy questions
        qs = []
        for i in range(1, 5):
            q = Question.objects.create(id=i, number=str(i), paper=p)
            qs.insert(i, q)

        # Create dummy users
        cls.u = User.objects.create_user(
                username="user",
                password="password"
        )

        # Create dummy answers
        a = Answer.objects.create(
                question=qs[3],
                user=cls.u,
                html="<p> This is a dummy answer </p>"
        )

        a = Answer.objects.create(
                question=qs[2],
                user=_test_user,
                votes=5,
                user_voted="[" + str(cls.u.id) + "]",
                html="<p> This is a dummy answer </p>"
        )

        a = Answer.objects.create(
                question=qs[2],
                user=cls.u,
                votes=5,
                html="<p> This is a dummy answer </p>"
        )

    def test_upvote_answer(self):
        url = '/api/upvote/1'
        response = self.client.post(url, {})

        # Test status code
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Test votes have increased
        self.assertEquals(response.data['votes'], 1)

    def test_downvote_answer(self):
        self.client = APIClient()
        self.client.force_login(user=Voting.u)

        url = '/api/downvote/2/'
        response = self.client.post(url, {})

        # Test status code
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Test votes have increased
        self.assertEquals(response.data['votes'], 4)

    def test_cant_vote_twice(self):
        url = '/api/upvote/3/'
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




class EditPermissions(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(EditPermissions, cls).setUpTestData()

        # Create dummy PaperTitle
        t = PaperTitle.objects.create(title="__TEST__")

        # Create dummy paper
        p = Paper.objects.create(course="C356", year=2013, title=t)

        # Create dummy questions
        qs = []
        for i in range(1, 5):
            q = Question.objects.create(id=i, number=str(i), paper=p)
            qs.insert(i, q)

        # Create dummy users
        us = []
        for i in range(1, 5):
            u = User.objects.create_user(
                    id=i,
                    username="user_" + str(i),
                    password="password_" + str(i)
            )
            us.insert(i, u)

        # Create dummy answer
        a = Answer.objects.create(
                question=qs[3],
                user=us[2],
                html="<p> This is a dummy answer. </p>"
        )

        # Create dummy comment
        c = Comment.objects.create(
                answer=a,
                user=us[3],
                html="<p> This is a dummy comment. </p>"
        )

    def test_owner_can_edit_answer(self):
        A_ID = 1
        A_HTML = "<p> Updated answer. </p>"
        U_ID = 3
        U_NAME = "user_" + str(U_ID)
        U_PASS = "password_" + str(U_ID)

        url = '/api/update/answer/'
        data = {
            'id': A_ID,
            'html': A_HTML
        }

        # Test login.
        success = self.client.login(username=U_NAME, password=U_PASS)
        self.assertTrue(success)

        # Perform update.
        response = self.client.post(url, data, format='json')

        # Test status code.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_edit_not_your_comment(self):
        A_ID = 1
        A_HTML = "<p> Updated comment. </p>"
        U_ID = 1
        U_NAME = "user_" + str(U_ID)
        U_PASS = "password_" + str(U_ID)

        url = '/api/update/comment/'
        data = {
            'id': A_ID,
            'html': A_HTML
        }

        # Test login.
        success = self.client.login(username=U_NAME, password=U_PASS)
        self.assertTrue(success)

        # Perform update.
        response = self.client.post(url, data, format='json')

        # Test status code.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestRegisterUser(APITestCase):

    def test_register_user_student(self):
        url = '/api/register/student'

        data = {
            'username': "zubair",
            'password': "zubair"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['privilege'], 0)

    def test_register_user_staff(self):
        url = '/api/register/staff'

        data = {
            'username': "zubair_staff",
            'password': "zubair_staff"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['privilege'], 1)
