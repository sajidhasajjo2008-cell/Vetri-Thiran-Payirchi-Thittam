from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

# Actual EduGenie Module functions
from qa import answer_question
from quiz import generate_quiz

app = FastAPI(title="EduGenie Live Integration")


class LearningRequest(BaseModel):
    question: str
    task: str


@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/script.js")
def javascript():
    return FileResponse(
        "script.js",
        media_type="application/javascript"
    )


@app.get("/style.css")
def stylesheet():
    return FileResponse(
        "style.css",
        media_type="text/css"
    )


@app.post("/generate")
def generate_response(request: LearningRequest):

    question = request.question.strip()
    task = request.task.strip().lower()

    try:

        # -------------------------------
        # Question & Answer
        # -------------------------------
        if task == "qa":
            answer = answer_question(question)

            return {
                "answer": answer,
                "task": task
            }

        # -------------------------------
        # Quiz Generation
        # -------------------------------
        elif task == "quiz":

            questions = generate_quiz(
                passage=question,
                number_of_questions=3
            )

            return {
                "answer": questions,
                "task": task
            }

        # -------------------------------
        # Other tasks
        # -------------------------------
        elif task == "explain":
            answer = (
                "Explanation:\n\n"
                f"{question}\n\n"
                "This topic can be explained using "
                "simple concepts and examples."
            )

        elif task == "summarize":
            answer = (
                "Summary:\n\n"
                f"{question}"
            )

        elif task == "recommendations":
            answer = (
                "Learning Recommendations:\n\n"
                "1. Learn the basic concepts.\n"
                "2. Study examples.\n"
                "3. Practice related questions.\n"
                "4. Take a short quiz."
            )

        else:
            answer = "Please select a valid learning task."

        return {
            "answer": answer,
            "task": task
        }

    except Exception as exc:

        return {
            "answer": f"EduGenie Error: {str(exc)}",
            "task": task
        }