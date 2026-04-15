type Props = {
  label: string;
  title: string;
  body: string;
  footer: string;
};

export function AgentCard({ label, title, body, footer }: Props) {
  return (
    <article className="card">
      <span className="card__label">{label}</span>
      <h3 className="card__title">{title}</h3>
      <p className="card__body">{body}</p>
      <div className="card__footer">{footer}</div>
    </article>
  );
}
