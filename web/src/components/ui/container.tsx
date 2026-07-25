/**
 * Page gutter shared by every section: centred, capped at the 1440px container
 * width, with the responsive horizontal padding ramp.
 *
 * Extra classes are concatenated, never merged. Several call sites deliberately
 * stack a second max-width utility on top of `max-w-container` and rely on the
 * stylesheet's own ordering to resolve it — de-duplicating here would silently
 * change the resolved width.
 */
export function Container({
  className,
  children,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="container"
      className={
        'max-w-container mx-auto w-full px-4 sm:px-6 lg:px-8' +
        (className ? ' ' + className : '')
      }
      {...props}
    >
      {children}
    </div>
  );
}
