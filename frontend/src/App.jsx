import { useState } from "react";
import { uploadPdf, askQuestion } from "./services/api";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");

  const [uploadResult, setUploadResult] = useState(null);
  const [answerResult, setAnswerResult] = useState(null);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  const [error, setError] = useState("");

  // ----------------------------------
  // Upload PDF
  // ----------------------------------

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF file first.");
      return;
    }

    try {
      setError("");
      setUploading(true);

      const result = await uploadPdf(file);

      setUploadResult(result);

      // Clear old answer after a new upload
      setAnswerResult(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  // ----------------------------------
  // Ask Question
  // ----------------------------------

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    try {
      setError("");
      setAsking(true);

      const result = await askQuestion(question);

      setAnswerResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  };

  // ----------------------------------
  // Clear answer
  // ----------------------------------

  const handleClearAnswer = () => {
    setAnswerResult(null);
    setError("");
  };

  return (
    <div className="app-container">
      {/* -------------------------------- */}
      {/* Header */}
      {/* -------------------------------- */}

      <header className="app-header">
        <div className="header-badge">
          HYBRID RAG DEMO
        </div>

        <h1>Supplier Hybrid AI Assistant</h1>

        <p>
          Vector Search + Knowledge Graph + GPT
        </p>
      </header>

      {/* -------------------------------- */}
      {/* Error */}
      {/* -------------------------------- */}

      {error && (
        <div className="error-box">
          <strong>Error</strong>
          <span>{error}</span>
        </div>
      )}

      {/* -------------------------------- */}
      {/* Upload */}
      {/* -------------------------------- */}

      <section className="card">
        <div className="section-number">01</div>

        <h2>Upload Supplier Policy</h2>

        <p className="section-description">
          Upload a PDF to index its content into the
          vector store and knowledge graph.
        </p>

        <div className="upload-row">
          <input
            type="file"
            accept=".pdf"
            onChange={(event) => {
              setFile(event.target.files[0]);
              setError("");
            }}
          />

          <button
            className="primary-button"
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading ? "Indexing..." : "Upload & Index"}
          </button>
        </div>

        {uploadResult && (
          <div className="success-box">
            <div className="success-title">
              Document processed successfully
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">
                  Document
                </span>

                <strong className="stat-value document-value">
                  {uploadResult.filename}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Pages
                </span>

                <strong className="stat-value">
                  {uploadResult.pages ?? "-"}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Chunks
                </span>

                <strong className="stat-value">
                  {uploadResult.chunks ?? "-"}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Graph Nodes
                </span>

                <strong className="stat-value">
                  {uploadResult.graph_nodes ?? "-"}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">
                  Graph Edges
                </span>

                <strong className="stat-value">
                  {uploadResult.graph_edges ?? "-"}
                </strong>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* -------------------------------- */}
      {/* Ask Question */}
      {/* -------------------------------- */}

      <section className="card">
        <div className="section-number">02</div>

        <h2>Ask a Question</h2>

        <p className="section-description">
          Ask questions about the supplier policies
          that have been indexed.
        </p>

        <textarea
          value={question}
          onChange={(event) => {
            setQuestion(event.target.value);
            setError("");
          }}
          placeholder="Example: What happens to non-compliant invoices?"
          rows={5}
        />

        <div className="question-actions">
          <button
            className="primary-button"
            onClick={handleAskQuestion}
            disabled={asking}
          >
            {asking ? "Retrieving..." : "Ask Question"}
          </button>

          {answerResult && (
            <button
              className="secondary-button"
              onClick={handleClearAnswer}
            >
              Clear Answer
            </button>
          )}
        </div>
      </section>

      {/* -------------------------------- */}
      {/* Results */}
      {/* -------------------------------- */}

      {answerResult && (
        <section className="card results-card">
          <div className="section-number">03</div>

          <h2>Answer & Retrieval Evidence</h2>

          {/* -------------------------------- */}
          {/* Answer */}
          {/* -------------------------------- */}

          <div className="answer-box">
            <div className="result-label">
              ANSWER
            </div>

            <p className="answer-text">
              {answerResult.answer}
            </p>
          </div>

          {/* -------------------------------- */}
          {/* Retrieval Overview */}
          {/* -------------------------------- */}

          <div className="retrieval-overview">
            <div className="result-label">
              RETRIEVAL OVERVIEW
            </div>

            <div className="retrieval-cards">
              <div className="retrieval-card">
                <div className="retrieval-title">
                  Vector Retrieval
                </div>

                <div className="retrieval-value">
                  {answerResult.primary_source
                    ? 1 +
                      (answerResult.supporting_sources
                        ?.length || 0)
                    : 0}
                </div>

                <div className="retrieval-description">
                  Policy chunks
                </div>
              </div>

              <div className="retrieval-card">
                <div className="retrieval-title">
                  Graph Retrieval
                </div>

                <div className="retrieval-value">
                  {answerResult.graph_results?.length || 0}
                </div>

                <div className="retrieval-description">
                  Business relationships
                </div>
              </div>

              <div className="retrieval-card">
                <div className="retrieval-title">
                  Retrieval Mode
                </div>

                <div className="retrieval-value mode-value">
                  {answerResult.graph_results?.length
                    ? "Hybrid"
                    : "Vector"}
                </div>

                <div className="retrieval-description">
                  Vector + Graph
                </div>
              </div>
            </div>
          </div>

          {/* -------------------------------- */}
          {/* Primary Source */}
          {/* -------------------------------- */}

          {answerResult.primary_source && (
            <div className="evidence-section">
              <div className="result-label">
                PRIMARY SOURCE
              </div>

              <div className="source-card primary-source">
                <div className="source-icon">
                  📄
                </div>

                <div className="source-details">
                  <div className="source-document">
                    {answerResult.primary_source.document}
                  </div>

                  <div className="source-page">
                    Page {answerResult.primary_source.page}
                  </div>

                  <div className="source-chunk">
                    {answerResult.primary_source.chunk_id}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* -------------------------------- */}
          {/* Supporting Sources */}
          {/* -------------------------------- */}

          {answerResult.supporting_sources &&
            answerResult.supporting_sources.length > 0 && (
              <div className="evidence-section">
                <div className="result-label">
                  SUPPORTING SOURCES
                </div>

                <div className="source-list">
                  {answerResult.supporting_sources.map(
                    (source, index) => (
                      <div
                        className="source-card"
                        key={`${source.chunk_id}-${index}`}
                      >
                        <div className="source-icon">
                          📄
                        </div>

                        <div className="source-details">
                          <div className="source-document">
                            {source.document}
                          </div>

                          <div className="source-page">
                            Page {source.page}
                          </div>

                          <div className="source-chunk">
                            {source.chunk_id}
                          </div>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

          {/* -------------------------------- */}
          {/* Knowledge Graph */}
          {/* -------------------------------- */}

          {answerResult.graph_results &&
            answerResult.graph_results.length > 0 && (
              <div className="evidence-section graph-section">
                <div className="result-label">
                  KNOWLEDGE GRAPH EVIDENCE
                </div>

                <p className="graph-description">
                  These business relationships were
                  retrieved from the knowledge graph.
                </p>

                <div className="graph-list">
                  {answerResult.graph_results.map(
                    (relationship, index) => (
                      <div
                        className="graph-relationship"
                        key={`${relationship.source}-${relationship.target}-${index}`}
                      >
                        <div className="graph-node">
                          {relationship.source}
                        </div>

                        <div className="graph-connector">
                          <div className="graph-line" />

                          <div className="graph-relation">
                            {relationship.relationship}
                          </div>

                          <div className="graph-arrow">
                            →
                          </div>
                        </div>

                        <div className="graph-node">
                          {relationship.target}
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

          {/* -------------------------------- */}
          {/* No Graph */}
          {/* -------------------------------- */}

          {(!answerResult.graph_results ||
            answerResult.graph_results.length === 0) && (
            <div className="no-graph-box">
              <div className="result-label">
                KNOWLEDGE GRAPH
              </div>

              <p>
                No relevant graph relationship was
                found for this question.
              </p>
            </div>
          )}
        </section>
      )}

      {/* -------------------------------- */}
      {/* Architecture Footer */}
      {/* -------------------------------- */}

      <footer className="architecture-footer">
        <div className="architecture-title">
          Hybrid RAG Pipeline
        </div>

        <div className="architecture-flow">
          <span>Question</span>
          <span>→</span>
          <span>Vector Search</span>
          <span>+</span>
          <span>Graph Search</span>
          <span>→</span>
          <span>GPT</span>
          <span>→</span>
          <span>Grounded Answer</span>
        </div>
      </footer>
    </div>
  );
}

export default App;