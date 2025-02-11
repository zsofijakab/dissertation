from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template import loader
from .models import Student
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import resolve
import anthropic
import os

shared_context = {
    "variable": "",
    "interest": "",
}

# Get the API key from environment variables
api_key = os.getenv('CLAUDE_API_KEY')

# Ensure the key exists
if not api_key:
    raise ValueError("CLAUDE_API_KEY environment variable is not set.")

client = anthropic.Anthropic(api_key=api_key)


def main(request):
    global shared_context
    if request.method == "POST":
        # Update the VARIABLE field (teacher input)
        shared_context["variable"] = request.POST.get("variable")

    return render(request, "template.html", {"variable": shared_context["variable"]})

def students(request):
    print(resolve(request.path_info))
    global shared_context
    story = None
    questions = None

    if request.method == "POST":
        # Update the INTEREST field (student input)
        shared_context["interest"] = request.POST.get("interest")

        # Prepare the prompts based on the shared context
        system_prompt = (
            "You are an AI assistant with a passion for creative writing and storytelling. "
            "Your task is to create engaging stories, offering imaginative plot twists and dynamic "
            "character development with the aim of bettering children’s literacy. The teacher wants students "
            f"to read about {shared_context['variable']}. Take the student’s interest into account when creating a story. "
            "After creating the story, also generate questions that can be used to analyze the student’s understanding "
            "of the story. These questions should include those that can be answered in the text, questions requiring causal "
            "inference within seperate parts of the text, and questions linking to past experiences or the real world."
            "Once the story is finished, before listing the questions, state Questions: and then list the questions, separated by a new line."
        )

        user_prompt = f"The student is interested in reading about {shared_context['interest']}"

        # Call the Anthropic Messages API to generate the story and questions
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Use a valid Claude model
            max_tokens=4000,
            temperature=1,
            system=system_prompt,  # Provide the system prompt here
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )


        # Parse the response
        print(response.content[0].text)
        print(response.content[0])
        print(response)
        ai_output = response.content[0].text
        if ai_output:
            # Assuming the response contains story and questions separated by a delimiter
            try:
                story, questions_raw = ai_output.split("Questions:")
                questions = [q.strip() for q in questions_raw.split("\n") if q.strip()]
            except ValueError:
                story = ai_output
                questions = []

    return render(
        request,
        "all_students.html",
        {"interest": shared_context["interest"], "story": story, "questions": questions},
    )

def evaluate_answers(request):
    if request.method == "POST":
        # Extract the story, questions, and answers
        story = request.POST.get("story")
        questions_and_answers = []

        for key, value in request.POST.items():
            if key.startswith("answers_"):
                question_key = key.replace("answers_", "questions_")
                question = request.POST.get(question_key)
                answer = value
                if question and answer:
                    questions_and_answers.append({"question": question, "answer": answer})

        # Prepare the prompt for the Anthropic API
        system_prompt = (
            "You are an AI assistant responsible for evaluating the correctness of student answers. "
            "Use the provided story as the reference to evaluate each answer. Respond with either 'Correct' or "
            "'Incorrect'. If it is incorrect, help the student find where in the story (which paragraph or sentence)"
            "they would find the correct answer. Do not give away why the answer is incorrect and what the correct answer is,"
            "simply suggest to the reader where in the story to check again."
        )

        user_prompt = f"The story is:\n{story}\n\nEvaluate the following questions and answers:\n\n"
        for qa in questions_and_answers:
            user_prompt += f"Question: {qa['question']}\nAnswer: {qa['answer']}\n\n"

        # Call the Anthropic API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Use a valid Claude model
            max_tokens=2000,
            temperature=1,
            system=system_prompt,  # Provide the system prompt here
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )

        # Parse the API response
        evaluation = response.content[0].text.strip()

        print(response)

        # Render the results to a new template
        return render(
            request,
            "evaluation_results.html",
            {
                "story": story,
                "questions_and_answers": questions_and_answers,
                "evaluation": evaluation,
            },
        )

    return HttpResponse("Invalid request", status=400)


@ensure_csrf_cookie
def test_csrf(request):
    return JsonResponse({'success': 'CSRF cookie is set'})
