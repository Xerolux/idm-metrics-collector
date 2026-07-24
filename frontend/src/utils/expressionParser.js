// Xerolux 2026
/**
 * Expression Parser for mathematical operations on query results.
 *
 * Supports operations like:
 * - A/B (divide query A by query B)
 * - A*100 (multiply query A by 100)
 * - (A+B)/2 (average of A and B)
 * - avg(A,B,C) (average of multiple queries)
 * - sum(A,B) (sum of A and B)
 * - min(A,B) (minimum of A and B)
 * - max(A,B) (maximum of A and B)
 */

/**
 * Validate an expression for syntax errors.
 *
 * @param {string} expression - The expression to validate
 * @returns {Object} - { valid: boolean, error: string }
 */
export function validateExpression(expression) {
  if (!expression || !expression.trim()) {
    return { valid: false, error: 'Expression is empty' }
  }

  // Check for balanced parentheses
  const parenCount = (expression.match(/\(/g) || []).length - (expression.match(/\)/g) || []).length
  if (parenCount !== 0) {
    const extra = parenCount > 0 ? '(' : ')'
    return {
      valid: false,
      error: `Unbalanced parentheses: ${Math.abs(parenCount)} extra ${extra}`
    }
  }

  // Check for invalid characters (only allow alphanumeric, operators, parentheses, commas, dots, spaces)
  if (!/^[\w\s+\-*/().,]+$/.test(expression)) {
    return { valid: false, error: 'Expression contains invalid characters' }
  }

  // Check for consecutive operators
  if (/[^\w\s][^\w\s]/.test(expression.replace(/\s/g, ''))) {
    return { valid: false, error: 'Invalid operator sequence' }
  }

  return { valid: true, error: '' }
}

/**
 * Parse an expression and extract query references.
 *
 * @param {string} expression - The expression to parse
 * @returns {Array<string>} - List of query labels referenced in the expression
 */
export function parseExpression(expression) {
  // Extract all standalone uppercase letters (A, B, C, etc.)
  const matches = expression.match(/\b([A-Z])\b/g) || []
  return [...new Set(matches)]
}

// Cache for compiled expression functions (keyed by expression string)
const _compiledCache = new Map()
const _MAX_CACHE = 200

/**
 * Compile an expression into a reusable function.
 * Translates avg/sum/min/max macros, then builds a Function with named parameters.
 *
 * @param {string} expression - The expression to compile
 * @param {Array<string>} queryLabels - Variable names extracted from the expression
 * @returns {Function} - Function that takes (...values) and returns the result
 */
function compileExpression(expression, queryLabels) {
  if (_compiledCache.has(expression)) {
    return _compiledCache.get(expression)
  }

  let expr = expression
  expr = expr.replace(/avg\s*\(([^)]+)\)/g, (_match, args) => {
    const argList = args.split(',').map((a) => a.trim())
    return `(${argList.join('+')})/${argList.length}`
  })
  expr = expr.replace(/sum\s*\(([^)]+)\)/g, (_match, args) => {
    const argList = args.split(',').map((a) => a.trim())
    return `(${argList.join('+')})`
  })
  expr = expr.replace(/min\s*\(/g, 'Math.min(')
  expr = expr.replace(/max\s*\(/g, 'Math.max(')

  const func = new Function(...queryLabels, 'return ' + expr)

  if (_compiledCache.size >= _MAX_CACHE) {
    const firstKey = _compiledCache.keys().next().value
    _compiledCache.delete(firstKey)
  }
  _compiledCache.set(expression, func)
  return func
}

/**
 * Evaluate an expression at a specific timestamp.
 *
 * @param {string} expression - The expression to evaluate
 * @param {number} timestamp - The timestamp to evaluate at
 * @param {Object} queryData - Dictionary mapping query labels to their data
 *                            Format: { 'A': [(timestamp1, value1), (timestamp2, value2), ...] }
 * @returns {number|null} - The calculated value or null if any query has no value at this timestamp
 */
export function evaluateExpression(expression, timestamp, queryData) {
  const queryLabels = parseExpression(expression)

  const args = []
  for (const label of queryLabels) {
    if (!queryData[label]) return null
    const value = queryData[label].find(([ts]) => ts === timestamp)?.[1]
    if (value === undefined) return null
    args.push(value)
  }

  try {
    const func = compileExpression(expression, queryLabels)
    return parseFloat(func(...args))
  } catch (error) {
    console.error(`Error evaluating expression '${expression}':`, error)
    return null
  }
}

/**
 * Evaluate an expression over all timestamps.
 * Uses O(1) Map lookups and pre-compiled functions for performance.
 *
 * @param {string} expression - The expression to evaluate
 * @param {Object} queryData - Dictionary mapping query labels to their data
 * @returns {Array} - List of [timestamp, value] pairs
 */
export function evaluateExpressionSeries(expression, queryData) {
  const queryLabels = parseExpression(expression)

  const allTimestamps = new Set()
  const lookups = {}

  for (const [label, data] of Object.entries(queryData)) {
    if (queryLabels.includes(label)) {
      const map = new Map()
      for (const [ts, val] of data) {
        allTimestamps.add(ts)
        map.set(ts, val)
      }
      lookups[label] = map
    } else {
      for (const [ts] of data) {
        allTimestamps.add(ts)
      }
    }
  }

  let func
  try {
    func = compileExpression(expression, queryLabels)
  } catch (error) {
    console.error(`Failed to compile expression '${expression}':`, error)
    return []
  }

  const results = []
  const sorted = Array.from(allTimestamps).sort((a, b) => a - b)

  for (const ts of sorted) {
    const args = []
    let complete = true
    for (const label of queryLabels) {
      const val = lookups[label]?.get(ts)
      if (val === undefined) {
        complete = false
        break
      }
      args.push(val)
    }
    if (!complete) continue

    try {
      const result = func(...args)
      if (result !== null && result !== undefined && !Number.isNaN(result)) {
        results.push([ts, parseFloat(result)])
      }
    } catch {
      // skip evaluation errors for individual timestamps
    }
  }

  return results
}

/**
 * Get expression examples.
 *
 * @returns {Array<Object>} - List of example expressions with descriptions
 */
export function getExpressionExamples() {
  return [
    { expression: 'A/B', description: 'Divide A by B' },
    { expression: 'A*100', description: 'Multiply A by 100' },
    { expression: '(A+B)/2', description: 'Average of A and B' },
    { expression: 'avg(A,B,C)', description: 'Average of A, B, and C' },
    { expression: '(A-B)*100/B', description: 'Percentage difference' },
    { expression: 'sum(A,B,C)', description: 'Sum of A, B, and C' },
    { expression: 'min(A,B)', description: 'Minimum of A and B' },
    { expression: 'max(A,B)', description: 'Maximum of A and B' },
    { expression: '(A+B+C)/3', description: 'Average using operators' },
    { expression: 'A*0.5+B*0.5', description: 'Weighted average (50% A, 50% B)' }
  ]
}

/**
 * Get expression help text.
 *
 * @returns {string} - Help text for expressions
 */
export function getExpressionHelp() {
  return `
Mathematical Expressions Help:

Operators:
  +    Addition (A + B)
  -    Subtraction (A - B)
  *    Multiplication (A * 100)
  /    Division (A / B)
  ()   Grouping ((A + B) / 2)

Functions:
  avg(A,B,C)  Average of multiple queries
  sum(A,B)    Sum of multiple queries
  min(A,B)    Minimum of multiple queries
  max(A,B)    Maximum of multiple queries

Examples:
  A/B                    Divide A by B
  A*100                  Multiply A by 100
  (A+B)/2                Average of A and B
  avg(A,B,C)             Average of A, B, and C
  (A-B)*100/B            Percentage difference
  sum(A,B,C)             Sum of A, B, and C

Note:
  - Query labels are uppercase letters: A, B, C, etc.
  - Division by zero returns null
  - Invalid expressions return null
  - Use parentheses to control operation order
`
}
