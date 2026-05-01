import { useState } from "react"

const METHOD_COLOR = {
  GET:    { bg: "#dcfce7", text: "#166534" },
  POST:   { bg: "#dbeafe", text: "#1e40af" },
  PUT:    { bg: "#fef9c3", text: "#854d0e" },
  DELETE: { bg: "#fee2e2", text: "#991b1b" },
  PATCH:  { bg: "#f3e8ff", text: "#6b21a8" },
}

function locationBadge(loc) {
  const colors = {
    path:  ["#fef3c7", "#92400e"],
    query: ["#dbeafe", "#1e40af"],
    body:  ["#f3e8ff", "#6b21a8"],
  }
  const [bg, color] = colors[loc] || ["#f3f4f6", "#374151"]
  return { background: bg, color, fontSize: 11, fontWeight: 500, padding: "2px 7px", borderRadius: 20 }
}

function StatsBar({ routes }) {
  const counts = routes.reduce((acc, r) => {
    acc[r.method] = (acc[r.method] || 0) + 1
    return acc
  }, {})
  const methodOrder = ["GET", "POST", "PUT", "PATCH", "DELETE"]
  return (
    <div style={s.statsBar}>
      <div style={s.statItem}>
        <span style={s.statNumber}>{routes.length}</span>
        <span style={s.statLabel}>endpoints</span>
      </div>
      <div style={s.statDivider} />
      {methodOrder.filter(m => counts[m]).map(m => {
        const mc = METHOD_COLOR[m]
        return (
          <div key={m} style={s.statItem}>
            <span style={{ ...s.statNumber, color: mc.text }}>{counts[m]}</span>
            <span style={{ ...s.statLabel, background: mc.bg, color: mc.text, padding: "1px 7px", borderRadius: 20 }}>{m}</span>
          </div>
        )
      })}
    </div>
  )
}

function ParamTable({ params }) {
  if (!params || params.length === 0) return null
  return (
    <div style={{ marginBottom: 16 }}>
      <p style={s.sectionLabel}>Parameters</p>
      <table style={s.table}>
        <thead>
          <tr>
            {["Name", "Type", "Location", "Required", "Default"].map(h => (
              <th key={h} style={s.th}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {params.map((p, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? "#fafafa" : "white" }}>
              <td style={{ ...s.td, fontFamily: "monospace", fontWeight: 500 }}>{p.name}</td>
              <td style={{ ...s.td, color: "#7c3aed", fontFamily: "monospace" }}>{p.type}</td>
              <td style={s.td}><span style={locationBadge(p.location)}>{p.location}</span></td>
              <td style={s.td}>{p.required ? "✓" : "—"}</td>
              <td style={{ ...s.td, fontFamily: "monospace", color: "#666" }}>{p.default || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ResponseSchema({ schema, returnType }) {
  if (!schema) return null

  const isArray = schema.type === "array"
  const fields = schema.fields

  return (
    <div style={{ marginBottom: 16 }}>
      <p style={s.sectionLabel}>Response schema</p>
      <div style={s.schemaBox}>
        <div style={s.schemaHeader}>
          <span style={s.schemaType}>{schema.type}</span>
          {(schema.model || schema.inner_model || returnType) && returnType !== "any" && (
            <code style={s.schemaModel}>
              {isArray
                ? `List[${schema.inner_model || ""}]`
                : (schema.model || returnType)}
            </code>
          )}
        </div>

        {fields && (
          <table style={{ ...s.table, marginTop: 0 }}>
            <thead>
              <tr>
                {["Field", "Type", "Required"].map(h => (
                  <th key={h} style={s.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(fields).map(([fieldName, fieldInfo], i) => (
                <tr key={i} style={{ background: i % 2 === 0 ? "#fafafa" : "white" }}>
                  <td style={{ ...s.td, fontFamily: "monospace", fontWeight: 500 }}>{fieldName}</td>
                  <td style={{ ...s.td, color: "#7c3aed", fontFamily: "monospace" }}>{fieldInfo.type}</td>
                  <td style={s.td}>{fieldInfo.required ? "✓" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {schema.example !== undefined && schema.example !== null && (
          <div style={{ padding: "10px 12px", borderTop: fields ? "1px solid #e5e7eb" : "none" }}>
            <p style={{ ...s.sectionLabel, marginBottom: 6 }}>Example response</p>
            <pre style={{ ...s.curlPre, margin: 0 }}>
              {JSON.stringify(schema.example, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

function CurlBlock({ curl }) {
  const [copied, setCopied] = useState(false)
  function copy() {
    navigator.clipboard.writeText(curl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <div style={{ marginBottom: 16 }}>
      <p style={s.sectionLabel}>Curl command</p>
      <div style={s.curlBox}>
        <pre style={s.curlPre}>{curl}</pre>
        <button onClick={copy} style={s.copyBtn}>{copied ? "Copied!" : "Copy"}</button>
      </div>
    </div>
  )
}

function EndpointCard({ route }) {
  const [open, setOpen] = useState(false)
  const mc = METHOD_COLOR[route.method] || { bg: "#f3f4f6", text: "#374151" }
  return (
    <div style={s.card}>
      <div onClick={() => setOpen(!open)} style={s.cardHeader}>
        <span style={{ ...s.methodBadge, background: mc.bg, color: mc.text }}>
          {route.method}
        </span>
        <code style={s.path}>{route.path}</code>
        {route.description && route.description !== "No description available." && (
          <span style={s.shortDesc}>{route.description.split(".")[0]}</span>
        )}
        <span style={{ marginLeft: "auto", color: "#999", fontSize: 12 }}>{open ? "▲" : "▼"}</span>
      </div>

      {open && (
        <div style={s.cardBody}>
          {route.description && (
            <p style={s.description}>{route.description}</p>
          )}

          {route.tags && route.tags.length > 0 && (
            <div style={{ marginBottom: 12, display: "flex", gap: 6, flexWrap: "wrap" }}>
              {route.tags.map((tag, i) => (
                <span key={i} style={{ fontSize: 11, padding: "2px 8px", background: "#f3e8ff", color: "#6b21a8", borderRadius: 20, fontWeight: 500 }}>
                  {tag}
                </span>
              ))}
            </div>
          )}

          <ParamTable params={route.params} />
          <ResponseSchema schema={route.response_schema} returnType={route.return_type} />
          <CurlBlock curl={route.curl} />

          <div style={{ fontSize: 12, color: "#999" }}>
            Function: <code style={{ fontFamily: "monospace" }}>{route.function}</code>
            {route.return_type && route.return_type !== "any" && (
              <span> · Returns: <code style={{ fontFamily: "monospace", color: "#7c3aed" }}>{route.return_type}</code></span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function groupRoutes(routes) {
  const groups = {}
  routes.forEach(r => {
    const key = r.group || r.path.split("/").filter(Boolean)[0] || "general"
    if (!groups[key]) groups[key] = []
    groups[key].push(r)
  })
  return groups
}

function RouteGroup({ name, routes }) {
  const [open, setOpen] = useState(true)
  return (
    <div style={s.group}>
      <div onClick={() => setOpen(!open)} style={s.groupHeader}>
        <span style={s.groupName}>{name}</span>
        <span style={s.groupCount}>{routes.length} endpoint{routes.length !== 1 ? "s" : ""}</span>
        <span style={{ marginLeft: "auto", color: "#999", fontSize: 11 }}>{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div style={s.groupBody}>
          {routes.map((r, i) => <EndpointCard key={i} route={r} />)}
        </div>
      )}
    </div>
  )
}

export default function DocsView({ routes, onBack }) {
  const [search, setSearch] = useState("")
  const [filter, setFilter] = useState("ALL")
  const methods = ["ALL", ...new Set(routes.map(r => r.method))]

  const filtered = routes.filter(r => {
    const matchSearch =
      r.path.toLowerCase().includes(search.toLowerCase()) ||
      (r.description || "").toLowerCase().includes(search.toLowerCase()) ||
      (r.tags || []).some(t => t.toLowerCase().includes(search.toLowerCase()))
    const matchMethod = filter === "ALL" || r.method === filter
    return matchSearch && matchMethod
  })

  const groups = groupRoutes(filtered)

  function exportMarkdown() {
    let md = "# API Documentation\n\n"
    md += `> Generated by DocForge — ${routes.length} endpoints\n\n`
    Object.entries(groups).forEach(([groupName, groupRoutes]) => {
      md += `## ${groupName.charAt(0).toUpperCase() + groupName.slice(1)}\n\n`
      groupRoutes.forEach(r => {
        md += `### ${r.method} \`${r.path}\`\n\n`
        if (r.description) md += `${r.description}\n\n`
        if (r.tags?.length) {
          md += `**Tags:** ${r.tags.join(", ")}\n\n`
        }
        if (r.params?.length) {
          md += "#### Parameters\n\n| Name | Type | Location | Required | Default |\n|------|------|----------|----------|---------|\n"
          r.params.forEach(p => {
            md += `| \`${p.name}\` | \`${p.type}\` | ${p.location} | ${p.required ? "Yes" : "No"} | ${p.default || "—"} |\n`
          })
          md += "\n"
        }
        if (r.response_schema?.fields) {
          md += "#### Response schema\n\n| Field | Type | Required |\n|-------|------|----------|\n"
          Object.entries(r.response_schema.fields).forEach(([f, info]) => {
            md += `| \`${f}\` | \`${info.type}\` | ${info.required ? "Yes" : "No"} |\n`
          })
          md += "\n"
        }
        if (r.response_schema?.example) {
          md += "#### Example response\n\n```json\n"
          md += JSON.stringify(r.response_schema.example, null, 2)
          md += "\n```\n\n"
        }
        if (r.curl) md += `#### Curl\n\n\`\`\`bash\n${r.curl}\n\`\`\`\n\n`
        md += "---\n\n"
      })
    })
    const blob = new Blob([md], { type: "text/markdown" })
    const a = document.createElement("a")
    a.href = URL.createObjectURL(blob)
    a.download = "api-docs.md"
    a.click()
  }

  return (
    <div style={s.page}>
      <div style={s.topBar}>
        <div>
          <h1 style={s.h1}>API Documentation</h1>
          <p style={s.h1Sub}>DocForge</p>
        </div>
        <div style={s.topActions}>
          <button onClick={exportMarkdown} style={s.outlineBtn}>Export .md</button>
          <button onClick={onBack} style={s.outlineBtn}>← New file</button>
        </div>
      </div>

      <StatsBar routes={routes} />

      <div style={s.controls}>
        <input
          placeholder="Search by path, description or tag..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={s.searchInput}
        />
        <div style={s.filterRow}>
          {methods.map(m => (
            <button key={m} onClick={() => setFilter(m)}
              style={{
                ...s.filterBtn,
                background: filter === m ? "#111" : "white",
                color: filter === m ? "white" : "#555",
                borderColor: filter === m ? "#111" : "#ddd"
              }}>
              {m}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 && (
        <p style={{ textAlign: "center", color: "#999", marginTop: 40 }}>
          No endpoints match your search.
        </p>
      )}

      {Object.entries(groups).map(([name, groupRoutes]) => (
        <RouteGroup key={name} name={name} routes={groupRoutes} />
      ))}
    </div>
  )
}

const s = {
  page:        { maxWidth: 780, margin: "0 auto", padding: "32px 20px", fontFamily: "-apple-system, sans-serif" },
  topBar:      { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20, flexWrap: "wrap", gap: 12 },
  h1:          { fontSize: 22, fontWeight: 600, color: "#111", marginBottom: 2 },
  h1Sub:       { fontSize: 13, color: "#888" },
  topActions:  { display: "flex", gap: 8 },
  outlineBtn:  { padding: "7px 14px", background: "white", border: "1px solid #ddd", borderRadius: 8, cursor: "pointer", fontSize: 13, color: "#333" },
  statsBar:    { display: "flex", alignItems: "center", gap: 20, background: "white", border: "1px solid #e5e7eb", borderRadius: 10, padding: "14px 20px", marginBottom: 20, flexWrap: "wrap" },
  statItem:    { display: "flex", flexDirection: "column", alignItems: "center", gap: 3 },
  statNumber:  { fontSize: 20, fontWeight: 600, color: "#111", lineHeight: 1 },
  statLabel:   { fontSize: 11, color: "#888", fontWeight: 500 },
  statDivider: { width: 1, height: 32, background: "#e5e7eb", margin: "0 4px" },
  controls:    { marginBottom: 20 },
  searchInput: { width: "100%", padding: "10px 14px", border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 14, marginBottom: 12, outline: "none" },
  filterRow:   { display: "flex", gap: 6, flexWrap: "wrap" },
  filterBtn:   { padding: "5px 12px", border: "1px solid", borderRadius: 20, cursor: "pointer", fontSize: 12, fontWeight: 500, transition: "all 0.15s" },
  group:       { marginBottom: 24 },
  groupHeader: { display: "flex", alignItems: "center", gap: 10, padding: "10px 4px", cursor: "pointer", borderBottom: "2px solid #e5e7eb", marginBottom: 12 },
  groupName:   { fontSize: 15, fontWeight: 600, color: "#111", textTransform: "capitalize" },
  groupCount:  { fontSize: 12, color: "#888", background: "#f3f4f6", padding: "2px 8px", borderRadius: 20 },
  groupBody:   {},
  card:        { border: "1px solid #e5e7eb", borderRadius: 10, marginBottom: 8, overflow: "hidden", background: "white" },
  cardHeader:  { display: "flex", alignItems: "center", gap: 10, padding: "13px 16px", cursor: "pointer", flexWrap: "wrap" },
  methodBadge: { fontSize: 11, fontWeight: 700, padding: "3px 8px", borderRadius: 5, minWidth: 56, textAlign: "center", flexShrink: 0 },
  path:        { fontSize: 14, fontFamily: "monospace", color: "#111", fontWeight: 500 },
  shortDesc:   { fontSize: 12, color: "#888", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
  cardBody:    { padding: "16px", borderTop: "1px solid #f3f4f6", background: "#fafafa" },
  description: { fontSize: 14, color: "#444", marginBottom: 12, lineHeight: 1.6 },
  sectionLabel:{ fontSize: 11, fontWeight: 600, color: "#888", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 8 },
  table:       { width: "100%", borderCollapse: "collapse", fontSize: 13, border: "1px solid #e5e7eb", borderRadius: 6, overflow: "hidden" },
  th:          { padding: "8px 12px", background: "#f9fafb", color: "#555", fontWeight: 500, textAlign: "left", borderBottom: "1px solid #e5e7eb", fontSize: 12 },
  td:          { padding: "8px 12px", borderBottom: "1px solid #f3f4f6", color: "#333" },
  schemaBox:   { border: "1px solid #e5e7eb", borderRadius: 8, overflow: "hidden" },
  schemaHeader:{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", background: "#f9fafb", borderBottom: "1px solid #e5e7eb" },
  schemaType:  { fontSize: 11, fontWeight: 600, color: "#888", textTransform: "uppercase" },
  schemaModel: { fontSize: 12, fontFamily: "monospace", color: "#7c3aed", background: "#f3e8ff", padding: "1px 6px", borderRadius: 4 },
  curlBox:     { display: "flex", gap: 8, alignItems: "flex-start" },
  curlPre:     { flex: 1, background: "#1a1a1a", color: "#e5e5e5", padding: "12px 14px", borderRadius: 8, fontSize: 12, fontFamily: "monospace", overflow: "auto", margin: 0, lineHeight: 1.6, whiteSpace: "pre-wrap" },
  copyBtn:     { padding: "8px 14px", background: "#111", color: "white", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 12, whiteSpace: "nowrap", flexShrink: 0 },
}