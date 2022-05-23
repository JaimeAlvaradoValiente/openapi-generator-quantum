//
// Return.swift
//
// Generated by openapi-generator
// https://openapi-generator.tech
//

import Foundation
#if canImport(AnyCodable)
import AnyCodable
#endif
import Vapor

/** Model for testing reserved words */
public final class Return: Content, Hashable {

    public var `return`: Int?

    public init(`return`: Int? = nil) {
        self.`return` = `return`
    }

    public enum CodingKeys: String, CodingKey, CaseIterable {
        case `return` = "return"
    }

    // Encodable protocol methods

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encodeIfPresent(`return`, forKey: .`return`)
    }

    public static func == (lhs: Return, rhs: Return) -> Bool {
        lhs.`return` == rhs.`return`
        
    }

    public func hash(into hasher: inout Hasher) {
        hasher.combine(`return`?.hashValue)
        
    }
}

