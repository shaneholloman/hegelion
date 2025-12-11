import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { ProcessVisualizer } from './components/ProcessVisualizer';
import { ResultCard } from './components/ResultCard';
import { RESULTS } from './data';
import { Triangle, Code, Brain, CheckCircle, XCircle, ArrowRight, RefreshCw } from 'lucide-react';
import hegelImage from './assets/hegel.jpg';

function App() {
  return (
    <div className="min-h-screen flex flex-col font-sans text-foreground bg-background selection:bg-black selection:text-white">
      <Header />

      <main className="flex-grow">
        {/* Hero Section */}
        <section className="container mx-auto px-4 py-24 md:py-32 grid grid-cols-1 md:grid-cols-2 gap-12 items-center border-b border-foreground">
          <div className="space-y-6">
            <div className="inline-block border border-foreground px-3 py-1 font-mono text-xs uppercase tracking-wider">
              v0.4.0 — Now with Autocoding
            </div>
            <h1 className="font-serif text-6xl md:text-8xl leading-[0.9] tracking-tight">
              The Truth <br /> is the Whole.
            </h1>
            <p className="font-mono text-lg md:text-xl max-w-md border-l-2 border-foreground pl-6 py-2">
              Dialectical reasoning for questions. Verified implementations for code.
            </p>
            <div className="pt-8 flex gap-4">
              <a
                href="https://github.com/Hmbown/Hegelion/tree/main/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-foreground text-background px-8 py-4 font-mono font-bold uppercase hover:invert border border-foreground transition-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:translate-x-[2px] active:translate-y-[2px] active:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] inline-block"
              >
                Get Started
              </a>
              <a
                href="https://github.com/Hmbown/Hegelion"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-background text-foreground px-8 py-4 font-mono font-bold uppercase hover:bg-foreground hover:text-background border border-foreground transition-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:translate-x-[2px] active:translate-y-[2px] active:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] inline-block"
              >
                View on GitHub
              </a>
            </div>
          </div>

          <div className="flex justify-center items-center relative h-full min-h-[400px] border-l border-foreground border-dashed">
            {/* Abstract Triad Art */}
            <div className="relative w-64 h-64">
              <div className="absolute inset-0 border-2 border-foreground rotate-0 transition-transform duration-[10s] hover:rotate-180"></div>
              <div className="absolute inset-4 border-2 border-foreground rotate-45"></div>
              <div className="absolute inset-8 border-2 border-foreground rotate-12 bg-foreground/5"></div>
              <Triangle className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 stroke-[1px]" />
            </div>
          </div>
        </section>

        {/* Two Modes Section */}
        <section className="border-b border-foreground">
          <div className="container mx-auto px-4 py-12 border-b border-foreground">
            <h2 className="font-mono text-sm uppercase tracking-widest mb-2">Two Modes</h2>
            <p className="font-serif text-3xl">Force the model to oppose itself.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2">
            {/* Dialectical Reasoning */}
            <div className="border-b md:border-b-0 md:border-r border-foreground p-8 md:p-12">
              <div className="flex items-center gap-3 mb-6">
                <Brain className="w-8 h-8" />
                <h3 className="font-serif text-2xl">Dialectical Reasoning</h3>
              </div>
              <p className="font-mono text-sm mb-6 opacity-80">
                For questions requiring deep analysis. Three separate LLM calls force genuine self-critique.
              </p>
              <div className="flex items-center gap-2 font-mono text-sm">
                <span className="border border-foreground px-2 py-1">Thesis</span>
                <ArrowRight className="w-4 h-4" />
                <span className="border border-foreground px-2 py-1">Antithesis</span>
                <ArrowRight className="w-4 h-4" />
                <span className="border border-foreground px-2 py-1 bg-foreground text-background">Synthesis</span>
              </div>
            </div>
            {/* Autocoding */}
            <div className="p-8 md:p-12">
              <div className="flex items-center gap-3 mb-6">
                <Code className="w-8 h-8" />
                <h3 className="font-serif text-2xl">Autocoding</h3>
              </div>
              <p className="font-mono text-sm mb-6 opacity-80">
                For verified implementations. Player builds, Coach verifies independently. No premature success claims.
              </p>
              <div className="flex items-center gap-2 font-mono text-sm">
                <span className="border border-foreground px-2 py-1">Player</span>
                <ArrowRight className="w-4 h-4" />
                <span className="border border-foreground px-2 py-1">Coach</span>
                <ArrowRight className="w-4 h-4" />
                <RefreshCw className="w-4 h-4" />
                <span className="border border-foreground px-2 py-1 bg-foreground text-background">Approved</span>
              </div>
            </div>
          </div>
        </section>

        {/* Process Section */}
        <section className="bg-background">
          <div className="container mx-auto px-4 py-12 border-b border-foreground">
            <h2 className="font-mono text-sm uppercase tracking-widest mb-2">The Process</h2>
            <p className="font-serif text-3xl">Thesis. Antithesis. Synthesis.</p>
          </div>
          <ProcessVisualizer />
        </section>

        {/* Autocoding Section */}
        <section className="border-y border-foreground bg-foreground text-background">
          <div className="container mx-auto px-4 py-24">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div className="space-y-6">
                <div className="inline-block border border-background px-3 py-1 font-mono text-xs uppercase tracking-wider">
                  New in v0.4.0
                </div>
                <h2 className="font-serif text-5xl md:text-6xl leading-none">
                  Player-Coach Loop.
                </h2>
                <p className="font-serif text-xl leading-relaxed opacity-90">
                  Based on <a href="https://block.xyz/documents/adversarial-cooperation-in-code-synthesis.pdf" target="_blank" rel="noopener noreferrer" className="underline hover:no-underline">Block AI's g3 agent research</a>. Two roles iterate until requirements are verified.
                </p>
                <div className="space-y-4 font-mono text-sm">
                  <div className="flex items-start gap-3">
                    <Code className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-bold">Player</span> — Implements requirements, writes tests. Does NOT declare success.
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-bold">Coach</span> — Independently verifies each requirement. Ignores player's self-assessment.
                    </div>
                  </div>
                </div>
                <p className="font-mono text-sm border-l border-background pl-4 py-2 opacity-70">
                  "Discard the player's self-report of success. Have the coach perform independent evaluation."
                </p>
              </div>

              {/* Coach Checklist Visualization */}
              <div className="border border-background p-6 font-mono text-sm">
                <div className="mb-4 pb-4 border-b border-background opacity-60">
                  COACH VERIFICATION
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span>Authentication endpoint exists</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span>JWT validation middleware added</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <XCircle className="w-5 h-5 text-red-400" />
                    <span>Missing password validation test</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span>Error handling for invalid tokens</span>
                  </div>
                </div>
                <div className="mt-6 pt-4 border-t border-background">
                  <span className="opacity-60">VERDICT:</span> <span className="text-yellow-400">NEEDS WORK</span>
                </div>
                <div className="mt-2 text-xs opacity-50">
                  → Player will address missing test, then Coach re-verifies
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Who is Hegel? Section */}
        <section className="border-b border-foreground">
          <div className="container mx-auto px-4 py-24 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1">
              <div className="border border-foreground p-2 inline-block mb-6">
                <img src={hegelImage} alt="Georg Wilhelm Friedrich Hegel" className="w-full max-w-sm grayscale contrast-125 block" />
              </div>
              <p className="font-mono text-xs uppercase tracking-widest opacity-80">
                Georg Wilhelm Friedrich Hegel (1770–1831)
              </p>
            </div>
            <div className="order-1 md:order-2 space-y-6">
              <h2 className="font-serif text-5xl md:text-6xl leading-none">
                The Dialectical Method.
              </h2>
              <p className="font-serif text-xl leading-relaxed opacity-90">
                Hegelion is inspired by the philosophy of G.W.F. Hegel, who argued that truth is not a static fact but a dynamic process.
              </p>
              <p className="font-serif text-lg leading-relaxed opacity-80">
                In his dialectic, an initial idea (<b>Thesis</b>) inevitably encounters its contradiction (<b>Antithesis</b>). The tension between these two is not a failure, but the engine of progress, resolved only by rising to a higher level of understanding (<b>Synthesis</b>).
              </p>
              <p className="font-mono text-sm border-l border-foreground pl-4 py-2 opacity-70">
                "The bud disappears when the blossom breaks through, and we might say that the former is refuted by the latter."
              </p>
            </div>
          </div>
        </section>

        {/* Showcase Section */}
        <section className="container mx-auto px-4 py-24">

          <div className="mb-16 flex flex-col md:flex-row justify-between items-end gap-6 border-b border-foreground pb-6">
            <div>
              <h2 className="font-serif text-5xl mb-4">Showcase</h2>
              <p className="font-mono text-sm max-w-md">
                Selected dialectical reasoning traces generated by Hegelion.
                Demonstrating the power of self-critique.
              </p>
            </div>
            <div className="font-mono text-xs uppercase border border-foreground px-2 py-1">
              {RESULTS.length} Records Found
            </div>
          </div>

          <div className="space-y-0">
            {RESULTS.map((result) => (
              <ResultCard key={result.id} result={result} />
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

export default App;
