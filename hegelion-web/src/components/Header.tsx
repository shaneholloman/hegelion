

export const Header: React.FC = () => {
    return (
        <header className="sticky top-0 z-50 bg-background border-b border-foreground">
            <div className="container mx-auto px-4 h-16 flex justify-between items-center">
                {/* Logo */}
                <div className="font-sans font-bold text-2xl tracking-tighter uppercase">
                    HEGELION
                </div>

                {/* Navigation */}
                <nav className="flex items-center gap-6">
                    <a
                        href="https://github.com/Hmbown/Hegelion"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-mono text-sm hover:underline decoration-1 underline-offset-4 flex items-center gap-2 group"
                    >
                        <span className="group-hover:bg-foreground group-hover:text-background transition-none px-1">[GITHUB]</span>
                    </a>
                    <a
                        href="https://github.com/Hmbown/Hegelion/tree/main/docs"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-mono text-sm hover:underline decoration-1 underline-offset-4 flex items-center gap-2 group"
                    >
                        <span className="group-hover:bg-foreground group-hover:text-background transition-none px-1">[DOCS]</span>
                    </a>
                    <a
                        href="https://pypi.org/project/hegelion/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-mono text-sm hover:underline decoration-1 underline-offset-4 flex items-center gap-2 group"
                    >
                        <span className="group-hover:bg-foreground group-hover:text-background transition-none px-1">[PYPI]</span>
                    </a>
                </nav>
            </div>
        </header>
    );
};
