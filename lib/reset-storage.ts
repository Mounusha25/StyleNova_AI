/**
 * Utility to clear all app storage and reset to fresh state
 * Since persistence is removed, this mainly clears any remaining localStorage
 */

// Clear any remaining localStorage keys
function clearAppStorage() {
  // Clear any leftover keys from when persistence was enabled
  const keysToRemove = [
    'quiz-storage',
    'recommendation-storage', 
    'user-storage'
  ];
  
  keysToRemove.forEach(key => {
    localStorage.removeItem(key);
    console.log(`✅ Cleared ${key}`);
  });
  
  // Clear all localStorage to be safe
  localStorage.clear();
  
  console.log('🔄 All storage cleared! App will use fresh data on next load.');
}

// For browser console use
if (typeof window !== 'undefined') {
  (window as any).clearAppStorage = clearAppStorage;
  console.log('💡 To reset app data, run: clearAppStorage()');
}

export { clearAppStorage };