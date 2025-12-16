# C++ Design Patterns

## Header Guards

```cpp
#ifndef MY_CLASS_H
#define MY_CLASS_H

// Or use pragma once (widely supported)
#pragma once

#include <iostream>
#include <vector>

class MyClass {
private:
    int value;

public:
    MyClass();
    ~MyClass();
    void doSomething();
};

#endif
```

## Singleton Pattern

```cpp
class Singleton {
private:
    static Singleton* instance;
    Singleton() {}

public:
    static Singleton* getInstance() {
        if (!instance) {
            instance = new Singleton();
        }
        return instance;
    }
    
    // Delete copy constructor and assignment
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;
};

// Thread-safe C++11 version
class Singleton {
public:
    static Singleton& getInstance() {
        static Singleton instance;
        return instance;
    }
private:
    Singleton() = default;
};
```

## Factory Pattern

```cpp
enum class ShapeType { Circle, Square, Triangle };

class ShapeFactory {
public:
    static std::unique_ptr<Shape> createShape(ShapeType type) {
        switch (type) {
            case ShapeType::Circle:
                return std::make_unique<Circle>();
            case ShapeType::Square:
                return std::make_unique<Square>();
            default:
                return nullptr;
        }
    }
};
```

## Observer Pattern

```cpp
class Observer {
public:
    virtual ~Observer() = default;
    virtual void update(int value) = 0;
};

class Subject {
private:
    std::vector<Observer*> observers;

public:
    void attach(Observer* obs) { observers.push_back(obs); }
    void detach(Observer* obs) {
        observers.erase(
            std::remove(observers.begin(), observers.end(), obs),
            observers.end()
        );
    }
    void notify(int value) {
        for (auto obs : observers) obs->update(value);
    }
};
```

## RAII Pattern

```cpp
class FileHandler {
private:
    std::FILE* file;
public:
    FileHandler(const char* filename, const char* mode)
        : file(std::fopen(filename, mode)) {
        if (!file) throw std::runtime_error("Failed to open file");
    }
    ~FileHandler() {
        if (file) std::fclose(file);
    }
    
    // Disable copy
    FileHandler(const FileHandler&) = delete;
    FileHandler& operator=(const FileHandler&) = delete;
    
    // Enable move
    FileHandler(FileHandler&& other) noexcept : file(other.file) {
        other.file = nullptr;
    }
};
```
