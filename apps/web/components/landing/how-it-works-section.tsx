const STEPS = [
  {
    number: "01",
    title: "Describe what you need",
    description:
      "Answer a short guided search — city, budget, brand, fuel type, age, and kilometres — or tell the chat assistant instead.",
  },
  {
    number: "02",
    title: "Compare five ranked matches",
    description:
      "We line up the five closest listings side by side with a match percentage and the reasons behind it.",
  },
  {
    number: "03",
    title: "Inspect, save, and continue",
    description:
      "Open a detailed page for any car, save up to five favourites, then continue to the original marketplace listing.",
  },
]

export function HowItWorksSection() {
  return (
    <section className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 sm:py-20">
      <div className="mb-10 max-w-2xl">
        <h2 className="font-heading text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
          How BuySeconds works
        </h2>
        <p className="mt-3 text-base leading-relaxed text-muted-foreground">
          Three steps between "I need a car" and a shortlist worth trusting.
        </p>
      </div>
      <ol className="grid grid-cols-1 gap-8 sm:grid-cols-3">
        {STEPS.map((step) => (
          <li key={step.number} className="flex flex-col gap-3">
            <span className="font-heading text-sm font-semibold text-primary">
              {step.number}
            </span>
            <h3 className="font-heading text-xl font-semibold">{step.title}</h3>
            <p className="text-sm leading-relaxed text-muted-foreground">{step.description}</p>
          </li>
        ))}
      </ol>
    </section>
  )
}
