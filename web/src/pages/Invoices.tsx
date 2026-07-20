// Invoices — dealer's own billing data, no gating per 05-MONETIZATION-MAP.md.

import React, { useEffect, useState } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { Plus, FileText, Clock, AlertCircle, CheckCircle, Search, X } from 'lucide-react'
import { Badge, Button, EmptyState, Input, Modal } from '../components'
import Card from '../components/Card'
import { ACCENT, BAD, WARN } from '../lib/theme'

// ── Types & static data ───────────────────────────────────────────────────────

type InvoiceStatus = 'paid' | 'pending' | 'overdue'

interface Invoice { id: string; number: string; client: string; vehicle: string; amount: number; date: string; dueDate: string; status: InvoiceStatus }
interface InvoiceForm { client: string; vehicle: string; amount: string; date: string; dueDate: string }

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

const STATUS_CFG: Record<InvoiceStatus, { label: string; color: 'green' | 'yellow' | 'red'; Icon: React.ElementType }> = {
  paid:    { label: 'Pagada',    color: 'green',  Icon: CheckCircle },
  pending: { label: 'Pendiente', color: 'yellow', Icon: Clock       },
  overdue: { label: 'Vencida',   color: 'red',    Icon: AlertCircle },
}

const facturadoMes = INVOICES.filter(inv => inv.date >= '2026-04-01').reduce((s, inv) => s + inv.amount, 0)
const pendienteCobro = INVOICES.filter(inv => inv.status === 'pending').reduce((s, inv) => s + inv.amount, 0)
const totalVencido = INVOICES.filter(inv => inv.status === 'overdue').reduce((s, inv) => s + inv.amount, 0)
const cobradasMes = INVOICES.filter(inv => inv.status === 'paid' && inv.date >= '2026-04-01').length

// ── Animated euro figure ───────────────────────────────────────────────────────
// Counts up from 0 on mount instead of rendering the final figure statically —
// same spring-driven pattern as Inteligencia.tsx's AnimNum.

function AnimEuro({ value }: { value: number }) {
  const mv = useMotionValue(0)
  const spring = useSpring(mv, { stiffness: 60, damping: 16 })
  const display = useTransform(spring, v => `€${Math.round(v).toLocaleString()}`)
  useEffect(() => { mv.set(value) }, [value, mv])
  return <motion.span>{display}</motion.span>
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Invoices() {
  const [modalOpen, setModalOpen]     = useState(false)
  const [search, setSearch]           = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | InvoiceStatus>('all')
  const [form, setForm]               = useState<InvoiceForm>(EMPTY_FORM)

  const filtered = INVOICES.filter(inv => {
    const q = search.toLowerCase()
    const matchSearch = !q || inv.client.toLowerCase().includes(q) || inv.number.toLowerCase().includes(q) || inv.vehicle.toLowerCase().includes(q)
    const matchStatus = statusFilter === 'all' || inv.status === statusFilter
    return matchSearch && matchStatus
  })

  function handleField(field: keyof InvoiceForm) {
    return (e: React.ChangeEvent<HTMLInputElement>) => setForm(f => ({ ...f, [field]: e.target.value }))
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
    { label: 'Facturado mes', value: facturadoMes, accent: ACCENT, Icon: FileText, meta: `${cobradasMes} cobradas` },
    { label: 'Pendiente cobro', value: pendienteCobro, accent: WARN, Icon: Clock, meta: `${INVOICES.filter(i => i.status === 'pending').length} facturas` },
    { label: 'Vencido', value: totalVencido, accent: BAD, Icon: AlertCircle, meta: `${INVOICES.filter(i => i.status === 'overdue').length} sin cobrar` },
  ]

  const filterTabs: { id: 'all' | InvoiceStatus; label: string; count: number }[] = [
    { id: 'all',     label: 'Todas',      count: INVOICES.length },
    { id: 'paid',    label: 'Pagadas',    count: INVOICES.filter(i => i.status === 'paid').length },
    { id: 'pending', label: 'Pendientes', count: INVOICES.filter(i => i.status === 'pending').length },
    { id: 'overdue', label: 'Vencidas',   count: INVOICES.filter(i => i.status === 'overdue').length },
  ]

  const formValid = form.client.trim() !== '' && form.vehicle.trim() !== '' && form.amount !== '' && form.date !== ''

  return (
    <div className="mx-auto flex flex-col gap-5" style={{ padding: 'clamp(16px, 3vw, 24px)', maxWidth: 1200 }}>

      <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }} className="flex items-end justify-between">
        <div>
          <h1 className="text-[22px] font-extrabold leading-none tracking-[-0.03em]" style={{ color: 'var(--text-primary)' }}>Facturas</h1>
          <p className="mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>Gestión de facturas · Abril 2026</p>
        </div>
        <Button variant="primary" size="sm" icon={<Plus className="h-3.5 w-3.5" />} onClick={() => setModalOpen(true)}>Nueva factura</Button>
      </motion.div>

      <div className="grid grid-cols-3 gap-3.5">
        {kpis.map(({ label, value, accent, Icon, meta }, i) => (
          <motion.div key={label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.07, duration: 0.4, ease: [0.32, 0.72, 0, 1] }}>
            <Card hover className="!p-[18px_20px_16px]">
              <div className="mb-3.5 flex items-start justify-between">
                <div className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-[9px]" style={{ background: `${accent}18`, border: `1px solid ${accent}38` }}>
                  <Icon style={{ width: 15, height: 15, color: accent }} />
                </div>
                <span className="text-[10px] font-semibold" style={{ color: 'var(--text-muted)' }}>{meta}</span>
              </div>
              <div className="mb-[5px] text-[32px] font-extrabold leading-none tracking-[-0.03em] tabular-nums" style={{ color: 'var(--text-primary)' }}><AnimEuro value={value} /></div>
              <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{label}</p>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-[3px] rounded-[10px] p-[3px]" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}>
          {filterTabs.map(tab => {
            const active = statusFilter === tab.id
            return (
              <motion.button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                whileTap={{ scale: 0.96 }}
                className="flex items-center gap-[5px] rounded-[7px] border-0 px-[11px] py-[5px] text-[11px] font-semibold transition-colors"
                style={{ background: active ? 'var(--bg-elevated)' : 'transparent', color: active ? 'var(--text-primary)' : 'var(--text-muted)', boxShadow: active ? '0 1px 4px rgba(0,0,0,0.12)' : 'none' }}
              >
                {tab.label}
                <span
                  className="inline-flex h-4 min-w-[16px] items-center justify-center rounded-full px-1 text-[9.5px] font-bold tabular-nums"
                  style={{ background: active ? `${ACCENT}26` : 'var(--bg-surface)', color: active ? ACCENT : 'var(--text-muted)' }}
                >
                  {tab.count}
                </span>
              </motion.button>
            )
          })}
        </div>

        <div className="max-w-[280px] flex-1">
          <Input
            icon={<Search className="h-3.5 w-3.5" />}
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar factura, cliente…"
            iconRight={
              search ? (
                <button
                  type="button"
                  onClick={() => setSearch('')}
                  className="text-text-muted transition-colors hover:text-text-primary"
                  aria-label="Limpiar búsqueda"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              ) : undefined
            }
          />
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28, duration: 0.38 }}>
        <Card className="!p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-xs" style={{ minWidth: 680 }}>
              <thead>
                <tr className="border-b border-border-subtle">
                  {['Número', 'Cliente', 'Vehículo', 'Importe', 'Fecha', 'Vencimiento', 'Estado'].map(h => (
                    <th key={h} className="p-[10px_16px] text-left text-[9.5px] font-bold uppercase tracking-[0.09em]" style={{ color: 'var(--text-muted)' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle">
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-0">
                      <EmptyState
                        icon={<FileText className="h-6 w-6" />}
                        title="Sin resultados"
                        message="No hay facturas que coincidan con los filtros seleccionados."
                      />
                    </td>
                  </tr>
                ) : (
                  filtered.map((inv, i) => {
                    const cfg = STATUS_CFG[inv.status]
                    return (
                      <motion.tr
                        key={inv.id}
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.025, duration: 0.2 }}
                        className="transition-colors hover:bg-bg-surface"
                      >
                        <td className="p-[11px_16px] font-semibold tabular-nums" style={{ color: ACCENT }}>{inv.number}</td>
                        <td className="p-[11px_16px] font-medium" style={{ color: 'var(--text-primary)' }}>{inv.client}</td>
                        <td className="p-[11px_16px]" style={{ color: 'var(--text-secondary)' }}>{inv.vehicle}</td>
                        <td className="p-[11px_16px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>€{inv.amount.toLocaleString()}</td>
                        <td className="p-[11px_16px] text-[11px] tabular-nums" style={{ color: 'var(--text-muted)' }}>{inv.date}</td>
                        <td className="p-[11px_16px] text-[11px] tabular-nums" style={{ color: inv.status === 'overdue' ? BAD : 'var(--text-muted)' }}>{inv.dueDate}</td>
                        <td className="p-[11px_16px]"><Badge color={cfg.color} dot>{cfg.label}</Badge></td>
                      </motion.tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </motion.div>

      <Modal open={modalOpen} onClose={closeModal} title="Nueva factura" size="md">
        <div className="flex flex-col gap-3.5">
          <Input label="Cliente" placeholder="Nombre del cliente o empresa" value={form.client} onChange={handleField('client')} />
          <Input label="Vehículo" placeholder="Marca, modelo y año" value={form.vehicle} onChange={handleField('vehicle')} />
          <Input label="Importe (€)" type="number" placeholder="0" value={form.amount} onChange={handleField('amount')} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Fecha de factura" type="date" value={form.date} onChange={handleField('date')} />
            <Input label="Fecha de vencimiento" type="date" value={form.dueDate} onChange={handleField('dueDate')} />
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <Button variant="ghost" size="sm" onClick={closeModal}>Cancelar</Button>
            <Button variant="primary" size="sm" disabled={!formValid} onClick={handleCreate}>Crear factura</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
