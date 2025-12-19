### Header Guards and Organization
```
#ifndef MY_CLASS_H
#define MY_CLASS_H

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

### Singleton Pattern 
```
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
};
```
### Factory Pattern
```
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
### Observer Pattern
```
class Observer {
public:
    virtual void update(int value) = 0;
};

class Subject {
private:
    std::vector<Observer*> observers;

public:
    void attach(Observer* obs) { observers.push_back(obs); }
    void notify(int value) {
        for (auto obs : observers) obs->update(value);
    }
};
```
