import React from 'react';
import { ArrowRight, RefreshCw } from 'lucide-react';

export const ProcessVisualizer: React.FC = () => {
    return (
        <div className="w-full border-y border-foreground py-12 md:py-24 overflow-hidden">
            <div className="container mx-auto px-4">
                <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16">

                    {/* Thesis Node */}
                    <div className="flex flex-col items-center gap-4 text-center group">
                        <div className="w-24 h-24 border border-foreground flex items-center justify-center bg-background shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] group-hover:invert transition-none duration-0">
                            <span className="font-mono font-bold text-xl">THESIS</span>
                        </div>
                        <p className="font-serif italic max-w-[200px]">Initial generation based on prompt.</p>
                    </div>

                    <ArrowRight className="w-8 h-8 hidden md:block" />
                    <ArrowRight className="w-8 h-8 md:hidden rotate-90" />

                    {/* Antithesis Node */}
                    <div className="flex flex-col items-center gap-4 text-center group">
                        <div className="w-24 h-24 border border-foreground flex items-center justify-center bg-background shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] group-hover:invert transition-none duration-0">
                            <span className="font-mono font-bold text-xl">ANTI-</span>
                        </div>
                        <p className="font-serif italic max-w-[200px]">Council critique & counter-arguments.</p>
                    </div>

                    <ArrowRight className="w-8 h-8 hidden md:block" />
                    <ArrowRight className="w-8 h-8 md:hidden rotate-90" />

                    {/* Synthesis Node */}
                    <div className="flex flex-col items-center gap-4 text-center group">
                        <div className="w-24 h-24 border border-foreground flex items-center justify-center bg-foreground text-background shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] group-hover:invert transition-none duration-0">
                            <span className="font-mono font-bold text-xl">SYNTH-</span>
                        </div>
                        <p className="font-serif italic max-w-[200px]">Resolved, higher-order truth.</p>
                    </div>

                </div>

                <div className="mt-12 flex justify-center">
                    <div className="flex items-center gap-2 font-mono text-xs uppercase border border-foreground px-3 py-1 hover:bg-foreground hover:text-background cursor-help transition-none">
                        <RefreshCw className="w-3 h-3" />
                        <span>The Dialectical Loop</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
