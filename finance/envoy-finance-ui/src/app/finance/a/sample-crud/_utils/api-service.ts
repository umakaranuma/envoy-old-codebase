import { form } from '@/constans/Form';
import { responseHandling } from '@/helpers/handlers/responseHandler';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllSample(params: params, abortDuplicate: boolean) {
  // Construct query string from parameters
  const queryString = new URLSearchParams(params).toString();

  // Send HTTP request to fetch all sample
  return responseHandling(
    await sendRequest({
      url: `${process.env.ELDERPA_PROXY_PREFIX}/api/sample?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

// Function to fetch a single sample by its ID
export async function getOneSample(id: string) {
  // Send HTTP request to fetch a single sample
  return responseHandling(
    await sendRequest({
      url: `${process.env.ELDERPA_PROXY_PREFIX}/api/samples/${id}`,
      method: 'GET',
    }),
  );
}

// Function to create a new sample
export async function createSample(formData: any) {
  // Clear any previous errors associated with the sample store form
  clearError(form.sample_crud.store);

  // Send an HTTP POST request to the server to create a new sample
  const response = await sendRequest({
    url: `${process.env.ELDERPA_PROXY_PREFIX}/api/samples`,
    method: 'POST',
    data: formData,
  });

  // Process the response data and handle any errors specific to the sample store form
  return responseHandling(response);
}

// Function to update an existing sample
export async function updateSample(id: string, formData: any) {
  // Clear any previous errors associated with the sample update form
  clearError(form.sample_crud.update);

  // Send an HTTP PUT request to the server to update the sample with the provided ID
  const response = await sendRequest({
    url: `${process.env.ELDERPA_PROXY_PREFIX}/api/samples/${id}`,
    method: 'PUT',
    data: formData,
  });

  // Process the response data and handle any errors specific to the sample update form
  return responseHandling(response);
}

// Function to delete an existing sample
export async function deleteSample(id: string) {
  // Send an HTTP DELETE request to the server to delete the sample with the provided ID
  const response = await sendRequest({
    url: `${process.env.ELDERPA_PROXY_PREFIX}/api/samples/${id}`,
    method: 'DELETE',
  });

  // Process the response data and handle any errors
  return responseHandling(response);
}
