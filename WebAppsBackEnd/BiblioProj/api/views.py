from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from api.models import Question, Answer, Paper, Comment, PaperTitle
from api.permissions import IsOwner
from api.serializers import PaperSerializer, QuestionSerializer, \
    AnswerSerializer, CommentSerializer, NewUserSerializer

from django.http import HttpResponse, JsonResponse

from rest_framework import generics, mixins

from rest_framework import status
from rest_framework import permissions

from rest_framework.views import APIView

from django.contrib.auth.models import User

from rest_framework_jwt.settings import api_settings

import os
import os.path

_ANSWERS_RESOURCE_DIR = 'answers'
_COMMENTS_RESOURCE_DIR = 'comments'
_PAST_PAPERS_DIR = 'pastpapers'


class LogInUser(APIView):

    permission_classes = []

    def post(self, request):
        user = get_unique(User, username=request.data['username'])

        if user is None:
            return http_error_not_found(
                    "User: ",  str(request.data['username'])
            )

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        privilege = 0

        if user.is_staff:
            privilege = 1

        return Response({"privilege": privilege, "token": token, "user": {"id": user.id}})


class RegUser(APIView):
    permission_classes = []

    def is_staff(self):
        raise Exception("This should be overridden")

    def post(self, request):

        serializer = NewUserSerializer(data=request.data)

        if serializer.is_valid(raise_exception=False):
            u = User.objects.create_user(username=serializer.data['username'], password=serializer.data['password'],
                                         is_staff=self.is_staff())
            return Response({"id": u.id, "privilege": 1 if u.is_staff else 0})

        return Response(status=status.HTTP_400_BAD_REQUEST)


class RegStaff(RegUser):

    def is_staff(self):
        return True


class RegStudent(RegUser):

    def is_staff(self):
        return False


class PaperPDF(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaperSerializer
    queryset = Paper.objects.all()

    def get(self, request, course_code, year):
        # Get paper from database.
        paper = get_unique(Paper, course=course_code, year=year)
        if paper is None:
            return http_error_not_found(
                    "(Paper, Year)",
                    "(" + course_code + ", " + year + ")"
            )

        # Set the response's fields
        data = {
                'title': paper.title.title,
                'pdf': paper.pdf,
                'paper_id': paper.id
        }

        return Response(data)




class PaperQuestions(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_code, year):
        # Get paper id for (course_code, year).
        paper = get_unique(Paper, course=course_code, year=year)
        if paper is None:
            return http_error_not_found(
                    "(Paper, Year)",
                    "(" + course_code + ", " + year + ")",
                    drf=False
            )

        # Get all questions with that paper id
        questions = Question.objects.filter(paper=paper)

        # Serialise into (question id, question number)
        serializer = QuestionSerializer(questions, many=True)

        return JsonResponse(serializer.data, safe=False)

    def post(self, request, paper_id):
        serializer = QuestionSerializer(data=request.data, many=True,
                                        context={'paper_id': paper_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaperData(mixins.DestroyModelMixin,
                generics.CreateAPIView):

    permission_classes = [permissions.IsAuthenticated]

    # RENAME if we can think of a better name
    def get_related_model(self):
        raise Exception("ERROR: get_related_model(): URLs should point to a subclass of PaperData.")

    def get_related_serialized_data(self, record, user_id):
        raise Exception("ERROR: get_related_serialized_data(): URLs should point to a subclass of PaperData.")

    def get(self, request, id, format=None):
        # Get record
        model = self.get_related_model()
        record = get_unique(model, pk=id)
        if record is None:
            http_error_not_found("Record", id)

        user = get_unique(User, username=request.user)

        # Get corresponding data and serialize and return
        serialized_data = self.get_related_serialized_data(record, user.id)
        return Response(serialized_data)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class Answers(PaperData):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get_related_model(self):
        return Question

    def get_related_serialized_data(self, question, user_id):
        answers = Answer.objects.filter(question=question)
        serializer = AnswerSerializer(answers, many=True, context={"user_id": user_id})
        return serializer.data


class Comments(PaperData):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_related_model(self):
        return Answer

    def get_related_serialized_data(self, answer, user_id):
        comments = Comment.objects.filter(answer=answer)
        serializer = CommentSerializer(comments, many=True)
        return serializer.data


class Resource(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id, resource_name):
        # Construct path to resource
        current_dir = os.path.dirname(os.path.realpath(__file__))
        resource_path = os.path.join(current_dir, self.get_name_of_resource_directory(), id, resource_name)

        try:
            resource = open(resource_path, 'rb')

        except IOError:
            return http_error_not_found(
                    "Looking for resource of something with ID = " + id + ". Resource",
                    resource_name
            )

        with resource:
            return HttpResponse(resource.read(), content_type="image/jpeg")

    def get_name_of_resource_directory(self):
        raise Exception("ERROR: get_name_of_resource_directory(): URLs should point ot subclass of Resource.")


class AnswerResource(Resource):
    def get_name_of_resource_directory(self):
        return _ANSWERS_RESOURCE_DIR


class CommentResource(Resource):
    def get_name_of_resource_directory(self):
        return _COMMENTS_RESOURCE_DIR


class Edit(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get(self, request):
        return HttpResponse("GET not allowed when editing answer", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_model(self):
        raise Exception("ERROR: get_model(): URLs should point to a subclass of Edit.")

    def get_serializer(self):
        raise Exception("ERROR: get_serializer(): URLs should point to a subclass of Edit.")

    def get_name_of_resource_directory(self):
        raise Exception("ERROR: get_name_of_resource_directory(): URLs should point ot subclass of Edit.")

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        model = self.get_model()
        record = get_unique(model, id=data['id'])

        if record is None:
            return Response("Could not find " +
                         self.get_name_of_resource_directory() + " with id: " + str(data['id']), status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request=request, obj=record)

        serializer = self.get_serializer()
        serialized = serializer(record, data=data, partial=True)

        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data)

        return Response("Invalid JSON for edit")


class AnswerEdit(Edit):

    def get_model(self):
        return Answer

    def get_serializer(self):
        return AnswerSerializer

    def get_name_of_resource_directory(self):
        return _ANSWERS_RESOURCE_DIR


class CommentEdit(Edit):

    def get_model(self):
        return Comment

    def get_serializer(self):
        return CommentSerializer

    def get_name_of_resource_directory(self):
        return _COMMENTS_RESOURCE_DIR


class Votes(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, answer_id):
        # Get answer
        answer = get_unique(Answer, pk=answer_id)
        # Get user
        user = get_unique(User, username=request.user)
        if answer is None:
            return http_error_not_found("Answer", answer_id)

        if user is None:
            return http_error_not_found("User", user.id)

        if user == answer.user:
            return Response("Front end should have prevented user + " +
                            str(user.id) + " from voting on their own answer.",
                            status=status.HTTP_400_BAD_REQUEST)

        # Update list of user id's
        import json

        json_dec = json.decoder.JSONDecoder()

        if answer.user_voted == "":
            user_ids = []
        else:
            user_ids = json_dec.decode(answer.user_voted)

        if not self.modify_voting_list(user_id=user.id, user_ids=user_ids):
            return Response(
                   "ERROR: User has already voted",
                    status=status.HTTP_400_BAD_REQUEST
            )

        # Update the list of users who have voted
        answer.user_voted = json.dumps(user_ids)

        # Update votes
        answer.votes = self.updateVotes(answer.votes)

        # Save answer
        answer.full_clean()
        answer.save()

        # Return new votes
        response_data = {'votes': answer.votes}
        return Response(response_data, status=status.HTTP_201_CREATED)

    def updateVotes(self, votes):
        return Response("ERROR: updateVotes(): URLs should point to a "
                        "subclass of Votes.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def modify_voting_list(self, user_ids, user_id):
        return Response("ERROR WRITE A PROPER MESSAGE")


class UpVote(Votes):
    def updateVotes(self, votes):
        return votes + 1

    def modify_voting_list(self, user_ids, user_id):

        if user_id in user_ids:
            return False

        user_ids.append(user_id)

        return True


class DownVote(Votes):
    def updateVotes(self, votes):
        return votes - 1

    def modify_voting_list(self, user_ids, user_id):

        if user_id not in user_ids:
            return False

        user_ids.remove(user_id)

        return True


class AvailablePapers(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        course_year_mappings = {}
        papers = Paper.objects.all()

        for paper in papers:
            course_str = str(paper.course)
            course_data = {}
            course_data.setdefault("Years", [])
            course_data.setdefault("Name", paper.title.title)
            course_data.setdefault("paper_id", paper.id)
            course_year_mappings.setdefault(course_str, course_data)

        for paper in papers:
            course_str = str(paper.course)
            course_year_mappings[course_str]['Years'].append(paper.year)

        return Response(course_year_mappings)


# Gets the instance of the model from that database that uniquely has the given
# kwargs. If such an object does not exist, returns None.
def get_unique(model, **kwargs):
    # Get paper id for (course_code, year).
    try:
        return model.objects.get(**kwargs)

    except model.DoesNotExist:
        return None


# 404 not found HttpResonse for given model.
def http_error_not_found(model_name, id, drf=True):
    if drf:
        return Response(
            "Error: " + model_name + " with ID = " + id + " not found.",
            status=status.HTTP_404_NOT_FOUND
        )
    else:
        return HttpResponse(
            "Error: " + model_name + " with ID = " + id + " not found.",
            status=status.HTTP_404_NOT_FOUND
        )
