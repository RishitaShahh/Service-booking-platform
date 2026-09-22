/**
 * Utility functions for formatting currency (₹ / INR), dates, and times.
 */

/**
 * Format price in Indian Rupees (₹ / INR).
 * @param {number} amount - Price amount
 * @returns {string} Formatted currency string (e.g. ₹150.00)
 */
export const formatCurrency = (amount) => {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0.00';
  return `₹${Number(amount).toFixed(2)}`;
};

/**
 * Parse an ISO date/time string safely into a JS Date object.
 * @param {string|Date} isoStr - ISO date string or Date instance
 * @returns {Date} JS Date instance
 */

export const parseDate = (isoStr) => {
  if (!isoStr) return new Date();
  if (isoStr instanceof Date) return isoStr;
  
  // If string does not contain timezone offset (no 'Z' or '+'), treat as local time
  const str = String(isoStr);
  if (str.includes('T') && !str.includes('Z') && !str.includes('+') && !str.includes('-')) {
    // Replace T with space or parse components
    const [datePart, timePart] = str.split('T');
    const [year, month, day] = datePart.split('-').map(Number);
    const [hour, minute, second] = timePart.split(':').map(Number);
    return new Date(year, month - 1, day, hour || 0, minute || 0, second || 0);
  }
  return new Date(isoStr);
};

/**
 * Format a date string into readable Indian English date (e.g. Wed, 23 Sep 2026).
 * @param {string|Date} isoStr - ISO date string
 * @returns {string} Formatted date string
 */
export const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A';
  const d = parseDate(isoStr);
  return d.toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
};

/**
 * Format a time string into 12-hour AM/PM format (e.g. 09:00 AM).
 * @param {string|Date} isoStr - ISO time string
 * @returns {string} Formatted time string
 */
export const formatTime = (isoStr) => {
  if (!isoStr) return 'N/A';
  const d = parseDate(isoStr);
  return d.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
};
