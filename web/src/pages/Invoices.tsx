// Invoices — Invoice management with KPIs, filterable table, and create modal
// Pattern: tok() + GCard (mirrors Dashboard.tsx)

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Plus, FileText, Clock, AlertCircle, CheckCircle, Search } from 'lucide-react'
import { Badge, Button, Input, Modal } from '../components'

// ── Theme helpers ─────────────────────────────────────────────────────────────

function useIsDark() {
  const [dark, setDark] = useState(() => !document.documentElement.classList.contains('light'))
  useEffect(() => {
    const obs = new MutationObserver(() =>
      setDark(!document.documentElement.classList.contains('light'))
    )
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => obs.disconnect()
  }, [])
  return dark
}

function tok(dark: boolean) {
  return {
    t1:       dark ? '#f1f5f9' : '#0f172a',
    t2:       dark ? '#cbd5e1' : '#334155',
    t3:       dark ? '#94a3b8' : '#64748b',
    t4:       dark ? '#475569' : '#94a3b8',
    div:      dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)',
    cardBg:   dark ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.82)',
    cardBord: dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
    subBg:    dark ? 'rgba(255,255,255,0.03)'  : 'rgba(0,0,0,0.03)',
    subBord:  dark ? 'rgba(255,255,255,0.06)'  : 'rgba(0,0,0,0.07)',
  }
}

function GCard({
  dark,
  children,
  style,
}: {
  dark: boolean
  children: React.ReactNode
  style?: React.CSSProperties
}) {
  const c = tok(dark)
  return (
    <div
      style={{
        background: c.cardBg,
        border: `1px solid ${c.cardBord}`,
        borderRadius: 14,
        backdropFilter: 'blur(24px) saturate(180%)',
        WebkitBackdropFilter: 'blur(24px) saturate(180%)',
        boxShadow: dark
          ? '0 4px 24px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.07)'
          : '0 4px 20px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.90)',
        overflow: 'hidden',
        ...style,
      }}
    >
      {children}
    </div>
  )
}

// ── Types & static data ───────────────────────────────────────────────────────

type InvoiceStatus = 'paid' | 'pending' | 'overdue'

interface Invoice {
  id: string
  number: string
  client: string
  vehicle: string
  amount: number
  date: string
  dueDate: string
  status: InvoiceStatus
}

interface InvoiceForm {
  client: string
  vehicle: string
  amount: string
  date: string
  dueDate: string
}

const EMPTY_FORM: InvoiceForm = { client: '', vehicle: '', amount: '', date: '', dueDate: '' }

const INVOICES: Invoice[] = [
  { id: '1',  number: 'INV-2026-041', client: 'AutoGroup Bavaria',   vehicle: 'BMW X5 2021',        amount: 46500, date: '2026-04-15', dueDate: '2026-05-15', status: 'paid'    },
  { id: '2',  number: 'INV-2026-040', client: 'Premium Cars Madrid',  vehicle: 'Porsche Macan 2020',  amount: 52000, date: '2026-04-12', dueDate: '2026-05-12', status: 'paid'    },
  { id: '3',  number: 'INV-2026-039', client: 'EliteAuto Valencia',   vehicle: 'Audi Q5 2021',        amount: 38500, date: '2026-04-10', dueDate: '2026-05-10', status: 'pending' },
  { id: '4',  number: 'INV-2026-038', client: 'CarHub Barcelona',     vehicle: 'Mercedes GLC 2020',   amount: 42000, date: '2026-04-08', dueDate: '2026-05-08', status: 'pending' },
  { id: '5',  number: 'INV-2026-037', client: 'DriveNow Sevilla',     vehicle: 'BMW 530d 2020',       amount: 33500, date: '2026-04-06', dueDate: '2026-04-20', status: 'overdue' },
  { id: '6',  number: 'INV-2026-036', client: 'TopMotors Bilbao',     vehicle: 'VW Tiguan 2022',      amount: 29000, date: '2026-04-04', dueDate: '2026-04-18', status: 'overdue' },
  { id: '7',  number: 'INV-2026-035', client: 'AutoWorld Zaragoza',   vehicle: 'Skoda Octavia 2021',  amount: 17500, date: '2026-04-02', dueDate: '2026-05-02', status: 'paid'    },
  { id: '8',  number: 'INV-2026-034', client: 'FreshCars Málaga',     vehicle: 'Toyota Yaris 2022',   amount: 13500, date: '2026-03-30', dueDate: '2026-04-30', status: 'paid'    },
]

const STATUS_CFG: Record<
  InvoiceStatus,
  { label: string; color: 'green' | 'yellow' | 'red'; Icon: React.ElementType }
> = {
  paid:    { label: 'Pagada',    color: 'green',  Icon: CheckCircle },
  pending: { label: 'Pendiente', color: 'yellow', Icon: Clock       },
  overdue: { label: 'Vencida',   color: 'red',    Icon: AlertCircle },
}

// Pre-computed KPI totals
const facturadoMes = INVOICES
  .filter((inv) => inv.date >= '2026-04-01')
  .reduce((s, inv) => s + inv.amount, 0)

const pendienteCobro = INVOICES
  .filter((inv) => inv.status === 'pending')
  .reduce((s, inv) => s + inv.amount, 0)

const totalVencido = INVOICES
  .filter((inv) => inv.status === 'overdue')
  .reduce((s, inv) => s + inv.amount, 0)

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Invoices() {
  const dark = useIsDark()
  const c = tok(dark)

  const [modalOpen, setModalOpen]     = useState(false)
  const [search, setSearch]           = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | InvoiceStatus>('all')
  const [form, setForm]               = useState<InvoiceForm>(EMPTY_FORM)
  const [hoveredId, setHoveredId]     = useState<string | null>(null)

  const filtered = INVOICES.filter((inv) => {
    const q = search.toLowerCase()
    const matchSearch =
      !q ||
      inv.client.toLowerCase().includes(q) ||
      inv.number.toLowerCase().includes(q) ||
      inv.vehicle.toLowerCase().includes(q)
    const matchStatus = statusFilter === 'all' || inv.status === statusFilter
    return matchSearch && matchStatus
  })

  function handleField(field: keyof InvoiceForm) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [field]: e.target.value }))
  }

  function handleCreate() {
    setModalOpen(false)
    setForm(EMPTY_FORM)
  }

  function closeModal() {
    setModalOpen(false)
    setForm(EMPTY_FORM)
  }

  const kpis = [
    {
      label: 'Facturado mes',
      value: facturadoMes,
      accent: '#3b82f6',
      Icon: FileText,
      meta: '+22% vs Mar',
    },
    {
      label: 'Pendiente cobro',
      value: pendienteCobro,
      accent: '#d97706',
      Icon: Clock,
      meta: `${INVOICES.filter((i) => i.status === 'pending').length} facturas`,
    },
    {
      label: 'Vencido',
      value: totalVencido,
      accent: '#e11d48',
      Icon: AlertCircle,
      meta: `${INVOICES.filter((i) => i.status === 'overdue').length} sin cobrar`,
    },
  ]

  const filterTabs: { id: 'all' | InvoiceStatus; label: string; count: number }[] = [
    { id: 'all',     label: 'Todas',      count: INVOICES.length },
    { id: 'paid',    label: 'Pagadas',    count: INVOICES.filter((i) => i.status === 'paid').length },
    { id: 'pending', label: 'Pendientes', count: INVOICES.filter((i) => i.status === 'pending').length },
    { id: 'overdue', label: 'Vencidas',   count: INVOICES.filter((i) => i.status === 'overdue').length },
  ]

  const formValid =
    form.client.trim() !== '' &&
    form.vehicle.trim() !== '' &&
    form.amount !== '' &&
    form.date !== ''

  return (
    <div
      style={{
        padding: 'clamp(16px, 3vw, 24px)',
        maxWidth: 1200,
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
      }}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}
      >
        <div>
          <h1
            style={{
              fontSize: 22,
              fontWeight: 800,
              letterSpacing: '-0.03em',
              color: c.t1,
              lineHeight: 1,
            }}
          >
            Invoices
          </h1>
          <p style={{ fontSize: 12, color: c.t3, marginTop: 4 }}>
            Gestión de facturas · Abril 2026
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          icon={<Plus className="w-3.5 h-3.5" />}
          onClick={() => setModalOpen(true)}
        >
          Nueva factura
        </Button>
      </motion.div>

      {/* KPI row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {kpis.map(({ label, value, accent, Icon, meta }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07, duration: 0.40, ease: [0.32, 0.72, 0, 1] }}
            whileHover={{ y: -2, transition: { duration: 0.18 } }}
          >
            <GCard dark={dark} style={{ padding: '18px 20px 16px' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  marginBottom: 14,
                }}
              >
                <div
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: 9,
                    flexShrink: 0,
                    background: `${accent}18`,
                    border: `1px solid ${accent}28`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Icon style={{ width: 15, height: 15, color: accent }} />
                </div>
                <span style={{ fontSize: 10, fontWeight: 600, color: c.t4 }}>{meta}</span>
              </div>
              <div
                style={{
                  fontSize: 32,
                  fontWeight: 800,
                  letterSpacing: '-0.03em',
                  lineHeight: 1,
                  color: c.t1,
                  marginBottom: 5,
                  fontVariantNumeric: 'tabular-nums',
                }}
              >
                €{value.toLocaleString()}
              </div>
              <p style={{ fontSize: 10.5, color: c.t4 }}>{label}</p>
            </GCard>
          </motion.div>
        ))}
      </div>

      {/* Filter bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 12,
          flexWrap: 'wrap',
        }}
      >
        {/* Status tabs */}
        <div
          style={{
            display: 'flex',
            gap: 3,
            background: c.subBg,
            borderRadius: 10,
            padding: 3,
            border: `1px solid ${c.subBord}`,
          }}
        >
          {filterTabs.map((tab) => {
            const active = statusFilter === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                style={{
                  padding: '5px 11px',
                  borderRadius: 7,
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: 'none',
                  fontFamily: 'General Sans, Inter, system-ui',
                  background: active
                    ? dark
                      ? 'rgba(255,255,255,0.10)'
                      : '#fff'
                    : 'transparent',
                  color: active ? c.t1 : c.t4,
                  boxShadow: active ? '0 1px 4px rgba(0,0,0,0.12)' : 'none',
                  transition: 'all 150ms',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 5,
                }}
              >
                {tab.label}
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minWidth: 16,
                    height: 16,
                    padding: '0 4px',
                    borderRadius: 99,
                    fontSize: 9.5,
                    background: active ? 'rgba(59,130,246,0.15)' : c.subBg,
                    color: active ? '#3b82f6' : c.t4,
                    fontWeight: 700,
                  }}
                >
                  {tab.count}
                </span>
              </button>
            )
          })}
        </div>

        {/* Search */}
        <div style={{ position: 'relative', flex: 1, maxWidth: 280 }}>
          <Search
            style={{
              position: 'absolute',
              left: 10,
              top: '50%',
              transform: 'translateY(-50%)',
              width: 13,
              height: 13,
              color: c.t4,
              pointerEvents: 'none',
            }}
          />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar factura, cliente…"
            style={{
              width: '100%',
              paddingLeft: 30,
              paddingRight: 12,
              paddingTop: 7,
              paddingBottom: 7,
              borderRadius: 9,
              fontSize: 12,
              fontFamily: 'General Sans, Inter, system-ui',
              background: c.subBg,
              border: `1px solid ${c.subBord}`,
              color: c.t1,
              outline: 'none',
              transition: 'border-color 150ms',
            }}
            onFocus={(e) => (e.currentTarget.style.borderColor = 'rgba(59,130,246,0.40)')}
            onBlur={(e) => (e.currentTarget.style.borderColor = c.subBord)}
          />
        </div>
      </div>

      {/* Table */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.28, duration: 0.38 }}
      >
        <GCard dark={dark} style={{ padding: 0 }}>
          <div style={{ overflowX: 'auto' }}>
            <table
              style={{ width: '100%', minWidth: 680, fontSize: 12, borderCollapse: 'collapse' }}
            >
              <thead>
                <tr style={{ borderBottom: `1px solid ${c.div}` }}>
                  {['Número', 'Cliente', 'Vehículo', 'Importe', 'Fecha', 'Vencimiento', 'Estado'].map(
                    (h) => (
                      <th
                        key={h}
                        style={{
                          padding: '10px 16px',
                          textAlign: 'left',
                          fontSize: 9.5,
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: '0.09em',
                          color: c.t4,
                        }}
                      >
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      style={{
                        padding: '36px 16px',
                        textAlign: 'center',
                        color: c.t4,
                        fontSize: 12,
                      }}
                    >
                      No hay facturas que coincidan con los filtros seleccionados.
                    </td>
                  </tr>
                ) : (
                  filtered.map((inv, i) => {
                    const cfg = STATUS_CFG[inv.status]
                    const hovered = hoveredId === inv.id
                    return (
                      <tr
                        key={inv.id}
                        onMouseEnter={() => setHoveredId(inv.id)}
                        onMouseLeave={() => setHoveredId(null)}
                        style={{
                          borderBottom:
                            i < filtered.length - 1 ? `1px solid ${c.div}` : 'none',
                          background: hovered
                            ? dark
                              ? 'rgba(255,255,255,0.025)'
                              : 'rgba(0,0,0,0.02)'
                            : 'transparent',
                          transition: 'background 120ms',
                        }}
                      >
                        <td
                          style={{
                            padding: '11px 16px',
                            fontWeight: 600,
                            color: '#3b82f6',
                            fontVariantNumeric: 'tabular-nums',
                          }}
                        >
                          {inv.number}
                        </td>
                        <td
                          style={{ padding: '11px 16px', fontWeight: 500, color: c.t1 }}
                        >
                          {inv.client}
                        </td>
                        <td style={{ padding: '11px 16px', color: c.t3 }}>{inv.vehicle}</td>
                        <td
                          style={{
                            padding: '11px 16px',
                            fontWeight: 700,
                            color: c.t1,
                            fontVariantNumeric: 'tabular-nums',
                          }}
                        >
                          €{inv.amount.toLocaleString()}
                        </td>
                        <td
                          style={{ padding: '11px 16px', color: c.t4, fontSize: 11 }}
                        >
                          {inv.date}
                        </td>
                        <td
                          style={{
                            padding: '11px 16px',
                            fontSize: 11,
                            color: inv.status === 'overdue' ? '#e11d48' : c.t4,
                          }}
                        >
                          {inv.dueDate}
                        </td>
                        <td style={{ padding: '11px 16px' }}>
                          <Badge color={cfg.color} dot>
                            {cfg.label}
                          </Badge>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        </GCard>
      </motion.div>

      {/* Nueva factura modal */}
      <Modal open={modalOpen} onClose={closeModal} title="Nueva factura" size="md">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Input
            label="Cliente"
            placeholder="Nombre del cliente o empresa"
            value={form.client}
            onChange={handleField('client')}
          />
          <Input
            label="Vehículo"
            placeholder="Marca, modelo y año"
            value={form.vehicle}
            onChange={handleField('vehicle')}
          />
          <Input
            label="Importe (€)"
            type="number"
            placeholder="0"
            value={form.amount}
            onChange={handleField('amount')}
          />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <Input
              label="Fecha de factura"
              type="date"
              value={form.date}
              onChange={handleField('date')}
            />
            <Input
              label="Fecha de vencimiento"
              type="date"
              value={form.dueDate}
              onChange={handleField('dueDate')}
            />
          </div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: 8,
              paddingTop: 4,
            }}
          >
            <Button variant="ghost" size="sm" onClick={closeModal}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              size="sm"
              disabled={!formValid}
              onClick={handleCreate}
            >
              Crear factura
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
