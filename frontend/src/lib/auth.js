const STORAGE_KEY = 'reminda.jwt';

let tokenInMemory = null;

export function initAuth() {
  if (tokenInMemory) {
    return tokenInMemory;
  }

  tokenInMemory = localStorage.getItem(STORAGE_KEY);
  return tokenInMemory;
}

export function setToken(token) {
  tokenInMemory = token;

  if (!token) {
    localStorage.removeItem(STORAGE_KEY);
    return;
  }

  localStorage.setItem(STORAGE_KEY, token);
}

export function getToken() {
  return tokenInMemory ?? initAuth();
}

export function clearToken() {
  tokenInMemory = null;
  localStorage.removeItem(STORAGE_KEY);
}
