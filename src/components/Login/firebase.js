// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDqpPeRfr3UOhisTPCuVPx3eRyn68DxxX8",
  authDomain: "tthackathon-project-site.firebaseapp.com",
  projectId: "tthackathon-project-site",
  storageBucket: "tthackathon-project-site.firebasestorage.app",
  messagingSenderId: "142048447274",
  appId: "1:142048447274:web:82fc3d9e94a5acca70ac53",
  measurementId: "G-JS8Y812FJG"
};
// init
const app = initializeApp(firebaseConfig);
//auth instance
const auth = getAuth(app);
export { auth };
