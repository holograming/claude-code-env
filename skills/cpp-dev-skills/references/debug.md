# Debugging with GDB

## Basic Usage

```bash
# Compile with debug symbols
g++ -g -O0 program.cpp -o program

# Start debugger
gdb ./program

# Or with arguments
gdb --args ./program arg1 arg2
```

## Common Commands

```
(gdb) break main          # Set breakpoint at function
(gdb) break file.cpp:10   # Breakpoint at line
(gdb) run                 # Start program
(gdb) continue            # Resume execution
(gdb) step                # Execute next line (enter functions)
(gdb) next                # Execute next line (skip functions)
(gdb) finish              # Run until function return
(gdb) print variable      # Print variable value
(gdb) p *ptr              # Dereference pointer
(gdb) watch variable      # Break when variable changes
(gdb) backtrace           # Show call stack
(gdb) frame N             # Switch to frame
(gdb) up/down             # Navigate stack
(gdb) info locals         # Show local variables
(gdb) quit                # Exit debugger
```

## Advanced Usage

```
(gdb) info breakpoints    # List all breakpoints
(gdb) delete 1            # Delete breakpoint 1
(gdb) condition 1 x > 10  # Break only if condition true
(gdb) set logging on      # Log session to file

# Custom command
(gdb) define loop_print
> print i
> continue
> end

# Automate breakpoint
(gdb) command 1
> silent
> print x
> continue
> end
```
