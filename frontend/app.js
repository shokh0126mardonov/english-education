const API_BASE = "";
const tokenKey = "english_education_access";
const refreshTokenKey = "english_education_refresh";
const authUserKey = "english_education_user";
const state = {
  token: localStorage.getItem(tokenKey),
  refresh: localStorage.getItem(refreshTokenKey),
  authUser: JSON.parse(localStorage.getItem(authUserKey) || "null"),
  me: null,
  users: [],
  parents: [],
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const views = {
  auth: $('[data-view="auth"]'),
  workspace: $('[data-view="workspace"]'),
};

function showToast(message, type = "info") {
  const toast = $("#toast");
  toast.textContent = message;
  toast.className = `toast ${type}`;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.add("hidden"), 3600);
}

function getFormData(form) {
  const payload = {};
  new FormData(form).forEach((value, key) => {
    if (value !== "") payload[key] = value;
  });
  return payload;
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (options.auth !== false && state.token) headers.set("Authorization", `Bearer ${state.token}`);

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body:
      options.body && !(options.body instanceof FormData)
        ? JSON.stringify(options.body)
        : options.body,
  });

  if (response.status === 401) {
    if (options.auth !== false) logout("Sessiya tugadi. Qayta login qiling.");
    throw new Error("Unauthorized");
  }

  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }
  if (!response.ok) {
    const message =
      data?.detail ||
      Object.entries(data || {})
        .map(([field, value]) => `${field}: ${Array.isArray(value) ? value.join(" ") : value}`)
        .join(" ") ||
      "API xatolik qaytardi.";
    throw new Error(message);
  }
  return data;
}

function isAdmin() {
  return ["ADMIN", "SUPERADMIN"].includes(getRole());
}

function isSuperAdmin() {
  return getRole() === "SUPERADMIN";
}

function canCheckTelegram() {
  return ["TEACHER", "ADMIN", "SUPERADMIN"].includes(getRole());
}

function getRole() {
  return state.me?.role || state.authUser?.role || "-";
}

function getUserId() {
  return state.me?.id || state.authUser?.id || null;
}

function fullName(user) {
  const name = `${user?.first_name || ""} ${user?.last_name || ""}`.trim();
  return name || user?.username || "-";
}

function studentUsers() {
  return state.users.filter((user) => user.role === "STUDENT");
}

function getUserById(id) {
  return state.users.find((user) => String(user.id) === String(id));
}

function studentLabel(user) {
  if (!user) return "Student topilmadi";
  const name = fullName(user);
  const meta = [user.username, user.phone].filter(Boolean).join(" • ");
  return meta ? `${name} (${meta})` : name;
}

function renderStudentOptions(selectedId = "") {
  const select = $("#parentForm").elements.user;
  const students = studentUsers();
  select.innerHTML = [
    '<option value="">Student tanlang</option>',
    ...students.map(
      (student) =>
        `<option value="${student.id}" ${String(student.id) === String(selectedId) ? "selected" : ""}>${escapeHtml(studentLabel(student))}</option>`,
    ),
  ].join("");
}

function initials(user) {
  return fullName(user)
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function setAuthView(isLoggedIn) {
  views.auth.classList.toggle("hidden", isLoggedIn);
  views.workspace.classList.toggle("hidden", !isLoggedIn);
}

function setSection(name) {
  $$(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.section === name));
  $$(".section").forEach((panel) => panel.classList.toggle("active", panel.dataset.panel === name));
  $("#pageTitle").textContent = name[0].toUpperCase() + name.slice(1);
}

function applyPermissions() {
  $$("[data-admin-only]").forEach((element) => element.classList.toggle("hidden", !isAdmin()));
  $$("[data-telegram-access]").forEach((element) =>
    element.classList.toggle("hidden", !canCheckTelegram()),
  );
  if (!isAdmin() && ["users", "parents"].includes($(".nav-item.active")?.dataset.section)) {
    setSection("overview");
  }
}

function renderShell() {
  $("#roleBadge").textContent = getRole();
  $("#currentRole").textContent = getRole();
  $("#currentName").textContent = fullName(state.me);
  $("#currentPhone").textContent = state.me?.phone || "-";
  $("#userInitials").textContent = initials(state.me);
  $("#usersCount").textContent = isAdmin() ? state.users.length : "N/A";
  $("#parentsCount").textContent = isAdmin() ? state.parents.length : "N/A";
  $("#apiStatus").textContent = isAdmin()
    ? "Users va parents ma'lumotlari yuklandi."
    : "Profil endpointlari faol. CRUD bo'limlari admin ruxsatini talab qiladi.";
  applyPermissions();
}

function renderUsers() {
  const tbody = $("#usersTable");
  tbody.innerHTML = state.users
    .map(
      (user) => `
        <tr>
          <td>${user.id}</td>
          <td>${escapeHtml(fullName(user))}</td>
          <td>${escapeHtml(user.username)}</td>
          <td><span class="role-pill">${escapeHtml(user.role)}</span></td>
          <td>${escapeHtml(user.phone || "-")}</td>
          <td>
            <div class="row-actions">
              <button class="secondary-action small" data-edit-user="${user.id}">Edit</button>
              <button class="secondary-action small danger-action" data-delete-user="${user.id}">Delete</button>
            </div>
          </td>
        </tr>
      `,
    )
    .join("");
}

function renderParents() {
  const tbody = $("#parentsTable");
  tbody.innerHTML = state.parents
    .map((parent) => {
      const student = getUserById(parent.user);
      return `
        <tr>
          <td>${parent.id}</td>
          <td>
            <strong class="table-primary">${escapeHtml(studentLabel(student))}</strong>
            <span class="table-muted">ID: ${parent.user}</span>
          </td>
          <td>${escapeHtml(parent.full_name || "-")}</td>
          <td>${escapeHtml(parent.phone || "-")}</td>
          <td>
            <div class="row-actions">
              <button class="secondary-action small" data-edit-parent="${parent.id}">Edit</button>
              <button class="secondary-action small danger-action" data-delete-parent="${parent.id}">Delete</button>
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function renderProfileForm() {
  const form = $("#profileForm");
  ["id", "username", "first_name", "last_name", "email", "phone"].forEach((field) => {
    form.elements[field].value = state.me?.[field] || "";
  });
}

function escapeHtml(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[char],
  );
}

async function bootstrap() {
  if (!state.token) {
    setAuthView(false);
    return;
  }

  try {
    state.me = await api("/User/users/me/");
    state.me.role = getRole();
    if (!state.authUser && getUserId()) state.authUser = { id: getUserId(), role: getRole() };
    setAuthView(true);
    try {
      await loadCollections();
    } catch (error) {
      showToast(error.message, "error");
    }
    renderProfileForm();
    renderShell();
  } catch (error) {
    logout("Sessiya tugadi. Qayta login qiling.");
  }
}

async function loadCollections() {
  if (!isAdmin()) {
    state.users = [];
    state.parents = [];
    return;
  }
  const [users, parents] = await Promise.all([api("/User/users/"), api("/User/parents/")]);
  state.users = Array.isArray(users) ? users : users.results || [];
  state.parents = Array.isArray(parents) ? parents : parents.results || [];
  renderUsers();
  renderParents();
}

function logout(message) {
  localStorage.removeItem(tokenKey);
  localStorage.removeItem(refreshTokenKey);
  localStorage.removeItem(authUserKey);
  state.token = null;
  state.refresh = null;
  state.authUser = null;
  state.me = null;
  state.users = [];
  state.parents = [];
  setAuthView(false);
  if (message) $("#loginMessage").textContent = message;
}

function openUserDialog(user = null) {
  const form = $("#userForm");
  form.reset();
  $("#userDialogTitle").textContent = user ? "Userni tahrirlash" : "Yangi user";
  form.elements.id.value = user?.id || "";
  form.elements.username.value = user?.username || "";
  form.elements.first_name.value = user?.first_name || "";
  form.elements.last_name.value = user?.last_name || "";
  form.elements.email.value = user?.email || "";
  form.elements.phone.value = user?.phone || "";
  form.elements.role.value = user?.role || "STUDENT";
  form.elements.password.required = !user;
  $$("option", form.elements.role).forEach((option) => {
    option.disabled = !isSuperAdmin() && ["ADMIN", "SUPERADMIN"].includes(option.value);
  });
  form.elements.role.disabled =
    !isSuperAdmin() && Boolean(user) && ["ADMIN", "SUPERADMIN"].includes(user.role);
  $("#userDialog").showModal();
}

function openParentDialog(parent = null) {
  const form = $("#parentForm");
  form.reset();
  $("#parentDialogTitle").textContent = parent ? "Parentni tahrirlash" : "Yangi parent";
  renderStudentOptions(parent?.user || "");
  form.elements.id.value = parent?.id || "";
  form.elements.full_name.value = parent?.full_name || "";
  form.elements.phone.value = parent?.phone || "";
  if (!studentUsers().length) {
    showToast("Parent qo'shish uchun avval STUDENT role bilan user yarating.", "error");
  }
  $("#parentDialog").showModal();
}

$("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("#loginMessage").textContent = "";
  try {
    const data = await api("/User/login/", {
      method: "POST",
      body: getFormData(event.currentTarget),
      auth: false,
    });
    state.token = data.access;
    state.refresh = data.refresh;
    state.authUser = { id: data.id, role: data.role };
    localStorage.setItem(tokenKey, state.token);
    localStorage.setItem(refreshTokenKey, state.refresh);
    localStorage.setItem(authUserKey, JSON.stringify(state.authUser));
    await bootstrap();
    showToast("Tizimga muvaffaqiyatli kirdingiz.");
  } catch (error) {
    $("#loginMessage").textContent = error.message;
  }
});

$("#logoutBtn").addEventListener("click", () => logout());
$("#refreshAllBtn").addEventListener("click", async () => {
  try {
    state.me = await api("/User/users/me/");
    await loadCollections();
    renderProfileForm();
    renderShell();
    showToast("Ma'lumotlar yangilandi.");
  } catch (error) {
    showToast(error.message, "error");
  }
});

$$(".nav-item").forEach((button) => {
  button.addEventListener("click", () => setSection(button.dataset.section));
});

$("#newUserBtn").addEventListener("click", () => openUserDialog());
$("#newParentBtn").addEventListener("click", () => openParentDialog());

$("#saveUserBtn").addEventListener("click", async () => {
  const form = $("#userForm");
  if (!form.reportValidity()) return;
  const payload = getFormData(form);
  const id = payload.id;
  delete payload.id;
  if (id && !payload.password) delete payload.password;
  if (!isSuperAdmin() && ["ADMIN", "SUPERADMIN"].includes(payload.role)) {
    if (!id) {
      showToast("Admin yoki Superadmin yaratish faqat Superadmin uchun.", "error");
      return;
    }
    delete payload.role;
  }

  try {
    await api(id ? `/User/users/${id}/` : "/User/users/", {
      method: id ? "PATCH" : "POST",
      body: payload,
    });
    $("#userDialog").close();
    await loadCollections();
    renderShell();
    showToast("User saqlandi.");
  } catch (error) {
    showToast(error.message, "error");
  }
});

$("#saveParentBtn").addEventListener("click", async () => {
  const form = $("#parentForm");
  if (!form.reportValidity()) return;
  const payload = getFormData(form);
  const id = payload.id;
  delete payload.id;

  try {
    await api(id ? `/User/parents/${id}/` : "/User/parents/", {
      method: id ? "PATCH" : "POST",
      body: payload,
    });
    $("#parentDialog").close();
    await loadCollections();
    renderShell();
    showToast("Parent saqlandi.");
  } catch (error) {
    showToast(error.message, "error");
  }
});

document.addEventListener("click", async (event) => {
  const editUserId = event.target.closest("[data-edit-user]")?.dataset.editUser;
  const deleteUserId = event.target.closest("[data-delete-user]")?.dataset.deleteUser;
  const editParentId = event.target.closest("[data-edit-parent]")?.dataset.editParent;
  const deleteParentId = event.target.closest("[data-delete-parent]")?.dataset.deleteParent;

  if (editUserId) openUserDialog(state.users.find((user) => String(user.id) === editUserId));
  if (editParentId) openParentDialog(state.parents.find((parent) => String(parent.id) === editParentId));

  if (deleteUserId && confirm("User o'chirilsinmi?")) {
    try {
      await api(`/User/users/${deleteUserId}/`, { method: "DELETE" });
      await loadCollections();
      renderShell();
      showToast("User o'chirildi.");
    } catch (error) {
      showToast(error.message, "error");
    }
  }

  if (deleteParentId && confirm("Parent o'chirilsinmi?")) {
    try {
      await api(`/User/parents/${deleteParentId}/`, { method: "DELETE" });
      await loadCollections();
      renderShell();
      showToast("Parent o'chirildi.");
    } catch (error) {
      showToast(error.message, "error");
    }
  }
});

$("#profileForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    state.me = await api("/User/users/me/", {
      method: "PATCH",
      body: getFormData(event.currentTarget),
    });
    renderProfileForm();
    renderShell();
    showToast("Profil saqlandi.");
  } catch (error) {
    showToast(error.message, "error");
  }
});

$("#passwordForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/User/users/change-password/", {
      method: "POST",
      body: getFormData(event.currentTarget),
    });
    event.currentTarget.reset();
    showToast("Parol almashtirildi. Yangi parol bilan qayta kirishingiz mumkin.");
  } catch (error) {
    showToast(error.message, "error");
  }
});

$("#telegramForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const studentId = event.currentTarget.elements.studentId.value;
  const box = $("#telegramResult");
  box.className = "result-box";
  box.textContent = "Tekshirilmoqda...";

  try {
    await api(`/User/telegram-check/${studentId}/`);
    box.className = "result-box success";
    box.textContent = "Telegram ulangan.";
  } catch (error) {
    box.className = "result-box error";
    box.textContent =
      error.message === "API xatolik qaytardi." ? "Telegram ulanmagan yoki student topilmadi." : error.message;
  }
});

bootstrap();
