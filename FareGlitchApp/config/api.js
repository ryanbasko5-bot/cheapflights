// API Configuration
// TODO: Update this URL after deploying your backend!

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000'  // Local development
  : 'https://YOUR-BACKEND-URL-HERE';  // Production - CHANGE THIS!

export const API_ENDPOINTS = {
  deals: {
    recent: `${API_BASE_URL}/api/deals/recent`,
    teaser: (dealId) => `${API_BASE_URL}/api/deals/${dealId}/teaser`,
  },
  subscription: {
    subscribe: `${API_BASE_URL}/api/subscribe`,
    checkStatus: `${API_BASE_URL}/api/subscription/status`,
  },
};

export default API_BASE_URL;
