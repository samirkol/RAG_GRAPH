const API_BASE_URL = "http://127.0.0.1:8000";

export async function uploadPdf(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/upload`,
    {
      method: "POST",
      body: formData
    }
  );

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail || "Failed to upload PDF."
    );
  }

  return response.json();
}


export async function askQuestion(question) {
  const response = await fetch(
    `${API_BASE_URL}/ask?question=${encodeURIComponent(question)}`,
    {
      method: "POST"
    }
  );

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail || "Failed to get answer."
    );
  }

  return response.json();
}