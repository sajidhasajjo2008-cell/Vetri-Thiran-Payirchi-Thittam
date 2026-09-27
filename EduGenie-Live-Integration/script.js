async function askQuestion() {
    const question = document.getElementById("question").value;
    const task = document.getElementById("task").value;
    const result = document.getElementById("result");

    if (question.trim() === "") {
        result.innerText = "Please enter a question.";
        return;
    }

    result.innerText = "EduGenie is processing your request...";

    try {
        const response = await fetch("http://127.0.0.1:8000/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                task: task
            })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        result.innerText = data.answer;

    } catch (error) {
        result.innerText =
            "Error connecting to the EduGenie server.";
    }
}