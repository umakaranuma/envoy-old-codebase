import { IValidationErrors } from '@/interface/ICommon';

/**
 * Displays validation error messages on the form.
 *
 * @param {IValidationErrors} errors - The validation errors to display.
 * @param {string} formId - The ID of the form on which to display errors.
 */
export function printError(errors: IValidationErrors, formId: string, t: any) {
  // Iterate over each error key-value pair
  Object.entries(errors).forEach(([key, value]) => {
    // Select all elements with the specific error class within the form
    const elements = document.querySelectorAll(`#${formId} .error-${key}`);

    // Convert the NodeList to an array and iterate over each element
    Array.from(elements).forEach((element) => {
      // Add the 'is-invalid' class to the element to indicate an error
      element.classList.add('is-invalid');

      // Iterate over each error message for the current key
      value.forEach((error: any) => {
        const { error_type, tokens } = error;

        const updatedTokens: any = {};

        Object.entries(tokens).forEach(([tKey, kValue]: [string, any]) => {
          if (tKey.startsWith('_')) {
            tKey = tKey.substring(1);
            updatedTokens[tKey] = t(kValue);
          } else {
            updatedTokens[tKey] = kValue;
          }
        });

        // Create a new span element to display the error message
        const errorElement = document.createElement('span');
        errorElement.classList.add('error', 'invalid-feedback', 'mb-2');
        errorElement.setAttribute('role', 'alert');
        errorElement.style.display = 'block';
        errorElement.innerHTML = `<strong>${t(error_type, updatedTokens)}</strong>`;

        // Insert the error message element after the current element
        element.parentNode?.insertBefore(errorElement, element.nextSibling);
      });
    });
  });
}

/**
 * Clears all validation errors from the form.
 *
 * @param {string} formId - The ID of the form from which to clear errors.
 */
export function clearError(formId: string, key?: string) {
  if (key) {
    // Only clear errors for the specific key
    const formControls = document.querySelectorAll(`#${formId} .error-${key}`);
    formControls.forEach((control) => control.classList.remove('is-invalid'));

    const errorElements = document.querySelectorAll(`#${formId} .error-${key} ~ .error`);
    errorElements.forEach((errorElement) => errorElement.remove());
  } else {
    // Clear all errors as before
    const formControls = document.querySelectorAll(`#${formId} .form-control, #${formId} .form-control-fack`);
    formControls.forEach((control) => control.classList.remove('is-invalid'));

    const errorElements = document.querySelectorAll(`#${formId} .error`);
    errorElements.forEach((errorElement) => errorElement.remove());
  }
}
