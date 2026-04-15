import { TopBar } from "../components/TopBar";
import { Hero } from "../components/Hero";
import { AgentsSection } from "../components/AgentsSection";

export function Home() {
  return (
    <main>
      <TopBar />
      <Hero />
      <AgentsSection />
    </main>
  );
}
