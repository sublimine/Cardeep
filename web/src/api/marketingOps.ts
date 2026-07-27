// 07-marketing F5 — authenticated client for POST /vehicles/{ulid}/adcopy (C7).
//
// Goes through client.ts's Bearer-token `api`, NOT cardeep.ts (the public X-API-Key
// census read client) — same separation web/src/api/dealerOps.ts already established:
// ad copy is a GASTO-gated, session-owned action (the endpoint requires the caller's
// dealer_membership to cover the vehicle's dealer, mirroring dealer_ops.py's
// _authorize_vehicle), never a plain public read.
import { api, ApiError } from './client'
import type { AdCopyResult, AdCopyClaim } from './cardeep'

export type { AdCopyResult, AdCopyClaim }

interface Envelope<T> { ok: boolean; data: T; error: string | null; meta: Record<string, unknown> | null }

/** Distinguishes the honest "not configured yet" GASTO gate (503) from a real error —
 * the UI renders these very differently (an expected, informative state vs a failure). */
export class AdCopyNotConfiguredError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'AdCopyNotConfiguredError'
  }
}

/** ApiError.message is the RAW response body text (client.ts's apiRequest does not
 * parse it on failure) — extract the clean `error` field when it is JSON, falling
 * back to the raw text for a genuinely non-JSON failure (network error, etc). */
function extractErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    try {
      const parsed = JSON.parse(err.message) as { error?: string }
      return parsed.error ?? err.message
    } catch {
      return err.message
    }
  }
  return err instanceof Error ? err.message : 'Error al generar la descripción'
}

export const marketingOps = {
  generateAdCopy: async (vehicleUlid: string): Promise<AdCopyResult> => {
    try {
      const body = await api.post<Envelope<AdCopyResult> | AdCopyResult>(`/vehicles/${vehicleUlid}/adcopy`, {})
      // api.post already unwraps the {ok,data,error,meta} envelope (see client.ts),
      // matching dealerOps.ts's own comment on this exact ambiguity.
      return (body as Envelope<AdCopyResult>).data ?? (body as AdCopyResult)
    } catch (err) {
      const message = extractErrorMessage(err)
      if (err instanceof ApiError && err.status === 503) {
        throw new AdCopyNotConfiguredError(message)
      }
      throw new Error(message)
    }
  },
}
