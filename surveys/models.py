from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

from twz_server_django.model_mixins import CreatedModifiedModel


class Survey(CreatedModifiedModel):
    title = models.CharField(max_length=255, null=False, blank=False)
    groups = JSONField(default=[
        {
            "uuid": "4663b60c-9555-4761-a8a4-f8a45dbb46a2",
            "title": "This is a group title",
            "description": "this is a group description, not required.",
            "questions": [
                {
                    "uuid": "77fcb271-8718-413c-8a31-10d7aa0dd960",
                    "question": "This is a boolean question",
                    "type": "radio",
                    "answers": [
                        {
                            "title": "Yes"
                        },
                        {
                            "title": "No"
                        }
                    ]
                },
                {
                    "uuid": "3533584e-cb6e-422f-b2c5-5aadb1887c7b",
                    "question": "This is a multiple choice with other question",
                    "type": "radio-with-other",
                    "answers": [
                        {
                            "title": "Very much"
                        },
                        {
                            "title": "No at all"
                        },
                        {
                            "title": "Impartial"
                        },
                        {
                            "title": "Enter small text here"
                        },
                        {
                            "title": "Other"
                        }
                    ]
                }
            ]
        },
        {
            "uuid": "1a7e7f13-e765-4ae3-9196-63d9e5e40702",
            "title": "This is a group title",
            "description": "this is a group description, not required.",
            "questions": [
                {
                    "uuid": "61fdae77-918c-4f4c-9ae6-0b9800a7a15b",
                    "question": "This is a free form text area question",
                    "type": "longtext",
                    "answers": None
                },
                {
                    "uuid": "a2ebf7aa-f68b-486a-80aa-d054879f0e7d",
                    "question": "What is most the important features to you?",
                    "type": "checkbox",
                    "answers": [
                        {
                            "title": "It works"
                        },
                        {
                            "title": "It is green"
                        },
                        {
                            "title": "Swiping"
                        },
                        {
                            "title": "Social Feed"
                        }
                    ]
                },
                {
                    "uuid": "7be87e2b-4169-46e0-8d4b-2f9ff9f88773",
                    "question": "What is most the important features to you?",
                    "type": "checkbox-with-other",
                    "answers": [
                        {
                            "title": "It works"
                        },
                        {
                            "title": "It is green"
                        },
                        {
                            "title": "Swiping"
                        },
                        {
                            "title": "Social Feed"
                        },
                        {
                            "title": "Other"
                        }
                    ]
                },
                {
                    "uuid": "f72e7a64-f912-4965-b4e3-fda274099571",
                    "question": "How important is getting a job to you?",
                    "type": "scale",
                    "scale": [1, 5],
                    "answers": None
                },
                {
                    "uuid": "0a2eec3b-241b-4b71-a081-5a382af81434",
                    "question": "This is a short text question?",
                    "type": "shorttext",
                    "answers": None
                }
            ]
        }
    ], null=False, blank=False)

    def __str__(self):
        return u"Survey - %s" % self.title


class SurveyResponse(CreatedModifiedModel):
    title = models.CharField(max_length=255, null=False, blank=False)
    survey = models.ForeignKey('surveys.Survey', null=False)
    user = models.ForeignKey('drf_users.User', null=False)
    answer_data = JSONField(default=[], null=False, blank=False)

    def __str__(self):
        return u"%s Response from %s" % (self.survey.title, self.user)
