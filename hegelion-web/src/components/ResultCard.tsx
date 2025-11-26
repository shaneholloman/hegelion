import React, { useState } from 'react';
import { ChevronDown, ChevronUp, MessageSquare, Scale, Zap, Maximize2, Copy, Check } from 'lucide-react';
import type { Result } from '../data';
import { ResultModal } from './ResultModal';

interface ResultCardProps {
    result: Result;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleCopy = (e: React.MouseEvent) => {
        e.stopPropagation();
        navigator.clipboard.writeText(result.synthesis);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleMaximize = (e: React.MouseEvent) => {
        e.stopPropagation();
        setIsModalOpen(true);
    };

    return (
        <>
            <div className="border border-foreground bg-background mb-8 group/card">
                {/* Header */}
                <div
                    className="border-b border-foreground p-4 flex justify-between items-start cursor-pointer hover:invert transition-none duration-0 group"
                    onClick={() => setIsExpanded(!isExpanded)}
                >
                    <h3 className="font-mono text-lg font-bold uppercase tracking-tight max-w-[70%] md:max-w-[80%]">
                        {result.query}
                    </h3>
                    <div className="flex items-center gap-4">
                        <span className="font-mono text-xs hidden sm:inline-block opacity-60 group-hover:opacity-100">[ID: {result.id}]</span>

                        <div className="flex items-center gap-2">
                            <button
                                onClick={handleMaximize}
                                className="p-1 hover:bg-background hover:text-foreground border border-transparent hover:border-background transition-none"
                                title="Full Screen"
                            >
                                <Maximize2 className="w-4 h-4" />
                            </button>
                            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                        </div>
                    </div>
                </div>

                {/* Content Grid */}
                <div className={`grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-foreground ${isExpanded ? 'block' : 'hidden'}`}>

                    {/* Thesis */}
                    <div className="p-6 flex flex-col gap-4">
                        <div className="flex items-center gap-2 font-mono text-sm uppercase border-b border-foreground pb-2 w-fit">
                            <MessageSquare className="w-4 h-4" />
                            <span>Thesis</span>
                        </div>
                        <p className="font-serif text-lg leading-relaxed line-clamp-[10]">
                            {result.thesis}
                        </p>
                    </div>

                    {/* Antithesis */}
                    <div className="p-6 flex flex-col gap-4 bg-foreground/5">
                        <div className="flex items-center gap-2 font-mono text-sm uppercase border-b border-foreground pb-2 w-fit">
                            <Scale className="w-4 h-4" />
                            <span>Antithesis</span>
                        </div>
                        <p className="font-serif text-lg leading-relaxed italic line-clamp-[10]">
                            {result.antithesis}
                        </p>

                        {/* Council Critiques Preview */}
                        <div className="mt-auto pt-4 border-t border-foreground border-dashed">
                            <h4 className="font-mono text-xs uppercase mb-2 opacity-60">Council Critiques</h4>
                            <div className="flex flex-wrap gap-2">
                                {result.council_critiques.map((c, i) => (
                                    <span key={i} className="font-mono text-xs border border-foreground px-1 py-0.5">
                                        {c.role}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Synthesis */}
                    <div className="p-6 flex flex-col gap-4 bg-foreground text-background selection:bg-background selection:text-foreground relative">
                        <div className="flex justify-between items-start border-b border-background pb-2">
                            <div className="flex items-center gap-2 font-mono text-sm uppercase w-fit">
                                <Zap className="w-4 h-4" />
                                <span>Synthesis</span>
                            </div>
                            <button
                                onClick={handleCopy}
                                className="hover:bg-background hover:text-foreground p-1 transition-none"
                                title="Copy Synthesis"
                            >
                                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                            </button>
                        </div>
                        <p className="font-serif text-lg leading-relaxed font-medium">
                            {result.synthesis}
                        </p>
                    </div>

                </div>

                {/* Preview (when collapsed) */}
                {!isExpanded && (
                    <div className="p-4 font-serif text-sm text-foreground/60 italic truncate flex justify-between items-center">
                        <span>{result.synthesis}</span>
                        <span className="font-mono text-xs uppercase opacity-50 ml-4 hidden md:inline-block">Click to expand</span>
                    </div>
                )}
            </div>

            <ResultModal
                result={result}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </>
    );
};
