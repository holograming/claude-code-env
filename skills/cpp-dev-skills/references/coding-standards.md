# C++ Coding Standards (Google Style Guide)

**For Claude Automation:** Claude MUST follow these standards for ALL C++ code generation (templates + dialogue).

**Status:** Phase 1 Core Document | Priority Level: ⭐ **CRITICAL**

---

## 1. Naming Conventions (Priority 1 - MUST)

All naming conventions follow Google C++ Style Guide with clarifications for cpp-dev-skills.

### Type Names: `UpperCamelCase`

Use `UpperCamelCase` for all type definitions:
- Classes
- Structs
- Unions
- Enumerations
- Type aliases

```cpp
// ✅ CORRECT
class DatabaseConnection { };
struct ConnectionConfig { };
enum class LogLevel { };
union DataValue { };
using ByteArray = std::vector<std::uint8_t>;

// ❌ INCORRECT
class database_connection { };
struct ConnectionConfig { };
enum logLevel { };
```

### Function Names: `UpperCamelCase()`

Use `UpperCamelCase()` for all functions and methods (including getters/setters):

```cpp
// ✅ CORRECT
class File {
 public:
  void Open(const std::string& path);
  void Close();
  std::string GetFileName() const;
  void SetPermissions(int perms);
  bool IsOpen() const;
};

// ❌ INCORRECT
class File {
 public:
  void open(const std::string& path);  // lowercase
  void close();
  std::string get_file_name() const;   // snake_case
  void set_permissions(int perms);
};
```

**Exception:** Operator overloads use their standard notation:
```cpp
// ✅ CORRECT
bool operator==(const File& other) const;
File& operator=(const File& other);
std::ostream& operator<<(std::ostream& os, const File& f);
```

### Variable Names: `lower_with_underscores`

Use `lower_with_underscores` for local variables and parameters:

```cpp
// ✅ CORRECT
void ProcessData(const std::string& input_file, int max_retries) {
  std::vector<int> data_points;
  int current_index = 0;
  bool is_valid = true;

  for (int i = 0; i < max_retries; ++i) {
    // ...
  }
}

// ❌ INCORRECT
void processData(const std::string& inputFile, int maxRetries) {
  std::vector<int> dataPoints;
  int CurrentIndex = 0;
  bool IsValid = true;
}
```

### Member Variables: `trailing_underscore_`

Use `trailing_underscore_` for member variables (class/struct fields):

```cpp
// ✅ CORRECT
class NetworkSocket {
 private:
  std::string host_;
  int port_;
  bool is_connected_;
  std::unique_ptr<Connection> connection_;

 public:
  // No trailing underscore in methods
  void Connect();
  std::string GetHost() const { return host_; }
};

// ❌ INCORRECT
class NetworkSocket {
 private:
  std::string host;        // No underscore
  int mPort;               // "m" prefix (deprecated)
  bool connected;
  std::unique_ptr<Connection> connection;
};
```

### Constants: `kConstantName`

Use `kConstantName` (k-prefix in `UpperCamelCase`) for constants:

```cpp
// ✅ CORRECT
namespace config {

constexpr int kMaxConnections = 100;
constexpr int kDefaultPort = 8080;
constexpr std::string_view kApplicationName = "MyApp";
const float kPi = 3.14159f;

}

class Database {
 private:
  static constexpr int kMaxRetries = 3;
  static constexpr std::chrono::milliseconds kTimeout{5000};
};

// ❌ INCORRECT
constexpr int MAX_CONNECTIONS = 100;      // UPPERCASE (C-style macro)
constexpr int DefaultPort = 8080;         // No k-prefix
const float PI = 3.14159f;                // UPPERCASE
```

### Namespaces: `lower_with_underscores`

Use `lower_with_underscores` for namespace names:

```cpp
// ✅ CORRECT
namespace network {
namespace http {

class Client { };

}  // namespace http
}  // namespace network

// Usage
network::http::Client client;

// ❌ INCORRECT
namespace Network::HTTP { }     // Mixed case
namespace NETWORK { }           // UPPERCASE
```

### Template Parameters: Descriptive Names

Use clear descriptive names for template parameters:

```cpp
// ✅ CORRECT (descriptive)
template<typename ContainerType>
void Process(const ContainerType& data) { }

template<typename KeyType, typename ValueType>
class Cache { };

// ❌ INCORRECT (cryptic)
template<typename T>
void Process(const T& data) { }  // Too generic (but acceptable in some contexts)

template<typename K, typename V>
class Cache { };  // Single letters only
```

---

## 2. File Organization

### Header Guard: `#pragma once`

Use `#pragma once` instead of traditional `#ifndef` guards:

```cpp
// ✅ CORRECT (modern, shorter)
#pragma once

#include <vector>
#include <string>

class MyClass { };

// ❌ INCORRECT (legacy, verbose)
#ifndef MY_CLASS_H_
#define MY_CLASS_H_

#include <vector>
#include <string>

class MyClass { };

#endif  // MY_CLASS_H_
```

**Rationale:** `#pragma once` is:
- Supported by all modern compilers (GCC 3.4+, Clang 1.7+, MSVC 7.0+)
- Less error-prone (no header guard typos)
- Shorter and more readable
- Standard in cpp-dev-skills

### Include Order

Organize includes in this specific order with blank lines between groups:

```cpp
// ✅ CORRECT include order
#pragma once

// 1. C++ Standard Library (most to least specific)
#include <iostream>
#include <vector>
#include <memory>
#include <string>

// 2. Third-party libraries
#include <nlohmann/json.hpp>
#include <boost/asio.hpp>

// 3. Project headers (relative paths)
#include "myapp/config.h"
#include "myapp/database.h"

// 4. Local headers (if needed)
#include "internal_helper.h"

class MyClass { };

// ❌ INCORRECT include order
#include "myapp/database.h"
#include <iostream>
#include <nlohmann/json.hpp>
#include "myapp/config.h"
#include <vector>
```

### File Organization

Structure files as follows:

**Header File (.h)**
```cpp
#pragma once

#include <memory>
#include <string>

#include "project/config.h"

namespace myapp {

/// @brief Brief description of the class.
///
/// Longer description if needed. Explain design decisions,
/// thread safety, ownership semantics.
class MyClass {
 public:
  /// @brief Constructor description.
  /// @param name Configuration name.
  explicit MyClass(const std::string& name);

  // Destructor if non-trivial
  ~MyClass();

  // Delete copy operations (or define if needed)
  MyClass(const MyClass&) = delete;
  MyClass& operator=(const MyClass&) = delete;

  // Define move operations if beneficial
  MyClass(MyClass&&) noexcept = default;
  MyClass& operator=(MyClass&&) noexcept = default;

  /// @brief Public method description.
  /// @param value Parameter description.
  /// @return Return value description.
  void ProcessData(int value);

  /// @brief Getter for internal state.
  /// @return Current state value.
  int GetState() const;

 private:
  // Private helper methods
  void ValidateInput();

  // Member variables (trailing underscore)
  std::string name_;
  int state_;
  std::unique_ptr<Helper> helper_;
};

}  // namespace myapp
```

**Source File (.cpp)**
```cpp
#include "myapp/my_class.h"

#include <algorithm>
#include <stdexcept>

#include "myapp/logger.h"

namespace myapp {

MyClass::MyClass(const std::string& name)
    : name_(name), state_(0), helper_(std::make_unique<Helper>()) {
}

MyClass::~MyClass() = default;

void MyClass::ProcessData(int value) {
  ValidateInput();
  // Implementation
}

int MyClass::GetState() const {
  return state_;
}

void MyClass::ValidateInput() {
  // Private implementation
}

}  // namespace myapp
```

### One Class Per File

With few exceptions:
- One public class per `.h`/`.cpp` pair
- OK to include small private helpers in same file
- Template implementations in `.hpp` or inline

```cpp
// ✅ CORRECT
// file: database.h
class Database { };

// file: query.h
class Query { };  // Separate file

// ❌ INCORRECT
// file: database.h
class Database { };
class Query { };      // Should be separate file
class CacheManager { };
```

---

## 3. Code Formatting

### Indentation: 4 Spaces

Use 4 spaces for indentation (NOT tabs):

```cpp
// ✅ CORRECT (4 spaces)
namespace myapp {

class Example {
 public:
  void Method() {
    if (condition) {
      std::cout << "Hello" << std::endl;
    }
  }
};

}  // namespace myapp

// ❌ INCORRECT (tabs)
// ❌ INCORRECT (2 spaces - Google style deviation, but NOT for cpp-dev-skills)
```

**Note:** Google C++ Style uses 2 spaces; cpp-dev-skills uses 4 spaces for better readability.

### Line Length: 120 Characters

Keep lines under 120 characters (adjust at `.clang-format`):

```cpp
// ✅ CORRECT (long parameter list broken)
void ProcessLargeDataset(const std::vector<int>& input_data,
                          const std::string& config_file,
                          int max_retries,
                          bool verbose_output) {
  // Implementation
}

// Alternatively, move parameter to next line for clarity
bool IsValidConfiguration(
    const std::string& config_path,
    const ValidationOptions& options) {
  // Implementation
  return true;
}

// ❌ INCORRECT (exceeds 120 chars on one line)
void ProcessLargeDataset(const std::vector<int>& input_data, const std::string& config_file, int max_retries, bool verbose_output) {
  // Implementation
}
```

### Braces: Opening on Same Line

Opening braces go on the same line (not on new line):

```cpp
// ✅ CORRECT (brace on same line)
if (condition) {
  DoSomething();
} else {
  DoOtherThing();
}

class MyClass {
  void Method() {
    // Implementation
  }
};

for (int i = 0; i < 10; ++i) {
  Process(i);
}

// ❌ INCORRECT (brace on new line - Allman style)
if (condition)
{
  DoSomething();
}
else
{
  DoOtherThing();
}
```

### Pointer and Reference Alignment

Place `*` and `&` with the type (left-aligned):

```cpp
// ✅ CORRECT (left-aligned)
int* ptr = nullptr;
int& ref = value;
const std::string* ptr_to_str = nullptr;

void Function(int* param, const std::string& str_ref) {
  // Implementation
}

// ❌ INCORRECT (right-aligned - old style)
int *ptr = nullptr;
int &ref = value;
const std::string *ptr_to_str = nullptr;
```

### Spaces Around Operators

Use spaces around binary operators:

```cpp
// ✅ CORRECT
int result = a + b * c;
bool is_valid = (x > 5) && (y < 10);
if (count == 0) { }

// ❌ INCORRECT
int result = a+b*c;
bool is_valid = (x>5)&&(y<10);
```

---

## 4. Comments and Documentation

### File Header Comments

Every source file begins with a header comment:

```cpp
// {project_name} - Brief description of file purpose
// Copyright (c) 2025
//
// Longer description if needed. Explain the overall design,
// important algorithms, or assumptions.

#pragma once

#include <vector>

class MyClass { };
```

### Function Documentation

Document public API functions with `///` (Doxygen style):

```cpp
/// @brief Brief one-line description (ends with period).
///
/// Longer detailed description explaining:
/// - What the function does
/// - Important preconditions
/// - Thread safety guarantees
/// - Performance characteristics (if relevant)
///
/// @param name Parameter description.
/// @param value Another parameter description.
/// @return Description of return value.
/// @throws std::invalid_argument If name is empty.
/// @see RelatedFunction()
void ProcessData(const std::string& name, int value);
```

**For class methods:**

```cpp
class FileHandler {
 public:
  /// @brief Opens a file for reading/writing.
  /// @param path File path (must exist).
  /// @param mode File open mode (r/w/a).
  /// @return True if successful, false otherwise.
  /// @note This method is thread-safe.
  bool Open(const std::string& path, const std::string& mode);

  /// @brief Reads entire file content.
  /// @return File content as string.
  /// @throws std::runtime_error If file is not open.
  std::string Read() const;
};
```

### Inline Comments

Comments should explain **WHY**, not WHAT. The code shows WHAT:

```cpp
// ✅ CORRECT (explains why)
// Use exponential backoff to avoid overwhelming the server
for (int attempt = 0; attempt < kMaxRetries; ++attempt) {
  const int delay_ms = kBaseDelay * (1 << attempt);  // 2^n backoff
  if (AttemptConnection(delay_ms)) {
    return true;
  }
}

// ❌ INCORRECT (just restates code)
for (int attempt = 0; attempt < kMaxRetries; ++attempt) {
  int delay_ms = 100 * (1 << attempt);  // exponential backoff
  if (AttemptConnection(delay_ms)) {   // if successful
    return true;                         // return true
  }
}
```

### Section Comments

For complex functions, use section headers:

```cpp
void ComplexOperation() {
  // Phase 1: Input validation
  ValidateInputs();

  // Phase 2: Data transformation
  TransformData();

  // Phase 3: Result aggregation
  AggregateResults();
}
```

---

## 5. Modern C++ Best Practices (C++11/14/17)

### Use Smart Pointers, Never Raw `new`/`delete`

```cpp
// ✅ CORRECT (smart pointers)
class ResourceManager {
 private:
  std::unique_ptr<Resource> exclusive_;      // Unique ownership
  std::shared_ptr<Cache> shared_;            // Shared ownership
  std::weak_ptr<Parent> parent_;             // Non-owning reference
};

// ❌ INCORRECT (raw pointers with manual memory management)
class ResourceManager {
 private:
  Resource* exclusive_;   // Must manually delete
  Cache* shared_;         // No cleanup semantics
};
```

### Use `auto` When Type Is Obvious

```cpp
// ✅ CORRECT (type is obvious from RHS)
auto result = std::make_unique<MyClass>();
auto path = GetConfigPath();
std::vector<int> numbers = GetNumbers();
auto iter = numbers.begin();

// Also fine (explicit when it adds clarity)
std::unique_ptr<MyClass> result = std::make_unique<MyClass>();

// ❌ INCORRECT (type not obvious)
auto x = ReadFile();  // What is x? File? String? Stream?
auto Compute(int a, int b);  // Is return type obvious to reader?
```

### Range-Based For Loops

```cpp
// ✅ CORRECT (range-based)
std::vector<int> numbers = {1, 2, 3, 4, 5};
for (int num : numbers) {
  Process(num);
}

for (const auto& name : names) {
  std::cout << name << std::endl;
}

// ❌ INCORRECT (index-based when not needed)
for (int i = 0; i < numbers.size(); ++i) {
  Process(numbers[i]);
}
```

### Use `nullptr` Instead of `NULL`

```cpp
// ✅ CORRECT
if (ptr == nullptr) {
  Handle();
}

std::unique_ptr<Object> obj = nullptr;

// ❌ INCORRECT
if (ptr == NULL) { }
if (ptr == 0) { }
std::unique_ptr<Object> obj = NULL;
```

### Virtual Function Override

Always use `override` for virtual functions in derived classes:

```cpp
// ✅ CORRECT
class Base {
 public:
  virtual void DoWork() = 0;
  virtual ~Base() = default;
};

class Derived : public Base {
 public:
  void DoWork() override {  // Explicit override
    // Implementation
  }
  ~Derived() override = default;
};

// ❌ INCORRECT (missing override)
class Derived : public Base {
 public:
  void DoWork() {  // Compiler won't catch signature mismatches
    // Implementation
  }
};
```

### Use `enum class` Not Plain `enum`

```cpp
// ✅ CORRECT (scoped, type-safe)
enum class Status {
  kUnknown = 0,
  kSuccess = 1,
  kError = 2,
};

Status status = Status::kSuccess;

// ❌ INCORRECT (unscoped, pollutes namespace)
enum Status {
  UNKNOWN = 0,
  SUCCESS = 1,
  ERROR = 2,
};

Status status = SUCCESS;  // Ambiguous if multiple enums have SUCCESS
```

### Move Semantics and Rvalue References

```cpp
// ✅ CORRECT (move semantics)
class DataBuffer {
 public:
  DataBuffer(std::vector<uint8_t>&& data)
      : data_(std::move(data)) { }

  void SetData(std::vector<uint8_t>&& new_data) {
    data_ = std::move(new_data);
  }

 private:
  std::vector<uint8_t> data_;
};

// Usage
std::vector<uint8_t> large_data = CreateLargeData();
DataBuffer buffer(std::move(large_data));  // Efficient move

// ❌ INCORRECT (inefficient copy)
class DataBuffer {
 public:
  void SetData(const std::vector<uint8_t>& new_data) {
    data_ = new_data;  // Copies entire vector
  }
};
```

### Explicit Constructors and Conversions

```cpp
// ✅ CORRECT (explicit conversions)
class String {
 public:
  explicit String(const char* cstr) { }
  explicit String(int size) { }
};

String s1(10);         // OK: clear intent
String s2 = "text";    // ERROR: must be explicit

// ❌ INCORRECT (implicit conversions)
class String {
 public:
  String(const char* cstr) { }  // Allows implicit conversion
  String(int size) { }
};

String s = "text";  // Silent conversion
```

---

## 6. Comprehensive Examples

### Example 1: Simple Library Header

```cpp
// calculator - Mathematical operations library
// Copyright (c) 2025

#pragma once

#include <string>

namespace calculator {

/// @brief Performs basic arithmetic operations.
class Calculator {
 public:
  /// @brief Constructs calculator with initial value.
  /// @param initial_value Starting value for operations.
  explicit Calculator(double initial_value = 0.0);

  /// @brief Adds value to current state.
  /// @param value Value to add.
  void Add(double value);

  /// @brief Subtracts value from current state.
  void Subtract(double value);

  /// @brief Multiplies current state by value.
  void Multiply(double value);

  /// @brief Gets current accumulated value.
  /// @return Current value.
  double GetResult() const { return result_; }

  /// @brief Resets calculator to initial value.
  void Reset();

 private:
  double result_;
};

}  // namespace calculator
```

```cpp
// calculator.cpp implementation
#include "calculator/calculator.h"

namespace calculator {

Calculator::Calculator(double initial_value)
    : result_(initial_value) {
}

void Calculator::Add(double value) {
  result_ += value;
}

void Calculator::Subtract(double value) {
  result_ -= value;
}

void Calculator::Multiply(double value) {
  result_ *= value;
}

void Calculator::Reset() {
  result_ = 0.0;
}

}  // namespace calculator
```

### Example 2: Using Modern C++ Features

```cpp
// data_processor - Batch data processing
// Copyright (c) 2025

#pragma once

#include <memory>
#include <vector>

#include "calculator/calculator.h"

namespace myapp {

/// @brief Processes large datasets with configurable filters.
class DataProcessor {
 public:
  explicit DataProcessor(const std::string& config_file);
  ~DataProcessor();

  DataProcessor(const DataProcessor&) = delete;
  DataProcessor& operator=(const DataProcessor&) = delete;

  /// @brief Processes input data vector.
  /// @param data Input data to process.
  /// @return Processed results.
  std::vector<double> Process(const std::vector<int>& data);

 private:
  std::unique_ptr<calculator::Calculator> calculator_;
  std::vector<int> filter_values_;

  void LoadConfiguration(const std::string& config_file);
  bool ValidateInput(const std::vector<int>& data) const;
};

}  // namespace myapp
```

```cpp
#include "myapp/data_processor.h"

#include <algorithm>
#include <fstream>
#include <sstream>

namespace myapp {

DataProcessor::DataProcessor(const std::string& config_file)
    : calculator_(std::make_unique<calculator::Calculator>()) {
  LoadConfiguration(config_file);
}

DataProcessor::~DataProcessor() = default;

std::vector<double> DataProcessor::Process(const std::vector<int>& data) {
  if (!ValidateInput(data)) {
    return {};
  }

  std::vector<double> results;

  // Modern: range-based for loop
  for (int value : data) {
    calculator_->Add(value);
    results.push_back(calculator_->GetResult());
  }

  return results;
}

void DataProcessor::LoadConfiguration(const std::string& config_file) {
  std::ifstream file(config_file);
  // Configuration loading logic
}

bool DataProcessor::ValidateInput(const std::vector<int>& data) const {
  // Use algorithm with range-based approach
  return std::any_of(data.begin(), data.end(),
                     [](int val) { return val > 0; });
}

}  // namespace myapp
```

---

## 7. Exception Cases

### Qt Framework Conventions

Qt uses different conventions; these are acceptable:

```cpp
// Qt-specific: slots/signals in lowercase
class MainWindow : public QMainWindow {
  Q_OBJECT

 public slots:
  void on_pushButton_clicked();

 private slots:
  void HandleDataReceived(const QString& data);

 signals:
  void dataProcessed(const QString& result);
};
```

### Windows API Integration

When wrapping Windows API, use project conventions (not Windows naming):

```cpp
// ✅ CORRECT (wrap in project conventions)
namespace win32 {

/// @brief Wrapper for Windows file operations.
class WindowsFile {
 public:
  explicit WindowsFile(const std::string& path);
  bool Open();              // Not OpenFile (API name)
  bool Read(std::string& buffer);

 private:
  HANDLE file_handle_;      // Member variable naming
};

}  // namespace win32

// ❌ INCORRECT (expose raw API naming)
class WindowsFile {
 public:
  HANDLE hFile;  // Raw Windows naming
  BOOL OpenFile();  // Raw Windows naming
};
```

---

## 8. Automated Enforcement

### clang-format Configuration

The `.clang-format` file in the project root enforces these standards:

```bash
# Automatically format code (before commits)
clang-format -i src/myclass.cpp

# Check if code matches standards (dry-run)
clang-format --dry-run --Werror src/myclass.cpp
```

### clang-tidy Integration

Run static analysis to catch common issues:

```bash
cmake -B build -DCMAKE_CXX_CLANG_TIDY="clang-tidy"
cmake --build build
```

### CMake Configuration

Templates generated by `init_project.py` automatically include:
- Correct indentation settings
- File header comments
- Function documentation
- Modern C++ standards

---

## 9. Quick Reference Checklist

Before committing C++ code, verify:

### Naming
- [ ] Type names: `UpperCamelCase`
- [ ] Function names: `UpperCamelCase()`
- [ ] Variable names: `lower_with_underscores`
- [ ] Member variables: `trailing_underscore_`
- [ ] Constants: `kConstantName`
- [ ] Namespaces: `lower_with_underscores`

### File Organization
- [ ] Header guard: `#pragma once`
- [ ] Include order: stdlib → third-party → project
- [ ] One class per file
- [ ] File header comment present

### Formatting
- [ ] Indentation: 4 spaces (no tabs)
- [ ] Line length: ≤ 120 characters
- [ ] Opening brace: same line
- [ ] Pointer/reference: left-aligned

### Documentation
- [ ] File header comment
- [ ] Public API function docs (/// @brief, @param, @return)
- [ ] Comments explain WHY, not WHAT

### Modern C++
- [ ] Smart pointers (no raw new/delete)
- [ ] `auto` used appropriately
- [ ] Range-based for loops
- [ ] `nullptr` not NULL
- [ ] `override` on virtual functions
- [ ] `enum class` not plain enum

---

## 10. References

| Topic | Reference |
|-------|-----------|
| Detailed CMake | `references/cmake.md` |
| Build Tools | `references/codequality.md` |
| Compiler Selection | `references/compilers.md` |
| Automation Protocol | `automation/automation-guide.md` |
| Design Patterns | `references/designpatterns.md` |

---

## 11. Questions & Support

**Q: Can I deviate from these standards?**
A: No. These standards apply to all cpp-dev-skills generated code and Claude-written C++. Consistency is critical.

**Q: What about header-only libraries?**
A: Use same conventions. Place implementation in `.hpp` files with detailed inline documentation.

**Q: Should I format code before or after writing?**
A: Both. Write with standards in mind, then run `clang-format -i` before committing.

**Q: Are there exceptions for legacy code?**
A: New code follows these standards. Existing code can be refactored gradually using clang-tidy.

---

**Last Updated:** 2025-12-19
**Version:** 1.0
**Status:** Active (cpp-dev-skills Phase 1 - Core Documentation)
