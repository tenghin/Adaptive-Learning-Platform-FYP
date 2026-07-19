export function unwrapData(response) {
  if (response?.data?.success === false) {
    throw new Error(response.data.message || 'Request failed');
  }

  return response?.data?.data || {};
}

export function getErrorMessage(error) {
  return (
    error?.response?.data?.message ||
    error?.message ||
    'Something went wrong'
  );
}
