import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { Monitor, Moon, Sun } from 'lucide-react';

import { cn } from '@/lib/utils';

export type ThemeChoice = 'light' | 'dark' | 'system';

const STORAGE_KEY = 'cardeep-theme';

type ThemeContextValue = {
  choice: ThemeChoice;
  resolved: 'light' | 'dark';
  setChoice: (next: ThemeChoice) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

function readStored(): ThemeChoice {
  if (typeof window === 'undefined') return 'system';
  const raw = window.localStorage.getItem(STORAGE_KEY);
  return raw === 'light' || raw === 'dark' ? raw : 'system';
}

function systemPrefersDark() {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

/**
 * Theme state for the whole page.
 *
 * `system` is the default and leaves the CSS media query in charge — the
 * stylesheet already carries both palettes, so nothing needs to be written to
 * the DOM. Choosing a side stamps `data-theme` on `<html>`, which outranks the
 * media query.
 */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [choice, setChoiceState] = useState<ThemeChoice>(readStored);
  const [systemDark, setSystemDark] = useState(systemPrefersDark);

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = (event: MediaQueryListEvent) => setSystemDark(event.matches);
    media.addEventListener('change', onChange);
    return () => media.removeEventListener('change', onChange);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    if (choice === 'system') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', choice);
  }, [choice]);

  const setChoice = useCallback((next: ThemeChoice) => {
    setChoiceState(next);
    if (next === 'system') window.localStorage.removeItem(STORAGE_KEY);
    else window.localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const resolved = choice === 'system' ? (systemDark ? 'dark' : 'light') : choice;

  return (
    <ThemeContext.Provider value={{ choice, resolved, setChoice }}>{children}</ThemeContext.Provider>
  );
}

export function useTheme() {
  const value = useContext(ThemeContext);
  if (!value) throw new Error('useTheme must be used inside ThemeProvider');
  return value;
}

const OPTIONS: readonly { value: ThemeChoice; label: string; Icon: typeof Sun }[] = [
  { value: 'light', label: 'Tema claro', Icon: Sun },
  { value: 'system', label: 'Seguir al sistema', Icon: Monitor },
  { value: 'dark', label: 'Tema oscuro', Icon: Moon },
];

/**
 * Three-way switch rather than a toggle: "system" has to stay reachable, and a
 * two-state control silently strands anyone who never picked a side.
 */
export function ThemeToggle({ className }: { className?: string }) {
  const { choice, setChoice } = useTheme();

  return (
    <div
      role="radiogroup"
      aria-label="Tema"
      className={cn('glass-chip inline-flex items-center gap-0.5 rounded-full p-0.5', className)}
    >
      {OPTIONS.map(({ value, label, Icon }) => {
        const active = choice === value;
        return (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={label}
            title={label}
            onClick={() => setChoice(value)}
            className={cn(
              'grid size-7 cursor-pointer place-items-center rounded-full transition-colors duration-200',
              active
                ? 'bg-primary text-on-primary'
                : 'text-muted-foreground hover:text-foreground',
            )}
          >
            <Icon className="size-3.5" strokeWidth={2} />
          </button>
        );
      })}
    </div>
  );
}
