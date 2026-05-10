import { useCallback, useEffect, useState } from "react";
import { appointments, benefits, pets, salon, services, timeSlots } from "./data";

const navItems = [
  ["Главная", ""],
  ["Услуги", "services"],
  ["Запись", "booking"],
  ["Кабинет", "account"],
  ["Мои записи", "appointments"],
  ["Контакты", "contacts"],
];

const statusStyles = {
  "ожидает подтверждения": "bg-amber-100 text-amber-800",
  подтверждена: "bg-blue-100 text-blue-800",
  оплачена: "bg-emerald-100 text-emerald-800",
  отменена: "bg-rose-100 text-rose-800",
  завершена: "bg-slate-200 text-slate-700",
};

const currentAppointmentStatuses = ["ожидает подтверждения", "подтверждена", "оплачена"];

function appointmentCanPay(item) {
  if (item.status === "отменена" || item.status === "оплачена") return false;
  if (item.payment === "оплачена") return false;
  return true;
}

function mergeDemoPaid(item, demoPaidById) {
  if (!demoPaidById[item.id]) return item;
  return { ...item, status: "оплачена", payment: "оплачена" };
}

function money(value) {
  return `${value.toLocaleString("ru-RU")} ₽`;
}

function routeTo(path) {
  window.location.hash = path ? `#${path}` : "#";
}

function Button({ children, variant = "primary", className = "", ...props }) {
  const styles =
    variant === "secondary"
      ? "border border-orange-200 bg-white text-cocoa hover:bg-orange-50"
      : "bg-cocoa text-white hover:bg-orange-950";

  return (
    <button className={`rounded-full px-5 py-3 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${styles} ${className}`} {...props}>
      {children}
    </button>
  );
}

function Card({ children, className = "" }) {
  return <section className={`rounded-3xl border border-orange-100 bg-white p-6 shadow-soft ${className}`}>{children}</section>;
}

function Badge({ children, className = "" }) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${className}`}>{children}</span>;
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function Input(props) {
  return <input className="w-full rounded-2xl border border-orange-100 bg-white px-4 py-3 outline-none focus:border-cocoa" {...props} />;
}

function Select({ children, ...props }) {
  return (
    <select className="w-full rounded-2xl border border-orange-100 bg-white px-4 py-3 outline-none focus:border-cocoa" {...props}>
      {children}
    </select>
  );
}

function Textarea(props) {
  return <textarea className="min-h-28 w-full rounded-2xl border border-orange-100 bg-white px-4 py-3 outline-none focus:border-cocoa" {...props} />;
}

function Modal({ title, children, onClose, wide = false }) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-cocoa/30 p-4">
      <Card className={`w-full ${wide ? "max-w-lg" : "max-w-md"}`}>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-xl font-bold text-cocoa">{title}</h3>
          <button className="text-2xl text-slate-400" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </div>
        {children}
      </Card>
    </div>
  );
}

function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-orange-100 bg-cream/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4">
        <button className="text-2xl font-black text-cocoa" onClick={() => routeTo("")}>
          {salon.name}
        </button>
        <nav className="flex flex-wrap gap-2 text-sm font-semibold text-slate-600">
          {navItems.map(([label, path]) => (
            <button key={path || "home"} className="rounded-full px-3 py-2 hover:bg-white" onClick={() => routeTo(path)}>
              {label}
            </button>
          ))}
        </nav>
        <Button onClick={() => routeTo("booking")}>Записаться</Button>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="mt-16 bg-cocoa text-orange-50">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-10 md:grid-cols-3">
        <div>
          <h3 className="text-xl font-bold">{salon.name}</h3>
          <p className="mt-2 text-orange-100">{salon.tagline}</p>
        </div>
        <div className="space-y-1 text-sm">
          <p>{salon.address}</p>
          <p>{salon.phone}</p>
          <p>{salon.email}</p>
        </div>
        <div className="space-y-1 text-sm">
          <p>{salon.telegram}</p>
          <p>{salon.socials.join(" · ")}</p>
          <p>Политика конфиденциальности</p>
        </div>
      </div>
    </footer>
  );
}

function ServiceCard({ service }) {
  return (
    <Card className="flex h-full flex-col">
      <h3 className="text-xl font-bold text-cocoa">{service.title}</h3>
      <p className="mt-2 text-slate-600">{service.description}</p>
      <div className="mt-4 flex-1 space-y-2 text-sm text-slate-600">
        <p><b>Рекомендации:</b> {service.recommendations}</p>
        <p><b>Ограничения:</b> {service.restrictions}</p>
      </div>
      <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-lg font-black text-cocoa">{money(service.price)}</p>
          <p className="text-sm text-slate-500">{service.duration}</p>
        </div>
        <Button onClick={() => routeTo(`booking/${service.id}`)}>Записаться</Button>
      </div>
    </Card>
  );
}

function PetCard({ pet }) {
  return (
    <Card>
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-mint text-2xl">🐾</div>
      <h3 className="text-xl font-bold text-cocoa">{pet.name}</h3>
      <p className="text-slate-600">{pet.type}, {pet.breed}</p>
      <p className="mt-2 text-sm text-slate-500">{pet.size} · {pet.age} · {pet.notes}</p>
    </Card>
  );
}

function AppointmentCard({ item, compact = false, footer = null }) {
  const service = services.find((entry) => entry.id === item.serviceId);

  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-cocoa">{service?.title}</h3>
          <p className="text-slate-600">{item.pet} · {item.date}, {item.time}</p>
          {!compact && <p className="mt-2 text-sm text-slate-500">{item.address}</p>}
        </div>
        <Badge className={statusStyles[item.status] || "bg-slate-100 text-slate-700"}>{item.status}</Badge>
      </div>
      <div className="mt-4 border-t border-orange-100 pt-4">
        <p className="text-lg font-black text-cocoa">{money(item.amount)}</p>
        <p className="mt-1 text-sm text-slate-600">
          <span className="font-semibold text-slate-700">Оплата:</span> {item.payment}
        </p>
      </div>
      {!compact && (
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => routeTo("booking")}>Повторить</Button>
            <Button variant="secondary">Перенести</Button>
            <Button variant="secondary">Отменить</Button>
          </div>
        </div>
      )}
      {footer}
    </Card>
  );
}

function BookingSummary({ booking, onPrepayChange = () => {}, showPrepayBlock = true }) {
  const selectedService = services.find((service) => service.id === booking.serviceId);

  return (
    <Card className="bg-orange-50">
      <h3 className="text-xl font-bold text-cocoa">Итог записи</h3>
      <dl className="mt-4 space-y-2 text-sm text-slate-700">
        <div className="flex justify-between gap-4"><dt>Услуга</dt><dd className="font-semibold">{selectedService?.title || "Не выбрана"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Стоимость</dt><dd className="font-semibold">{selectedService ? money(selectedService.price) : "—"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Питомец</dt><dd className="font-semibold">{booking.petName || "Не указан"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Дата и время</dt><dd className="font-semibold">{booking.date || "Дата"} · {booking.time || "время"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Клиент</dt><dd className="font-semibold">{booking.name || "Имя"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Уведомление</dt><dd className="font-semibold">{booking.notification}</dd></div>
        <div className="flex justify-between gap-4"><dt>Предоплата</dt><dd className="font-semibold">{booking.prepay ? "Нужна" : "Позже"}</dd></div>
      </dl>
      {showPrepayBlock && (
        <div className="mt-5 rounded-2xl border border-orange-200 bg-white p-4 shadow-sm">
          <h4 className="text-sm font-bold uppercase tracking-wide text-cocoa">Предоплата</h4>
          <p className="mt-2 text-sm leading-relaxed text-slate-600">
            На востребованные слоты и длинные услуги салон может запросить предоплату. Отметьте, если готовы внести её заранее — мы уточним сумму и способ оплаты в сообщении или по телефону.
          </p>
          <label className="mt-4 flex cursor-pointer items-start gap-3 rounded-2xl border border-orange-100 bg-orange-50/80 p-4 text-sm font-semibold text-slate-700">
            <input className="mt-1 h-4 w-4 shrink-0 accent-cocoa" type="checkbox" checked={booking.prepay} onChange={(event) => onPrepayChange(event.target.checked)} />
            <span>Нужна предоплата</span>
          </label>
        </div>
      )}
    </Card>
  );
}

function HomePage() {
  return (
    <>
      <section className="grid items-center gap-10 py-12 md:grid-cols-[1.1fr_0.9fr]">
        <div>
          <Badge className="bg-mint text-emerald-900">Запись без звонков за 2 минуты</Badge>
          <h1 className="mt-5 text-5xl font-black tracking-tight text-cocoa md:text-7xl">Груминг, после которого питомцу комфортно</h1>
          <p className="mt-5 max-w-2xl text-lg text-slate-600">{salon.tagline}. Выберите услугу, дату, питомца и получите напоминание перед визитом.</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button onClick={() => routeTo("booking")}>Записаться</Button>
            <Button variant="secondary" onClick={() => routeTo("services")}>Посмотреть услуги</Button>
          </div>
        </div>
        <div className="rounded-[2rem] bg-white p-6 shadow-soft">
          <div className="grid aspect-square place-items-center rounded-[1.5rem] bg-gradient-to-br from-orange-100 to-mint text-center">
            <div>
              <p className="text-7xl">🐶</p>
              <p className="mt-4 text-xl font-bold text-cocoa">Уход по породе, размеру и характеру</p>
            </div>
          </div>
        </div>
      </section>

      <Section title="Популярные услуги" action={<Button variant="secondary" onClick={() => routeTo("services")}>Все услуги</Button>}>
        <Grid>{services.slice(0, 3).map((service) => <ServiceCard key={service.id} service={service} />)}</Grid>
      </Section>

      <Section title="Как это работает">
        <Grid>
          {["Выберите услугу", "Укажите питомца", "Подберите дату и время", "Подтвердите запись"].map((step, index) => (
            <Card key={step}>
              <span className="text-3xl font-black text-orange-200">0{index + 1}</span>
              <h3 className="mt-3 text-xl font-bold text-cocoa">{step}</h3>
            </Card>
          ))}
        </Grid>
      </Section>

      <Section title="Преимущества">
        <Grid>{benefits.map((benefit) => <Card key={benefit}><p className="text-lg font-semibold text-slate-700">{benefit}</p></Card>)}</Grid>
      </Section>

    </>
  );
}

function Section({ title, action, children }) {
  return (
    <section className="py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-3xl font-black text-cocoa">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

function Grid({ children }) {
  return <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">{children}</div>;
}

function ServicesPage() {
  return (
    <PageTitle title="Каталог услуг" subtitle="Выберите подходящий уход и сразу переходите к записи." >
      <Grid>{services.map((service) => <ServiceCard key={service.id} service={service} />)}</Grid>
    </PageTitle>
  );
}

function bookingInitialServiceIdProp(initialServiceId) {
  return initialServiceId && services.some((s) => s.id === initialServiceId) ? initialServiceId : services[0].id;
}

function BookingPage({ initialServiceId }) {
  const [step, setStep] = useState(0);
  const [contactError, setContactError] = useState("");
  const [isConfirming, setIsConfirming] = useState(false);
  const [booking, setBooking] = useState(() => ({
    serviceId: bookingInitialServiceIdProp(initialServiceId),
    petName: pets[0].name,
    date: "2026-05-18",
    time: timeSlots[2],
    name: "Анна",
    phone: "+7 999 123-45-67",
    email: "anna@example.com",
    comment: "",
    notification: "Telegram",
    prepay: true,
  }));
  const steps = ["Услуга", "Питомец", "Дата", "Контакты", "Проверка"];

  useEffect(() => {
    if (!initialServiceId || !services.some((s) => s.id === initialServiceId)) return;
    setBooking((prev) => ({ ...prev, serviceId: initialServiceId }));
    setStep(0);
  }, [initialServiceId]);

  const update = (field, value) => {
    if ((field === "name" || field === "phone") && contactError) {
      setContactError("");
    }
    setBooking((current) => ({ ...current, [field]: value }));
  };
  const goNext = () => {
    if (step === 3 && (!booking.name.trim() || !booking.phone.trim())) {
      setContactError("Мы не нашли данные записи");
      return;
    }
    setStep((value) => Math.min(steps.length - 1, value + 1));
  };
  const confirm = () => {
    setIsConfirming(true);
    setTimeout(() => routeTo("appointments"), 1200);
  };

  return (
    <PageTitle title="Онлайн-запись" subtitle="Пошаговый wizard показывает будущую структуру бронирования без бэкенда.">
      <div className="mb-6 flex flex-wrap gap-2">
        {steps.map((item, index) => (
          <Badge key={item} className={index === step ? "bg-cocoa text-white" : "bg-orange-100 text-cocoa"}>{index + 1}. {item}</Badge>
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card>
          {step === 0 && (
            <Field label="Выберите услугу">
              <Select value={booking.serviceId} onChange={(event) => update("serviceId", event.target.value)}>
                {services.map((service) => <option key={service.id} value={service.id}>{service.title} · {money(service.price)}</option>)}
              </Select>
            </Field>
          )}
          {step === 1 && (
            <div className="grid gap-4">
              <Field label="Питомец">
                <Select value={booking.petName} onChange={(event) => update("petName", event.target.value)}>
                  {pets.map((pet) => <option key={pet.id}>{pet.name}</option>)}
                  <option>Новый питомец</option>
                </Select>
              </Field>
            </div>
          )}
          {step === 2 && (
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="Дата"><Input type="date" value={booking.date} onChange={(event) => update("date", event.target.value)} /></Field>
              <Field label="Свободное время">
                <div className="grid grid-cols-3 gap-2">
                  {timeSlots.map((slot) => (
                    <button key={slot} className={`rounded-2xl border p-3 font-semibold ${booking.time === slot ? "border-cocoa bg-cocoa text-white" : "border-orange-100 bg-white text-cocoa"}`} onClick={() => update("time", slot)}>
                      {slot}
                    </button>
                  ))}
                </div>
              </Field>
            </div>
          )}
          {step === 3 && (
            <div className="grid gap-4 md:grid-cols-2">
              {contactError && (
                <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 font-semibold text-rose-800 md:col-span-2">
                  {contactError}
                </div>
              )}
              <Field label="Имя клиента"><Input value={booking.name} onChange={(event) => update("name", event.target.value)} /></Field>
              <Field label="Телефон"><Input value={booking.phone} onChange={(event) => update("phone", event.target.value)} /></Field>
              <Field label="Email или Telegram"><Input value={booking.email} onChange={(event) => update("email", event.target.value)} /></Field>
              <Field label="Способ уведомления">
                <Select value={booking.notification} onChange={(event) => update("notification", event.target.value)}>
                  {["Telegram", "Телефон", "Email"].map((item) => <option key={item}>{item}</option>)}
                </Select>
              </Field>
              <Field label="Комментарий грумеру"><Textarea value={booking.comment} onChange={(event) => update("comment", event.target.value)} /></Field>
            </div>
          )}
          {step === 4 && (
            <p className="text-sm leading-relaxed text-slate-600">
              Проверьте итог записи в блоке справа: услугу, время и предоплату. Если всё верно, нажмите «Подтвердить запись».
            </p>
          )}
          {isConfirming && (
            <div className="mt-6 rounded-2xl border border-orange-200 bg-orange-50 p-4 font-semibold text-cocoa">
              Подтверждаем запись...
            </div>
          )}
          <div className="mt-6 flex justify-between gap-3">
            <Button variant="secondary" disabled={step === 0 || isConfirming} onClick={() => setStep((value) => Math.max(0, value - 1))}>Назад</Button>
            {step < steps.length - 1 ? <Button disabled={isConfirming} onClick={goNext}>Дальше</Button> : <Button disabled={isConfirming} onClick={confirm}>{isConfirming ? "Подтверждаем..." : "Подтвердить запись"}</Button>}
          </div>
        </Card>
        <BookingSummary booking={booking} onPrepayChange={(value) => update("prepay", value)} showPrepayBlock />
      </div>
    </PageTitle>
  );
}

function PetProfilePage() {
  return (
    <PageTitle title="Профиль питомца" subtitle="Создание или редактирование данных, которые помогут грумеру подготовиться.">
      <Card className="grid gap-4 md:grid-cols-2">
        <div className="grid place-items-center rounded-3xl bg-orange-50 p-8 text-center">
          <div className="text-6xl">🐕</div>
        </div>
        <div className="grid gap-4">
          <Field label="Имя питомца"><Input defaultValue="Бублик" /></Field>
          <Field label="Вид животного"><Select defaultValue="Собака"><option>Собака</option><option>Кошка</option><option>Другое</option></Select></Field>
          <Field label="Порода"><Input defaultValue="Корги" /></Field>
          <Field label="Размер"><Select defaultValue="Средний"><option>Маленький</option><option>Средний</option><option>Крупный</option></Select></Field>
          <Field label="Возраст"><Input defaultValue="3 года" /></Field>
          <Field label="Особенности ухода, аллергии, поведение"><Textarea defaultValue="Боится фена, просим делать короткие паузы." /></Field>
          <Button onClick={() => routeTo("account")}>Сохранить питомца</Button>
        </div>
      </Card>
    </PageTitle>
  );
}

function digitsOnly(value) {
  return value.replace(/\D/g, "");
}

function validatePaymentFields(method, { cardNumber, expiry, cvv, phoneSbp }) {
  if (method === "card") {
    const cardDigits = digitsOnly(cardNumber);
    if (cardDigits.length !== 16) {
      return "Введите номер карты полностью — 16 цифр.";
    }
    const exp = expiry.trim();
    if (!/^\d{2}\/\d{2}$/.test(exp)) {
      return "Укажите срок действия в формате ММ/ГГ.";
    }
    const month = Number(exp.slice(0, 2));
    if (month < 1 || month > 12) {
      return "Месяц в сроке действия должен быть от 01 до 12.";
    }
    const cvvDigits = digitsOnly(cvv);
    if (cvvDigits.length !== 3 && cvvDigits.length !== 4) {
      return "Введите CVC/CVV — 3 или 4 цифры.";
    }
    return null;
  }
  const phoneDigits = digitsOnly(phoneSbp);
  if (phoneDigits.length < 11) {
    return "Укажите номер телефона полностью — не менее 11 цифр.";
  }
  if (!phoneDigits.startsWith("7")) {
    return "Номер должен быть в формате РФ: начинается с 7 после +.";
  }
  return null;
}

function PaymentModalForm({ appointment, onClose, onPaid }) {
  const service = services.find((s) => s.id === appointment.serviceId);
  const [method, setMethod] = useState("card");
  const [cardNumber, setCardNumber] = useState("");
  const [expiry, setExpiry] = useState("");
  const [cvv, setCvv] = useState("");
  const [phoneSbp, setPhoneSbp] = useState("+7 ");
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    const message = validatePaymentFields(method, { cardNumber, expiry, cvv, phoneSbp });
    if (message) {
      setSubmitError(message);
      return;
    }
    setSubmitError(null);
    onPaid?.();
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div>
        <p className="text-slate-600">Оплата прошла успешно (демо). Карточка записи обновлена до перезагрузки страницы; после обновления снова покажутся исходные данные из моков.</p>
        <Button className="mt-5 w-full sm:w-auto" onClick={onClose}>Закрыть</Button>
      </div>
    );
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div className="rounded-2xl border border-orange-100 bg-orange-50/80 p-4 text-sm text-slate-700">
        <p className="font-semibold text-cocoa">{service?.title ?? "Услуга"}</p>
        <p className="mt-1">{appointment.pet} · {appointment.date}, {appointment.time}</p>
        <p className="mt-2 text-lg font-black text-cocoa">{money(appointment.amount)}</p>
      </div>
      <p className="text-xs text-slate-500">Учебная форма: реальные платежи не выполняются.</p>
      <Field label="Способ оплаты">
        <Select
          value={method}
          onChange={(event) => {
            setSubmitError(null);
            setMethod(event.target.value);
          }}
        >
          <option value="card">Банковская карта</option>
          <option value="sbp">СБП</option>
        </Select>
      </Field>
      {submitError ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-800" role="alert">
          {submitError}
        </div>
      ) : null}
      {method === "card" ? (
        <>
          <Field label="Номер карты">
            <Input
              inputMode="numeric"
              autoComplete="cc-number"
              placeholder="0000 0000 0000 0000"
              maxLength={19}
              value={cardNumber}
              onChange={(event) => {
                setSubmitError(null);
                setCardNumber(event.target.value);
              }}
            />
          </Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Срок (ММ/ГГ)">
              <Input
                placeholder="ММ/ГГ"
                maxLength={5}
                value={expiry}
                onChange={(event) => {
                  setSubmitError(null);
                  setExpiry(event.target.value);
                }}
              />
            </Field>
            <Field label="CVC/CVV">
              <Input
                inputMode="numeric"
                type="password"
                placeholder="•••"
                maxLength={4}
                value={cvv}
                onChange={(event) => {
                  setSubmitError(null);
                  setCvv(event.target.value);
                }}
              />
            </Field>
          </div>
        </>
      ) : (
        <Field label="Телефон, привязанный к СБП">
          <Input
            type="tel"
            value={phoneSbp}
            onChange={(event) => {
              setSubmitError(null);
              setPhoneSbp(event.target.value);
            }}
            placeholder="+7 900 000-00-00"
          />
        </Field>
      )}
      <div className="flex flex-wrap gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onClose}>Отмена</Button>
        <Button type="submit">Оплатить</Button>
      </div>
    </form>
  );
}

function AppointmentRecordActions({ item, onOpenPay, onOpenInfo }) {
  return (
    <div className="flex flex-wrap gap-2 border-t border-orange-100 pt-4">
      {appointmentCanPay(item) ? (
        <Button type="button" onClick={() => onOpenPay(item)}>Оплатить</Button>
      ) : null}
      <Button variant="secondary" type="button" onClick={() => routeTo("booking")}>Повторить</Button>
      <Button variant="secondary" type="button" onClick={() => onOpenInfo("Перенос записи")}>Перенести</Button>
      <Button variant="secondary" type="button" onClick={() => onOpenInfo("Отмена записи")}>Отменить</Button>
    </div>
  );
}

function AccountPage({ demoPaidById, markDemoPaid }) {
  const [modal, setModal] = useState(null);
  const currentAppointments = appointments.filter((item) => currentAppointmentStatuses.includes(item.status));

  return (
    <PageTitle title="Личный кабинет" subtitle="Контакты владельца, питомцы и ближайшие записи.">
      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card>
          <h2 className="text-2xl font-bold text-cocoa">Анна Смирнова</h2>
          <p className="mt-2 text-slate-600">{salon.phone}</p>
          <p className="text-slate-600">anna@example.com</p>
          <Button className="mt-5" onClick={() => routeTo("pet")}>Добавить питомца</Button>
        </Card>
        <div className="space-y-8">
          <Section title="Питомцы"><Grid>{pets.map((pet) => <PetCard key={pet.id} pet={pet} />)}</Grid></Section>
          <Section title="Записи">
            <div className="grid gap-4">
              {currentAppointments.map((item) => {
                const merged = mergeDemoPaid(item, demoPaidById);
                return (
                  <AppointmentCard
                    key={item.id}
                    item={merged}
                    compact
                    footer={
                      <AppointmentRecordActions
                        item={merged}
                        onOpenPay={(entry) => setModal({ kind: "pay", appointment: entry })}
                        onOpenInfo={(title) => setModal({ kind: "info", title })}
                      />
                    }
                  />
                );
              })}
            </div>
          </Section>
        </div>
      </div>
      {modal?.kind === "info" && (
        <Modal title={modal.title} onClose={() => setModal(null)}>
          <p className="text-slate-600">Mock-модальное окно. В реальной версии здесь будет выбор новой даты или подтверждение отмены.</p>
          <Button className="mt-5" onClick={() => setModal(null)}>Готово</Button>
        </Modal>
      )}
      {modal?.kind === "pay" && (
        <Modal wide title="Оплата записи" onClose={() => setModal(null)}>
          <PaymentModalForm
            appointment={modal.appointment}
            onClose={() => setModal(null)}
            onPaid={() => markDemoPaid(modal.appointment.id)}
          />
        </Modal>
      )}
    </PageTitle>
  );
}

function AppointmentsPage({ demoPaidById, markDemoPaid }) {
  const [modal, setModal] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const currentAppointments = appointments.filter((item) => currentAppointmentStatuses.includes(item.status));

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <PageTitle title="Мои записи" subtitle="Активные записи: подтверждённые, ожидающие и оплаченные. История отменённых и завершённых — в будущей версии или через поддержку.">
      <div className="grid gap-4">
        {isLoading ? (
          <Card className="animate-pulse">
            <p className="font-semibold text-cocoa">Загружаем записи...</p>
            <p className="mt-2 text-sm text-slate-500">Проверяем актуальные бронирования.</p>
          </Card>
        ) : (
          currentAppointments.map((item) => {
            const merged = mergeDemoPaid(item, demoPaidById);
            return (
              <AppointmentCard
                key={item.id}
                item={merged}
                compact
                footer={
                  <AppointmentRecordActions
                    item={merged}
                    onOpenPay={(entry) => setModal({ kind: "pay", appointment: entry })}
                    onOpenInfo={(title) => setModal({ kind: "info", title })}
                  />
                }
              />
            );
          })
        )}
      </div>
      {modal?.kind === "info" && (
        <Modal title={modal.title} onClose={() => setModal(null)}>
          <p className="text-slate-600">Mock-модальное окно. В реальной версии здесь будет выбор новой даты или подтверждение отмены.</p>
          <Button className="mt-5" onClick={() => setModal(null)}>Готово</Button>
        </Modal>
      )}
      {modal?.kind === "pay" && (
        <Modal wide title="Оплата записи" onClose={() => setModal(null)}>
          <PaymentModalForm
            appointment={modal.appointment}
            onClose={() => setModal(null)}
            onPaid={() => markDemoPaid(modal.appointment.id)}
          />
        </Modal>
      )}
    </PageTitle>
  );
}

function ContactsPage() {
  return (
    <PageTitle title="Контакты" subtitle="Информация о салоне, часы работы и форма обратной связи.">
      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <Card>
          <div className="grid gap-3 text-slate-700 md:grid-cols-2">
            <p><b>Адрес:</b> {salon.address}</p>
            <p><b>Телефон:</b> {salon.phone}</p>
            <p><b>Email:</b> {salon.email}</p>
            <p><b>Telegram:</b> {salon.telegram}</p>
            <p><b>Часы:</b> {salon.hours}</p>
            <p><b>Соцсети:</b> {salon.socials.join(", ")}</p>
          </div>
        </Card>
        <Card className="space-y-4">
          <Field label="Ваше имя"><Input placeholder="Имя" /></Field>
          <Field label="Контакт"><Input placeholder="Телефон или Telegram" /></Field>
          <Field label="Сообщение"><Textarea placeholder="Как мы можем помочь?" /></Field>
          <Button>Отправить</Button>
        </Card>
      </div>
    </PageTitle>
  );
}

function PageTitle({ title, subtitle, children }) {
  return (
    <div className="py-10">
      <div className="mb-8 max-w-3xl">
        <h1 className="text-4xl font-black text-cocoa md:text-5xl">{title}</h1>
        <p className="mt-3 text-lg text-slate-600">{subtitle}</p>
      </div>
      {children}
    </div>
  );
}

export default function App() {
  const [hash, setHash] = useState(window.location.hash.replace("#", ""));
  const [demoPaidById, setDemoPaidById] = useState({});
  const markDemoPaid = useCallback((appointmentId) => {
    setDemoPaidById((prev) => ({ ...prev, [appointmentId]: true }));
  }, []);

  useEffect(() => {
    const onHashChange = () => setHash(window.location.hash.replace("#", ""));
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const hashSegments = hash.split("/").filter(Boolean);
  const page = hashSegments[0] ?? "";
  const bookingServiceSegment = page === "booking" ? hashSegments[1] : undefined;
  const bookingInitialServiceId =
    bookingServiceSegment && services.some((s) => s.id === bookingServiceSegment) ? bookingServiceSegment : undefined;

  const currentPage = {
    "": <HomePage />,
    services: <ServicesPage />,
    booking: <BookingPage initialServiceId={bookingInitialServiceId} />,
    pet: <PetProfilePage />,
    account: <AccountPage demoPaidById={demoPaidById} markDemoPaid={markDemoPaid} />,
    appointments: <AppointmentsPage demoPaidById={demoPaidById} markDemoPaid={markDemoPaid} />,
    contacts: <ContactsPage />,
  }[page] || <HomePage />;

  return (
    <div className="min-h-screen bg-cream text-slate-900">
      <Header />
      <main className="mx-auto max-w-7xl px-4">{currentPage}</main>
      <Footer />
    </div>
  );
}
