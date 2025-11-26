export interface Critique {
    role: string;
    text: string;
}

export interface Result {
    id: string;
    query: string;
    thesis: string;
    antithesis: string;
    synthesis: string;
    council_critiques: Critique[];
}

export const RESULTS: Result[] = [
    {
        id: "1",
        query: "Is free will compatible with determinism?",
        thesis: "Free will and determinism are compatible. This position, compatibilism, redefines 'free will' not as metaphysical libertarian freedom (the ability to have done otherwise in identical circumstances), but as the practical ability to act according to one's desires, beliefs, and rational deliberation without external coercion.",
        antithesis: "Compatibilism collapses under the manipulation argument. If a neuroscientist manipulates your brain to desire coffee, you act 'freely' by compatibilist standards but lack genuine freedom. Determinism is just manipulation by distant causes (Big Bang) rather than a scientist. If manipulation undermines responsibility, so does determinism.",
        synthesis: "The deadlock dissolves when we recognize free will is not binary but exists on a **spectrum of self-authorship**. Freedom comes in degrees based on how much an action reflects stable, reflective patterns versus transient states. The manipulated agent lacks freedom because causation bypasses their character; the cultivated agent possesses freedom because causation runs *through* their reflective self-modification.",
        council_critiques: [
            { role: "Logician", text: "Compatibilist freedom cannot distinguish between authentic choice and manipulated desires." },
            { role: "Ethicist", text: "Genuine responsibility requires being the ultimate source of actions, which determinism precludes." }
        ]
    }
];
