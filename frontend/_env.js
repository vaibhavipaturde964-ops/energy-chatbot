/**
 * EcoBot frontend environment configuration.
 *
 * For LOCAL development: edit BACKEND_URL below to point to your local FastAPI server.
 * For VERCEL deployment: Vercel will serve this file as-is, but you should replace
 * the placeholder with your actual Render backend URL before pushing, OR
 * use the Vercel build step to inject it.
 *
 * The GROQ_API_KEY must NEVER appear in this file.
 */
window.__ENV = {
  BACKEND_URL: "http://localhost:8000"   // Replace with your Render URL after deployment
};
