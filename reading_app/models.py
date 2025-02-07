from django.db import models

# Create your models here.

class Student(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    level = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Question(models.Model):
    text = models.TextField()
    level = models.IntegerField()

    def __str__(self):
        return self.text


class Answer(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.student.firstname} to {self.question.text}"