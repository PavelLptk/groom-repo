import { useEffect, useState } from "react";
import { appointments, benefits, pets, reviews, salon, services, timeSlots } from "./data";

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
    <button className={`rounded-full px-5 py-3 text-sm font-semibold transition ${styles} ${className}`} {...props}>
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

function Modal({ title, children, onClose }) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-cocoa/30 p-4">
      <Card className="w-full max-w-md">
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
      <div className="mb-4 flex flex-wrap gap-2">
        <Badge className="bg-mint text-emerald-900">{service.type}</Badge>
        <Badge className="bg-orange-100 text-cocoa">{service.duration}</Badge>
      </div>
      <h3 className="text-xl font-bold text-cocoa">{service.title}</h3>
      <p className="mt-2 flex-1 text-slate-600">{service.short}</p>
      <div className="mt-5 flex items-center justify-between gap-3">
        <span className="text-lg font-black text-cocoa">{money(service.price)}</span>
        <Button onClick={() => routeTo(`service/${service.id}`)}>Выбрать услугу</Button>
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

function AppointmentCard({ item, compact = false }) {
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
      {!compact && (
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-slate-600">{money(item.amount)} · {item.payment}</p>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => routeTo("booking")}>Повторить</Button>
            <Button variant="secondary">Перенести</Button>
            <Button variant="secondary">Отменить</Button>
          </div>
        </div>
      )}
    </Card>
  );
}

function BookingSummary({ booking }) {
  const selectedService = services.find((service) => service.id === booking.serviceId);

  return (
    <Card className="bg-orange-50">
      <h3 className="text-xl font-bold text-cocoa">Итог записи</h3>
      <dl className="mt-4 space-y-2 text-sm text-slate-700">
        <div className="flex justify-between gap-4"><dt>Услуга</dt><dd className="font-semibold">{selectedService?.title || "Не выбрана"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Питомец</dt><dd className="font-semibold">{booking.petName || "Не указан"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Дата и время</dt><dd className="font-semibold">{booking.date || "Дата"} · {booking.time || "время"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Клиент</dt><dd className="font-semibold">{booking.name || "Имя"}</dd></div>
        <div className="flex justify-between gap-4"><dt>Уведомление</dt><dd className="font-semibold">{booking.notification}</dd></div>
        <div className="flex justify-between gap-4"><dt>Предоплата</dt><dd className="font-semibold">{booking.prepay ? "Нужна" : "Позже"}</dd></div>
      </dl>
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

      <Section title="Отзывы клиентов">
        <Grid>{reviews.map((review) => <Card key={review.name}><p className="text-slate-600">“{review.text}”</p><p className="mt-4 font-bold text-cocoa">{review.name}</p></Card>)}</Grid>
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
  const [filters, setFilters] = useState({ type: "Все", size: "Все", price: "Все" });
  const filteredServices = services.filter((service) => {
    const byType = filters.type === "Все" || service.type.includes(filters.type);
    const bySize = filters.size === "Все" || service.size === filters.size || service.size === "Любой";
    const byPrice = filters.price === "Все" || service.price <= Number(filters.price);
    return byType && bySize && byPrice;
  });

  return (
    <PageTitle title="Каталог услуг" subtitle="Фильтруйте услуги по животному, размеру и бюджету." >
      <Card className="mb-6 grid gap-4 md:grid-cols-3">
        <Field label="Тип животного">
          <Select value={filters.type} onChange={(event) => setFilters({ ...filters, type: event.target.value })}>
            {["Все", "Собака", "Кошка"].map((item) => <option key={item}>{item}</option>)}
          </Select>
        </Field>
        <Field label="Размер">
          <Select value={filters.size} onChange={(event) => setFilters({ ...filters, size: event.target.value })}>
            {["Все", "Любой", "Маленький", "Средний", "Крупный"].map((item) => <option key={item}>{item}</option>)}
          </Select>
        </Field>
        <Field label="Цена до">
          <Select value={filters.price} onChange={(event) => setFilters({ ...filters, price: event.target.value })}>
            <option>Все</option>
            <option value="1000">1 000 ₽</option>
            <option value="2500">2 500 ₽</option>
            <option value="4000">4 000 ₽</option>
          </Select>
        </Field>
      </Card>
      <Grid>{filteredServices.map((service) => <ServiceCard key={service.id} service={service} />)}</Grid>
    </PageTitle>
  );
}

function ServicePage({ serviceId }) {
  const service = services.find((item) => item.id === serviceId) || services[0];

  return (
    <PageTitle title={service.title} subtitle={service.description}>
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <div className="space-y-6">
          <Card>
            <h2 className="text-2xl font-bold text-cocoa">Что входит</h2>
            <ul className="mt-4 grid gap-3 md:grid-cols-2">
              {service.included.map((item) => <li key={item} className="rounded-2xl bg-orange-50 p-4 text-slate-700">{item}</li>)}
            </ul>
          </Card>
          <Card>
            <h2 className="text-2xl font-bold text-cocoa">Галерея</h2>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              {["До ухода", "Процесс", "После"].map((item) => (
                <div key={item} className="grid aspect-video place-items-center rounded-3xl bg-gradient-to-br from-orange-100 to-mint font-bold text-cocoa">{item}</div>
              ))}
            </div>
          </Card>
          <Card>
            <h2 className="text-2xl font-bold text-cocoa">Рекомендации и ограничения</h2>
            <p className="mt-3 text-slate-600">{service.recommendations}</p>
            <p className="mt-2 text-slate-600">{service.restrictions}</p>
          </Card>
        </div>
        <Card className="h-fit">
          <Badge className="bg-mint text-emerald-900">{service.pets}</Badge>
          <p className="mt-5 text-4xl font-black text-cocoa">{money(service.price)}</p>
          <p className="mt-2 text-slate-600">Примерная длительность: {service.duration}</p>
          <Button className="mt-6 w-full" onClick={() => routeTo("booking")}>Записаться</Button>
        </Card>
      </div>
    </PageTitle>
  );
}

function BookingPage() {
  const [step, setStep] = useState(0);
  const [booking, setBooking] = useState({
    serviceId: services[0].id,
    petName: pets[0].name,
    date: "2026-05-18",
    time: timeSlots[2],
    name: "Анна",
    phone: "+7 999 123-45-67",
    email: "anna@example.com",
    comment: "",
    notification: "Telegram",
    prepay: true,
  });
  const steps = ["Услуга", "Питомец", "Дата", "Контакты", "Проверка"];

  const update = (field, value) => setBooking((current) => ({ ...current, [field]: value }));
  const confirm = () => routeTo("success");

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
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="Питомец">
                <Select value={booking.petName} onChange={(event) => update("petName", event.target.value)}>
                  {pets.map((pet) => <option key={pet.id}>{pet.name}</option>)}
                  <option>Новый питомец</option>
                </Select>
              </Field>
              <Button variant="secondary" onClick={() => routeTo("pet")}>Создать профиль питомца</Button>
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
              <Field label="Имя клиента"><Input value={booking.name} onChange={(event) => update("name", event.target.value)} /></Field>
              <Field label="Телефон"><Input value={booking.phone} onChange={(event) => update("phone", event.target.value)} /></Field>
              <Field label="Email или Telegram"><Input value={booking.email} onChange={(event) => update("email", event.target.value)} /></Field>
              <Field label="Способ уведомления">
                <Select value={booking.notification} onChange={(event) => update("notification", event.target.value)}>
                  {["Telegram", "Телефон", "Email"].map((item) => <option key={item}>{item}</option>)}
                </Select>
              </Field>
              <Field label="Комментарий грумеру"><Textarea value={booking.comment} onChange={(event) => update("comment", event.target.value)} /></Field>
              <label className="flex items-center gap-3 rounded-2xl bg-orange-50 p-4 font-semibold text-slate-700">
                <input type="checkbox" checked={booking.prepay} onChange={(event) => update("prepay", event.target.checked)} />
                Нужна предоплата
              </label>
            </div>
          )}
          {step === 4 && <BookingSummary booking={booking} />}
          <div className="mt-6 flex justify-between gap-3">
            <Button variant="secondary" disabled={step === 0} onClick={() => setStep((value) => Math.max(0, value - 1))}>Назад</Button>
            {step < steps.length - 1 ? <Button onClick={() => setStep((value) => value + 1)}>Дальше</Button> : <Button onClick={confirm}>Подтвердить запись</Button>}
          </div>
        </Card>
        <BookingSummary booking={booking} />
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
          <Button variant="secondary" className="mt-4">Загрузить фото</Button>
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

function AccountPage() {
  return (
    <PageTitle title="Личный кабинет" subtitle="Контакты владельца, питомцы, ближайшие записи и история посещений.">
      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card>
          <h2 className="text-2xl font-bold text-cocoa">Анна Смирнова</h2>
          <p className="mt-2 text-slate-600">{salon.phone}</p>
          <p className="text-slate-600">anna@example.com</p>
          <Button className="mt-5" onClick={() => routeTo("pet")}>Добавить питомца</Button>
        </Card>
        <div className="space-y-8">
          <Section title="Питомцы"><Grid>{pets.map((pet) => <PetCard key={pet.id} pet={pet} />)}</Grid></Section>
          <Section title="Записи"><div className="grid gap-4">{appointments.map((item) => <AppointmentCard key={item.id} item={item} compact />)}</div></Section>
        </div>
      </div>
    </PageTitle>
  );
}

function AppointmentsPage() {
  const [tab, setTab] = useState("будущие");
  const [modal, setModal] = useState(null);
  const visible = appointments.filter((item) => {
    if (tab === "будущие") return ["ожидает подтверждения", "подтверждена", "оплачена"].includes(item.status);
    if (tab === "прошедшие") return item.status === "завершена";
    return item.status === "отменена";
  });

  return (
    <PageTitle title="Мои записи" subtitle="Управление будущими, прошедшими и отмененными бронированиями.">
      <div className="mb-6 flex flex-wrap gap-2">
        {["будущие", "прошедшие", "отмененные"].map((item) => (
          <Button key={item} variant={tab === item ? "primary" : "secondary"} onClick={() => setTab(item)}>{item}</Button>
        ))}
      </div>
      <div className="grid gap-4">
        {visible.map((item) => (
          <Card key={item.id}>
            <AppointmentCard item={item} compact />
            <div className="mt-4 flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => setModal("Перенос записи")}>Перенести</Button>
              <Button variant="secondary" onClick={() => setModal("Отмена записи")}>Отменить</Button>
              <Button onClick={() => routeTo("payment")}>Оплатить</Button>
            </div>
          </Card>
        ))}
      </div>
      {modal && (
        <Modal title={modal} onClose={() => setModal(null)}>
          <p className="text-slate-600">Mock-модальное окно. В реальной версии здесь будет выбор новой даты или подтверждение отмены.</p>
          <Button className="mt-5" onClick={() => setModal(null)}>Готово</Button>
        </Modal>
      )}
    </PageTitle>
  );
}

function SuccessPage() {
  const service = services[2];

  return (
    <PageTitle title="Запись создана" subtitle="Мы отправим напоминание выбранным способом уведомления.">
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card>
          <div className="text-6xl">✅</div>
          <h2 className="mt-4 text-3xl font-black text-cocoa">Ваша запись ожидает подтверждения</h2>
          <p className="mt-3 text-slate-600">Комплексный груминг для Бублика: 18 мая, 12:30. Контакт: +7 999 123-45-67, уведомление в Telegram.</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button onClick={() => routeTo("appointments")}>Перейти в Мои записи</Button>
            <Button variant="secondary">Добавить в календарь</Button>
          </div>
        </Card>
        <Card>
          <h3 className="text-xl font-bold text-cocoa">Предоплата</h3>
          <p className="mt-2 text-slate-600">Для фиксации времени можно внести {money(1000)} из {money(service.price)}.</p>
          <Button className="mt-5 w-full" onClick={() => routeTo("payment")}>Перейти к оплате</Button>
        </Card>
      </div>
    </PageTitle>
  );
}

function PaymentPage() {
  const [paid, setPaid] = useState(false);
  const service = services[2];

  return (
    <PageTitle title="Оплата / Предоплата" subtitle="Mock-страница без реальной платежной интеграции.">
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card className="space-y-4">
          <Field label="Способ оплаты">
            <Select><option>Банковская карта</option><option>СБП</option><option>Наличными в салоне</option></Select>
          </Field>
          <Field label="Номер карты"><Input placeholder="0000 0000 0000 0000" /></Field>
          <div className="grid gap-4 md:grid-cols-2">
            <Field label="Срок"><Input placeholder="12/29" /></Field>
            <Field label="CVC"><Input placeholder="123" /></Field>
          </div>
          <Button onClick={() => setPaid(true)}>Оплатить mock</Button>
        </Card>
        <Card>
          <h3 className="text-xl font-bold text-cocoa">Сводка</h3>
          <p className="mt-3 text-slate-600">Комплексный груминг · Бублик · 18 мая, 12:30</p>
          <p className="mt-4 text-sm text-slate-500">Предоплата</p>
          <p className="text-3xl font-black text-cocoa">{money(1000)}</p>
          <p className="mt-2 text-sm text-slate-500">Полная стоимость: {money(service.price)}</p>
          <Badge className={`mt-5 ${paid ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"}`}>
            {paid ? "paid" : "ожидает оплаты"}
          </Badge>
        </Card>
      </div>
    </PageTitle>
  );
}

function ContactsPage() {
  return (
    <PageTitle title="Контакты" subtitle="Информация о салоне, часы работы, карта-заглушка и форма обратной связи.">
      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <Card>
          <div className="grid aspect-video place-items-center rounded-3xl bg-gradient-to-br from-orange-100 to-mint text-center text-xl font-bold text-cocoa">
            Карта-заглушка: {salon.address}
          </div>
          <div className="mt-6 grid gap-3 text-slate-700 md:grid-cols-2">
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

  useEffect(() => {
    const onHashChange = () => setHash(window.location.hash.replace("#", ""));
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const [page, id] = hash.split("/");
  const currentPage = {
    "": <HomePage />,
    services: <ServicesPage />,
    service: <ServicePage serviceId={id} />,
    booking: <BookingPage />,
    pet: <PetProfilePage />,
    account: <AccountPage />,
    appointments: <AppointmentsPage />,
    success: <SuccessPage />,
    payment: <PaymentPage />,
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
