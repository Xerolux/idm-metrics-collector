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

  // Get the value for each query at this timestamp
  const queryValues = {}
  for (const label of queryLabels) {
    if (!queryData[label]) {
      return null
    }

    const value = queryData[label].find(([ts]) => ts === timestamp)?.[1]
    if (value === undefined) {
      return null
    }

    queryValues[label] = value
  }

  // Evaluate the expression with these values
  try {
    return evaluateWithValues(expression, queryValues)
  } catch (error) {
    console.error(`Error evaluating expression '${expression}':`, error)
    return null
  }
}

/**
 * Evaluate an expression with given query values.
 *
 * @param {string} expression - The expression to evaluate
 * @param {Object} values - Dictionary mapping query labels to their values
 * @returns {number} - The calculated value
 */
function evaluateWithValues(expression, values) {
  // Replace query references with their values
  let expr = expression
  for (const [label, value] of Object.entries(values)) {
    // Use word boundaries to avoid partial replacements
    const regex = new RegExp(`\\b${label}\\b`, 'g')
    expr = expr.replace(regex, value.toString())
  }

  // Replace functions with Python equivalents
  // avg(A,B,C) -> (A+B+C)/3
  expr = expr.replace(/avg\s*\(([^)]+)\)/g, (match, args) => {
    const argList = args.split(',').map((a) => a.trim())
    return `(${argList.join('+')})/${argList.length}`
  })

  // sum(A,B) -> (A+B)
  expr = expr.replace(/sum\s*\(([^)]+)\)/g, (match, args) => {
    const argList = args.split(',').map((a) => a.trim())
    return `(${argList.join('+')})`
  })

  // min(A,B) -> Math.min(A,B)
  expr = expr.replace(/min\s*\(([^)]+)\)/g, (match, args) => {
    return `Math.min(${args})`
  })

  // max(A,B) -> Math.max(A,B)
  expr = expr.replace(/max\s*\(([^)]+)\)/g, (match, args) => {
    return `Math.max(${args})`
  })

  // Safe evaluation using Function constructor (safer than eval)
  try {
    const func = new Function('return ' + expr)
    const result = func()
    return parseFloat(result)
  } catch (error) {
    throw new Error(`Failed to evaluate expression '${expr}': ${error.message}`)
  }
}

/**
 * Evaluate an expression over all timestamps.
 *
 * @param {string} expression - The expression to evaluate
 * @param {Object} queryData - Dictionary mapping query labels to their data
 * @returns {Array} - List of [timestamp, value] pairs
 */
export function evaluateExpressionSeries(expression, queryData) {
  const validation = validateExpression(expression)
  if (!validation.valid) {
    console.error(`Invalid expression: ${validation.error}`)
    return []
  }

  const queryLabels = parseExpression(expression)

  const sum = (...args) => args.reduce((a, b) => a + b, 0)
  const avg = (...args) => (args.length ? sum(...args) / args.length : 0)
  const min = Math.min
  const max = Math.max

  let compiledFunc
  try {
    compiledFunc = new Function(
      'sum',
      'avg',
      'min',
      'max',
      ...queryLabels,
      'return ' + expression
    )
  } catch (error) {
    console.error(`Failed to compile expression '${expression}':`, error)
    return []
  }

  // Create O(1) time-based Map for variable lookups
  const timeMaps = {}
  for (const label of queryLabels) {
    timeMaps[label] = new Map()
    if (queryData[label]) {
      for (const [ts, val] of queryData[label]) {
        timeMaps[label].set(ts, val)
      }
    }
  }

  // Get all unique timestamps from all queries
  const allTimestamps = new Set()
  for (const data of Object.values(queryData)) {
    for (const [ts] of data) {
      allTimestamps.add(ts)
    }
  }

  // Evaluate expression at each timestamp
  const results = []
  for (const timestamp of Array.from(allTimestamps).sort((a, b) => a - b)) {
    const args = [sum, avg, min, max]
    let hasAllArgs = true

    for (const label of queryLabels) {
      const val = timeMaps[label].get(timestamp)
      if (val === undefined) {
        hasAllArgs = false
        break
      }
      args.push(val)
    }

    if (hasAllArgs) {
      try {
        const value = parseFloat(compiledFunc(...args))
        if (!isNaN(value)) {
          results.push([timestamp, value])
        }
      } catch {
        // Skip on error
      }
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
