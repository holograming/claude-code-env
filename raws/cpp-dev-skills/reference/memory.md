```
# Memory leak detection
valgrind --leak-check=full --show-leak-kinds=all ./program

# Detailed report
valgrind --leak-check=full --track-origins=yes ./program

# CPU profiling
valgrind --tool=callgrind ./program
kcachegrind callgrind.out.*
```