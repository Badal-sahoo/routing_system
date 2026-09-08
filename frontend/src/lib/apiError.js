export function getErrorMessage(error, fallback = "Something went wrong.") {
  const data = error?.response?.data;

  if (typeof data === "string" && data) return data;
  if (data?.detail) return data.detail;

  if (data && typeof data === "object") {
    const entries = Object.entries(data);
    if (entries.length > 0) {
      const [field, messages] = entries[0];
      const message = Array.isArray(messages) ? messages[0] : messages;
      return `${field}: ${message}`;
    }
  }

  return error?.message || fallback;
}
