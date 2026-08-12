@freestanding(expression)
public macro stringify<T>(_ value: T) = #externalMacro(module: "FixtureMacros", type: "StringifyMacro")

public let globalValue = 1

public prefix func ! (value: Marker) -> Marker {
    value
}

public struct Box<Value> where Value: Sendable {
    public let value: Value

    public func map<Output>(_ transform: (Value) -> Output) -> Output {
        transform(self.value)
    }

    struct Nested {}
}

public extension Box {
    var description: String { String(describing: self.value) }
}

public typealias Marker = Box<Int>
