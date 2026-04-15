import type { AnchorHTMLAttributes } from "react";

type Props = AnchorHTMLAttributes<HTMLAnchorElement> & {
  label: string;
};

export function CTAButton({ label, className, ...rest }: Props) {
  return (
    <a className={`btn btn--primary ${className ?? ""}`.trim()} {...rest}>
      <span>{label}</span>
      <span className="btn__arrow" aria-hidden="true">
        →
      </span>
    </a>
  );
}
