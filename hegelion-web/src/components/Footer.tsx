import React from 'react';

export const Footer: React.FC = () => {
    return (
        <footer className="border-t border-foreground py-12 bg-background">
            <div className="container mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
                <div className="col-span-1 md:col-span-2">
                    <h4 className="font-sans font-bold text-xl uppercase mb-4">Hegelion</h4>
                    <p className="font-serif italic max-w-md">
                        "The Truth is the Whole." <br />
                        Automated dialectical reasoning for the age of artificial intelligence.
                    </p>
                </div>

                <div className="flex flex-col gap-2">
                    <h5 className="font-mono text-xs uppercase font-bold mb-2">Resources</h5>
                    <a href="https://github.com/Hmbown/Hegelion/tree/main/docs" target="_blank" rel="noopener noreferrer" className="font-mono text-sm hover:bg-foreground hover:text-background w-fit px-1 transition-none">Documentation</a>
                    <a href="https://github.com/Hmbown/Hegelion" target="_blank" rel="noopener noreferrer" className="font-mono text-sm hover:bg-foreground hover:text-background w-fit px-1 transition-none">API Reference</a>
                    <a href="https://github.com/Hmbown/Hegelion/tree/main/examples" target="_blank" rel="noopener noreferrer" className="font-mono text-sm hover:bg-foreground hover:text-background w-fit px-1 transition-none">Examples</a>
                </div>

                <div className="flex flex-col gap-2">
                    <h5 className="font-mono text-xs uppercase font-bold mb-2">Legal</h5>
                    <a href="#" className="font-mono text-sm hover:bg-foreground hover:text-background w-fit px-1 transition-none">MIT License</a>
                    <a href="#" className="font-mono text-sm hover:bg-foreground hover:text-background w-fit px-1 transition-none">Privacy</a>
                </div>
            </div>

            <div className="container mx-auto px-4 mt-12 pt-8 border-t border-foreground border-dashed flex justify-between items-center">
                <span className="font-mono text-xs">© 2025 Shannon Labs</span>
                <span className="font-mono text-xs">v0.3.1</span>
            </div>
        </footer>
    );
};
