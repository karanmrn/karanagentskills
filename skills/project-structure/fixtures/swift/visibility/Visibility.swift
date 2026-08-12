import Foundation
@testable import FixtureKit
public import FixtureUI

public struct Widget {
    public func render() -> String { "w" }
    func layout() {}
    private var cache: Int = 0
    unowned(unsafe) var owner: AnyObject?
}

func internalHelper() {}

private let secretToken = "x"

let internalValue = 2

open class Base {
    open func overrideMe() {}
}

public protocol Renderer {
    func draw()
}

// One-line attributed declaration: the symbol is attributedOneLiner, never `token` from the body.
@MainActor func attributedOneLiner() -> Int { let token = 1; return token }

distributed actor Worker {
    distributed func ping() {}
}

public private(set) var counter = 0

let first = 1, second = 2

let point: (x: Int, y: Int) = (0, 0)

let escaped = """
embedded \"""quote\""" and \(first)
"""

let pattern = #/\{[a-z]+\}/#

let (left, right) = (1, 2)

let _ = internalValue

let interpolated = "prefix \(String(describing: "{")) suffix"

let rawEscaped = #"quote-pound \#"# still raw"#

let rawInterp = #"x \#("#" + "{") y"#

let tricky = "\(wrap("("))"

let generics: Dictionary<String, (Int, Bool)> = [:]

let (x: boundX, y: boundY) = (x: 1, y: 2)

let triple: Triple<Int, (String, Bool), Double> = makeTriple()

@_documentation(visibility: internal) public struct DocumentedAPI {}

#if canImport(AppKit)
final class PlatformView: NSViewType {
#else
final class PlatformView: UIViewType {
#endif
    func refresh() {}
}

extension Dictionary<String, Int> {
    var footprint: Int { count }
}

struct AfterAll {}
