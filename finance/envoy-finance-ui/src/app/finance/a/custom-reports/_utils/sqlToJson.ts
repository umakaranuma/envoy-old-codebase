import { Field, Filter, SqlToJsonResult } from './model';

// Allowed filter types
const ALLOWED_FILTER_TYPES = [
  'number',
  'text',
  'password',
  'email',
  'checkbox',
  'radio',
  'color',
  'file',
  'date',
  'datetime-local',
  'range',
  'textarea',
  'datalist',
  'tel',
  'week',
  'month',
  'time',
  'search',
  'submit',
  'reset',
  'url',
];

function extractBaseColumn(expr: string): string {
  // Remove function calls, table prefixes, and extract the base column name
  // Examples:
  //   e.id -> id
  //   TIME_FORMAT(ar.date_from, '%H:%i') -> date_from
  //   ROUND(ar.hours, 2) -> hours
  //   p.display_name -> display_name
  //   SUM(e.salary) -> salary
  //   ar.remarks -> remarks
  //   id -> id
  //   'constant' -> constant
  // Try to extract the innermost identifier
  let match = expr.match(/([a-zA-Z0-9_]+)\s*\(/); // function call
  if (match) {
    // Extract argument inside function
    const args = expr.substring(expr.indexOf('(') + 1, expr.lastIndexOf(')'));
    // If multiple args, take the first identifier
    const argMatch = args.match(/([a-zA-Z0-9_]+)(\.[a-zA-Z0-9_]+)?/);
    if (argMatch) {
      if (argMatch[2]) return argMatch[2].slice(1); // .column
      return argMatch[1];
    }
  }
  // Table prefix
  match = expr.match(/([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)/);
  if (match) return match[2];
  // Just identifier
  match = expr.match(/([a-zA-Z0-9_]+)/);
  if (match) return match[1];
  return expr;
}

function inferFieldDataType(fieldName: string): string {
  const name = fieldName.toLowerCase();
  // Numeric IDs and references
  if (
    (/id$/i.test(name) && name !== 'email') ||
    name.endsWith('_id') ||
    name.endsWith('id') ||
    name.includes('reference') ||
    name.includes('ref') ||
    name.includes('number') ||
    name.includes('count') ||
    name.includes('score') ||
    name.includes('quantity') ||
    name.includes('amount') ||
    name.includes('salary') ||
    name.includes('total') ||
    name.includes('price') ||
    name.includes('age') ||
    name.includes('year') ||
    name.includes('month') ||
    name.includes('day')
  )
    return 'number';
  // Dates and times
  if (
    name.includes('date') ||
    name.includes('dob') ||
    name.includes('time') ||
    name.endsWith('at') ||
    name.endsWith('_at') ||
    name.endsWith('_on') ||
    name.includes('created') ||
    name.includes('updated') ||
    name.includes('expiry') ||
    name.includes('timestamp') ||
    name.includes('joined') ||
    name.match(/_at$/) ||
    name.match(/at$/) ||
    name.match(/^(s|e)_date$/) ||
    name.match(/start_date|end_date/)
  )
    return 'date';
  // Booleans
  if (
    name.startsWith('is_') ||
    name.startsWith('has_') ||
    name.startsWith('can_') ||
    name.startsWith('should_') ||
    name.startsWith('was_') ||
    name.startsWith('were_') ||
    name.startsWith('does_') ||
    name.startsWith('did_') ||
    name.startsWith('will_') ||
    name.startsWith('had_')
  )
    return 'boolean';
  // Email
  if (name.includes('email')) return 'email';
  // Phone
  if (name.includes('phone') || name.includes('mobile')) return 'text';
  // Address
  if (name.includes('address') || name.includes('city') || name.includes('state') || name.includes('country') || name.includes('zipcode') || name.includes('postal')) return 'text';
  // File/media
  if (name.includes('file') || name.includes('image') || name.includes('avatar') || name.includes('document') || name.includes('attachment') || name.includes('picture')) return 'file';
  // URL/link
  if (name.includes('url') || name.includes('link')) return 'text';
  // Password/token
  if (name.includes('password') || name.includes('token')) return 'text';
  // Default
  return 'text';
}

export function sqlToJson(sql: string): SqlToJsonResult {
  const normalizedSql = sql.replace(/\s+/g, ' ').trim();

  if (!normalizedSql) {
    return { filters: [], fields: [] };
  }

  if (!normalizedSql.match(/^select\s/i)) {
    throw new Error('SQL query must start with SELECT');
  }

  // Map $variable to column name in WHERE clause
  const whereMatch = normalizedSql.match(/where\s+([^;]*)/i);
  const varToColumn: Record<string, string> = {};
  // Track variables used in BETWEEN for special handling
  const betweenVariables: Set<string> = new Set();
  // Store range filters to add later
  const rangeFilters: Filter[] = [];
  if (whereMatch) {
    const whereClause = whereMatch[1];
    // Detect BETWEEN $start AND $end patterns
    const betweenRegex = /([a-zA-Z0-9_.]+)\s+BETWEEN\s+\$([a-zA-Z0-9_]+)\s+AND\s+\$([a-zA-Z0-9_]+)/gi;
    let bm: RegExpExecArray | null;
    while ((bm = betweenRegex.exec(whereClause)) !== null) {
      // bm[1] is column, bm[2] is start variable, bm[3] is end variable
      const col = bm[1].includes('.') ? bm[1].split('.').pop()! : bm[1];
      betweenVariables.add(bm[2]);
      betweenVariables.add(bm[3]);
      // Determine range type based on column name
      let rangeType = 'range';
      const colLower = col.toLowerCase();
      if (colLower.includes('datetime')) {
        rangeType = 'datetimeRange';
      } else if (colLower.includes('date')) {
        rangeType = 'dateRange';
      } else if (colLower.includes('time')) {
        rangeType = 'timeRange';
      }
      // Add a single range filter for this column
      const title = col
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase())
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/^([a-zA-Z])/, (c) => c.toUpperCase());
      rangeFilters.push({
        code: col,
        type: rangeType,
        default: 'today',
        title: title.trim(),
      });
    }
    // Match patterns like: u.is_active = $checkbox
    const varColRegex = /([a-zA-Z0-9_.]+)\s*[=><!]+\s*\$([a-zA-Z0-9_]+)/g;
    let m: RegExpExecArray | null;
    while ((m = varColRegex.exec(whereClause)) !== null) {
      // m[1] is column, m[2] is variable
      // Remove table prefix if present
      const col = m[1].includes('.') ? m[1].split('.').pop()! : m[1];
      varToColumn[m[2]] = col;
    }
    // Also handle LIKE and other operators
    const varColLikeRegex = /([a-zA-Z0-9_.]+)\s+LIKE\s+'%?\$([a-zA-Z0-9_]+)%?'/gi;
    while ((m = varColLikeRegex.exec(whereClause)) !== null) {
      const col = m[1].includes('.') ? m[1].split('.').pop()! : m[1];
      varToColumn[m[2]] = col;
    }
  }

  const varFilters: Filter[] = Array.from(new Set([...normalizedSql.matchAll(/\$([a-zA-Z0-9_]+)/g)].map((m) => m[1])))
    .filter((variable) => !betweenVariables.has(variable)) // Exclude variables used in BETWEEN
    .map((variable) => {
      const code = varToColumn[variable] || variable;
      const titleSource = code;
      const title = titleSource
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase())
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/^([a-zA-Z])/, (c) => c.toUpperCase());
      // Only use variable as type if in ALLOWED_FILTER_TYPES, else default to 'text'
      const type = ALLOWED_FILTER_TYPES.includes(variable) ? variable : 'text';
      // Default for date
      const isDate = type === 'date';
      return {
        code,
        type,
        default: isDate ? 'today' : '',
        title: title.trim(),
      };
    });

  const literalFilters: Filter[] = (() => {
    const whereMatch = normalizedSql.match(/where\s+([^;]*)/i);
    if (!whereMatch) return [];

    const whereClause = whereMatch[1];
    const filters: Filter[] = [];

    const equalRegex = /(\w+)\s*=\s*'((?:[^']|'')*)'/g;
    let m: RegExpExecArray | null;
    while ((m = equalRegex.exec(whereClause)) !== null) {
      const value = m[2].replace(/''/g, "'");
      const isDate = m[1].toLowerCase().includes('date') || m[1].toLowerCase().startsWith('fdate') || m[1].toLowerCase().endsWith('date');
      const title = m[1]
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase())
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/^([a-zA-Z])/, (c) => c.toUpperCase());
      const type = isDate ? 'date' : inferFieldDataType(m[1]);
      filters.push({
        code: m[1],
        type,
        default: isDate ? 'today' : value,
        title: title.trim(),
      });
    }

    const likeRegex = /(\w+)\s+LIKE\s+'%([^%]+)%'/gi;
    while ((m = likeRegex.exec(whereClause)) !== null) {
      const title = m[1]
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase())
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/^([a-zA-Z])/, (c) => c.toUpperCase());
      const type = inferFieldDataType('text');
      filters.push({
        code: m[1],
        type,
        default: m[2],
        title: title.trim(),
      });
    }

    const unique = new Map<string, Filter>();
    for (const f of filters) {
      if (!unique.has(f.code)) unique.set(f.code, f);
    }
    return Array.from(unique.values());
  })();

  const filterMap = new Map<string, Filter>();
  // Add range filters first (so they take precedence if code overlaps)
  for (const f of [...rangeFilters, ...varFilters, ...literalFilters]) {
    if (!filterMap.has(f.code)) filterMap.set(f.code, f);
  }
  const filters = Array.from(filterMap.values());

  const selectMatch = normalizedSql.match(/select\s+(.+?)\s+from\s+/i);
  let fields: Field[] = [];
  if (selectMatch) {
    const selectFields = selectMatch[1].trim();
    if (selectFields !== '*') {
      const fieldTokens = selectFields.split(/,\s*(?![^()]*\))/);
      fields = fieldTokens
        .map((f) => f.trim())
        .filter((f) => f.length > 0)
        .map((code) => {
          const aliasMatch = code.match(/(.+?)\s+AS\s+(\w+)/i);
          const fieldExpr = aliasMatch ? aliasMatch[1].trim() : code;
          const label = aliasMatch ? aliasMatch[2] : code.includes('.') ? code.split('.').pop()! : code;

          // Extract base column name for code
          const baseCode = extractBaseColumn(fieldExpr);

          // Use comprehensive field data type inference
          const dataType = inferFieldDataType(baseCode);

          return {
            code: baseCode,
            label: label.charAt(0).toLowerCase() + label.slice(1),
            dataType,
          };
        });
    }
  }

  return { filters, fields };
}
