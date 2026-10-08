# React frontend

These entry modules point to the canonical authored pages in src/content/dashboard. The existing Data app runtime owns data loading, navigation, filters, source inspection and public hosting. SalesPerformance.jsx, Pipeline.jsx, AIInsights.jsx and DataQuality.jsx are actual page compositions used by DashboardContent.jsx, not separate duplicate apps. The seven views include compensation and project methods.

The public app reads the reviewed snapshot through its same-origin API; it does not call the separate FastAPI service automatically. To switch to live CRM, configure and deploy the backend, validate its data and integrate it through the supported data refresh path. Never embed credentials in frontend code.
