import { printError } from './validationErrorHandler';

/**
 * Handle index-wise validation errors
 * Supports the format: { "0": { field: errors }, "1": { field: errors } }
 */
export function handleIndexWiseValidationErrors(responseData: any, formId: string, t: (key: string) => string): boolean {
  if (!responseData.result || typeof responseData.result !== 'object') {
    return false;
  }

  const transformedErrors: any = {};

  // Check if result has numeric keys (like "0", "1", "2")
  const numericKeys = Object.keys(responseData.result).filter((key) => !isNaN(Number(key)));

  if (numericKeys.length > 0) {
    console.log('Validation errors found with numeric keys:', responseData.result);

    numericKeys.forEach((key) => {
      const index = Number(key);
      const errorData = responseData.result[key];

      // Process each field in the error data
      Object.entries(errorData).forEach(([field, errors]: [string, any]) => {
        const fieldName = `${field}_${index}`;
        transformedErrors[fieldName] = errors;

        // Log for debugging
        console.log(`Row ${index + 1}: ${field} - Validation errors:`, errors);
      });
    });

    // Use printError with transformed errors
    printError(transformedErrors, formId, t);
    return true;
  }

  return false;
}

/**
 * Handle duplicate errors with group mapping
 */
export function handleDuplicateErrorsWithGroups(duplicateErrors: any[], setErrors: (errors: Record<number, string[]>) => void, getGroupedEntries: () => any[]): boolean {
  if (!duplicateErrors || duplicateErrors.length === 0) {
    return false;
  }

  console.log('Duplicate errors found:', duplicateErrors);

  const newGroupErrors: Record<number, string[]> = {};
  const groupedEntries = getGroupedEntries();

  duplicateErrors.forEach((err: any) => {
    let groupIndex = 0;
    let currentIndex = 0;

    for (const group of groupedEntries) {
      if (err.index >= currentIndex && err.index < currentIndex + group.length) {
        if (!newGroupErrors[groupIndex]) {
          newGroupErrors[groupIndex] = [];
        }
        newGroupErrors[groupIndex].push(err.error);
        break;
      }
      currentIndex += group.length;
      groupIndex++;
    }
  });

  setErrors(newGroupErrors);
  return true;
}

/**
 * Complete 417 error handler for index-wise errors
 */
export function handle417IndexWiseErrors(
  responseData: any,
  formId: string,
  t: (key: string) => string,
  setErrors?: (errors: Record<number, string[]>) => void,
  getGroupedEntries?: () => any[],
): boolean {
  if (responseData.status_code !== 417) {
    return false;
  }

  console.log('417 Validation Error:', responseData);

  // Handle duplicate errors first
  if (responseData.result.duplicate_errors && setErrors && getGroupedEntries) {
    if (handleDuplicateErrorsWithGroups(responseData.result.duplicate_errors, setErrors, getGroupedEntries)) {
      return true;
    }
  }

  // Handle validation errors with numeric keys
  if (handleIndexWiseValidationErrors(responseData, formId, t)) {
    return true;
  }

  // Handle validation errors with index (legacy format)
  if (responseData.result.validation_errors && responseData.result.validation_errors.length > 0) {
    console.log('Validation errors found (legacy format):', responseData.result.validation_errors);

    const transformedErrors: any = {};
    responseData.result.validation_errors.forEach((error: any) => {
      const index = error.index;
      const fieldErrors = Object.entries(error).filter(([key]) => key !== 'index');

      fieldErrors.forEach(([field, errors]: [string, any]) => {
        const fieldName = `${field}_${index}`;
        transformedErrors[fieldName] = errors;
      });
    });

    return true;
  }

  return true;
}
