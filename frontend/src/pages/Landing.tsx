import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Landing.css'

export function Landing() {
  const { isAuthenticated, user } = useAuth()

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('in')
            obs.unobserve(e.target)
          }
        }),
      { threshold: 0.12 },
    )
    document.querySelectorAll('.fi').forEach((el) => obs.observe(el))
    return () => obs.disconnect()
  }, [])

  return (
    <>
      {/* ════════════════ HEADER ════════════════ */}
      <header className="site-header">
        <div className="container">
          <div className="header-inner">
            <Link to="/" className="logo">
              re<span className="dot">·</span>min<span className="dot">·</span>da
            </Link>
            {isAuthenticated ? (
              <div className="header-auth">
                <span className="header-tenant">{user?.tenant_name}</span>
                <Link to="/app" className="btn-primary">Abrir o app →</Link>
              </div>
            ) : (
              <Link to="/login" className="btn-outline">Entrar</Link>
            )}
          </div>
        </div>
      </header>

      {/* ════════════════ HERO ════════════════ */}
      <section className="hero">
        <div className="container">
          <div className="hero-grid">

            {/* Texto */}
            <div className="fi">
              <div className="hero-eyebrow">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <circle cx="8" cy="8" r="8" fill="#ecfdf5" />
                  <path d="M4.5 8.5l2 2 5-5" stroke="#10b981" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Para salões, clínicas, pet shops e mais
              </div>

              <h1 className="display hero-title">
                Pare de confirmar<br />horário <span className="accent">na mão.</span>
              </h1>

              <p className="lead hero-sub">
                O Reminda confirma seus agendamentos pelo WhatsApp, cobra o sinal via Pix e lembra seus clientes automaticamente — enquanto você só atende.
              </p>

              <div className="chip-row">
                <span className="chip">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.967-.94 1.164-.173.199-.347.223-.644.075-.297-.149-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.521.149-.173.198-.297.298-.496.099-.198.05-.372-.025-.521-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.372-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z" fill="#25d366" />
                    <path d="M12.04 2C6.495 2 2 6.495 2 12.04c0 1.946.556 3.76 1.514 5.287L2 22l4.79-1.498A10.014 10.014 0 0012.04 22C17.585 22 22 17.505 22 11.96 22 6.415 17.585 2 12.04 2z" stroke="#25d366" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                  </svg>
                  WhatsApp automático
                </span>
                <span className="chip">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <circle cx="12" cy="12" r="9" stroke="#f59e0b" strokeWidth="1.5" />
                    <path d="M12 7v1.5M12 15.5V17M9.5 10c0-.83.67-1.5 1.5-1.5h2a1.5 1.5 0 010 3H11a1.5 1.5 0 000 3h2a1.5 1.5 0 001.5-1.5" stroke="#f59e0b" strokeWidth="1.4" strokeLinecap="round" />
                  </svg>
                  Pix integrado
                </span>
                <span className="chip">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <rect x="6" y="2" width="12" height="20" rx="2.5" stroke="#3b82f6" strokeWidth="1.5" />
                    <circle cx="12" cy="17" r="1" fill="#3b82f6" />
                  </svg>
                  Tudo no celular
                </span>
              </div>
            </div>

            {/* Phone mockup */}
            <div className="mockup-wrap fi d1">
              <div className="mockup-glow" aria-hidden="true" />
              <div className="phone" role="img" aria-label="Demonstração do Reminda no WhatsApp">
                <div className="phone-bar">
                  <div className="phone-pill" />
                </div>
                <div className="wa-top">
                  <div className="wa-avatar" aria-hidden="true">🤖</div>
                  <div>
                    <span className="wa-name">Reminda</span>
                    <span className="wa-status">● online</span>
                  </div>
                </div>
                <div className="wa-body">
                  <div className="bubble bubble-bot">
                    Oi, Ana! 👋 Sua consulta com o Dr. Carlos é <strong>amanhã às 14h</strong>. Confirmamos?<br /><br />
                    Digite <strong>1</strong> para ✅ Sim<br />
                    Digite <strong>2</strong> para ❌ Cancelar
                    <div className="btime">09:30</div>
                  </div>
                  <div className="bubble bubble-user">
                    1
                    <div className="btime">09:31 ✓✓</div>
                  </div>
                  <div className="bubble bubble-bot">
                    Perfeito! ✅ Te esperamos amanhã às 14h. Até lá 😊
                    <div className="btime">09:31</div>
                  </div>
                  <div className="pix-bubble">
                    <div className="pix-label">💳 Sinal via Pix</div>
                    <div className="pix-val">R$ 50,00 recebido</div>
                    <div className="pix-ok">
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <path d="M5 12l5 5L20 7" stroke="#059669" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      Confirmado · 08:45
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ════════════════ PROBLEM ════════════════ */}
      <section className="problem">
        <div className="container">
          <div className="problem-inner fi">
            <p className="eyebrow" style={{ color: 'rgba(255,255,255,.4)' }}>O problema</p>
            <div className="big-stat" aria-label="3 horas por semana">3h</div>
            <h2 className="h2 problem-title">
              É o tempo médio que donos de<br />pequenos negócios perdem toda semana
            </h2>
            <p className="problem-body">
              Confirmando horário por ligação. Lembrando cliente de pagar o sinal. Arrumando confusão de agenda. Tudo na raça, tudo manual. O Reminda resolve isso de vez.
            </p>
          </div>
        </div>
      </section>

      {/* ════════════════ PILLARS ════════════════ */}
      <section className="pillars">
        <div className="container">
          <div className="section-head fi">
            <p className="eyebrow">O que o Reminda faz</p>
            <h2 className="h2">Três coisas. Feitas direito.</h2>
          </div>
          <div className="cards">

            <div className="card fi">
              <div className="card-icon g">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.967-.94 1.164-.173.199-.347.223-.644.075-.297-.149-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.521.149-.173.198-.297.298-.496.099-.198.05-.372-.025-.521-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.372-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z" fill="#10b981" />
                  <path d="M12.04 2C6.495 2 2 6.495 2 12.04c0 1.946.556 3.76 1.514 5.287L2 22l4.79-1.498A10.014 10.014 0 0012.04 22C17.585 22 22 17.505 22 11.96 22 6.415 17.585 2 12.04 2z" stroke="#10b981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <h3 className="h3">WhatsApp automático</h3>
              <p>Confirmação e lembrete chegam no celular do cliente no momento certo. Sem você precisar digitar uma palavra.</p>
            </div>

            <div className="card fi d1">
              <div className="card-icon a">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle cx="12" cy="12" r="9" stroke="#f59e0b" strokeWidth="1.5" />
                  <path d="M12 7v1.5M12 15.5V17M9.5 10c0-.83.67-1.5 1.5-1.5h2a1.5 1.5 0 010 3H11a1.5 1.5 0 000 3h2a1.5 1.5 0 001.5-1.5" stroke="#f59e0b" strokeWidth="1.4" strokeLinecap="round" />
                </svg>
              </div>
              <h3 className="h3">Pix integrado</h3>
              <p>Cobra o sinal antes do horário. Quem paga, aparece. Corta o furo sem precisar ficar atrás de ninguém.</p>
            </div>

            <div className="card fi d2">
              <div className="card-icon b">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <rect x="5" y="2" width="14" height="20" rx="3" stroke="#3b82f6" strokeWidth="1.5" />
                  <circle cx="12" cy="17.5" r="1" fill="#3b82f6" />
                  <path d="M9 7h6M9 11h4" stroke="#3b82f6" strokeWidth="1.4" strokeLinecap="round" />
                </svg>
              </div>
              <h3 className="h3">Zero planilha</h3>
              <p>Agenda, clientes e cobranças num lugar só, no celular. Sem computador, sem Excel, sem dor de cabeça.</p>
            </div>

          </div>
        </div>
      </section>

      {/* ════════════════ HOW IT WORKS ════════════════ */}
      <section className="how">
        <div className="container">
          <div className="section-head fi">
            <p className="eyebrow">Como funciona</p>
            <h2 className="h2">Simples como deve ser.</h2>
          </div>
          <div className="steps">

            <div className="step fi">
              <div className="step-num">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle cx="12" cy="8" r="3.5" stroke="#10b981" strokeWidth="1.6" />
                  <path d="M5 20c0-3.87 3.13-7 7-7s7 3.13 7 7" stroke="#10b981" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
              </div>
              <h3 className="h3">Cadastre clientes e serviços</h3>
              <p>Nome, telefone e o que você oferece. Rápido, sem complicação, leva menos de 5 minutos.</p>
            </div>

            <div className="step fi d1">
              <div className="step-num">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <rect x="3" y="5" width="18" height="17" rx="2.5" stroke="#10b981" strokeWidth="1.6" />
                  <path d="M3 11h18" stroke="#10b981" strokeWidth="1.6" />
                  <path d="M8 3v4M16 3v4" stroke="#10b981" strokeWidth="1.6" strokeLinecap="round" />
                  <rect x="8" y="14" width="3" height="3" rx="0.5" fill="#10b981" />
                </svg>
              </div>
              <h3 className="h3">Crie o agendamento</h3>
              <p>Selecione cliente, serviço e horário. O Reminda já manda o WhatsApp e cobra o sinal via Pix.</p>
            </div>

            <div className="step fi d2">
              <div className="step-num">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M5 12.5l5 5 9-9" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <h3 className="h3">Só aparece e atende</h3>
              <p>Sinal recebido. Cliente confirmado. Lembrete enviado. Você só precisa estar lá.</p>
            </div>

          </div>
        </div>
      </section>

      {/* ════════════════ FOOTER ════════════════ */}
      <footer className="site-footer">
        <div className="container">
          <div className="logo" style={{ marginBottom: '8px' }}>
            re<span className="dot">·</span>min<span className="dot">·</span>da
          </div>
          <p className="tagline">Agendamentos sem complicação para pequenos negócios.</p>
          <p className="copy">© 2025 Reminda · Em desenvolvimento</p>
        </div>
      </footer>
    </>
  )
}
