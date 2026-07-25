/**
 * The 5x5 dot matrix inside the button's accent box, drawn as a right-pointing
 * arrow. `1` is a lit dot, `0` a dimmed one.
 */
const ARROW_MATRIX = [
  [0, 0, 1, 0, 0],
  [0, 0, 0, 1, 0],
  [1, 1, 1, 1, 1],
  [0, 0, 0, 1, 0],
  [0, 0, 1, 0, 0],
] as const;

type ButtonProps = React.ComponentProps<'button'> & {
  /** Optional portrait revealed inside the accent box while hovering. */
  avatar?: string;
};

/**
 * Primary call-to-action used across the whole page.
 *
 * On hover three things happen together over 400ms: the yellow accent box
 * travels from the left edge to the right and flips 180deg, swapping its dot
 * matrix for a portrait; a translucent overlay wipes in from the left via
 * clip-path; and the label slides left to make room.
 *
 * `className` is appended rather than merged, so call sites add positioning or
 * descendant overrides without any utility being silently dropped.
 */
export function Button({ className, children, avatar, ...props }: ButtonProps) {
  return (
    <button
      className={
        'group relative flex w-fit cursor-pointer items-center gap-2 rounded-lg border border-white/20 bg-black py-2 pr-4 pl-11 tracking-tight' +
        (className ? ' ' + className : '')
      }
      {...props}
    >
      <div
        data-slot="button-box"
        className="bg-primary absolute inset-y-0 left-1 z-40 my-auto flex size-8 flex-col items-center justify-center gap-px rounded-[5px] transition-all duration-400 ease-out group-hover:left-[calc(100%-2.3rem)] group-hover:rotate-180 group-hover:transform"
      >
        <div className="flex flex-col gap-px group-hover:hidden">
          {ARROW_MATRIX.map((row, rowIndex) => (
            <div key={rowIndex} className="flex gap-px">
              {row.map((lit, dotIndex) => (
                <span
                  key={dotIndex}
                  className={
                    lit
                      ? 'inline-block size-0.75 shrink-0 rounded-full bg-white duration-200 ease-linear'
                      : 'inline-block size-0.75 shrink-0 rounded-full bg-white/25'
                  }
                />
              ))}
            </div>
          ))}
        </div>
        {avatar ? (
          <img
            alt="Avatar"
            loading="lazy"
            width={32}
            height={32}
            decoding="async"
            className="hidden rotate-180 rounded-[5px] blur-sm transition-all duration-400 ease-out group-hover:block group-hover:blur-none"
            src={avatar}
          />
        ) : null}
      </div>
      <div className="absolute -inset-px rounded-lg bg-white/20 transition-[clip-path] duration-400 ease-out [clip-path:inset(0_100%_0_0)] group-hover:[clip-path:inset(0_0%_0_0)]" />
      <span className="inline-block text-white transition-transform duration-400 group-hover:-translate-x-8">
        {children}
      </span>
    </button>
  );
}
