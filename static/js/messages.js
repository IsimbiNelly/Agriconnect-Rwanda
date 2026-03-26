/* ============================================================
   AgriConnect – Messages Page
   ============================================================ */

let _currentUser   = null;
let _activeConvId  = null;
let _pollTimer     = null;

document.addEventListener('DOMContentLoaded', async () => {
  _currentUser = requireAuth();
  if (!_currentUser) return;

  populateNavUser();
  buildNav(_currentUser.role);
  document.getElementById('btn-logout').addEventListener('click', logout);
  initNotificationBell('notif-bell', 'notif-badge', 'notif-list');

  // Check if URL has ?to=<user_id> to open a conversation directly
  const params = new URLSearchParams(location.search);
  const toId   = params.get('to') ? parseInt(params.get('to')) : null;

  await loadConversations(toId);

  // New conversation button
  document.getElementById('btn-new-conv').addEventListener('click', openUserPicker);
  document.getElementById('close-picker').addEventListener('click', () => {
    document.getElementById('user-picker').style.display = 'none';
  });

  // Real-time: refresh chat when a new message arrives
  connectWS((data) => {
    if (data.type === 'message') {
      loadConversations(_activeConvId);
      if (_activeConvId === data.sender_id) {
        loadChat(_activeConvId);
      }
    }
  });
});

function buildNav(role) {
  const links = role === 'farmer'
    ? `<a href="/farmer/dashboard" class="nav-link">🏠 <span>Dashboard</span></a>
       <a href="/farmer/products"  class="nav-link">📦 <span>My Products</span></a>
       <a href="/farmer/orders"    class="nav-link">🛒 <span>Orders</span></a>
       <a href="/messages"         class="nav-link active">💬 <span>Messages</span></a>`
    : `<a href="/buyer/dashboard" class="nav-link">🛒 <span>Browse Market</span></a>
       <a href="/buyer/orders"    class="nav-link">📋 <span>My Orders</span></a>
       <a href="/messages"        class="nav-link active">💬 <span>Messages</span></a>`;
  document.getElementById('nav-links').innerHTML = links;

  const brand = document.getElementById('nav-brand');
  brand.href = role === 'farmer' ? '/farmer/dashboard' : '/buyer/dashboard';
}

// ── Conversations list ────────────────────────────────────────

async function loadConversations(openId = null) {
  const listEl = document.getElementById('conv-list-items');
  try {
    const convs = await apiFetch('/api/messages/conversations');

    if (convs.length === 0) {
      listEl.innerHTML = `
        <div style="padding:20px;text-align:center;color:var(--gray-400);font-size:13px;">
          No conversations yet.<br>Click ✏️ to start one.
        </div>`;
    } else {
      listEl.innerHTML = convs.map(c => convItem(c)).join('');
      listEl.querySelectorAll('.conv-item').forEach(el => {
        el.addEventListener('click', () => {
          const uid = parseInt(el.dataset.uid);
          listEl.querySelectorAll('.conv-item').forEach(e => e.classList.remove('active'));
          el.classList.add('active');
          loadChat(uid);
        });
      });
    }

    // Auto-open a specific conversation
    if (openId) {
      const existing = listEl.querySelector(`[data-uid="${openId}"]`);
      if (existing) {
        existing.click();
      } else {
        // Conversation doesn't exist yet – just open chat with that user
        openChatWith(openId);
      }
    }
  } catch (err) {
    listEl.innerHTML = `<div style="padding:16px;color:var(--danger);">Failed to load.</div>`;
  }
}

function convItem(c) {
  const init = (c.other_user.full_name[0] || '?').toUpperCase();
  const badge = c.unread_count > 0
    ? `<span class="conv-badge">${c.unread_count}</span>` : '';
  return `
    <div class="conv-item" data-uid="${c.other_user.id}">
      <div class="conv-avatar">${init}</div>
      <div style="flex:1;min-width:0;">
        <div class="conv-name">${c.other_user.full_name}</div>
        <div class="conv-preview">${c.last_message}</div>
      </div>
      ${badge}
    </div>`;
}

// ── Chat window ───────────────────────────────────────────────

async function loadChat(otherId) {
  _activeConvId = otherId;
  clearInterval(_pollTimer);

  const chatArea = document.getElementById('chat-area');
  chatArea.innerHTML = `
    <div class="chat-header" id="chat-header">
      <div class="conv-avatar" style="width:36px;height:36px;font-size:14px;" id="chat-avatar">?</div>
      <span id="chat-name">Loading…</span>
    </div>
    <div class="chat-messages" id="chat-messages">
      <div class="loading" style="align-self:center;display:flex;gap:8px;align-items:center;">
        <div class="spinner"></div><span>Loading messages…</span>
      </div>
    </div>
    <div class="chat-input-bar">
      <input type="text" id="msg-input" placeholder="Type a message…" autocomplete="off">
      <button class="btn btn-primary btn-sm" id="msg-send">Send</button>
    </div>`;

  document.getElementById('msg-send').addEventListener('click', sendMessage);
  document.getElementById('msg-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMessage();
  });

  await renderMessages(otherId);

  // Poll every 5 s for new messages
  _pollTimer = setInterval(() => renderMessages(otherId), 5000);
}

async function renderMessages(otherId) {
  try {
    const msgs   = await apiFetch(`/api/messages/conversation/${otherId}`);
    const msgsEl = document.getElementById('chat-messages');
    if (!msgsEl) return;

    // Get other user name from first message if possible
    const other = msgs.find(m => m.sender_id === otherId || m.receiver_id === otherId);
    if (other) {
      const name = other.sender_id === otherId ? other.sender.full_name : other.receiver.full_name;
      const el = document.getElementById('chat-name');
      const av = document.getElementById('chat-avatar');
      if (el) el.textContent = name;
      if (av) av.textContent = name[0].toUpperCase();
    } else {
      // Fetch from users list
      try {
        const users = await apiFetch('/api/messages/users');
        const found = users.find(u => u.id === otherId);
        if (found) {
          const el = document.getElementById('chat-name');
          const av = document.getElementById('chat-avatar');
          if (el) el.textContent = found.full_name;
          if (av) av.textContent = found.full_name[0].toUpperCase();
        }
      } catch { /* ignore */ }
    }

    const wasAtBottom = msgsEl.scrollHeight - msgsEl.scrollTop - msgsEl.clientHeight < 60;

    msgsEl.innerHTML = msgs.length === 0
      ? `<div style="text-align:center;color:var(--gray-400);font-size:13px;align-self:center;">
           No messages yet. Say hello! 👋
         </div>`
      : msgs.map(m => bubbleHTML(m)).join('');

    if (wasAtBottom || msgs.length <= 3) {
      msgsEl.scrollTop = msgsEl.scrollHeight;
    }
  } catch { /* ignore */ }
}

function bubbleHTML(m) {
  const mine = m.sender_id === _currentUser.id;
  const t    = new Date(m.created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
  return `
    <div class="msg-bubble ${mine ? 'sent' : 'received'}">
      ${m.content}
      <div class="msg-time">${t}</div>
    </div>`;
}

async function sendMessage() {
  const input = document.getElementById('msg-input');
  const text  = input.value.trim();
  if (!text || !_activeConvId) return;

  input.value = '';
  try {
    await apiFetch('/api/messages', {
      method: 'POST',
      body: { receiver_id: _activeConvId, content: text },
    });
    await renderMessages(_activeConvId);
    await loadConversations(_activeConvId);
  } catch (err) {
    showToast(err.message, 'error');
    input.value = text;
  }
}

// ── Open chat with a user that has no existing conversation ──

async function openChatWith(userId) {
  _activeConvId = userId;
  clearInterval(_pollTimer);

  const chatArea = document.getElementById('chat-area');

  // Try to get the user's name
  let name = `User #${userId}`;
  try {
    const users = await apiFetch('/api/messages/users');
    const found = users.find(u => u.id === userId);
    if (found) name = found.full_name;
  } catch { /* ignore */ }

  chatArea.innerHTML = `
    <div class="chat-header" id="chat-header">
      <div class="conv-avatar" style="width:36px;height:36px;font-size:14px;">${name[0].toUpperCase()}</div>
      <span>${name}</span>
    </div>
    <div class="chat-messages" id="chat-messages">
      <div style="text-align:center;color:var(--gray-400);font-size:13px;align-self:center;">
        No messages yet. Say hello! 👋
      </div>
    </div>
    <div class="chat-input-bar">
      <input type="text" id="msg-input" placeholder="Type a message…" autocomplete="off">
      <button class="btn btn-primary btn-sm" id="msg-send">Send</button>
    </div>`;

  document.getElementById('msg-send').addEventListener('click', sendMessage);
  document.getElementById('msg-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMessage();
  });

  _pollTimer = setInterval(() => renderMessages(userId), 5000);
}

// ── User picker for new conversation ─────────────────────────

async function openUserPicker() {
  const picker = document.getElementById('user-picker');
  picker.style.display = 'flex';

  const listEl = document.getElementById('user-pick-list');
  try {
    const users = await apiFetch('/api/messages/users');
    if (users.length === 0) {
      listEl.innerHTML = '<p style="color:var(--gray-400);font-size:13px;">No users available.</p>';
      return;
    }
    listEl.innerHTML = users.map(u => `
      <div class="user-pick-item" data-uid="${u.id}">
        <div class="conv-avatar" style="width:40px;height:40px;font-size:15px;">${u.full_name[0].toUpperCase()}</div>
        <div>
          <div style="font-weight:600;font-size:14px;">${u.full_name}</div>
          <div style="font-size:12px;color:var(--gray-400);">@${u.username} · ${u.role}</div>
        </div>
      </div>`).join('');

    listEl.querySelectorAll('.user-pick-item').forEach(el => {
      el.addEventListener('click', () => {
        picker.style.display = 'none';
        const uid = parseInt(el.dataset.uid);
        // Highlight in conv list if exists, otherwise open fresh chat
        const existing = document.querySelector(`#conv-list-items [data-uid="${uid}"]`);
        if (existing) {
          document.querySelectorAll('.conv-item').forEach(e => e.classList.remove('active'));
          existing.classList.add('active');
        }
        loadChat(uid);
      });
    });
  } catch (err) {
    listEl.innerHTML = `<p style="color:var(--danger);">Failed to load users.</p>`;
  }
}
