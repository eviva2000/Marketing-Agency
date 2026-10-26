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

function addAssistantMessage(reply, activity, structured) {
  const row = element("article", "message");
  row.append(element("div", "assistant-avatar", "A"));
  const content = element("div", "message-content");
  content.append(element("p", "message-label", "AGENCY BUILDER"));
  if (reply && reply !== "Structured result ready.") {
    const paragraph = element("p");
    paragraph.textContent = reply;
    content.append(paragraph);
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
  sendButton.disabled = value;
  messageInput.disabled = value;
  newChatButton.disabled = value;
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
    const button = element("button", "", "Retry");
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
    messageInput.disabled = false;
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
    addAssistantMessage(response.reply, response.activity, response.structured);
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
  if (!busy) sendMessage(messageInput.value);
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
