import * as Accordion from '@radix-ui/react-accordion';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Fragment } from 'react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';

/**
 * Every label icon is a 20x20 outline drawing sharing the same stroke setup, so
 * only the path data differs between them.
 */
const APPROACH_PATHS = [
  'M8.7513 2.5L6.66797 7.5L10.0013 18.3333L13.3346 7.5L11.2513 2.5',
  'M14.1682 2.5C14.427 2.5 14.6822 2.56024 14.9136 2.67595C15.145 2.79167 15.3463 2.95967 15.5016 3.16667L18.0016 6.5C18.216 6.78597 18.3328 7.13329 18.3347 7.49071C18.3367 7.84813 18.2237 8.19671 18.0124 8.485L11.3541 17.64C11.1997 17.8546 10.9965 18.0293 10.7613 18.1499C10.526 18.2705 10.2655 18.3333 10.0012 18.3333C9.73683 18.3333 9.47629 18.2705 9.24105 18.1499C9.00581 18.0293 8.80262 17.8546 8.64825 17.64L1.98991 8.485C1.77875 8.19662 1.6659 7.84799 1.668 7.49057C1.6701 7.13316 1.78705 6.78588 2.00158 6.5L4.49991 3.16917C4.65506 2.96149 4.85652 2.79286 5.08827 2.6767C5.32002 2.56053 5.57568 2.50003 5.83491 2.5H14.1682Z',
  'M1.66797 7.5H18.3346',
] as const;

const PROCESS_PATHS = [
  'M10 16.6641V18.3307',
  'M10 1.66406V3.33073',
  'M14.168 16.6641V18.3307',
  'M14.168 1.66406V3.33073',
  'M1.66797 10H3.33464',
  'M1.66797 14.1641H3.33464',
  'M1.66797 5.83594H3.33464',
  'M16.668 10H18.3346',
  'M16.668 14.1641H18.3346',
  'M16.668 5.83594H18.3346',
  'M5.83203 16.6641V18.3307',
  'M5.83203 1.66406V3.33073',
  'M14.9987 3.33594H4.9987C4.07822 3.33594 3.33203 4.08213 3.33203 5.0026V15.0026C3.33203 15.9231 4.07822 16.6693 4.9987 16.6693H14.9987C15.9192 16.6693 16.6654 15.9231 16.6654 15.0026V5.0026C16.6654 4.08213 15.9192 3.33594 14.9987 3.33594Z',
  'M12.5013 6.66406H7.5013C7.04106 6.66406 6.66797 7.03716 6.66797 7.4974V12.4974C6.66797 12.9576 7.04106 13.3307 7.5013 13.3307H12.5013C12.9615 13.3307 13.3346 12.9576 13.3346 12.4974V7.4974C13.3346 7.03716 12.9615 6.66406 12.5013 6.66406Z',
] as const;

const DESIGN_PHILOSOPHY_PATHS = [
  'M10.0013 5.83073C11.1519 5.83073 12.0846 4.89799 12.0846 3.7474C12.0846 2.5968 11.1519 1.66406 10.0013 1.66406C8.85071 1.66406 7.91797 2.5968 7.91797 3.7474C7.91797 4.89799 8.85071 5.83073 10.0013 5.83073Z',
  'M8.5 5.25L5.25 8.5',
  'M3.7513 12.0807C4.9019 12.0807 5.83464 11.148 5.83464 9.9974C5.83464 8.8468 4.9019 7.91406 3.7513 7.91406C2.60071 7.91406 1.66797 8.8468 1.66797 9.9974C1.66797 11.148 2.60071 12.0807 3.7513 12.0807Z',
  'M5.83203 10H14.1654',
  'M16.2513 12.0807C17.4019 12.0807 18.3346 11.148 18.3346 9.9974C18.3346 8.8468 17.4019 7.91406 16.2513 7.91406C15.1007 7.91406 14.168 8.8468 14.168 9.9974C14.168 11.148 15.1007 12.0807 16.2513 12.0807Z',
  'M11.5 14.75L14.75 11.5',
  'M10.0013 18.3307C11.1519 18.3307 12.0846 17.398 12.0846 16.2474C12.0846 15.0968 11.1519 14.1641 10.0013 14.1641C8.85071 14.1641 7.91797 15.0968 7.91797 16.2474C7.91797 17.398 8.85071 18.3307 10.0013 18.3307Z',
] as const;

const DEVELOPMENT_STACK_PATHS = [
  'M17.5 6.67017C17.4997 6.37789 17.4225 6.09084 17.2763 5.8378C17.13 5.58476 16.9198 5.37463 16.6667 5.2285L10.8333 1.89517C10.58 1.74889 10.2926 1.67188 10 1.67188C9.70744 1.67188 9.42003 1.74889 9.16667 1.89517L3.33333 5.2285C3.08022 5.37463 2.86998 5.58476 2.72372 5.8378C2.57745 6.09084 2.5003 6.37789 2.5 6.67017V13.3368C2.5003 13.6291 2.57745 13.9162 2.72372 14.1692C2.86998 14.4222 3.08022 14.6324 3.33333 14.7785L9.16667 18.1118C9.42003 18.2581 9.70744 18.3351 10 18.3351C10.2926 18.3351 10.58 18.2581 10.8333 18.1118L16.6667 14.7785C16.9198 14.6324 17.13 14.4222 17.2763 14.1692C17.4225 13.9162 17.4997 13.6291 17.5 13.3368V6.67017Z',
  'M2.75 5.83594L10 10.0026L17.25 5.83594',
  'M10 18.3333V10',
] as const;

const COMMUNICATION_PATHS = [
  'M2.49438 13.6155C2.61691 13.9246 2.64419 14.2633 2.57271 14.588L1.68521 17.3296C1.65661 17.4687 1.66401 17.6127 1.70669 17.7481C1.74937 17.8835 1.82593 18.0057 1.9291 18.1032C2.03227 18.2007 2.15864 18.2702 2.29621 18.3052C2.43379 18.3401 2.57801 18.3394 2.71521 18.303L5.55938 17.4713C5.86581 17.4105 6.18315 17.4371 6.47521 17.548C8.2547 18.379 10.2705 18.5548 12.167 18.0444C14.0635 17.534 15.7188 16.3702 16.8408 14.7583C17.9628 13.1464 18.4795 11.19 18.2996 9.23426C18.1198 7.27855 17.255 5.4492 15.8578 4.06897C14.4606 2.68874 12.6208 1.84634 10.663 1.69039C8.70526 1.53444 6.75532 2.07496 5.15725 3.21659C3.55917 4.35822 2.41565 6.02759 1.92846 7.93017C1.44126 9.83275 1.64169 11.8463 2.49438 13.6155Z',
  'M6.66797 10H6.6763',
  'M10 10H10.0083',
  'M13.332 10H13.3404',
] as const;

const DELIVERABLES_PATHS = [
  'M12.1145 18.0711C12.1461 18.15 12.2012 18.2174 12.2722 18.2641C12.3432 18.3108 12.4269 18.3347 12.5118 18.3325C12.5968 18.3303 12.6791 18.3022 12.7477 18.2519C12.8162 18.2016 12.8677 18.1316 12.8953 18.0511L18.312 2.21781C18.3386 2.14397 18.3437 2.06406 18.3266 1.98744C18.3096 1.91081 18.271 1.84064 18.2155 1.78513C18.16 1.72961 18.0898 1.69106 18.0132 1.67397C17.9366 1.65688 17.8566 1.66197 17.7828 1.68864L1.94947 7.10531C1.86905 7.13289 1.79899 7.18441 1.7487 7.25295C1.69841 7.3215 1.67028 7.40379 1.66811 7.48878C1.66593 7.57377 1.6898 7.65739 1.73652 7.72842C1.78324 7.79945 1.85057 7.85448 1.92947 7.88614L8.53781 10.5361C8.74671 10.6198 8.93652 10.7449 9.09578 10.9038C9.25504 11.0628 9.38046 11.2524 9.46447 11.4611L12.1145 18.0711Z',
  'M18.2104 1.78906L9.09375 10.9049',
] as const;

const SUPPORT_PATHS = [
  'M9.16797 14.1693L10.8346 15.8359C10.9988 16.0001 11.1937 16.1303 11.4081 16.2191C11.6226 16.308 11.8525 16.3537 12.0846 16.3537C12.3168 16.3537 12.5467 16.308 12.7611 16.2191C12.9756 16.1303 13.1705 16.0001 13.3346 15.8359C13.4988 15.6718 13.629 15.4769 13.7178 15.2624C13.8067 15.048 13.8524 14.8181 13.8524 14.5859C13.8524 14.3538 13.8067 14.1239 13.7178 13.9094C13.629 13.695 13.4988 13.5001 13.3346 13.3359',
  'M11.6688 11.6671L13.7521 13.7504C14.0837 14.0819 14.5333 14.2682 15.0021 14.2682C15.471 14.2682 15.9206 14.0819 16.2521 13.7504C16.5837 13.4189 16.7699 12.9693 16.7699 12.5004C16.7699 12.0316 16.5837 11.5819 16.2521 11.2504L13.0188 8.01709C12.5501 7.54892 11.9146 7.28595 11.2521 7.28595C10.5896 7.28595 9.95423 7.54892 9.48548 8.01709L8.75214 8.75042C8.42062 9.08194 7.97098 9.26819 7.50214 9.26819C7.0333 9.26819 6.58366 9.08194 6.25214 8.75042C5.92062 8.4189 5.73438 7.96926 5.73438 7.50042C5.73438 7.03158 5.92062 6.58194 6.25214 6.25042L8.59381 3.90875C9.35401 3.15054 10.3454 2.66755 11.411 2.53623C12.4766 2.40491 13.5556 2.63278 14.4771 3.18375L14.8688 3.41709C15.2236 3.63124 15.6455 3.70552 16.0521 3.62542L17.5021 3.33375',
  'M17.5013 2.5L18.3346 11.6667H16.668',
  'M2.5013 2.5L1.66797 11.6667L7.08464 17.0833C7.41616 17.4149 7.86579 17.6011 8.33464 17.6011C8.80348 17.6011 9.25311 17.4149 9.58464 17.0833C9.91616 16.7518 10.1024 16.3022 10.1024 15.8333C10.1024 15.3645 9.91616 14.9149 9.58464 14.5833',
  'M2.5 3.33594H9.16667',
] as const;

const ALWAYS_FREE_PATHS = [
  'M11.528 13.8041C11.7001 13.8831 11.894 13.9012 12.0777 13.8553C12.2615 13.8094 12.4241 13.7022 12.5388 13.5516L12.8346 13.1641C12.9899 12.9571 13.1912 12.7891 13.4226 12.6734C13.654 12.5576 13.9092 12.4974 14.168 12.4974H16.668C17.11 12.4974 17.5339 12.673 17.8465 12.9856C18.159 13.2981 18.3346 13.722 18.3346 14.1641V16.6641C18.3346 17.1061 18.159 17.53 17.8465 17.8426C17.5339 18.1551 17.11 18.3307 16.668 18.3307C12.6897 18.3307 8.87441 16.7504 6.06137 13.9373C3.24832 11.1243 1.66797 7.30898 1.66797 3.33073C1.66797 2.8887 1.84356 2.46478 2.15612 2.15222C2.46868 1.83966 2.89261 1.66406 3.33464 1.66406H5.83464C6.27666 1.66406 6.70059 1.83966 7.01315 2.15222C7.32571 2.46478 7.5013 2.8887 7.5013 3.33073V5.83073C7.5013 6.08947 7.44106 6.34466 7.32535 6.57609C7.20963 6.80751 7.04163 7.00882 6.83464 7.16406L6.44464 7.45656C6.29165 7.57338 6.18382 7.73955 6.13946 7.92685C6.0951 8.11416 6.11695 8.31104 6.2013 8.48406C7.3402 10.7973 9.21332 12.6681 11.528 13.8041Z',
] as const;

const WARNING_PATH =
  'M19.5099 5.85L13.5699 2.42C12.5999 1.86 11.3999 1.86 10.4199 2.42L4.48992 5.85C3.51992 6.41 2.91992 7.45 2.91992 8.58V15.42C2.91992 16.54 3.51992 17.58 4.48992 18.15L10.4299 21.58C11.3999 22.14 12.5999 22.14 13.5799 21.58L19.5199 18.15C20.4899 17.59 21.0899 16.55 21.0899 15.42V8.58C21.0799 7.45 20.4799 6.42 19.5099 5.85ZM11.2499 7.75C11.2499 7.34 11.5899 7 11.9999 7C12.4099 7 12.7499 7.34 12.7499 7.75V13C12.7499 13.41 12.4099 13.75 11.9999 13.75C11.5899 13.75 11.2499 13.41 11.2499 13V7.75ZM12.9199 16.63C12.8699 16.75 12.7999 16.86 12.7099 16.96C12.5199 17.15 12.2699 17.25 11.9999 17.25C11.8699 17.25 11.7399 17.22 11.6199 17.17C11.4899 17.12 11.3899 17.05 11.2899 16.96C11.1999 16.86 11.1299 16.75 11.0699 16.63C11.0199 16.51 10.9999 16.38 10.9999 16.25C10.9999 15.99 11.0999 15.73 11.2899 15.54C11.3899 15.45 11.4899 15.38 11.6199 15.33C11.9899 15.17 12.4299 15.26 12.7099 15.54C12.7999 15.64 12.8699 15.74 12.9199 15.87C12.9699 15.99 12.9999 16.12 12.9999 16.25C12.9999 16.38 12.9699 16.51 12.9199 16.63Z';

const ROWS = [
  {
    label: 'Approach',
    paths: APPROACH_PATHS,
    aceternity: 'Design and engineering in sync',
    traditional: 'Disconnected teams',
  },
  {
    label: 'Process',
    paths: PROCESS_PATHS,
    aceternity: 'Streamlined, transparent, and async',
    traditional: 'Endless calls, vague timelines',
  },
  {
    label: 'Design Philosophy',
    paths: DESIGN_PHILOSOPHY_PATHS,
    aceternity: 'Modern, minimal, and purposeful.',
    traditional: 'Trend-based and cluttered',
  },
  {
    label: 'Development Stack',
    paths: DEVELOPMENT_STACK_PATHS,
    aceternity: 'Built with modern frameworks',
    traditional: 'Outdated stacks',
  },
  {
    label: 'Communication',
    paths: COMMUNICATION_PATHS,
    aceternity: 'Clear updates',
    traditional: 'Multiple middlemen',
  },
  {
    label: 'Deliverables',
    paths: DELIVERABLES_PATHS,
    aceternity: 'Production-ready design systems',
    traditional: 'Static mockups',
  },
  {
    label: 'Support',
    paths: SUPPORT_PATHS,
    aceternity: 'Long-term partnership mindset',
    traditional: 'One-and-done projects',
  },
] as const;

type ComparisonRow = (typeof ROWS)[number];

/** Bottom cards: 24x24 outline icons drawn in the orange accent. */
const FEATURES = [
  {
    title: 'Instant Onboarding',
    paths: [
      'M11 20H2',
      'M11 4.5622V20.7192C11 20.8711 11.0347 21.021 11.1013 21.1575C11.1679 21.294 11.2648 21.4135 11.3845 21.507C11.5042 21.6005 11.6436 21.6655 11.7922 21.6971C11.9408 21.7287 12.0946 21.726 12.242 21.6892L19 20.0002V5.5622C18.9999 5.11621 18.8508 4.68303 18.5763 4.33153C18.3018 3.98002 17.9177 3.73035 17.485 3.6222L13.485 2.6222C13.1902 2.54852 12.8826 2.54297 12.5854 2.60595C12.2882 2.66894 12.0092 2.79881 11.7697 2.98571C11.5301 3.17261 11.3363 3.41163 11.203 3.68461C11.0696 3.9576 11.0002 4.25838 11 4.5622Z',
      'M11 4H8C7.46957 4 6.96086 4.21071 6.58579 4.58579C6.21071 4.96086 6 5.46957 6 6V20',
      'M14 12H14.01',
      'M22 20H19',
    ],
  },
  {
    title: 'High Impact, Low Overhead',
    paths: [
      'M6 22C5.46957 22 4.96086 21.7893 4.58579 21.4142C4.21071 21.0391 4 20.5304 4 20V4C4 3.46957 4.21071 2.96086 4.58579 2.58579C4.96086 2.21072 5.46957 2 6 2H14C14.3166 1.99949 14.6301 2.06161 14.9225 2.18277C15.215 2.30394 15.4806 2.48176 15.704 2.706L19.292 6.294C19.5168 6.51751 19.6952 6.78335 19.8167 7.07616C19.9382 7.36898 20.0005 7.68297 20 8V20C20 20.5304 19.7893 21.0391 19.4142 21.4142C19.0391 21.7893 18.5304 22 18 22H6Z',
      'M14 2V7C14 7.26522 14.1054 7.51957 14.2929 7.70711C14.4804 7.89464 14.7348 8 15 8H20',
      'M8 18V16',
      'M12 18V14',
      'M16 18V12',
    ],
  },
  {
    title: 'Stress-Free Collaboartion',
    paths: [
      'M10.9998 17L12.9998 19C13.1967 19.197 13.4306 19.3532 13.688 19.4598C13.9453 19.5665 14.2212 19.6213 14.4998 19.6213C14.7783 19.6213 15.0542 19.5665 15.3116 19.4598C15.5689 19.3532 15.8028 19.197 15.9998 19C16.1967 18.803 16.353 18.5692 16.4596 18.3118C16.5662 18.0544 16.6211 17.7786 16.6211 17.5C16.6211 17.2214 16.5662 16.9456 16.4596 16.6882C16.353 16.4308 16.1967 16.197 15.9998 16',
      'M14.0002 14L16.5002 16.5C16.8981 16.8978 17.4376 17.1213 18.0002 17.1213C18.5628 17.1213 19.1024 16.8978 19.5002 16.5C19.8981 16.1022 20.1215 15.5626 20.1215 15C20.1215 14.4374 19.8981 13.8978 19.5002 13.5L15.6202 9.62002C15.0577 9.05821 14.2952 8.74265 13.5002 8.74265C12.7052 8.74265 11.9427 9.05821 11.3802 9.62002L10.5002 10.5C10.1024 10.8978 9.56284 11.1213 9.00023 11.1213C8.43762 11.1213 7.89805 10.8978 7.50023 10.5C7.1024 10.1022 6.87891 9.56262 6.87891 9.00002C6.87891 8.43741 7.1024 7.89784 7.50023 7.50002L10.3102 4.69002C11.2225 3.78016 12.4121 3.20057 13.6909 3.04299C14.9696 2.88541 16.2644 3.15885 17.3702 3.82002L17.8402 4.10002C18.266 4.357 18.7723 4.44613 19.2602 4.35002L21.0002 4.00002',
      'M20.9998 3L21.9998 14H19.9998',
      'M2.99976 3L1.99976 14L8.49976 20.5C8.89758 20.8978 9.43715 21.1213 9.99976 21.1213C10.5624 21.1213 11.1019 20.8978 11.4998 20.5C11.8976 20.1022 12.1211 19.5626 12.1211 19C12.1211 18.4374 11.8976 17.8978 11.4998 17.5',
      'M3 4H11',
    ],
  },
] as const;

const TABLE_ROW_CLASS =
  'relative grid grid-cols-3 px-12 *:data-[slot=tabel-cell]:flex *:data-[slot=tabel-cell]:items-center *:data-[slot=tabel-cell]:gap-3 *:data-[slot=tabel-cell]:py-8';

const DIVIDER_CLASS = 'bg-natural-black/7 h-px w-full';

const VALUE_LABEL_CLASS = '-tracking-sm text-lg leading-4.5 font-medium';

/**
 * Base UI reads the open panel height from this variable; the Radix port drives
 * the height animation itself, so `auto` keeps the inner wrapper self-sizing.
 */
const ACCORDION_PANEL_VARS = {
  '--accordion-panel-height': 'auto',
  '--accordion-panel-width': 'auto',
} as React.CSSProperties;

function LabelIcon({ paths }: { paths: readonly string[] }) {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      {paths.map((d, index) => (
        <path
          key={index}
          d={d}
          stroke="black"
          strokeWidth="1.25"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      ))}
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="20" height="20" rx="10" fill="#12A113" />
      <path
        d="M14 7L8.5 12.5L6 10"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function WarningIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d={WARNING_PATH} fill="#FFBC00" />
    </svg>
  );
}

/**
 * Wordmark link next to "Aceternity Labs". The desktop table always scales the
 * mark up; the mobile accordion only does so from `lg` upwards.
 */
function LogoLink({ scaleClassName }: { scaleClassName: string }) {
  return (
    <a className={`size-5 ${scaleClassName}`} href="/">
      <img
        alt="Logo"
        loading="lazy"
        width={50}
        height={50}
        decoding="async"
        className={`block dark:hidden size-5 ${scaleClassName}`}
        src="/logo.webp"
      />
      <img
        alt="Logo"
        loading="lazy"
        width={50}
        height={50}
        decoding="async"
        className={`hidden dark:block size-5 ${scaleClassName}`}
        src="/logo-dark.webp"
      />
    </a>
  );
}

function DesktopRow({ row }: { row: ComparisonRow }) {
  return (
    <div className={TABLE_ROW_CLASS}>
      <div data-slot="tabel-cell" className="relative">
        <div className="absolute inset-0 -left-8 w-8/10 bg-secondary" />
        <span className="z-10">
          <LabelIcon paths={row.paths} />
        </span>
        <span className="-tracking-sm z-10 text-lg leading-4.5 font-medium">{row.label}</span>
      </div>
      <div data-slot="tabel-cell">
        <CheckIcon />
        <span className={VALUE_LABEL_CLASS}>{row.aceternity}</span>
      </div>
      <div data-slot="tabel-cell">
        <WarningIcon />
        <span className={VALUE_LABEL_CLASS}>{row.traditional}</span>
      </div>
    </div>
  );
}

function DesktopTable() {
  return (
    <div className="bg-natural-white hidden w-full rounded-3xl lg:block">
      <div className="w-full">
        <div className={TABLE_ROW_CLASS}>
          <div data-slot="tabel-cell" className="relative">
            <div className="absolute inset-0 top-4 -left-8 w-8/10 rounded-t-3xl bg-secondary" />
          </div>
          <div data-slot="tabel-cell">
            <LogoLink scaleClassName="scale-125" />
            <span className={VALUE_LABEL_CLASS}>Aceternity Labs</span>
          </div>
          <div data-slot="tabel-cell">
            <span className="-tracking-sm text-muted-foreground text-lg leading-4.5 font-medium">
              Traditional Service Providers
            </span>
          </div>
        </div>
        <div className={DIVIDER_CLASS} />
        {ROWS.map((row) => (
          <Fragment key={row.label}>
            <DesktopRow row={row} />
            <div className={DIVIDER_CLASS} />
          </Fragment>
        ))}
        <div className={TABLE_ROW_CLASS}>
          <div data-slot="tabel-cell" className="relative">
            <div className="absolute inset-0 bottom-4 -left-8 w-8/10 rounded-b-3xl bg-secondary" />
            <span className="z-10">
              <LabelIcon paths={ALWAYS_FREE_PATHS} />
            </span>
            <span className="-tracking-sm z-10 text-lg leading-4.5 font-medium">Always Free</span>
          </div>
          <div data-slot="tabel-cell">
            <Button avatar="/manu.webp">Book a Free Call</Button>
          </div>
          <div data-slot="tabel-cell">
            <Button
              className="**:data-[slot=button-box]:bg-gray-500 **:[span]:text-muted-foreground"
              avatar="/avatar/avatar-1.webp"
            >
              Book a Paid Call
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Below `lg` the three-column table collapses into one accordion item per row,
 * with the first item open by default.
 */
function MobileAccordion() {
  return (
    <div className="block w-full lg:hidden">
      <div className="w-full">
        <Accordion.Root
          type="single"
          collapsible
          defaultValue={ROWS[0].label}
          dir="ltr"
          data-slot="accordion"
          className="flex w-full flex-col gap-4"
        >
          {ROWS.map((row) => (
            <Accordion.Item
              key={row.label}
              value={row.label}
              data-slot="accordion-item"
              className="bg-natural-white rounded-3xl p-6"
            >
              <Accordion.Header className="flex">
                <Accordion.Trigger
                  data-slot="accordion-trigger"
                  className="group/accordion-trigger relative flex flex-1 justify-between rounded-lg border border-transparent text-left text-sm font-medium transition-all outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:after:border-ring aria-disabled:pointer-events-none aria-disabled:opacity-50 **:data-[slot=accordion-trigger-icon]:ml-auto **:data-[slot=accordion-trigger-icon]:size-6 **:data-[slot=accordion-trigger-icon]:text-muted-foreground items-center py-0"
                >
                  <div className="relative flex items-center gap-3">
                    <span className="z-10">
                      <LabelIcon paths={row.paths} />
                    </span>
                    <span className="-tracking-sm z-10 text-lg leading-4.5 font-medium">
                      {row.label}
                    </span>
                  </div>
                  <ChevronDown
                    aria-hidden="true"
                    data-slot="accordion-trigger-icon"
                    className="pointer-events-none shrink-0 group-aria-expanded/accordion-trigger:hidden"
                  />
                  <ChevronUp
                    aria-hidden="true"
                    data-slot="accordion-trigger-icon"
                    className="pointer-events-none hidden shrink-0 group-aria-expanded/accordion-trigger:inline"
                  />
                </Accordion.Trigger>
              </Accordion.Header>
              <Accordion.Content
                data-slot="accordion-content"
                style={ACCORDION_PANEL_VARS}
                className="overflow-hidden text-sm data-[state=open]:animate-accordion-down data-[state=closed]:animate-accordion-up"
              >
                <div className="h-(--accordion-panel-height) pt-0 pb-2.5 data-ending-style:h-0 data-starting-style:h-0 [&_a]:hover:text-foreground [&_p:not(:last-child)]:mb-4 mt-6 flex flex-col gap-6">
                  <div className={DIVIDER_CLASS} />
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center gap-3">
                      <LogoLink scaleClassName="lg:scale-125" />
                      <span className={VALUE_LABEL_CLASS}>Aceternity Labs</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <CheckIcon />
                      <span className={VALUE_LABEL_CLASS}>{row.aceternity}</span>
                    </div>
                  </div>
                  <div className={DIVIDER_CLASS} />
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center gap-3">
                      <span className="-tracking-sm text-muted-foreground text-lg leading-4.5 font-medium">
                        Traditional Service Providers
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <WarningIcon />
                      <span className={VALUE_LABEL_CLASS}>{row.traditional}</span>
                    </div>
                  </div>
                </div>
              </Accordion.Content>
            </Accordion.Item>
          ))}
        </Accordion.Root>
      </div>
    </div>
  );
}

export function Comparison() {
  return (
    <section className="w-full">
      <Container className="flex flex-col gap-15 py-20 md:py-30">
        <div className="flex flex-col gap-6">
          <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
            Aceternity VS Traditional Service Providers
          </h2>
          <div className="block lg:hidden">
            <Button avatar="/manu.webp">Book a Free Call</Button>
          </div>
        </div>
        <div className="flex flex-col gap-6">
          <DesktopTable />
          <MobileAccordion />
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="bg-natural-white flex lg:items-center flex-col gap-3 rounded-3xl px-6 py-8"
              >
                <div>
                  <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    {feature.paths.map((d, index) => (
                      <path
                        key={index}
                        d={d}
                        stroke="#FF6200"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    ))}
                  </svg>
                </div>
                <span className="font-medium text-xl leading-7 -tracking-sm">{feature.title}</span>
                <span className="-tracking-xs text-base leading-6 font-medium lg:text-center text-muted-foreground">
                  Skip Hiring Delays and Start seeing results faster than ever before with our
                  expert team
                </span>
              </div>
            ))}
          </div>
        </div>
      </Container>
    </section>
  );
}
