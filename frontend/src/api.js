/** Базовый URL API (только origin). В dev по умолчанию пустая строка — запросы идут на origin Vite, прокси см. vite.config.js. Пути в коде уже содержат /api/v1 — не добавляйте /api/v1 в VITE_API_URL. */
export const API_BASE = (() => {
  const v = import.meta.env.VITE_API_URL;
  if (v !== undefined && String(v).length > 0) {
    let base = String(v).replace(/\/$/, "");
    if (/\/api\/v1$/i.test(base)) base = base.replace(/\/api\/v1$/i, "");
    return base;
  }
  if (import.meta.env.DEV) return "";
  return "http://127.0.0.1:8010";
})();

const TOKEN_KEY = "groomcare_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export async function apiFetch(path, { method = "GET", body, auth = false, headers = {} } = {}) {
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const h = { ...headers };
  if (body !== undefined && !(body instanceof FormData)) {
    h["Content-Type"] = "application/json";
  }
  if (auth) {
    const t = getToken();
    if (t) h.Authorization = `Bearer ${t}`;
  }
  const res = await fetch(url, {
    method,
    headers: h,
    body: body !== undefined && !(body instanceof FormData) ? JSON.stringify(body) : body,
  });
  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const msg =
      (data && typeof data === "object" && data.detail) ||
      (data && typeof data === "object" && data.error) ||
      res.statusText ||
      `Ошибка ${res.status}`;
    throw new ApiError(typeof msg === "string" ? msg : JSON.stringify(msg), res.status, data);
  }
  return data;
}

export function mapService(row) {
  if (!row) return null;
  return {
    id: row.id,
    title: row.title,
    description: row.description,
    price: row.price,
    duration: row.duration_label || String(row.duration_minutes ?? "") + " мин",
    durationMinutes: row.duration_minutes,
    recommendations: row.recommendations || "",
    restrictions: row.restrictions || "",
    speciesAllowed: row.species_allowed || [],
  };
}

export function speciesToRu(species) {
  if (species === "dog") return "Собака";
  if (species === "cat") return "Кошка";
  return "Другое";
}

export function mapPet(row) {
  if (!row) return null;
  return {
    id: row.id,
    name: row.name,
    type: speciesToRu(row.species),
    breed: row.breed || "",
    size: row.size || "",
    age: row.age_label || "",
    notes: row.notes || "",
    species: row.species,
  };
}

const STATUS_RU = {
  draft: "черновик",
  pending_confirmation: "ожидает подтверждения",
  confirmed: "подтверждена",
  paid: "оплачена",
  completed: "завершена",
  cancelled: "отменена",
  no_show: "неявка",
};

export function statusToRu(en) {
  return STATUS_RU[en] || en;
}

function paymentLabel(payment) {
  if (!payment) return "оплата не создана";
  if (payment.status === "succeeded") return "оплачена";
  if (payment.status === "pending") return "ожидается оплата";
  if (payment.status === "failed") return "ошибка оплаты";
  return payment.status;
}

export function mapAppointment(row, servicesList) {
  const start = row.scheduled_start ? new Date(row.scheduled_start) : null;
  const dateStr = start
    ? start.toLocaleDateString("ru-RU", { day: "numeric", month: "long" })
    : "";
  const timeStr = start
    ? start.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit", hour12: false })
    : "";
  const statusRu = statusToRu(row.status);
  const pay = paymentLabel(row.payment);
  return {
    id: row.id,
    serviceId: row.service_id,
    pet: row.pet_display_name || "",
    date: dateStr,
    time: timeStr,
    status: statusRu,
    statusEn: row.status,
    address: row.salon_address_snapshot || "",
    amount: row.amount,
    payment: pay,
    paymentRaw: row.payment,
    scheduledStart: row.scheduled_start,
    _raw: row,
  };
}

export function notificationUiToApi(label) {
  if (label === "Telegram") return "telegram";
  if (label === "Телефон") return "sms";
  return "email";
}

export function fetchSalon() {
  return apiFetch("/api/v1/salon");
}

export function fetchServices() {
  return apiFetch("/api/v1/services");
}

export function fetchSlots(dateYmd, serviceId) {
  return apiFetch(`/api/v1/slots?date=${encodeURIComponent(dateYmd)}&service_id=${encodeURIComponent(serviceId)}`);
}

export function login(phone) {
  return apiFetch("/api/v1/auth/login", { method: "POST", body: { phone } });
}

export function fetchMe() {
  return apiFetch("/api/v1/me", { auth: true });
}

export function fetchPets() {
  return apiFetch("/api/v1/pets", { auth: true });
}

export function fetchAppointments() {
  return apiFetch("/api/v1/appointments", { auth: true });
}

export function createPet(pet) {
  return apiFetch("/api/v1/pets", {
    method: "POST",
    auth: true,
    body: {
      name: pet.name,
      species: pet.species,
      breed: pet.breed || "",
      size: pet.size || "",
      age_label: pet.age_label || "",
      notes: pet.notes || "",
    },
  });
}

export function createAppointment(body) {
  return apiFetch("/api/v1/appointments", {
    method: "POST",
    body,
    auth: true,
  });
}

/** Отмена (`cancel: true`) или перенос (`scheduled_start`: ISO из слотов). */
export function patchAppointment(appointmentId, body) {
  return apiFetch(`/api/v1/appointments/${encodeURIComponent(appointmentId)}`, {
    method: "PATCH",
    auth: true,
    body,
  });
}

export function createPayment(appointmentId, method, amount) {
  return apiFetch(`/api/v1/appointments/${appointmentId}/payments`, {
    method: "POST",
    auth: true,
    body: { method, amount },
  });
}

export const ACTIVE_APPOINTMENT_STATUSES_EN = ["pending_confirmation", "confirmed", "paid"];
