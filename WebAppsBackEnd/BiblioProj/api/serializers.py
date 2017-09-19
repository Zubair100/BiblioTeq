from django.contrib.auth.models import User
from rest_framework import serializers
import json
from rest_framework.exceptions import ValidationError
from api.models import Paper, Question, Comment, Answer, PaperTitle, \
    MAX_TITLE_LENGTH


# NOTE: Currently no update or delete Paper
# TODO: On POST, make title field of JSON be the title, not 'PaperTitle object'.
class PaperSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=MAX_TITLE_LENGTH)

    class Meta:
        model = Paper
        fields = '__all__'

    def create(self, validated_data):
        course = validated_data['course']
        title = validated_data['title']
        year = validated_data['year']

        papers_of_that_course = Paper.objects.filter(course=course)
        paper_title = None

        # Use existing title if papers of that course exist
        if papers_of_that_course.exists():
            # Check no paper of that year
            if papers_of_that_course.filter(year=year).exists():
                raise ValidationError(
                        "Paper with course code = " + course + " and "
                        "year " + str(year) + " already exists."
                )

            # Check title matches the title of existing papers of the same course.
            paper_title = papers_of_that_course.first().title
            correct_title = paper_title.title
            if title != correct_title:
                raise ValidationError(
                        "Papers with course code " + course + " appear to have "
                        "title \"" + correct_title + "\", not \"" + title + "\""
                        ". Contact an administrator if you think this is "
                        "incorrect.")

        # Else, create a new title in the database
        else:
            paper_title = PaperTitle.objects.create(title=title)

        # Create new Paper object
        validated_data['title'] = paper_title
        return Paper.objects.create(**validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'number',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        # Get paper
        paper = Paper.objects.get(pk=self.context['paper_id'])

        # Fail if paper does not exist
        if paper is None:
            raise ValidationError("Creating question for paper that does not "
                                  "exist: " + str(self.context['paper_id']))

        # Paper valid, set it
        validated_data['paper'] = paper

        # Fail if (paper, number) pair already exists
        number = validated_data['number']
        questions = Question.objects.filter(paper=paper, number=number)
        if questions.exists():
            raise ValidationError("Question number \'" + number + "\' of "
                                  "paper \'" + str(paper.id) + "\' already "
                                  "exists.")

        return Question.objects.create(**validated_data)


class NewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')


class OtherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)

    def to_internal_value(self, data):
        u = User.objects.filter(pk=data['id'])
        if not u.exists():
            raise serializers.ValidationError("Attempting to submit response "
                                              "with user ID that does not "
                                              "exist. ID = " + str(id))
        return u


class AnswerSerializer(serializers.ModelSerializer):
    cannot_update_fields = ['user', 'question', 'timestamp']
    user = OtherUserSerializer(required=True)
    can_vote = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        fields = ('id', 'user', 'votes', 'timestamp', 'html', 'can_vote', 'question')
        read_only_fields = ('can_vote',)

    def get_can_vote(self, answer):
        NOT_APPLICABLE = -1
        CAN_VOTE = 1
        CANT_VOTE = 0

        if 'user_id' not in self.context.keys():
            return NOT_APPLICABLE

        user_id = self.context['user_id']

        json_dec = json.decoder.JSONDecoder()
        user_ids = [] if answer.user_voted == "" else json_dec.decode(answer.user_voted)

        return CANT_VOTE if user_id in user_ids else CAN_VOTE

    def create(self, validated_data):
        # Can this ever be None?
        validated_data['user'] = validated_data['user'].first()
        assert validated_data['user'] is not None
        return Answer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user_data = get_validated_user_data(validated_data)

        for field_name in AnswerSerializer.cannot_update_fields:
            if validated_data.get(field_name) is not None:
                raise ValidationError(err_msg_cannot_update(Answer, field_name))

        instance.user = user_data.get('id', instance.user)
        instance.votes = validated_data.get('votes', instance.votes)
        instance.html = validated_data.get('html', instance.html)
        instance.save()

        return instance


class CommentSerializer(serializers.ModelSerializer):
    cannot_update_fields = ['user', 'answer', 'parent', 'timestamp']
    user = OtherUserSerializer(required=True)

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        # Can this ever be None?
        validated_data['user'] = validated_data['user'].first()
        assert validated_data['user'] is not None
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user_data = get_validated_user_data(validated_data)

        for field_name in AnswerSerializer.cannot_update_fields:
            if validated_data.get(field_name) is not None:
                raise ValidationError(err_msg_cannot_update(Answer, field_name))

        instance.user = user_data.get('id', instance.user)
        instance.html = validated_data.get('html', instance.html)
        instance.save()

        return instance


def get_validated_user_data(validated_data):
    return validated_data.pop('user', {})


def err_msg_cannot_update(model, field_name):
    return "Cannot update field \'" + field_name + "\' of model \'" + model + "\'."