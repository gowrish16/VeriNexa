export const API_BASE_URL = "http://127.0.0.1:8000";

function getAuthHeaders() {
  const token = localStorage.getItem("verilit_token");
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// 1. GET /papers
export async function fetchPapers() {
  try {
    const res = await fetch(`${API_BASE_URL}/papers`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.papers || [];
  } catch (err) {
    console.warn("Backend /papers unavailable:", err.message);
    return [];
  }
}

// 2. POST /upload
export async function uploadPaper(file, title) {
  const formData = new FormData();
  formData.append("file", file);
  if (title) {
    formData.append("title", title);
  }

  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    headers,
    body: formData,
  });

  const data = await res.json();
  if (res.status === 422 || data.status === "rejected") {
    const msg = data.detail?.message || data.message || "This document does not appear to be a biomedical research paper.";
    const details = data.detail?.details || data.details || "";
    const err = new Error(msg);
    err.details = details;
    err.isRejected = true;
    err.statusCode = 422;
    throw err;
  }

  if (!res.ok) {
    throw new Error(data.detail || `Upload failed with status ${res.status}`);
  }

  return data;
}

// 3. GET /compare?query=...
export async function comparePapers(query) {
  const url = `${API_BASE_URL}/compare?query=${encodeURIComponent(query)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`Compare failed with status ${res.status}`);
  return await res.json();
}

// 4. GET /integrity-check?paper_id=...&topic_query=...
export async function checkIntegrity(paperId, topicQuery) {
  const url = `${API_BASE_URL}/integrity-check?paper_id=${encodeURIComponent(paperId)}&topic_query=${encodeURIComponent(topicQuery)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`Integrity check failed with status ${res.status}`);
  return await res.json();
}

// 5. POST /api/chat
export async function chatAudit(question, sessionId = null) {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      question,
      session_id: sessionId || null,
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "RAG chat query failed");
  }
  return data;
}

// 6. GET /api/history
export async function fetchAuditHistory() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/history`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.sessions || [];
  } catch (err) {
    console.warn("Could not load history:", err);
    return [];
  }
}

// 7. GET /api/history/{session_id}
export async function fetchSessionMessages(sessionId) {
  const res = await fetch(`${API_BASE_URL}/api/history/${sessionId}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`Could not load session #${sessionId}`);
  return await res.json();
}

// 8. GET /files/:filename
export function getPdfFileUrl(filename) {
  return `${API_BASE_URL}/files/${encodeURIComponent(filename)}`;
}
