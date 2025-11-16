#!/bin/bash
# Script to record Hegelion GLM API demo as a GIF

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEMO_SCRIPT="$SCRIPT_DIR/demo_glm_api.py"
OUTPUT_GIF="$SCRIPT_DIR/demo_glm_api.gif"
TAPE_OUTPUT_FILE="demo_glm_api.gif"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🎬 Hegelion GLM API Demo Recording Script"
echo "=========================================="
echo ""

# Check for required environment variable
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ Error: OPENAI_API_KEY environment variable is not set${NC}"
    echo ""
    echo "Please set your GLM API key:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

# Check if demo script exists
if [ ! -f "$DEMO_SCRIPT" ]; then
    echo -e "${RED}❌ Error: Demo script not found at $DEMO_SCRIPT${NC}"
    exit 1
fi

# Make demo script executable
chmod +x "$DEMO_SCRIPT"

# Set GLM environment variables (allow overrides for local stubs)
export HEGELION_PROVIDER="${HEGELION_PROVIDER:-openai}"
export HEGELION_MODEL="${HEGELION_MODEL:-GLM-4.6}"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://api.z.ai/api/coding/paas/v4}"

echo "📋 Configuration:"
echo "  Provider: $HEGELION_PROVIDER"
echo "  Model: $HEGELION_MODEL"
echo "  Base URL: $OPENAI_BASE_URL"
echo ""

# Check for recording tools
RECORDING_TOOL=""
RECORDING_METHOD=""

if command -v vhs &> /dev/null; then
    RECORDING_TOOL="vhs"
    RECORDING_METHOD="vhs"
    echo -e "${GREEN}✓ Found vhs (charm.sh)${NC}"
elif command -v asciinema &> /dev/null && command -v agg &> /dev/null; then
    RECORDING_TOOL="asciinema"
    RECORDING_METHOD="asciinema"
    echo -e "${GREEN}✓ Found asciinema + agg${NC}"
else
    echo -e "${YELLOW}⚠️  No GIF recording tool found${NC}"
    echo ""
    echo "Please install one of the following:"
    echo ""
    echo "Option 1: vhs (recommended)"
    echo "  brew install vhs"
    echo "  # or visit: https://github.com/charmbracelet/vhs"
    echo ""
    echo "Option 2: asciinema + agg"
    echo "  brew install asciinema agg"
    echo "  # or visit: https://github.com/asciinema/asciinema and https://github.com/asciinema/agg"
    echo ""
    exit 1
fi

# Create VHS tape file if using vhs
if [ "$RECORDING_METHOD" = "vhs" ]; then
    TAPE_FILE="$SCRIPT_DIR/demo_glm_api.tape"
    
cat > "$TAPE_FILE" << EOF
Output $TAPE_OUTPUT_FILE
Set FontSize 14
Set Width 1200
Set Height 800
Set TypingSpeed 50ms
Set PlaybackSpeed 1.5

Type "cd $PROJECT_ROOT/examples"
Enter
Sleep 500ms

Type "export HEGELION_PROVIDER=openai"
Enter
Sleep 200ms

Type "export HEGELION_MODEL=GLM-4.6"
Enter
Sleep 200ms

Type "export OPENAI_BASE_URL=$OPENAI_BASE_URL"
Enter
Sleep 200ms

Type "python3 demo_glm_api.py"
Enter
Sleep 60s

Sleep 2s
EOF
    
    echo "📝 Created VHS tape file: $TAPE_FILE"
    echo ""
    echo "🎥 Recording demo..."
    echo ""
    
    cd "$PROJECT_ROOT"
    vhs "$TAPE_FILE"
    
    if [ -f "$OUTPUT_GIF" ]; then
        echo ""
        echo -e "${GREEN}✅ Recording complete!${NC}"
        echo "   Output: $OUTPUT_GIF"
    else
        echo ""
        echo -e "${YELLOW}⚠️  GIF not found at expected location${NC}"
        echo "   Checking for GIF in common directories..."
        POTENTIAL_PATHS=(
            "$PROJECT_ROOT/$TAPE_OUTPUT_FILE"
            "$SCRIPT_DIR/$TAPE_OUTPUT_FILE"
        )
        for candidate in "${POTENTIAL_PATHS[@]}"; do
            if [ -f "$candidate" ]; then
                mv "$candidate" "$OUTPUT_GIF"
                echo -e "${GREEN}✅ Found and moved GIF to: $OUTPUT_GIF${NC}"
                break
            fi
        done
        if [ ! -f "$OUTPUT_GIF" ]; then
            echo -e "${RED}❌ Recording may have failed - GIF not found${NC}"
            echo "   Check vhs output above for errors"
        fi
    fi

# Use asciinema + agg
elif [ "$RECORDING_METHOD" = "asciinema" ]; then
    CAST_FILE="$SCRIPT_DIR/demo_glm_api.cast"
    
    echo "🎥 Recording with asciinema..."
    echo "   (Automated recording - demo will run automatically)"
    echo ""
    
    # Create a wrapper script that sets env vars and runs the demo
    WRAPPER_SCRIPT="$SCRIPT_DIR/run_demo_wrapper.sh"
    cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
export HEGELION_PROVIDER=openai
export HEGELION_MODEL=GLM-4.6
export OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
cd "$(dirname "$0")"
python3 demo_glm_api.py
sleep 2
EOF
    
    chmod +x "$WRAPPER_SCRIPT"
    
    echo "Starting asciinema recording..."
    asciinema rec "$CAST_FILE" --command "$WRAPPER_SCRIPT"
    
    echo ""
    echo "🎨 Converting to GIF with agg..."
    agg "$CAST_FILE" "$OUTPUT_GIF"
    
    # Clean up temporary files
    rm -f "$CAST_FILE" "$WRAPPER_SCRIPT"
    
    if [ -f "$OUTPUT_GIF" ]; then
        echo ""
        echo -e "${GREEN}✅ Recording complete!${NC}"
        echo "   Output: $OUTPUT_GIF"
    else
        echo ""
        echo -e "${RED}❌ Conversion failed - GIF not found${NC}"
        exit 1
    fi
fi

echo ""
echo "🎉 Done! View your GIF at: $OUTPUT_GIF"

