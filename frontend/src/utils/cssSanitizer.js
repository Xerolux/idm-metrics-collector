// Xerolux 2026
/**
 * CSS Sanitizer - Removes potentially dangerous CSS constructs
 *
 * Protects against:
 * - CSS injection attacks
 * - JavaScript execution via CSS (expression(), url(javascript:))
 * - External resource loading (@import, url())
 * - Browser-specific exploits (-moz-binding, behavior)
 */

import DOMPurify from 'dompurify'

// Dangerous patterns that could execute code or load external resources
const DANGEROUS_PATTERNS = [
  // JavaScript in URLs
  /url\s*\(\s*["']?\s*javascript\s*:/gi,
  /url\s*\(\s*["']?\s*data\s*:\s*text\/html/gi,
  /url\s*\(\s*["']?\s*vbscript\s*:/gi,

  // IE expression() - executes JavaScript
  /expression\s*\(/gi,

  // External resource loading
  /@import/gi,

  // IE behavior property - loads HTC files
  /behavior\s*:/gi,

  // Firefox XBL binding
  /-moz-binding\s*:/gi,

  // Webkit mask with external URL (potential data exfiltration)
  /-webkit-mask\s*:\s*url\s*\([^)]*https?:/gi,

  // HTML comments that might break out of style tag
  /<!--/g,
  /-->/g,

  // Unicode escapes that might bypass filters (more comprehensive)
  /\\[0-9a-fA-F]{1,6}/g, // Any unicode escape
  /\\0/g // Null byte escape
]

// Patterns for external URLs (warn but allow with sanitization)
const EXTERNAL_URL_PATTERN = /url\s*\(\s*["']?\s*https?:\/\//gi

/**
 * Sanitize CSS input by removing dangerous patterns
 *
 * @param {string} css - The CSS string to sanitize
 * @param {Object} options - Sanitization options
 * @param {boolean} options.allowExternalUrls - Allow external URLs (default: false)
 * @param {boolean} options.strict - Use strict mode (default: true)
 * @returns {{ sanitized: string, warnings: string[], blocked: string[] }}
 */
export function sanitizeCss(css, options = {}) {
  const { allowExternalUrls = false, strict = true } = options

  if (!css || typeof css !== 'string') {
    return { sanitized: '', warnings: [], blocked: [] }
  }

  let sanitized = css
  const warnings = []
  const blocked = []

  // 1. Sanitize Structure (DOMPurify) to prevent HTML injection/breakouts
  // We wrap in <style> to use DOMPurify's HTML sanitization capabilities
  try {
    const cleanHtml = DOMPurify.sanitize(`<style>${sanitized}</style>`, {
      FORCE_BODY: true,
      ALLOWED_TAGS: ['style'],
      ALLOWED_ATTR: []
    })

    // Extract text content using browser DOM if available
    if (typeof document !== 'undefined') {
      const div = document.createElement('div')
      div.innerHTML = cleanHtml
      // Use textContent to get the pure CSS (decodes entities)
      sanitized = div.textContent || ''
    } else {
      // Fallback for non-browser environments (e.g. tests)
      // Extract content from <style> tags manually if DOM not available
      const match = cleanHtml.match(/<style>([\s\S]*)<\/style>/i)
      sanitized = match ? match[1] : ''
    }
  } catch (e) {
    warnings.push('DOMPurify sanitization failed: ' + e.message)
    // Fallback to original input but warn
  }

  // 2. Content Sanitization (Regex for CSS-specific attacks)
  for (const pattern of DANGEROUS_PATTERNS) {
    const matches = sanitized.match(pattern)
    if (matches) {
      blocked.push(`Blocked: ${matches[0]}`)
      sanitized = sanitized.replace(pattern, '/* BLOCKED */')
    }
  }

  // Handle external URLs
  if (!allowExternalUrls) {
    const externalMatches = sanitized.match(EXTERNAL_URL_PATTERN)
    if (externalMatches) {
      if (strict) {
        blocked.push(`Blocked external URL: ${externalMatches[0]}`)
        sanitized = sanitized.replace(EXTERNAL_URL_PATTERN, 'url(/* BLOCKED */')
      } else {
        warnings.push('CSS contains external URLs which may pose a security risk')
      }
    }
  }

  // Remove any null bytes
  sanitized = sanitized.replace(/\0/g, '')

  // Limit CSS length to prevent DoS
  const MAX_CSS_LENGTH = 50000
  if (sanitized.length > MAX_CSS_LENGTH) {
    warnings.push(`CSS truncated from ${sanitized.length} to ${MAX_CSS_LENGTH} characters`)
    sanitized = sanitized.substring(0, MAX_CSS_LENGTH)
  }

  return { sanitized, warnings, blocked }
}

/**
 * Validate CSS syntax (basic validation)
 *
 * @param {string} css - The CSS string to validate
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateCss(css) {
  const errors = []

  if (!css || typeof css !== 'string') {
    return { valid: true, errors: [] }
  }

  // Check balanced braces
  const openBraces = (css.match(/{/g) || []).length
  const closeBraces = (css.match(/}/g) || []).length

  if (openBraces !== closeBraces) {
    errors.push(`Unbalanced braces: ${openBraces} opening, ${closeBraces} closing`)
  }

  // Check balanced parentheses
  const openParens = (css.match(/\(/g) || []).length
  const closeParens = (css.match(/\)/g) || []).length

  if (openParens !== closeParens) {
    errors.push(`Unbalanced parentheses: ${openParens} opening, ${closeParens} closing`)
  }

  // Check balanced quotes
  const singleQuotes = (css.match(/'/g) || []).length
  const doubleQuotes = (css.match(/"/g) || []).length

  if (singleQuotes % 2 !== 0) {
    errors.push('Unbalanced single quotes')
  }

  if (doubleQuotes % 2 !== 0) {
    errors.push('Unbalanced double quotes')
  }

  return { valid: errors.length === 0, errors }
}

/**
 * Check if CSS contains any potentially dangerous patterns
 *
 * @param {string} css - The CSS string to check
 * @returns {boolean} - True if dangerous patterns found
 */
export function hasDangerousPatterns(css) {
  if (!css) return false

  for (const pattern of DANGEROUS_PATTERNS) {
    if (pattern.test(css)) {
      return true
    }
    // Reset regex lastIndex after test
    pattern.lastIndex = 0
  }

  return false
}

export default {
  sanitizeCss,
  validateCss,
  hasDangerousPatterns
}
