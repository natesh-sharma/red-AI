# RED-AI Changes

## Version 1.0.0

### Updates Made

1. **Tool Renamed**
   - From: `rhel-ai-tool`
   - To: `red-ai`
   - Binary name updated in Makefile and all documentation

2. **Owner Attribution**
   - Owner: Natesh Sharma
   - Added to banner display and README

3. **Root-Only Enforcement**
   - Tool now requires direct root execution (UID 0 only)
   - **Cannot be run with `sudo`** - must log in as root
   - **Cannot be run by non-root users** - will reject with error
   - Error message updated to clearly indicate requirement

4. **Documentation Updates**
   - README.md: Updated all examples to use `./red-ai` instead of `sudo ./rhel-ai-tool`
   - QUICK_START.md: Updated all examples and added troubleshooting for root-only requirement
   - Added clear warnings about sudo not working
   - Updated prerequisites to mention "Direct root access (UID 0)"

5. **Code Changes**
   - `red_ai.c`: Updated banner with developer name and new tool name
   - `command_executor.c`: Enhanced root check to prevent sudo execution
   - `Makefile`: Changed TARGET from `rhel-ai-tool` to `red-ai`
   - `.gitignore`: Added build artifacts and renamed binary

### Key Features

✓ Named: RED-AI
✓ Owner: Natesh Sharma
✓ Root-only execution (UID 0)
✓ No sudo execution allowed
✓ No non-root user execution allowed

### Testing the Tool

```bash
# Build
make

# Run as root user directly
./red-ai --help
./red-ai --dry-run "check kdump status"
```

### Security Notes

- The tool enforces strict root-only execution
- Will reject execution via sudo
- Will reject execution by non-root users
- Clear error messages guide users to the proper execution method
