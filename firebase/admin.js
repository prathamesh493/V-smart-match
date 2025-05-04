// firebase/admin.js
import { initializeApp, getApps, cert } from 'firebase-admin/app';

// Service account credentials for Firebase Admin SDK
// Either load from environment variables or from a JSON file
const serviceAccount = process.env.FIREBASE_SERVICE_ACCOUNT 
  ? JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT)
  : require('../firebase-service-account.json'); // You'll need to create this file

export const initAdmin = () => {
  // Only initialize if it hasn't been initialized already
  if (getApps().length === 0) {
    initializeApp({
      credential: cert(serviceAccount)
    });
  }
};