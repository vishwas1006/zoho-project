// frontend/pages/index.tsx

import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();

  const handleLogin = () => {
    window.location.href = "http://localhost:8000/auth/login";
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-10 rounded-2xl shadow-2xl text-center w-96">
        <h1 className="text-3xl font-bold text-white mb-2">Zoho Project Assistant</h1>
        <p className="text-gray-400 mb-8">Manage your projects using natural language</p>
        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition duration-200"
        >
          Login with Zoho
        </button>
      </div>
    </div>
  );
}