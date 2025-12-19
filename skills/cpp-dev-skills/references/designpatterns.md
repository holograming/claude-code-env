# C++ Design Patterns

## Header Guards

```cpp
// example - Header guard demonstration
// Copyright (c) 2025

#pragma once

#include <iostream>
#include <vector>

class MyClass {
 public:
  MyClass();
  ~MyClass();
  void DoSomething();

 private:
  int value_;
};
```

## Singleton Pattern

```cpp
// singleton - Thread-safe singleton implementation
// Copyright (c) 2025

class Singleton {
 public:
  static Singleton& GetInstance() {
    static Singleton instance;
    return instance;
  }

  Singleton(const Singleton&) = delete;
  Singleton& operator=(const Singleton&) = delete;

 private:
  Singleton() = default;
};
```

## Factory Pattern

```cpp
// factory - Shape factory pattern implementation
// Copyright (c) 2025

enum class ShapeType { kCircle, kSquare, kTriangle };

class ShapeFactory {
 public:
  static std::unique_ptr<Shape> CreateShape(ShapeType type) {
    switch (type) {
      case ShapeType::kCircle:
        return std::make_unique<Circle>();
      case ShapeType::kSquare:
        return std::make_unique<Square>();
      default:
        return nullptr;
    }
  }
};
```

## Observer Pattern

```cpp
// observer - Observer pattern implementation
// Copyright (c) 2025

class Observer {
 public:
  virtual ~Observer() = default;
  virtual void Update(int value) = 0;
};

class Subject {
 public:
  void Attach(Observer* obs) { observers_.push_back(obs); }

  void Detach(Observer* obs) {
    observers_.erase(
        std::remove(observers_.begin(), observers_.end(), obs),
        observers_.end());
  }

  void Notify(int value) {
    for (auto obs : observers_) {
      obs->Update(value);
    }
  }

 private:
  std::vector<Observer*> observers_;
};
```

## RAII Pattern

```cpp
// raii - RAII (Resource Acquisition Is Initialization) pattern
// Copyright (c) 2025

class FileHandler {
 public:
  FileHandler(const char* filename, const char* mode)
      : file_(std::fopen(filename, mode)) {
    if (!file_) {
      throw std::runtime_error("Failed to open file");
    }
  }

  ~FileHandler() {
    if (file_) {
      std::fclose(file_);
    }
  }

  FileHandler(const FileHandler&) = delete;
  FileHandler& operator=(const FileHandler&) = delete;

  FileHandler(FileHandler&& other) noexcept : file_(other.file_) {
    other.file_ = nullptr;
  }

 private:
  std::FILE* file_;
};
```
