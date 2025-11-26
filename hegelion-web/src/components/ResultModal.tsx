import React, { useEffect } from 'react';
import { X, Copy, Check } from 'lucide-react';
import type { Result } from '../data';

interface ResultModalProps {
    result: Result;
    isOpen: boolean;
    onClose: () => void;
}

export const ResultModal: React.FC<ResultModalProps> = ({ result, isOpen, onClose }) => {
    const [copied, setCopied] = React.useState(false);

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    if (!isOpen) return null;

    const handleCopy = () => {
        const text = `Query: ${result.query}\n\nThesis: ${result.thesis}\n\nAntithesis: ${result.antithesis}\n\nSynthesis: ${result.synthesis}`;
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 bg-foreground/90 backdrop-blur-sm">
            <div className="bg-background w-full max-w-5xl h-full max-h-[90vh] border border-foreground shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] flex flex-col overflow-hidden relative">

                {/* Modal Header */}
                <div className="flex justify-between items-start p-6 border-b border-foreground bg-background sticky top-0 z-10">
                    <div>
                        <span className="font-mono text-xs uppercase tracking-widest block mb-2 text-foreground/60">Dialectical Trace [ID: {result.id}]</span>
                        <h2 className="font-serif text-2xl md:text-4xl leading-tight max-w-3xl">{result.query}</h2>
                    </div>
                    <div className="flex gap-4">
                        <button
                            onClick={handleCopy}
                            className="p-2 hover:bg-foreground hover:text-background border border-foreground transition-none flex items-center gap-2 group"
                            title="Copy Full Trace"
                        >
                            {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                            <span className="font-mono text-xs uppercase hidden md:inline">{copied ? 'Copied' : 'Copy'}</span>
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-foreground hover:text-background border border-foreground transition-none"
                            title="Close"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>
                </div>

                {/* Modal Content */}
                <div className="overflow-y-auto p-6 md:p-12 space-y-12">

                    {/* Thesis */}
                    <section>
                        <div className="flex items-center gap-4 mb-4">
                            <div className="w-8 h-8 flex items-center justify-center border border-foreground font-mono font-bold bg-background">T</div>
                            <h3 className="font-mono text-lg uppercase tracking-widest">Thesis</h3>
                        </div>
                        <p className="font-serif text-xl md:text-2xl leading-relaxed pl-12 border-l border-foreground/20">
                            {result.thesis}
                        </p>
                    </section>

                    {/* Antithesis */}
                    <section>
                        <div className="flex items-center gap-4 mb-4">
                            <div className="w-8 h-8 flex items-center justify-center border border-foreground font-mono font-bold bg-foreground text-background">A</div>
                            <h3 className="font-mono text-lg uppercase tracking-widest">Antithesis</h3>
                        </div>
                        <div className="pl-12 border-l border-foreground/20 space-y-6">
                            <p className="font-serif text-xl md:text-2xl leading-relaxed italic">
                                {result.antithesis}
                            </p>

                            {/* Council Critiques */}
                            <div className="bg-foreground/5 p-6 border border-foreground/10">
                                <h4 className="font-mono text-xs uppercase font-bold mb-4 flex items-center gap-2">
                                    <span className="w-2 h-2 bg-foreground rounded-none"></span>
                                    Council Critiques
                                </h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {result.council_critiques.map((critique, idx) => (
                                        <div key={idx} className="font-mono text-sm">
                                            <span className="bg-foreground text-background px-1 py-0.5 mr-2 uppercase text-xs">{critique.role}</span>
                                            <span className="opacity-80">{critique.text}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Synthesis */}
                    <section className="bg-foreground text-background p-8 md:p-12 -mx-6 md:-mx-12 border-t border-foreground">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-8 h-8 flex items-center justify-center border border-background font-mono font-bold bg-background text-foreground">S</div>
                            <h3 className="font-mono text-lg uppercase tracking-widest">Synthesis</h3>
                        </div>
                        <p className="font-serif text-2xl md:text-3xl leading-relaxed font-medium">
                            {result.synthesis}
                        </p>
                    </section>

                </div>
            </div>
        </div>
    );
};
