"use strict";

const conversation = document.querySelector("#conversation");
const composer = document.querySelector("#composer");
const messageInput = document.querySelector("#message");
const sendButton = document.querySelector("#send");
const notice = document.querySelector("#notice");
const newChatButton = document.querySelector("#new-chat");

let sessionId = null;
let pendingMessage = null;
let busy = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function scrollConversation() {
  conversation.scrollTop = conversation.scrollHeight;
}

function addUserMessage(text) {
  const row = element("article", "message message-user");
  const content = element("div", "message-content");
  content.append(element("p", "", text));
  row.append(content);
  conversation.append(row);
  scrollConversation();
}

function addActivity(items) {
  if (!items || items.length === 0) return null;
  const list = element("ul", "activity-list");
  for (const item of items) {
    list.append(element("li", "", item.label));
  }
  return list;
}

function appendInlineMarkdown(parent, text) {
  const pattern = /\*\*([^*]+)\*\*|\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
  let cursor = 0;
  for (const match of text.matchAll(pattern)) {
    parent.append(document.createTextNode(text.slice(cursor, match.index)));
    if (match[1]) {
      const strong = element("strong", "", match[1]);
      parent.append(strong);
    } else {
      const link = element("a", "", match[2]);
      link.href = match[3];
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      parent.append(link);
    }
    cursor = match.index + match[0].length;
  }
  parent.append(document.createTextNode(text.slice(cursor)));
}

function tableCells(line) {
  const escapedPipe = "\u0000";
  let normalized = line.trim().replaceAll("\\|", escapedPipe);
  if (normalized.startsWith("|")) normalized = normalized.slice(1);
  if (normalized.endsWith("|")) normalized = normalized.slice(0, -1);
  return normalized.split("|").map((cell) => cell.replaceAll(escapedPipe, "|").trim());
}

function isTableSeparator(line) {
  const cells = tableCells(line);
  return cells.length > 1 && cells.every((cell) => /^:?-{3,}:?$/.test(cell));
}

function appendTable(parent, headerLine, rows) {
  const wrapper = element("div", "table-scroll");
  const table = element("table", "reply-table");
  const head = element("thead");
  const header = element("tr");
  tableCells(headerLine).forEach((text) => {
    const cell = element("th", "", text);
    cell.scope = "col";
    header.append(cell);
  });
  head.append(header);
  table.append(head);

  const body = element("tbody");
  rows.forEach((row) => {
    const tr = element("tr");
    const cells = tableCells(row);
    while (cells.length < header.children.length) cells.push("");
    cells.slice(0, header.children.length).forEach((text) => {
      const cell = element("td");
      appendInlineMarkdown(cell, text);
      tr.append(cell);
    });
    body.append(tr);
  });
  table.append(body);
  wrapper.append(table);
  parent.append(wrapper);
}

function appendReply(parent, text) {
  const lines = text.split("\n");
  let paragraph = [];
  const flushParagraph = () => {
    if (!paragraph.length) return;
    const node = element("p");
    appendInlineMarkdown(node, paragraph.join("\n"));
    const question = node.textContent.trim();
    if (question.endsWith("?")) {
      node.append(document.createTextNode(" "));
      const helpButton = element("button", "help-question-button", "Help me on this");
      helpButton.type = "button";
      helpButton.setAttribute("aria-label", `Get help understanding: ${question}`);
      helpButton.addEventListener("click", () => {
        sendMessage(`Research this question using web search and answer it with current, reliable evidence and citations. Explain how the evidence applies to my selected niche, then ask me the question again so I can make my own decision. This is a request for research, not my answer: ${question}`);
      });
      node.append(helpButton);
    }
    parent.append(node);
    paragraph = [];
  };

  for (let index = 0; index < lines.length; index += 1) {
    if (lines[index].includes("|") && isTableSeparator(lines[index + 1] || "")) {
      flushParagraph();
      const headerLine = lines[index];
      const rows = [];
      index += 2;
      while (index < lines.length && lines[index].includes("|")) {
        rows.push(lines[index]);
        index += 1;
      }
      appendTable(parent, headerLine, rows);
      index -= 1;
    } else if (lines[index].trim()) {
      paragraph.push(lines[index]);
    } else {
      flushParagraph();
    }
  }
  flushParagraph();
}

function nextStepPanel(description, buttonLabel, prompt) {
  const panel = element("section", "next-step");
  const copy = element("div");
  copy.append(element("p", "next-step-label", "NEXT STEP"));
  copy.append(element("p", "next-step-copy", description));
  const button = element("button", "next-step-button", buttonLabel);
  button.type = "button";
  button.addEventListener("click", () => sendMessage(prompt));
  panel.append(copy, button);
  return panel;
}

function field(parent, label, value) {
  if (value === undefined || value === null || value === "") return;
  const heading = element("h4", "", label);
  parent.append(heading);
  if (Array.isArray(value)) {
    const list = element("ul");
    value.forEach((entry) => list.append(element("li", "", String(entry))));
    parent.append(list);
  } else if (typeof value === "object") {
    parent.append(element("p", "", JSON.stringify(value)));
  } else {
    parent.append(element("p", "", String(value)));
  }
}

function structuredView(data) {
  if (!data) return null;
  const details = element("details", "structured");
  details.append(element("summary", "", "Structured result"));
  const body = element("div", "structured-body");
  if (Array.isArray(data.leads)) {
    body.append(element("h3", "", `${data.niche || "Confirmed"} · ${data.leads.length} leads`));
    body.append(nextStepPanel(
      "Review this approved list, then create personalized outreach drafts.",
      "Prepare outreach drafts",
      "Prepare personalized outreach drafts for these approved leads.",
    ));
    data.leads.forEach((lead) => {
      const record = element("section", "record");
      record.append(element("p", "record-title", lead.name || "Lead"));
      field(record, "Fit", lead.fit_reasoning);
      field(record, "Contact", lead.contact_info);
      field(record, "Found through", lead.how_found);
      field(record, "Outreach angle", lead.outreach_angle);
      body.append(record);
    });
    if (data.offer_package) field(body, "Offer", data.offer_package);
  } else if (Array.isArray(data.drafts)) {
    body.append(element("h3", "", `${data.niche || "Approved"} · ${data.drafts.length} drafts`));
    data.drafts.forEach((draft) => {
      const record = element("section", "record");
      record.append(element("p", "record-title", draft.lead_name || "Lead"));
      field(record, "Email subject", draft.email_subject);
      field(record, "Email draft", draft.email_body);
      field(record, "Call opener", draft.call_opener);
      field(record, "Personalization", draft.personalization_rationale);
      body.append(record);
    });
  } else if (data.offer_summary && data.final_pitch) {
    body.append(element("h3", "", data.niche || "Confirmed offer"));
    body.append(nextStepPanel(
      "Find prospective clients who match this offer.",
      "Find matching leads",
      "Find matching leads for this offer.",
    ));
    Object.entries(data.offer_summary).forEach(([key, value]) => field(body, key.replaceAll("_", " "), value));
    const pitch = element("section", "record");
    pitch.append(element("p", "record-title", "Pitch"));
    Object.entries(data.final_pitch).forEach(([key, value]) => field(pitch, key.replaceAll("_", " "), value));
    body.append(pitch);
  } else {
    body.append(element("pre", "", JSON.stringify(data, null, 2)));
  }
  details.append(body);
  return details;
}

function addAssistantMessage(reply, activity, structured, agentName) {
  const row = element("article", "message");
  row.append(element("div", "assistant-avatar", "A"));
  const content = element("div", "message-content");
  content.append(element("p", "message-label", "AGENCY BUILDER"));
  if (reply && reply !== "Structured result ready.") {
    appendReply(content, reply);
  }
  if (agentName === "Lead Gen Bot") {
    content.append(nextStepPanel(
      "Review these candidates. Approve the list to keep them, or ask for changes to the location or type of business.",
      "Approve this list",
      "This list looks good. Please keep these leads and prepare the structured lead list.",
    ));
  }
  const activityList = addActivity(activity);
  if (activityList) content.append(activityList);
  const result = structuredView(structured);
  if (result) content.append(result);
  row.append(content);
  conversation.append(row);
  scrollConversation();
}

function setBusy(value) {
  busy = value;
  sendButton.disabled = value || !sessionId;
  messageInput.disabled = value;
  newChatButton.disabled = value;
  document.querySelectorAll(".next-step-button, .help-question-button").forEach((button) => {
    button.disabled = value;
  });
  sendButton.querySelector("span:first-child").textContent = value ? "Working" : "Send";
  if (value) {
    const row = element("article", "message");
    row.id = "typing-indicator";
    row.setAttribute("aria-label", "Agency Builder is preparing a response");
    row.append(element("div", "assistant-avatar", "A"));
    row.append(element("span", "typing", "Working through your request"));
    conversation.append(row);
  } else {
    document.querySelector("#typing-indicator")?.remove();
  }
  scrollConversation();
}

function showNotice(text, retry = false) {
  notice.replaceChildren(document.createTextNode(text));
  if (retry) {
    const button = element("button", "", "Retry answer");
    button.type = "button";
    button.addEventListener("click", () => sendMessage(pendingMessage, false));
    notice.append(button);
  }
  notice.hidden = false;
}

function clearNotice() {
  notice.hidden = true;
  notice.replaceChildren();
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("The local server returned an unreadable response.");
  }
  if (!response.ok) throw new Error(payload.error || "The request failed.");
  return payload;
}

async function startSession() {
  const payload = await requestJson("/api/sessions", { method: "POST", body: "{}" });
  return payload.session_id;
}

async function connectSession() {
  try {
    sessionId = await startSession();
    sendButton.disabled = false;
    clearNotice();
  } catch {
    showNotice("Could not connect to the local server.");
    const retry = element("button", "", "Retry connection");
    retry.type = "button";
    retry.addEventListener("click", connectSession);
    notice.append(retry);
  }
}

async function sendMessage(text, addBubble = true) {
  if (!sessionId || busy || !text || !text.trim()) return;
  pendingMessage = text.trim();
  if (addBubble) addUserMessage(pendingMessage);
  clearNotice();
  setBusy(true);
  try {
    const response = await requestJson("/api/chat", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, message: pendingMessage }),
    });
    addAssistantMessage(response.reply, response.activity, response.structured, response.agent);
    pendingMessage = null;
  } catch (error) {
    showNotice(error.message, true);
  } finally {
    setBusy(false);
    if (!pendingMessage) messageInput.value = "";
    messageInput.focus();
  }
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!busy) {
    const text = messageInput.value;
    const isRetry = pendingMessage && text.trim() === pendingMessage;
    sendMessage(isRetry ? pendingMessage : text, !isRetry);
  }
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    composer.requestSubmit();
  }
});

document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});

newChatButton.addEventListener("click", async () => {
  const previousSession = sessionId;
  clearNotice();
  setBusy(true);
  try {
    sessionId = await startSession();
    conversation.replaceChildren();
    if (previousSession) {
      requestJson(`/api/sessions/${encodeURIComponent(previousSession)}`, { method: "DELETE" }).catch(() => {});
    }
    pendingMessage = null;
    messageInput.value = "";
    addAssistantMessage("This is a fresh conversation. Tell me about your experience or the industry you want to serve.", [], null);
  } catch (error) {
    showNotice(`Could not start a new conversation. ${error.message}`);
  } finally {
    setBusy(false);
    messageInput.focus();
  }
});

connectSession();
