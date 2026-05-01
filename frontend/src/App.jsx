import { useState } from "react"
import axios from "axios"
import DocsView from "./DocsView"

export default function App() {
  const [file, setFile]         = useState(null)
  const [loading, setLoading]   = useState(false)
  const [routes, setRoutes]     = useState(null)
  const [error, setError]       = useState("")
  const [dragging, setDragging] = useState(false)

  function handleFile(f) {
    if (!f) return
    const allowed = [".py", ".js", ".ts", ".zip"]
    const valid = allowed.some(ext => f.name.endsWith(ext))
    if (!valid) {
      setError("Only .py, .js, .ts, or .zip files are supported.")
      return
    }
    setFile(f)
    setError("")
  }

  async function handleGenerate() {
    if (!file) return
    setLoading(true)
    setError("")
    const formData = new FormData()
    formData.append("file", file)
    try {
      const res = await axios.post(
        "https://docforge-api-zk0e.onrender.comgenerate",
        formData
      )
      if (res.data.total === 0) {
        setError("No API routes found. Make sure your file uses FastAPI decorators like @app.get() or Express patterns like app.get().")
        setLoading(false)
        return
      }
      setRoutes(res.data.routes)
    } catch (e) {
      setError("Could not connect to backend. Make sure FastAPI is running on port 8000.")
    }
    setLoading(false)
  }

  if (loading) return (
    <div style={styles.center}>
      <div style={styles.spinner} />
      <h2 style={styles.loadTitle}>Parsing your code...</h2>
      <p style={styles.loadSub}>Extracting routes, types, and building curl commands.</p>
    </div>
  )

  if (routes) return (
    <DocsView routes={routes} onBack={() => { setRoutes(null); setFile(null) }} />
  )

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.h1}>DocForge</h1>
        <p style={styles.sub}>
          Upload a FastAPI or Express codebase and get instant interactive documentation.
        </p>

        <div
          style={{ ...styles.dropzone, borderColor: dragging ? "#111" : "#ddd", background: dragging ? "#f9f9f9" : "white" }}
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]) }}
        >
          <div style={styles.uploadIcon}>↑</div>
          <p style={styles.dropText}>{file ? file.name : "Drag and drop your file here"}</p>
          <p style={styles.dropSub}>{file ? `${(file.size / 1024).toFixed(1)} KB` : "or click to browse"}</p>
          <p style={styles.dropHint}>.py · .js · .ts · .zip</p>
          <input
            type="file"
            accept=".py,.js,.ts,.zip"
            onChange={e => handleFile(e.target.files[0])}
            style={styles.fileInput}
          />
        </div>

        <div style={styles.frameworkRow}>
          <span style={styles.frameworkBadge}>⚡ FastAPI</span>
          <span style={styles.frameworkBadge}>🟨 Express.js</span>
          <span style={styles.frameworkBadge}>📦 ZIP upload</span>
        </div>

        {error && <p style={styles.error}>{error}</p>}

        <button
          onClick={handleGenerate}
          disabled={!file}
          style={{ ...styles.btn, opacity: file ? 1 : 0.4, cursor: file ? "pointer" : "not-allowed" }}
        >
          Generate Documentation
        </button>
      </div>
    </div>
  )
}

const styles = {
  page:           { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "40px 20px" },
  card:           { background: "white", borderRadius: 16, padding: "40px", width: "100%", maxWidth: 500, boxShadow: "0 1px 3px rgba(0,0,0,0.08)" },
  h1:             { fontSize: 26, fontWeight: 600, marginBottom: 8, color: "#111" },
  sub:            { fontSize: 14, color: "#666", marginBottom: 28, lineHeight: 1.6 },
  dropzone:       { position: "relative", border: "2px dashed #ddd", borderRadius: 12, padding: "36px 24px", textAlign: "center", marginBottom: 16, transition: "all 0.15s" },
  uploadIcon:     { fontSize: 28, marginBottom: 10, color: "#999" },
  dropText:       { fontSize: 14, fontWeight: 500, color: "#333", marginBottom: 4 },
  dropSub:        { fontSize: 12, color: "#999", marginBottom: 4 },
  dropHint:       { fontSize: 11, color: "#bbb", letterSpacing: "0.05em" },
  fileInput:      { position: "absolute", inset: 0, opacity: 0, cursor: "pointer", width: "100%", height: "100%" },
  frameworkRow:   { display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" },
  frameworkBadge: { fontSize: 12, padding: "4px 10px", background: "#f3f4f6", borderRadius: 20, color: "#555" },
  error:          { color: "#dc2626", fontSize: 13, marginBottom: 12, padding: "8px 12px", background: "#fef2f2", borderRadius: 8 },
  btn:            { width: "100%", padding: "13px", background: "#111", color: "white", border: "none", borderRadius: 10, fontSize: 15, fontWeight: 500, transition: "opacity 0.15s" },
  center:         { minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12 },
  spinner:        { width: 36, height: 36, border: "3px solid #eee", borderTop: "3px solid #111", borderRadius: "50%", animation: "spin 0.8s linear infinite" },
  loadTitle:      { fontSize: 18, fontWeight: 500, color: "#111" },
  loadSub:        { fontSize: 13, color: "#666" },
}